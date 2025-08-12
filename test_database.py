import pytest 
from utils.mongodb import get_mongo_client , t_connection, get_collection
import os 
from dotenv import  load_dotenv

load_dotenv()
USER_COLLECTION = os.getenv("USER_COLLECTION")


def test_env_variables():
    mongodb_uri=os.getenv("MONGODB_URI")
    assert mongodb_uri is not None, "MONGODB_URI no esta configurado"
    print (f"Database:{mongodb_uri}")


def test_connection():
    try:
        connection_result = t_connection()
        assert connection_result is True, "La conexion a la BD fallo"
    except Exception as e:
        pytest.fail(f"Error en la conexion a MongoDB{str(e)}")
        

def test_mongo_client( ):
    try:
        client = get_mongo_client()
        assert client is not None,"El cliente de Mongo is NONE"
    except Exception as e:
        pytest.fail(f"Error en el llamado del cliente{str(e)}")
        
        
        
def test_get_collection():
    
  try:
        coll_users = get_collection(USER_COLLECTION)
        assert coll_users is not None,"Error al obtener la coleccion de usuarios"
  except Exception as e:
        pytest.fail(f"Error en el llamado del cliente{str(e)}")

        