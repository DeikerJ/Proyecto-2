import firebase_admin
import logging
import os
import requests
import base64
import json

from models.login import Login
from models.usuarios import Usuario

from utils.mongodb import get_collection
from utils.security import create_jwt_token

from firebase_admin import credentials, auth as firebase_auth
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from fastapi import HTTPException
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("DATABASE_NAME")
USER_COLLECTION = os.getenv("USER_COLLECTION")


def initialize_firebase():
    """Inicializa Firebase usando base64 o archivo local"""
    if firebase_admin._apps:
        return
    
    try:
        firebase_cred_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")
        
        if firebase_cred_base64:
            firebase_creds_json = base64.b64decode(firebase_cred_base64).decode('utf-8')
            firebase_creds = json.loads(firebase_creds_json)
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde credenciales BASE64")
        else:
            cred = credentials.Certificate("secrets/Altus.json")
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado desde archivo JSON local")

    except Exception as e:
        logger.error(f"Error al inicializar Firebase: {e}")
        raise HTTPException(status_code=500, detail=f"Error de configuración de Firebase")



async def create_user(user: Usuario) -> Usuario:
    initialize_firebase()
    user_record = {}
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
    except Exception as e:
        logger.error("Error creando el usuario en firebase")
        raise HTTPException(
            status_code=400,
            detail="Error al registrar usuario en firebase"
        )

    try:
        coll = get_collection(MONGO_URI, MONGO_DB_NAME, USER_COLLECTION)
        user_dict = {
            "name": user.name,
            "lastname": user.lastname,
            "email": user.email,
            "active": True,
            "admin": user.admin
        }
        
        inserted = coll.insert_one(user_dict)

        new_user = Usuario(
            id=str(inserted.inserted_id),
            name=user.name,
            lastname=user.lastname,
            email=user.email,
            password=user.password
        )

        new_user.password = "*********"
        return new_user

    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        logger.error(f"Error creando usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")


async def login(user: Login) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400,
            detail="Error al autenticar usuario"
        )

    coll = get_collection(MONGO_URI, MONGO_DB_NAME, USER_COLLECTION)
    user_info = coll.find_one({"email": user.email})

    if not user_info:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en la base de datos"
        )

    return {
        "message": "Usuario Autenticado correctamente",
        "idToken": create_jwt_token(
            user_info["name"],
            user_info["lastname"],
            user_info["email"],
            user_info["active"],
            user_info["admin"],
            str(user_info["_id"])
        )
    }
