from sqlmodel import Field, SQLModel

class SocioBase(SQLModel):
    nombre: str
    email: str 
    activo: bool = True  # Por defecto, el socio está activo

class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)  # no puede repetirse en la tabla


class SocioCreate(SocioBase):
    pass

class SocioUpdate(SQLModel):
    nombre: str | None = None
    email: str | None = None
    activo: bool | None = None