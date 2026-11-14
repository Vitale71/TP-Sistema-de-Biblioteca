from sqlmodel import Field, SQLModel

class LibroBase(SQLModel):
    titulo: str
    isbn: str
    stock: int = Field(ge=0) # ge = "greater or equal": mínimo 0
    anio: int

class Libro(LibroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True)  # no puede repetirse en la tabla
    stock: int

class LibroCreate(LibroBase):
    pass

class LibroUpdate(SQLModel):
    titulo: str | None = None
    isbn: str | None = None
    stock: int | None = Field(default=None, ge=0)
    anio: int | None = None