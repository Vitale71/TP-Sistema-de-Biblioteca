from tests.helpers import crear_autor, crear_libro, crear_socio


def test_raiz(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()


# ---------------------------- Autores ----------------------------


def test_crear_autor(client):
    resp = client.post(
        "/autores",
        json={"nombre": "Julio Cortázar", "nacionalidad": "Argentina"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["nombre"] == "Julio Cortázar"


def test_listar_y_obtener_autor(client):
    autor = crear_autor(client)

    listado = client.get("/autores")
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == autor["id"]

    detalle = client.get(f"/autores/{autor['id']}")
    assert detalle.status_code == 200
    assert detalle.json()["nombre"] == autor["nombre"]


def test_actualizar_autor_solo_cambia_lo_enviado(client):
    autor = crear_autor(client, nacionalidad="Argentina")

    resp = client.put(f"/autores/{autor['id']}", json={"nombre": "J. L. B."})

    assert resp.status_code == 200
    assert resp.json()["nombre"] == "J. L. B."
    assert resp.json()["nacionalidad"] == "Argentina"


def test_eliminar_autor(client):
    autor = crear_autor(client)

    resp = client.delete(f"/autores/{autor['id']}")

    assert resp.status_code == 204
    assert client.get(f"/autores/{autor['id']}").status_code == 404


def test_autor_inexistente_devuelve_404(client):
    assert client.get("/autores/999").status_code == 404
    assert client.put("/autores/999", json={"nombre": "X"}).status_code == 404
    assert client.delete("/autores/999").status_code == 404


# ----------------------------- Libros -----------------------------


def test_crear_y_obtener_libro(client):
    libro = crear_libro(client, stock=3)

    resp = client.get(f"/libros/{libro['id']}")

    assert resp.status_code == 200
    assert resp.json()["stock"] == 3
    assert resp.json()["autores"] == []


def test_libro_con_isbn_duplicado_devuelve_409(client):
    crear_libro(client, isbn="111")

    resp = client.post(
        "/libros",
        json={"titulo": "Otro", "isbn": "111", "stock": 1, "anio": 2000},
    )

    assert resp.status_code == 409


def test_libro_con_stock_negativo_devuelve_422(client):
    resp = client.post(
        "/libros",
        json={"titulo": "Malo", "isbn": "222", "stock": -3, "anio": 2000},
    )
    assert resp.status_code == 422


def test_actualizar_libro(client):
    libro = crear_libro(client, stock=1)

    resp = client.put(f"/libros/{libro['id']}", json={"stock": 7})

    assert resp.status_code == 200
    assert resp.json()["stock"] == 7
    assert resp.json()["titulo"] == libro["titulo"]


def test_actualizar_libro_con_stock_negativo_devuelve_422(client):
    libro = crear_libro(client)
    resp = client.put(f"/libros/{libro['id']}", json={"stock": -1})
    assert resp.status_code == 422


def test_actualizar_libro_con_isbn_duplicado_devuelve_409(client):
    crear_libro(client, isbn="AAA")
    otro = crear_libro(client, isbn="BBB")

    resp = client.put(f"/libros/{otro['id']}", json={"isbn": "AAA"})

    assert resp.status_code == 409


def test_eliminar_libro(client):
    libro = crear_libro(client)

    assert client.delete(f"/libros/{libro['id']}").status_code == 204
    assert client.get(f"/libros/{libro['id']}").status_code == 404


def test_libro_inexistente_devuelve_404(client):
    assert client.get("/libros/999").status_code == 404
    assert client.put("/libros/999", json={"stock": 1}).status_code == 404
    assert client.delete("/libros/999").status_code == 404


def test_filtro_libros_disponibles(client):
    crear_libro(client, isbn="CON-STOCK", stock=2)
    crear_libro(client, isbn="SIN-STOCK", stock=0)

    todos = client.get("/libros")
    disponibles = client.get("/libros?disponibles=true")

    assert len(todos.json()) == 2
    assert len(disponibles.json()) == 1
    assert disponibles.json()[0]["isbn"] == "CON-STOCK"


# ----------------------------- Socios -----------------------------


def test_crear_socio_queda_activo_por_defecto(client):
    resp = client.post(
        "/socios", json={"nombre": "Luis", "email": "luis@test.com"}
    )
    assert resp.status_code == 201
    assert resp.json()["activo"] is True


def test_socio_con_email_duplicado_devuelve_409(client):
    crear_socio(client, email="dup@test.com")

    resp = client.post(
        "/socios", json={"nombre": "Otro", "email": "dup@test.com"}
    )

    assert resp.status_code == 409


def test_listar_y_obtener_socio(client):
    socio = crear_socio(client)

    assert len(client.get("/socios").json()) == 1
    resp = client.get(f"/socios/{socio['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == socio["email"]


def test_actualizar_socio(client):
    socio = crear_socio(client)

    resp = client.put(f"/socios/{socio['id']}", json={"nombre": "Ana María"})

    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Ana María"


def test_actualizar_socio_con_email_duplicado_devuelve_409(client):
    crear_socio(client, email="uno@test.com")
    otro = crear_socio(client, email="dos@test.com")

    resp = client.put(f"/socios/{otro['id']}", json={"email": "uno@test.com"})

    assert resp.status_code == 409


def test_eliminar_socio(client):
    socio = crear_socio(client)

    assert client.delete(f"/socios/{socio['id']}").status_code == 204
    assert client.get(f"/socios/{socio['id']}").status_code == 404


def test_socio_inexistente_devuelve_404(client):
    assert client.get("/socios/999").status_code == 404
    assert client.put("/socios/999", json={"nombre": "X"}).status_code == 404
    assert client.delete("/socios/999").status_code == 404


# ------------------------ Relación Libro-Autor ------------------------


def test_asociar_autor_a_libro(client):
    libro = crear_libro(client)
    autor = crear_autor(client)

    resp = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")

    assert resp.status_code == 201
    assert [a["id"] for a in resp.json()["autores"]] == [autor["id"]]


def test_libro_muestra_sus_autores(client):
    libro = crear_libro(client)
    autor1 = crear_autor(client, nombre="Autor Uno")
    autor2 = crear_autor(client, nombre="Autor Dos")
    client.post(f"/libros/{libro['id']}/autores/{autor1['id']}")
    client.post(f"/libros/{libro['id']}/autores/{autor2['id']}")

    detalle = client.get(f"/libros/{libro['id']}").json()
    listado = client.get("/libros").json()

    assert len(detalle["autores"]) == 2
    assert len(listado[0]["autores"]) == 2


def test_asociar_autor_repetido_devuelve_409(client):
    libro = crear_libro(client)
    autor = crear_autor(client)
    client.post(f"/libros/{libro['id']}/autores/{autor['id']}")

    resp = client.post(f"/libros/{libro['id']}/autores/{autor['id']}")

    assert resp.status_code == 409


def test_asociar_con_libro_o_autor_inexistente_devuelve_404(client):
    libro = crear_libro(client)
    autor = crear_autor(client)

    assert client.post(f"/libros/999/autores/{autor['id']}").status_code == 404
    assert client.post(f"/libros/{libro['id']}/autores/999").status_code == 404
