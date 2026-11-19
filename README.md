# Sistema de Biblioteca (FastAPI + SQLModel)

API REST para gestionar el catálogo de una biblioteca (autores, libros y
socios) y sus préstamos, con reglas de negocio y códigos HTTP específicos.

## Requisitos

- Python 3.12 o superior

## Cómo correr el proyecto

Desde la carpeta `biblioteca-fastapi`:

```bash
cd biblioteca-fastapi

# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activarlo
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Levantar el servidor
fastapi dev main.py
```

- API: http://127.0.0.1:8000
- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs

Al arrancar se crea automáticamente la base de datos SQLite
`biblioteca.db` con todas las tablas. Si se modifica la estructura de un
modelo, hay que borrar ese archivo (con el servidor apagado) para que se
regenere.

## Cómo correr los tests

Con el entorno virtual activado, desde la carpeta `biblioteca-fastapi`:

```bash
pytest
```

Los tests usan una base de datos **en memoria**, por lo que no tocan
`biblioteca.db`. Al terminar, la terminal muestra el reporte de cobertura
(la consigna pide al menos 80 %).

## Estructura

```
biblioteca-fastapi/
├── main.py              # Aplicación FastAPI y registro de routers
├── database.py          # Conexión y sesión de base de datos
├── models/              # Modelos SQLModel (tablas y esquemas)
├── routers/             # Endpoints HTTP, uno por entidad
├── services/            # Reglas de negocio de los préstamos
├── tests/               # Tests con pytest
├── pytest.ini           # Configuración de pytest y cobertura
└── requirements.txt
```

## Endpoints

| Recurso | Endpoints |
|---|---|
| Autores | `POST /autores`, `GET /autores`, `GET/PUT/DELETE /autores/{id}` |
| Libros | `POST /libros`, `GET /libros` (`?disponibles=true`), `GET/PUT/DELETE /libros/{id}` |
| Libro-Autor | `POST /libros/{id}/autores/{autor_id}` |
| Socios | `POST /socios`, `GET /socios`, `GET/PUT/DELETE /socios/{id}` |
| Préstamos de un socio | `GET /socios/{id}/prestamos` (`?activos=true`) |
| Préstamos | `POST /prestamos`, `GET /prestamos`, `POST /prestamos/{id}/devolucion` |

## Reglas de negocio

Implementadas en `services/prestamos.py`:

| # | Regla | Error |
|---|---|---|
| 1 | Un socio no puede tener más de 3 préstamos activos | 409 |
| 2 | No se presta un libro sin stock; al prestar se descuenta 1 | 409 |
| 3 | Un socio inactivo no puede pedir préstamos | 403 |
| 4 | El plazo es de 14 días (`fecha_vencimiento = fecha_prestamo + 14`) | - |
| 5 | Al devolver se repone el stock y se calcula la multa: $100 por día de atraso | - |
| 6 | No se puede devolver un préstamo ya devuelto | 409 |
| 7 | Recurso inexistente | 404 |
| 8 | ISBN o email duplicado | 409 |

Un stock negativo se rechaza con `422` (validación de datos).
