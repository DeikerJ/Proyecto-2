from fastapi import FastAPI,Request
from pydantic import BaseModel, Field
import os 
from models.login import Login
from utils.security import validateuser, validateadmin
from controllers.usuarios_controller import create_user, login
import logging
import uvicorn

from routes.Participaciones import router as participaciones_router
from routes.retos import router as retos_router
from routes.comentarios import router as comentarios_router
from routes.categorias import router as categorias_router
from routes.Usuario import router as usuario_router
from dotenv import load_dotenv


load_dotenv()

URI = os.getenv("MONGODB_URI")

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],

)


@app.get("/")
def read_root():
    return {"version": "0.0.0"}

app.include_router(participaciones_router)
app.include_router(retos_router)
app.include_router(categorias_router)
app.include_router(usuario_router)
app.include_router(comentarios_router)


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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
def read_root():
    return {"version": "0.0.0"}


@app.post("/login")
async def login_access(l: Login) -> dict:
    return await login(l)

@app.get("/exampleuser")
@validateuser
async def exampleuser(request:Request):
    return {
        "message": "This is an example endpoint that requires user validation.",
        "email": request.state.email
    }
     
@app.get("/exampleadmin")
@validateadmin
async def exampleadmin(request:Request):
    return {
        "message": "This is an example endpoint that requires admin validation.",
        "admin": request.state.admin
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
    @app.get("/health")
    def health_check():
      try:
         return{
            "status":"healthy",
            "timestamp":"2025-08-12",
            "service":"Altus",
            "environment":"production"
        }
        
      except Exception as e:
        return{"status:unhealthy","error",str(e)}   
    
    
@app.get("/ready")
def readiness_check():
    try:
        from utils.mongodb import test_connection
        db_status = test_connection()
        return{
            "status":"ready" if db_status else "not_ready",
            "database":"connected" if db_status else "disconnected",
            "service": "Altus"
        }
    except Exception as e:
        return {"status":"not_ready","error":str(e)} 
        