from pydantic import BaseModel, Field, field_validator
import re

class Login(BaseModel):
    email: str = Field( alias="email",
        description="email electrónico del usuario"
    )
    password: str = Field(
        min_length=8,
        max_length=64,
        description="Contraseña, al menos 8 caracteres"
    )
    



    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str):
        patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron, value):
            raise ValueError("email electrónico no válido")
        return value

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Debe contener al menos una letra mayúscula")
        if not re.search(r"\d", value):
            raise ValueError("Debe contener al menos un número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Debe contener un carácter especial")
        return value
