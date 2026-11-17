from sqlmodel import Field, SQLModel
from datetime import date

class PrestamoBase(SQLModel):
    socio_id: int
    libro_id: int
    
class PrestamoCreate(PrestamoBase):
    pass  # Recibe únicamente socio_id y libro_id del cliente

class Prestamo(PrestamoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socio.id")
    libro_id: int = Field(foreign_key="libro.id")
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None  # Puede ser nula si no se ha devuelto aún
    multa: int | None = 0  # Puede ser nula si no hay multa, por defecto es 0

class PrestamoPublic(PrestamoBase):
    id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: int = 0