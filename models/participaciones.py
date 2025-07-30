from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Participacion(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente"
    )

    usuario_id: str = Field(
        description="ID del usuario que se inscribe al reto",
        examples=["usuario_abc123"]
    )

    reto_id: str = Field(
        description="ID del reto en el que participa",
        examples=["reto_xyz456"]
    )

    completado: bool = Field(
        default=False,
        description="Indica si el reto fue completado por el usuario"
    )

    fecha_inscripcion: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora en que el usuario se inscribió"
    )