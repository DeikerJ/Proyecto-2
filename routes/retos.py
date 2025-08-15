from fastapi import APIRouter, Depends, Query, HTTPException
from models.retos import Retos
from typing import Optional, List
from controllers.retos_controller import (
    create_reto,
    get_reto_by_id,
    update_reto,
    delete_reto,
    listar_retos
)
from utils.security import validate_token
from pydantic import BaseModel

router = APIRouter(
    prefix="/retos",
    tags=["retos"]
)

# Modelo para actualización parcial
class RetoUpdateParcial(BaseModel):
    activo: Optional[bool] = None

# POST /retos
@router.post("/", response_model=Retos)
async def post_reto(
    reto: Retos,
    user: dict = Depends(validate_token)
):
    reto.usuario_id = user["id"]
    return await create_reto(reto)

# GET /retos/{id}
@router.get("/{id}")
async def get_reto(id: str):
    reto = await get_reto_by_id(id)
    if not reto:
        raise HTTPException(status_code=404, detail="Reto no encontrado")
    return reto

# PUT /retos/{id} - actualización completa
@router.put("/{id}")
async def put_reto(id: str, reto: Retos):
    existente = await get_reto_by_id(id)
    if not existente:
        raise HTTPException(status_code=404, detail="Reto no encontrado")
    return await update_reto(id, reto)

# PATCH /retos/{id} - actualización parcial (activar/desactivar)
@router.patch("/{id}")
async def patch_reto(id: str, reto: RetoUpdateParcial):
    existente = await get_reto_by_id(id)
    if not existente:
        raise HTTPException(status_code=404, detail="Reto no encontrado")
    return await update_reto(id, reto.dict(exclude_unset=True))

# DELETE /retos/{id} - solo si está desactivado
@router.delete("/{id}")
async def delete_reto_endpoint(id: str):
    reto = await get_reto_by_id(id)
    if not reto:
        raise HTTPException(status_code=404, detail="Reto no encontrado")
    if reto.get("activo", True):
        raise HTTPException(status_code=400, detail="Primero desactiva el reto antes de eliminarlo")
    await delete_reto(id)
    return {"mensaje": "Reto eliminado correctamente"}

# GET /retos - listar
@router.get("/", response_model=List[Retos])
async def get_retos(
    usuario_id: Optional[str] = Query(None),
    categoria_id: Optional[str] = Query(None)
):
    return await listar_retos(usuario_id, categoria_id)
