import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from database import get_session
from main import app

# Importar los modelos para que SQLModel conozca todas las tablas
# y create_all las cree en la base de prueba.
import models.autor  # noqa: F401
import models.libro  # noqa: F401
import models.libro_autor  # noqa: F401
import models.prestamo  # noqa: F401
import models.socio  # noqa: F401


# Una "fixture" es una función que prepara algo para los tests.
# Cualquier test que la pida como parámetro la recibe lista para usar.
@pytest.fixture(name="session")
def session_fixture():
    # "sqlite://" (sin nombre de archivo) = base de datos en memoria.
    # StaticPool hace que todas las conexiones compartan esa misma base.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Al terminar el test, la base en memoria desaparece sola:
    # cada test arranca con todo vacío.


@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Reemplazamos get_session por una versión que devuelve la sesión
    # de prueba. Así los endpoints usan la base en memoria sin que
    # haya que cambiar nada en su código.
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # Sin "with", TestClient no ejecuta el lifespan: no se crea
    # biblioteca.db durante los tests.
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
