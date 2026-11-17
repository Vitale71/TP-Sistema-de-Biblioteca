from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from database import SessionDep
from models.prestamo import Prestamo, PrestamoCreate, PrestamoPublic
from services import prestamos as prestamos_service # Importar la función desde services/prestamos.py

router = APIRouter()

@router.post("/prestamos", response_model=PrestamoPublic, status_code=status.HTTP_201_CREATED)
def crear_prestamo(data: PrestamoCreate, session: SessionDep) -> PrestamoPublic:
    prestamo = prestamos_service.crear_prestamo(session, data.socio_id, data.libro_id)
    return prestamo


@router.get("/prestamos", response_model=list[PrestamoPublic], status_code=200)
def listar_prestamos(session: SessionDep) -> list[PrestamoPublic]:
    prestamos = session.exec(select(Prestamo)).all()
    return [PrestamoPublic.model_validate(p) for p in prestamos]
