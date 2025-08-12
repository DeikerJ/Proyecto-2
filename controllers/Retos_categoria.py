from models.Retos_categoria import RetoCategoria
from pymongo import MongoClient
import os 
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DATABASE_NAME")]
participaciones_collection = db["Retos_categoria"]

async def create_reto_categoria(relacion: RetoCategoria):
    # Evitar duplicados
    existe = await db.Retos_categoria.find_one({
        "id_reto": relacion.id_reto,
        "id_categoria": relacion.id_categoria
    })
    if existe:
        return {"error": "La relación ya existe"}

    await db.Retos_categoria.insert_one(relacion.dict())
    return relacion


async def get_categorias_por_reto(id_reto: str):
    relaciones = db.Retos_categoria.find({"id_reto": id_reto})
    return [RetoCategoria(**r) async for r in relaciones]


async def delete_reto_categoria(relacion: RetoCategoria):
    resultado = await db.Retos_categoria.delete_one({
        "id_reto": relacion.id_reto,
        "id_categoria": relacion.id_categoria
    })
    if resultado.deleted_count == 0:
        return {"error": "Relación no encontrada"}
    return {"message": "Relación eliminada"}
