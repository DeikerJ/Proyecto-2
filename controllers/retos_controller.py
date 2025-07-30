from models.retos import Retos
from bson import ObjectId
from pymongo import MongoClient
from fastapi import HTTPException
from dotenv import load_dotenv
import os
from typing import Optional,List
from motor.motor_asyncio import AsyncIOMotorClient 

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
DB = client[os.getenv("DATABASE_NAME")]
retos_coll = DB["Retos"]

# Crear reto
async def create_reto(reto: Retos) -> Retos:
    try:
        payload = {
            "title": reto.title.strip(),
            "description": reto.description.strip(),
            "categoria_id": reto.categoria_id,
            "usuario_id": reto.usuario_id
        }
        res = await retos_coll.insert_one(payload)
        reto.id = str(res.inserted_id)
        return reto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear reto: {e}")

# Obtener reto por ID
async def get_reto_by_id(reto_id: str) -> dict:
    try:
        doc = await retos_coll.find_one({"_id": ObjectId(reto_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Reto no encontrado")
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo reto: {e}")

# Modificar reto
async def update_reto(reto_id: str, reto: Retos) -> dict:
    try:
        update = {
            "$set": {
                "title": reto.title.strip(),
                "descripcion": reto.descripcion.strip(),
                "categoria_id": reto.categoria_id
            }
        }
        result = await retos_coll.update_one({"_id": ObjectId(reto_id)}, update)
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Reto no modificado")
        return await get_reto_by_id(reto_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando reto: {e}")

# Eliminar reto
async def delete_reto(reto_id: str):
    try:
        result = await retos_coll.delete_one({"_id": ObjectId(reto_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Reto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando reto: {e}")

# Listar retos por usuario
async def get_ret_os_by_usuario(usuario_id: str) -> List[dict]:
    try:
        cursor = retos_coll.find({"usuario_id": usuario_id})
        return [doc async for doc in cursor]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando retos: {e}")
    
async def listar_retos(usuario_id: Optional[str] = None,
                       categoria_id: Optional[str] = None) -> List[Retos]:
    # Armar filtro dinámico
    filtro = {}
    if usuario_id:
        filtro["usuario_id"] = usuario_id
    if categoria_id:
        filtro["categoria_id"] = categoria_id

    cursor = retos_coll.find(filtro)
    retos = []
    async for doc in cursor:  
        doc["id"] = str(doc["_id"])
        retos.append(Retos(**doc))
    return retos