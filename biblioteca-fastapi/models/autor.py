from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel
if TYPE_CHECKING:
    from models.libro import Libro


class AutorBase(SQLModel):
    # Campos que comparten todas las versiones
    nombre: str
    nacionalidad: str


class Autor(AutorBase, table=True):
    # table=True => esta clase ES una tabla en la base de datos
    id: int | None = Field(default=None, primary_key=True)
    autores: list["Libro"] = Relationship(
        back_populates="autor", link_model="LibroAutor"
    )


class AutorCreate(AutorBase):
    # Lo que el cliente manda al crear (sin id)
    pass


class AutorUpdate(SQLModel):
    # Para modificar: todos los campos son opcionales
    nombre: str | None = None
    nacionalidad: str | None = None


class AutorPublic(AutorBase):
    # Lo que el cliente recibe al pedir un autor
    id: int