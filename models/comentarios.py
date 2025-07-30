from pydantic import BaseModel, Field
from typing import Optional
import re

class comentarios(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente al crear el comentario"
    )
    
    text: str = Field(
        min_length=1,
        max_length=500,
        description="Texto del comentario",
        examples=["Este es un comentario sobre la categoría"]
    )
    
    reto_id: str = Field(
        description="ID del reto al que pertenece el comentario",
        examples=["reto_123"]
    )
    
    usuario_id: str = Field(
        description="ID del usuario que creó el comentario",
        examples=["usuario_123"]
    )