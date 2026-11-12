from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from database import SessionDep
from models.autor import (Autor, AutorCreate, AutorUpdate)

router = APIRouter()

autores: list[Autor] = []  # Lista para almacenar los autores

@router.post("/autores", response_model=Autor, status_code=status.HTTP_201_CREATED)
def crear_autor(autor: AutorCreate, session: SessionDep) -> Autor:
    nuevo_autor = Autor.model_validate(autor)  # convierte Create -> tabla
    session.add(nuevo_autor)       # lo deja "en espera"
    session.commit()            # lo guarda de verdad
    session.refresh(nuevo_autor)   # recarga para obtener el id generado
    return nuevo_autor

@router.get("/autores", response_model=list[Autor], status_code=200)
def listar_autores(session: SessionDep) -> list[Autor]:
    autores = session.exec(select(Autor)).all()
    return autores

@router.get("/autores/{autor_id}", response_model=Autor, status_code=200)
def obtener_autor(autor_id: int, session: SessionDep) -> Autor:
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor

@router.put("/autores/{autor_id}", response_model=Autor, status_code=200)
def actualizar_autor(autor_id: int, autor_update: AutorUpdate, session: SessionDep) -> Autor:
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    autor_data = autor_update.model_dump(exclude_unset=True) # Solo obtiene los campos enviados por el cliente

    autor.sqlmodel_update(autor, autor_update)  # Actualiza el objeto con los datos del cliente
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@router.delete("/autores/{autor_id}", status_code=204)
def eliminar_autor(autor_id: int, session: SessionDep):
    autor = session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    session.delete(autor)
    session.commit()
    return None