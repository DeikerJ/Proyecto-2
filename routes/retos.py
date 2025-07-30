from fastapi import APIRouter, Depends, Query
from models.retos import Retos
from typing import Optional, List
from controllers.retos_controller import (
    create_reto,
    get_reto_by_id,
    update_reto,
    delete_reto,
    get_ret_os_by_usuario,
    listar_retos
)
from utils.security import validate_token

router = APIRouter(
    prefix="/retos",
    tags=["retos"]
)

# POST /retos
@router.post("/", response_model=Retos)
async def post_reto(
    reto: Retos,
    user: dict = Depends(validate_token)
):
    reto.usuario_id = user["id"]
    return await create_reto(reto)

# GET /retos/{id}
@router.get("/retos/{id}")
async def get_reto(id: str):
    return await get_reto_by_id(id)

# PUT /retos/{id}
@router.put("/{id}")
async def put_reto(id: str, reto: Retos):
    return await update_reto(id, reto)

# DELETE /retos/{id}
@router.delete("/{id}")
async def delete_reto_endpoint(id: str):
    await delete_reto(id)
    return {"mensaje": "Reto eliminado correctamente"}

# GET /retos
#@router.get("/retos")
#async def get_misr(user: dict = Depends(validate_token)):
 #  return await get_ret_os_by_usuario(user["id"])

@router.get("/retos", response_model=List[Retos])
async def get_retos(
    usuario_id: Optional[str] = Query(
        None, description="Filtra por ID de usuario"
    ),
    categoria_id: Optional[str] = Query(
        None, description="Filtra por ID de categoría"
    )
):
    return await listar_retos(usuario_id, categoria_id)