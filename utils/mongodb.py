import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

DB = os.getenv("DATABASE_NAME")
URI = os.getenv("MONGODB_URI")
col = os.getenv("USER_COLLECTION")

# Validate that we have the required environment variables
if not DB:
    raise ValueError("Database name not found. Set DATABASE_NAME or MONGO_DB_NAME environment variable")
if not URI:
    raise ValueError("MongoDB URI not found. Set MONGODB_URI or URI environment variable")

_client = None

def get_mongo_client():
    global _client
    if _client is None:
        _client = MongoClient(
            URI,
            server_api=ServerApi("1"),
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000  # Timeout más corto
        )
    return _client


def get_collection(col):
    client = MongoClient(  
        URI
        , server_api = ServerApi("1")
        , tls = True
        , tlsAllowInvalidCertificates = True
    )
    client.admin.command("ping")
    return client[DB][col]


def t_connection():
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False
