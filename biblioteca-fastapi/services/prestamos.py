from datetime import date, timedelta

from fastapi import HTTPException
from sqlmodel import Session, col, select

from models.libro import Libro
from models.prestamo import Prestamo, PrestamoCreate
from models.socio import Socio

# Reglas de negocio como constantes
PLAZO_DIAS = 14
MULTA_POR_DIA = 100
MAX_PRESTAMOS_ACTIVOS = 3

def crear_prestamo(session: Session, socio_id: int, libro_id: int, hoy: date | None = None,) -> Prestamo:
    hoy = hoy or date.today()

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

    if len(activos) >= MAX_PRESTAMOS_ACTIVOS:
        raise HTTPException(status_code=409, detail="El socio ya tiene el máximo de préstamos activos",)

    libro.stock -= 1  # Disminuir el stock del libro
    prestamo = Prestamo(
        socio_id=socio_id,
        libro_id=libro_id,
        fecha_prestamo=hoy,
        fecha_vencimiento=hoy + timedelta(days=PLAZO_DIAS),
    )

    session.add(prestamo)
    session.add(libro)  # Asegurarse de que el cambio en el stock se guarde
    session.commit()    # un solo commit: se guarda todo o nada
    session.refresh(prestamo)

    return prestamo

def devolver_libro(session: Session, prestamo_id: int, hoy: date| None = None,) -> Prestamo:
    hoy = hoy or date.today()  # Si no se proporciona una fecha, usar la fecha actual

    prestamo = session.get(Prestamo, prestamo_id)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    
    if prestamo.fecha_devolucion is not None:
        raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")

    dias_atraso = max(0, (hoy - prestamo.fecha_vencimiento).days)
    prestamo.fecha_devolucion = hoy
    prestamo.multa = dias_atraso * MULTA_POR_DIA
    
    libro = session.get(Libro, prestamo.libro_id)
    if libro:
        libro.stock += 1
        session.add(libro)

    session.add(prestamo)
    session.commit()
    session.refresh(prestamo)
    return prestamo


def listar_prestamos_de_socio(
    session: Session,
    socio_id: int,
    solo_activos: bool = False,
) -> list[Prestamo]:
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    # Consulta armada por partes: la condición extra se suma si hace falta
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if solo_activos:
        consulta = consulta.where(col(Prestamo.fecha_devolucion).is_(None))

    return list(session.exec(consulta).all())