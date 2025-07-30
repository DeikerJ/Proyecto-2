import firebase_admin
import logging
import os
import requests

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

cred= credentials.Certificate("secrets/Altus.json")
firebase_admin.initialize_app(cred)


def get_collection(MONGO_URI, MONGO_DB_NAME, USER_COLLECTION):
    client = MongoClient(
        MONGO_URI
        ,server_api= ServerApi("1")
        ,tls = True
        ,tlsAllowInvalidCertificates = True
    )
    
    client.admin.command("ping")
    return client[MONGO_DB_NAME][USER_COLLECTION]



async def create_user(user: Usuario) -> Usuario:
    user_record = {}
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )
    except Exception as e:
        logger.warning(e)
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
            id=str(inserted.inserted_id)
            , name=user.name
            , lastname=user.lastname
            , email=user.email
            , password=user.password
        )

        user_dict = new_user.model_dump(exclude={"id", "password"})
        new_user.id = str(inserted.inserted_id)
        new_user.password = "*********"  # Mask the password in the response
        return new_user

    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def login(user: Login) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email
        , "password": user.password
        , "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400
            , detail="Error al autenticar usuario"
        )

    coll = get_collection(MONGO_URI, MONGO_DB_NAME, USER_COLLECTION)
    user_info = coll.find_one({ "email": user.email })

    if not user_info:
        raise HTTPException(
            status_code=404
            , detail="Usuario no encontrado en la base de datos"
        )

    return {
        "message": "Usuario Autenticado correctamente"
        , "idToken": create_jwt_token(
            user_info["name"]
            , user_info["lastname"]
            , user_info["email"]
            , user_info["active"]
            , user_info["admin"]
            , str(user_info["_id"])
        )
    }