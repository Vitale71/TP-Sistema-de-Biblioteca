from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from database import SessionDep
from models.socio import (Socio, SocioCreate, SocioUpdate)

router = APIRouter()

@router.post("/socios", status_code=status.HTTP_201_CREATED)
def crear_socio(socio: SocioCreate, session: SessionDep) -> Socio:
    nuevo_socio = Socio.model_validate(socio)  # convierte Create -> tabla
    try:
        session.add(nuevo_socio)       # lo deja "en espera"
        session.commit()            # lo guarda de verdad
        session.refresh(nuevo_socio)   # recarga para obtener el id generado
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email ya existe")
    return nuevo_socio  

@router.get("/socios", status_code=200)
def listar_socios(session: SessionDep) -> list[Socio]:
    socios = session.exec(select(Socio)).all()
    return socios

@router.get("/socios/{socio_id}", status_code=200)
def obtener_socio(socio_id: int, session: SessionDep) -> Socio:
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    return socio

@router.put("/socios/{socio_id}", status_code=200)
def actualizar_socio(socio_id: int, socio_update: SocioUpdate, session: SessionDep) -> Socio:
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    socio_data = socio_update.model_dump(exclude_unset=True) # Solo obtiene los campos enviados por el cliente

    socio.sqlmodel_update(socio_data)  # Actualiza el objeto con los datos del cliente
    session.add(socio)
    session.commit()
    session.refresh(socio)
    return socio

@router.delete("/socios/{socio_id}", status_code=204)
def eliminar_socio(socio_id: int, session: SessionDep):
    socio = session.get(Socio, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    
    session.delete(socio)
    session.commit()
    return None