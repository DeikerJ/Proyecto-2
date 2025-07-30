from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class Usuario(BaseModel):
    id: Optional[str] = Field(None, description="MongoDB ID")
    name: str = Field(
        description="Nombre del usuario",
        pattern=r"^[a-zA-Z\s]+$"
    )
    lastname: str = Field(
        description="Apellido del usuario",
        pattern=r"^[a-zA-Z\s]+$"
    )
    email: str = Field(
        description="Correo electrónico del usuario",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    active: bool = True
    admin: bool = False
    password: str = Field(
        min_length=8,
        max_length=64,
        description="Contraseña del usuario, debe tener al menos 8 caracteres",
        examples=["MiPassword123!"]
    )
    
    class Config:
        extra = "ignore"  # Ignora campos extra al crear instancias

    @classmethod
    def response_model(cls, **data):
        """Método para crear instancias sin validar password"""
        if 'password' in data:
            data.pop('password')
        return cls(**data)

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str):
        if not re.search(r'[A-Z]', value):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r'\d', value):
            raise ValueError("La contraseña debe contener al menos un número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return value