# controllers/categorias_controller.py

import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from models.categorias import Categoria
from pipelines.categorias_papelines import (
    pipeline_categorias_con_retos,
    pipeline_validar_eliminacion_categoria
)

load_dotenv()

# --- Inicializar cliente Mongo y colección ---
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME")

_client = AsyncIOMotorClient(MONGODB_URI)
_db = _client[DB_NAME]
categorias_coll = _db["Categorias"]


def _serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte un documento de Mongo a un dict apto para Pydantic:
    - Transforma _id a id (string)
    - Normaliza campos nombre/descripcion o name/text según tu esquema
    - Conserva cantidad_retos y retos si existen
    """
    name = doc.get("name") or doc.get("nombre")
    text = doc.get("text") or doc.get("descripcion")

    serialized: Dict[str, Any] = {
        "id": str(doc["_id"]),
        "name": name,
        "text": text,
    }

    if "cantidad_retos" in doc:
        serialized["cantidad_retos"] = doc["cantidad_retos"]
    if "retos" in doc:
        serialized["retos"] = doc["retos"]

    return serialized


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
            "name": {"$regex": f"^{name}$", "$options": "i"}
        })
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )

        payload = {"name": name, "text": text}
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


async def get_categorias() -> List[Dict[str, Any]]:
    """
    Lista todas las categorías con conteo y detalle de retos asociados.
    """
    try:
        cursor = categorias_coll.aggregate(pipeline_categorias_con_retos())
        docs = [ _serialize_doc(doc) async for doc in cursor ]
        return docs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo categorías: {e}"
        )


async def get_categoria_by_id(categoria_id: str) -> Dict[str, Any]:
    """
    Obtiene una categoría por su ID, incluyendo retos asociados.
    """
    try:
        match_stage = {"$match": {"_id": ObjectId(categoria_id)}}
        pipeline = [match_stage] + pipeline_categorias_con_retos()

        cursor = categorias_coll.aggregate(pipeline)
        docs = [ _serialize_doc(doc) async for doc in cursor ]

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
        updated = await get_categoria_by_id(categoria_id)
        return Categoria(**updated)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando categoría: {e}"
        )


async def deactivate_categoria(categoria_id: str) -> Categoria:
    """
    Elimina la categoría si no tiene retos asociados.
    Devuelve la categoría eliminada.
    """
    try:
        # 1. Validar que no tenga retos asociados
        pipeline = pipeline_validar_eliminacion_categoria(categoria_id)
        cursor = categorias_coll.aggregate(pipeline)
        docs = [doc async for doc in cursor]

        if not docs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        if docs[0].get("cantidad_retos", 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar: existen retos asociados"
            )

        # 2. Obtener doc antes de borrar
        categoria_doc = await categorias_coll.find_one(
            {"_id": ObjectId(categoria_id)}
        )
        if not categoria_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # 3. Borrar
        result = await categorias_coll.delete_one(
            {"_id": ObjectId(categoria_id)}
        )
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo eliminar la categoría"
            )

        # 4. Devolver la categoría borrada
        serialized = _serialize_doc(categoria_doc)
        return Categoria(**serialized)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando categoría: {e}"
        )
