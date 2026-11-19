from fastapi import APIRouter, status
from sqlmodel import select
from database import SessionDep
from models.prestamo import Prestamo, PrestamoCreate, PrestamoPublic
from services import prestamos as prestamos_service # Importar la función desde services/prestamos.py

router = APIRouter()

# El router solo habla HTTP: recibe, llama al service y devuelve.
# Las reglas de negocio viven en services/prestamos.py
@router.post("/prestamos", response_model=PrestamoPublic, status_code=status.HTTP_201_CREATED)
def crear_prestamo(data: PrestamoCreate, session: SessionDep) -> PrestamoPublic:
    return prestamos_service.crear_prestamo(session, data.socio_id, data.libro_id)


@router.get("/prestamos", response_model=list[PrestamoPublic])
def listar_prestamos(session: SessionDep) -> list[Prestamo]:
    return list(session.exec(select(Prestamo)).all())


# prestamo_id viene de la URL (está entre llaves en la ruta).
# Este endpoint no recibe body.
@router.post("/prestamos/{prestamo_id}/devolucion", response_model=PrestamoPublic, status_code=status.HTTP_200_OK,)
def devolver_libro(prestamo_id: int, session: SessionDep) -> Prestamo:
    return prestamos_service.devolver_libro(session, prestamo_id)