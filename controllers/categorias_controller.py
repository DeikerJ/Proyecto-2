
from models.categorias import Categoria
from utils.mongodb import get_collection
import os
from dotenv import load_dotenv
from typing import List
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from models.categorias import Categoria

from pipelines.categorias_papelines import (
    pipeline_categorias_con_retos,
    pipeline_validar_eliminacion_categoria
)

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client= AsyncIOMotorClient(mongodb_uri)

DB= client[os.getenv("DATABASE_NAME")]
categorias_coll = DB["Categorias"]


async def create_categoria(categoria: Categoria) -> Categoria:
    """
    Crea una nueva categoría, validando unicidad de nombre
    y devolviendo el objeto con id asignado.
    """
    try:
        name = categoria.name.strip()
        text = categoria.text.strip()

        # Verificar duplicado (case‐insensitive)
        dup = await categorias_coll.find_one({
            "nombre": {"$regex": f"^{name}$", "$options": "i"}
        })
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )

        payload = {"nombre": name, "descripcion": text}
        res = await categorias_coll.insert_one(payload)
        categoria.id = str(res.inserted_id)
        categoria.name = name
        categoria.text = text
        return categoria

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando categoría: {e}"
        )


async def get_categorias() -> List[dict]:
    """
    Lista todas las categorías con conteo y detalle de retos asociados.
    """
    try:
        cursor = categorias_coll.aggregate(pipeline_categorias_con_retos())
        return [doc async for doc in cursor]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo categorías: {e}"
        )


async def get_categoria_by_id(categoria_id: str) -> dict:
    """
    Obtiene una categoría por su ID, incluyendo retos asociados.
    """
    try:
        match_stage = { "$match": { "_id": ObjectId(categoria_id) } }
        pipeline = [match_stage] + pipeline_categorias_con_retos()
        cursor = categorias_coll.aggregate(pipeline)
        docs = [doc async for doc in cursor]

        if not docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        return docs[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo categoría: {e}"
        )


async def update_categoria(categoria_id: str, categoria: Categoria) -> Categoria:
    """
    Actualiza nombre y/o descripción de la categoría indicada.
    Valida unicidad de nombre.
    """
    try:
        name = categoria.name.strip()
        text = categoria.text.strip()

        # Verificar duplicado en otra categoría
        dup = await categorias_coll.find_one({
            "name": {"$regex": f"^{name}$", "$options": "i"},
            "_id": {"$ne": ObjectId(categoria_id)}
        })
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Otra categoría ya usa ese nombre"
            )

        update = {"$set": {"name": name, "text": text}}
        result = await categorias_coll.update_one(
            {"_id": ObjectId(categoria_id)},
            update
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada o sin cambios"
            )

        # Devolver la categoría actualizada
        return await get_categoria_by_id(categoria_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando categoría: {e}"
        )


async def deactivate_categoria(categoria_id: str) -> None:
    """
    Elimina la categoría si no tiene retos asociados.
    """
    try:
        # 1. Verificar cantidad de retos asociados
        pipeline = pipeline_validar_eliminacion_categoria(categoria_id)
        cursor = categorias_coll.aggregate(pipeline)
        docs = [doc async for doc in cursor]

        if not docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        if docs[0]["cantidad_retos"] > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar: existen retos asociados"
            )

        # 2. Eliminar
        result = await categorias_coll.delete_one(
            {"_id": ObjectId(categoria_id)}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando categoría: {e}"
        )