from sqlmodel import Field, SQLModel

class LibroBase(SQLModel):
    titulo: str
    isbn: str
    stock: int
    anio_publicacion: int

class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True)  # no puede repetirse en la tabla
    stock: int = Field(ge=0)  # ge = "greater or equal": mínimo 0

class LibroCreate(LibroBase):
    pass

class LibroUpdate(SQLModel):
    titulo: str | None = None
    isbn: str | None = None
    stock: int | None = None
    anio_publicacion: int | None = None