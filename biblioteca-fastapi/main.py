from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from routers import autores

# Create the application instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: inicializar recursos
    print("Starting up...")
    app.state.db = create_db_and_tables()

    yield # La aplicación sirve solicitudes aquí

    # Shutdown: liberar recursos
    print("Shutting down...")
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

# Router to user endpoints
app.include_router(tags=["Autores"], router=autores.router)


# Define a GET route for the root URL
@app.get("/")
def read_root():
    mensaje = "Etapa 0 trabajo practico"
    return {"message": mensaje}