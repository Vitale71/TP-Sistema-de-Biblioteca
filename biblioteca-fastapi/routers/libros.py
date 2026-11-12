from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from database import SessionDep
from models.libro import (Libro, LibroCreate, LibroUpdate)

router = APIRouter()

@router.post("/libros", status_code=status.HTTP_201_CREATED)
def crear_libro(libro: LibroCreate, session: SessionDep) -> Libro:
    nuevo_libro = Libro.model_validate(libro)  # convierte Create -> tabla
    session.add(nuevo_libro)       # lo deja "en espera"
    session.commit()            # lo guarda de verdad
    session.refresh(nuevo_libro)   # recarga para obtener el id generado
    return nuevo_libro


@router.get("/libros", status_code=200)
def listar_libros(session: SessionDep) -> list[Libro]:
    libros = session.exec(select(Libro)).all()
    return libros


@router.get("/libros/{libro_id}", status_code=200)
def obtener_libro(libro_id: int, session: SessionDep) -> Libro:
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


@router.put("/libros/{libro_id}", status_code=200)
def actualizar_libro(libro_id: int, libro_update: LibroUpdate, session: SessionDep) -> Libro:
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    libro_data = libro_update.model_dump(exclude_unset=True) # Solo obtiene los campos enviados por el cliente

    libro.sqlmodel_update(libro, libro_update)  # Actualiza el objeto con los datos del cliente
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro


@router.delete("/libros/{libro_id}", status_code=204)
def eliminar_libro(libro_id: int, session: SessionDep):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    session.delete(libro)
    session.commit()
    return None