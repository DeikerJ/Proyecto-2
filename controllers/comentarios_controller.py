from models.comentarios import comentarios
from fastapi import HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from typing import List
import os 
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
DB = client[os.getenv("DATABASE_NAME")]
comentarios_coll = DB["Comentarios"]

async def create_comentario(comentario: comentarios) -> comentarios:
    try:
        text = comentario.text.strip()
        payload={
            text: text,
            "reto_id": comentario.reto_id,
            "usuario_id": comentario.usuario_id
        }
        
        res =await comentarios_coll.insert_one(payload)
        comentario.id= str(res.inserted_id)
        comentario.text = text
        return comentario
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando el comentario: {e}"
        )
        
#para obtener comentarios por reto

async def get_comentarios_de_reto(reto_id:str) -> List[dict]:
    try: 
        cursor = await comentarios_coll.find({"reto_id": reto_id})
        return [doc async for doc in cursor]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo comentarios del reto: {e}"
        )
   

async def delete_comentario(comentario_id: str):
    if not ObjectId.is_valid(comentario_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resultado = await comentarios_coll.delete_one({"_id": ObjectId(comentario_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    return {"mensaje": "Comentario eliminado correctamente"}