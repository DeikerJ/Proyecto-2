from fastapi import APIRouter, Request, Depends
from models.Retos_categoria import RetoCategoria
from controllers.Retos_categoria import (
    create_reto_categoria,
    get_categorias_por_reto,
    delete_reto_categoria
)
from utils.security import validate_token, validateadmin

router = APIRouter(
    prefix="/retos-categorias",
    tags=["Retos-Categorías"]
)

@router.post("/", response_model=RetoCategoria)
async def create_reto_categoria_endpoint(
    request: Request,
    relacion: RetoCategoria,
    user: dict = Depends(validate_token)  
) -> RetoCategoria:
    #Crear relación entre reto y categoría"
    return await create_reto_categoria(relacion)


@router.get("/reto/{id_reto}", response_model=list[RetoCategoria])
async def get_categorias_de_reto_endpoint(id_reto: str):
    #Obtener todas las categorías de un reto
    return await get_categorias_por_reto(id_reto)


@router.delete("/", tags=["Retos-Categorías"])
@validateadmin #Solo si es admin puede eliminar una relacion de retos y categoria, que seria lo mismo que si tiene los permisos para hacerlo (autorizacion)
async def delete_reto_categoria_endpoint(
    request: Request,
    relacion: RetoCategoria
):
    """Eliminar relación entre reto y categoría"""
    return await delete_reto_categoria(relacion)
