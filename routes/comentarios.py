from fastapi import APIRouter, HTTPException, Request, Depends
from models.comentarios import comentarios
from controllers.comentarios_controller import (
    create_comentario,
    #get_comentarios_de_reto,
    #delete_comentario
)

router = APIRouter(
    prefix="/comentarios",
    tags=["comentarios"]
)

@router.post("/", response_model=comentarios)
async def crear_comentario(comentario: comentarios):
    return await create_comentario(comentario)

#@router.get("/reto/{reto_id}", response_model=list[Comentario])
#async def obtener_comentarios_de_reto(reto_id: str):
 #   return await get_comentarios_de_reto(reto_id)         (Lo dejo comentado porque no quiero pasar el limite de 16 endpoints por ahora)

#@router.delete("/{comentario_id}", response_model=dict)
#sync def eliminar_comentario(comentario_id: str):
 #   return await delete_comentario(comentario_id)
