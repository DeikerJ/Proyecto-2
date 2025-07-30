from fastapi import HTTPException
from models.participaciones import Participacion
from pymongo import MongoClient
import os 
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DATABASE_NAME")]
participaciones_collection = db["Participaciones"]

async def crear_participacion(participacion: Participacion):
    existente = participaciones_collection.find_one({
        "usuario_id": participacion.usuario_id,
        "reto_id": participacion.reto_id
    })

    if existente:
        raise HTTPException(
            status_code=409,
            detail="El usuario ya está inscrito en este reto."
        )

    resultado = participaciones_collection.insert_one(participacion.dict(exclude_unset=True))
    participacion.id = str(resultado.inserted_id)
    return participacion