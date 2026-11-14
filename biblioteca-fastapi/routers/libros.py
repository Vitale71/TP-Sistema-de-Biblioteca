from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from database import SessionDep
from models.autor import Autor
from models.libro import (Libro, LibroCreate, LibroUpdate)

router = APIRouter()

@router.post("/libros", status_code=status.HTTP_201_CREATED)
def crear_libro(libro: LibroCreate, session: SessionDep) -> Libro:
    nuevo_libro = Libro.model_validate(libro)  # convierte Create -> tabla
    try:
        session.add(nuevo_libro)       # lo deja "en espera"
        session.commit()            # lo guarda de verdad
        session.refresh(nuevo_libro)   # recarga para obtener el id generado
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Codigo ISBN ya existe")
    return nuevo_libro

@router.post("/libros/{libro_id}/autores/{autor_id}", status_code=status.HTTP_201_CREATED)
def asociar_autor_a_libro(libro_id: int, autor_id: int, session: SessionDep):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    if autor in libro.autores:
        raise HTTPException(status_code=409, detail="El autor ya está asociado a este libro")
    
    # Asociar el autor al libro
    libro.autores.append(autor) # SQLModel inserta la fila intermedia
    session.add(libro)
    session.commit()
    session.refresh(libro)
    
    return {"message": f"Autor {autor_id} asociado al libro {libro_id}"}



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

    libro.sqlmodel_update(libro_data)  # Actualiza el objeto con los datos del cliente
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