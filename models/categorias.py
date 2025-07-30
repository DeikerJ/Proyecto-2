from pydantic import BaseModel, Field
from typing import Optional
import re


class Categoria(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID- Se genera automáticamente al crear la categoría"
    )
    
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Nombre de la categoría",
        examples=["Colaborativas", "Individuales", "Tecnicas"]
    )
    
    text: str = Field(
        min_length=20,
        max_length=300,
        description="Descripción de la categoría",
        examples=["Categoría para proyectos colaborativos", "Proyectos individuales", "Técnicas de desarrollo"]
        
    )
    
    usuario_id: str = Field(
        description="ID del usuario que creó la categoría",
        examples=["usuario_123"]
    )
    
    
