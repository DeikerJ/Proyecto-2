from fastapi import APIRouter
from models.usuarios import Usuario
from controllers.usuarios_controller import create_user  

router = APIRouter()

@router.post("/usuarios/", response_model=Usuario)
async def register_user(user: Usuario):
    return await create_user(user)


