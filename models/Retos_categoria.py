from pydantic import BaseModel, Field
from typing import Optional 

class RetoCategoria(BaseModel):
    
    reto_id: Optional[str]= Field(
        default= None,
        examples=["reto_123"],
    )
        
    categoria_id:Optional[str] = Field(
        default=None,
        examples=["categoria_123"]
    )
    
    