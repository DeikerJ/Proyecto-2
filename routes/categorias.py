from fastapi import APIRouter, HTTPException, Request,Depends
from models.categorias import Categoria
from utils.security import validate_token
from motor.motor_asyncio import AsyncIOMotorClient
from controllers.categorias_controller import (
    create_categoria,
    get_categorias,
    get_categoria_by_id,
    update_categoria,
    deactivate_categoria
)
from utils.security import validateadmin

router = APIRouter(
    prefix="/categorias",
    tags=["categorías"]
)

@router.post("/", response_model=Categoria, tags=["categorías"])
async def create_categoria_endpoint(
    request: Request,
    categoria: Categoria,
    user: dict = Depends(validate_token)  
) -> Categoria:
    return await create_categoria(categoria)


@router.get("/", response_model=list[Categoria])
async def get_categorias_endpoint(request: Request) -> dict:
    """Obtener todas las categorías"""
    return await get_categorias()

@router.get("/{categoria_id}", response_model=Categoria, tags=["categorías"])
async def get_categoria_id_endpoint(categoria_id: str) -> Categoria:
    """Obtener una categoría por ID"""
    return await get_categoria_by_id(categoria_id)

@router.put("/{categoria_id}", response_model=Categoria, tags=["categorías"])
@validateadmin
async def update_categoria_endpoint(request: Request, categoria_id: str, categoria: Categoria) -> Categoria:
    """Actualizar una categoría"""
    return await update_categoria(categoria_id, categoria)

@router.delete("/{categoria_id}", response_model=Categoria, tags=["categorías"])
@validateadmin
async def deactivate_categoria_endpoint(request: Request, categoria_id: str) -> Categoria:
    """Desactivar una categoría"""
    return await deactivate_categoria(categoria_id)

  
