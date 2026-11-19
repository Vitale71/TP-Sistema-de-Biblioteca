"""Funciones auxiliares para preparar datos de prueba usando la API."""


def crear_autor(client, nombre="Jorge Luis Borges", nacionalidad="Argentina"):
    resp = client.post(
        "/autores", json={"nombre": nombre, "nacionalidad": nacionalidad}
    )
    assert resp.status_code == 201
    return resp.json()


def crear_libro(
    client, isbn="978-0-0000-0001", stock=1, titulo="Ficciones", anio=1944
):
    resp = client.post(
        "/libros",
        json={"titulo": titulo, "isbn": isbn, "stock": stock, "anio": anio},
    )
    assert resp.status_code == 201
    return resp.json()


def crear_socio(client, email="ana@test.com", activo=True):
    resp = client.post("/socios", json={"nombre": "Ana", "email": email})
    assert resp.status_code == 201
    socio = resp.json()
    if not activo:
        resp = client.put(f"/socios/{socio['id']}", json={"activo": False})
        assert resp.status_code == 200
        socio = resp.json()
    return socio


def pedir_prestamo(client, socio_id, libro_id):
    return client.post(
        "/prestamos", json={"socio_id": socio_id, "libro_id": libro_id}
    )


def stock_de(client, libro_id):
    return client.get(f"/libros/{libro_id}").json()["stock"]
