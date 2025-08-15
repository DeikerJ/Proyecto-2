
from pydantic import BaseModel, Field
from typing import Optional 
import re

class Retos(BaseModel):

    id: Optional[str] = Field(
       default=None,
       description="MongoDB ID - Se genera automáticamente al crear el reto" 
    )
    
    title: str = Field(
        default=None,
        description="Titulo del reto "
        
    )
    
    usuario_id: str = Field(
        description="ID del usuario que creó el reto",
        examples=["usuario_123"]
    )
    
    description: str = Field(
        min_length=20,
        max_length=500,
        description="Descripción detallada del reto",
        examples=["Descripción detallada del reto"]
    )
    
    categoria_id: str = Field(
        description="ID de la categoría a la que pertenece el reto",
        examples=["categoria_123"]
    )
    
    class RetoUpdate(BaseModel):
     title: Optional[str] = None
     description: Optional[str] = None
     categoria_id: Optional[str] = None
     activo: Optional[bool] = None