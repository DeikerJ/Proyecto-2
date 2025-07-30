from fastapi import APIRouter
from models.participaciones import Participacion
from controllers.participaciones_controller import crear_participacion

router = APIRouter(
    prefix="/participaciones",
    tags=["participaciones"]
)

@router.post("/", response_model=Participacion)
async def post_participacion(participacion: Participacion):
    return await crear_participacion(participacion)