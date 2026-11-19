from datetime import date, timedelta

import pytest

from services import prestamos as service
from tests.helpers import (
    crear_libro,
    crear_socio,
    pedir_prestamo,
    stock_de,
)


# ------------------ Préstamo exitoso (reglas 2 y 4) ------------------


def test_prestamo_exitoso_descuenta_stock_y_fija_vencimiento(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=2)

    resp = pedir_prestamo(client, socio["id"], libro["id"])

    assert resp.status_code == 201
    data = resp.json()
    assert data["multa"] == 0
    assert data["fecha_devolucion"] is None
    # Regla 4: vencimiento = fecha del préstamo + 14 días
    prestamo = date.fromisoformat(data["fecha_prestamo"])
    vencimiento = date.fromisoformat(data["fecha_vencimiento"])
    assert vencimiento == prestamo + timedelta(days=14)
    # Regla 2: al prestar se descuenta 1
    assert stock_de(client, libro["id"]) == 1


def test_regla4_plazo_de_14_dias_con_fecha_simulada(client, session):
    socio = crear_socio(client)
    libro = crear_libro(client)

    prestamo = service.crear_prestamo(
        session, socio["id"], libro["id"], hoy=date(2026, 3, 1)
    )

    assert prestamo.fecha_prestamo == date(2026, 3, 1)
    assert prestamo.fecha_vencimiento == date(2026, 3, 15)


def test_listar_prestamos(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=2)
    pedir_prestamo(client, socio["id"], libro["id"])

    resp = client.get("/prestamos")

    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ---------- Regla 1: máximo 3 préstamos activos por socio ----------


def test_regla1_tres_prestamos_permitidos_y_el_cuarto_rechazado(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=10)

    for _ in range(3):
        assert pedir_prestamo(client, socio["id"], libro["id"]).status_code == 201

    resp = pedir_prestamo(client, socio["id"], libro["id"])

    assert resp.status_code == 409
    # El préstamo rechazado no debe descontar stock
    assert stock_de(client, libro["id"]) == 7


def test_regla1_el_limite_es_por_socio(client):
    socio1 = crear_socio(client, email="uno@test.com")
    socio2 = crear_socio(client, email="dos@test.com")
    libro = crear_libro(client, stock=10)
    for _ in range(3):
        pedir_prestamo(client, socio1["id"], libro["id"])

    resp = pedir_prestamo(client, socio2["id"], libro["id"])

    assert resp.status_code == 201


def test_regla1_devolver_libera_cupo(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=10)
    ids = [
        pedir_prestamo(client, socio["id"], libro["id"]).json()["id"]
        for _ in range(3)
    ]
    assert pedir_prestamo(client, socio["id"], libro["id"]).status_code == 409

    assert client.post(f"/prestamos/{ids[0]}/devolucion").status_code == 200

    assert pedir_prestamo(client, socio["id"], libro["id"]).status_code == 201


# ------------------ Regla 2: sin stock no se presta ------------------


def test_regla2_libro_sin_stock_devuelve_409(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=0)

    resp = pedir_prestamo(client, socio["id"], libro["id"])

    assert resp.status_code == 409
    assert stock_de(client, libro["id"]) == 0


def test_regla2_el_ultimo_ejemplar_se_presta_una_sola_vez(client):
    socio1 = crear_socio(client, email="uno@test.com")
    socio2 = crear_socio(client, email="dos@test.com")
    libro = crear_libro(client, stock=1)

    assert pedir_prestamo(client, socio1["id"], libro["id"]).status_code == 201
    assert stock_de(client, libro["id"]) == 0
    assert pedir_prestamo(client, socio2["id"], libro["id"]).status_code == 409


# --------------- Regla 3: socio inactivo no puede pedir ---------------


def test_regla3_socio_inactivo_devuelve_403(client):
    socio = crear_socio(client, activo=False)
    libro = crear_libro(client, stock=1)

    resp = pedir_prestamo(client, socio["id"], libro["id"])

    assert resp.status_code == 403
    assert stock_de(client, libro["id"]) == 1


# -------------------- Regla 5: devolución y multa --------------------


