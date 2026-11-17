from datetime import date, timedelta

from fastapi import HTTPException
from requests import session
from sqlmodel import Session, col, select

from models.libro import Libro
from models.prestamo import Prestamo
from models.socio import Socio

def crear_prestamo(session: Session, socio_id: int, libro_id: int, hoy: date | None = None) -> Prestamo:
    hoy = hoy or date.today()  # Si no se proporciona una fecha, usar la fecha actual

    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    if not socio.activo:
        raise HTTPException(status_code=403, detail="El socio no está activo")

    if libro.stock == 0:
        raise HTTPException(status_code=409, detail="No hay stock de este libro")


    activos = session.exec(
        select(Prestamo).where(
            Prestamo.socio_id == socio_id, 
            col(Prestamo.fecha_devolucion).is_(None),
        )
    ).all()

    if len(activos) >= 3:
        raise HTTPException(status_code=409, detail="El socio ya tiene libros pendientes de devolución")

    libro.stock -= 1  # Disminuir el stock del libro
    prestamo = Prestamo(
        socio_id=socio_id,
        libro_id=libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=14),
        fecha_devolucion=None,
        multa=0
    )

    session.add(prestamo)
    session.add(libro)  # Asegurarse de que el cambio en el stock se guarde
    session.commit()    # un solo commit: se guarda todo o nada
    session.refresh(prestamo)

    return prestamo