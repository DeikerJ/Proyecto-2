import os
import logging
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# --- 1. Cargar variables de entorno ---
load_dotenv()
URI = os.getenv("MONGODB_URI")

# --- 2. Importar tus módulos (rutas, controladores, etc.) ---
from models.login import Login
from utils.security import validateuser, validateadmin
from controllers.usuarios_controller import login
from routes.Participaciones import router as participaciones_router
from routes.retos import router as retos_router
from routes.comentarios import router as comentarios_router
from routes.categorias import router as categorias_router
from routes.Usuario import router as usuario_router

# --- 3. Inicializar la aplicación FastAPI ---
app = FastAPI(
    title="Altus API",
    description="API para la plataforma de retos Altus.",
    version="1.0.1"
)

# --- 4. Configurar CORS (¡ESTA ES LA CORRECCIÓN PRINCIPAL!) ---
# Se especifican los orígenes permitidos. "*" no funciona con credenciales.
# Esto soluciona el error de CORS que estás viendo.
origins = [
    "http://localhost:5173",  # Origen de tu frontend en desarrollo
    "https://tu-frontend-en-produccion.com" # <-- REEMPLAZA con la URL de tu frontend desplegado
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos los encabezados
)

# --- 5. Definir modelos y endpoints del archivo principal ---
class UsuarioLogin(BaseModel):
    email: str = Field(
        description="Correo electrónico del usuario",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    password: str = Field(
        description="Contraseña del usuario",
        min_length=8,
        max_length=100
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to Altus API"}

@app.post("/login", tags=["Authentication"])
async def login_access(l: Login) -> dict:
    return await login(l)

# --- 6. Incluir los routers de otros módulos ---
# Es buena práctica agrupar rutas con prefijos y etiquetas para la documentación
app.include_router(participaciones_router, prefix="/api/v1", tags=["Participaciones"])
app.include_router(retos_router, prefix="/api/v1", tags=["Retos"])
app.include_router(categorias_router, prefix="/api/v1", tags=["Categorías"])
app.include_router(usuario_router, prefix="/api/v1", tags=["Usuarios"])
app.include_router(comentarios_router, prefix="/api/v1", tags=["Comentarios"])

# --- 7. Endpoints de monitoreo (Health & Readiness) ---
@app.get("/health", tags=["Monitoring"])
def health_check():
    return {"status": "healthy"}

@app.get("/ready", tags=["Monitoring"])
def readiness_check():
    try:
        # Aquí deberías tener una función que verifique la conexión a la BD
        # from utils.mongodb import test_connection
        # test_connection()
        return {"status": "ready", "dependencies": {"database": "connected"}}
    except Exception as e:
        logging.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}

# --- 8. Bloque de ejecución principal (debe ir al final del todo) ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port,reload=True)