def test_regla5_devolucion_a_tiempo_repone_stock_sin_multa(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=1)
    prestamo = pedir_prestamo(client, socio["id"], libro["id"]).json()
    assert stock_de(client, libro["id"]) == 0

    resp = client.post(f"/prestamos/{prestamo['id']}/devolucion")

    assert resp.status_code == 200
    data = resp.json()
    assert data["fecha_devolucion"] == date.today().isoformat()
    assert data["multa"] == 0
    assert stock_de(client, libro["id"]) == 1


# Cada caso: (días de diferencia respecto al vencimiento, multa esperada)
@pytest.mark.parametrize(
    "dias_respecto_al_vencimiento, multa_esperada",
    [
        (-3, 0),  # devuelve antes de tiempo
        (0, 0),  # devuelve justo el día del vencimiento
        (1, 100),  # 1 día de atraso
        (5, 500),  # 5 días de atraso
    ],
)
def test_regla5_calculo_de_multa(
    client, session, dias_respecto_al_vencimiento, multa_esperada
):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=1)
    prestamo = service.crear_prestamo(
        session, socio["id"], libro["id"], hoy=date(2026, 1, 1)
    )
    assert prestamo.id is not None
    fecha_devolucion = prestamo.fecha_vencimiento + timedelta(
        days=dias_respecto_al_vencimiento
    )

    devuelto = service.devolver_libro(
        session, prestamo.id, hoy=fecha_devolucion
    )

    assert devuelto.multa == multa_esperada
    assert devuelto.fecha_devolucion == fecha_devolucion
    assert stock_de(client, libro["id"]) == 1


# -------------- Regla 6: no se devuelve dos veces --------------


def test_regla6_devolver_un_prestamo_ya_devuelto_devuelve_409(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=1)
    prestamo = pedir_prestamo(client, socio["id"], libro["id"]).json()
    client.post(f"/prestamos/{prestamo['id']}/devolucion")

    resp = client.post(f"/prestamos/{prestamo['id']}/devolucion")

    assert resp.status_code == 409
    # La segunda devolución no debe volver a sumar stock
    assert stock_de(client, libro["id"]) == 1


# ------------------ Regla 7: recurso inexistente ------------------


def test_regla7_prestamo_con_socio_inexistente_devuelve_404(client):
    libro = crear_libro(client)
    assert pedir_prestamo(client, 999, libro["id"]).status_code == 404


def test_regla7_prestamo_con_libro_inexistente_devuelve_404(client):
    socio = crear_socio(client)
    assert pedir_prestamo(client, socio["id"], 999).status_code == 404


def test_regla7_devolver_prestamo_inexistente_devuelve_404(client):
    assert client.post("/prestamos/999/devolucion").status_code == 404


def test_regla7_prestamos_de_socio_inexistente_devuelve_404(client):
    assert client.get("/socios/999/prestamos").status_code == 404


# ---------- Préstamos de un socio (con filtro de activos) ----------


def test_prestamos_del_socio_con_y_sin_filtro_de_activos(client):
    socio = crear_socio(client)
    libro = crear_libro(client, stock=5)
    devuelto = pedir_prestamo(client, socio["id"], libro["id"]).json()
    activo = pedir_prestamo(client, socio["id"], libro["id"]).json()
    client.post(f"/prestamos/{devuelto['id']}/devolucion")

    todos = client.get(f"/socios/{socio['id']}/prestamos")
    activos = client.get(f"/socios/{socio['id']}/prestamos?activos=true")

    assert todos.status_code == 200
    assert len(todos.json()) == 2
    assert activos.status_code == 200
    assert [p["id"] for p in activos.json()] == [activo["id"]]


def test_prestamos_del_socio_no_incluye_los_de_otros_socios(client):
    socio1 = crear_socio(client, email="uno@test.com")
    socio2 = crear_socio(client, email="dos@test.com")
    libro = crear_libro(client, stock=5)
    pedir_prestamo(client, socio1["id"], libro["id"])

    resp = client.get(f"/socios/{socio2['id']}/prestamos")

    assert resp.json() == []
