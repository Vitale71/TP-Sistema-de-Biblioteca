from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# Dónde se guarda la base: un archivo SQLite en la carpeta del proyecto
DATABASE_URL = "sqlite:///biblioteca.db"

# El "engine" es la conexión con la base de datos
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    # Crea las tablas de todos los modelos con table=True (si no existen)
    SQLModel.metadata.create_all(engine)


def get_session():
    # Abre una sesión, se la presta al endpoint y la cierra al terminar
    with Session(engine) as session:
        yield session


# Atajo para no repetir Depends(get_session) en cada endpoint
SessionDep = Annotated[Session, Depends(get_session)]