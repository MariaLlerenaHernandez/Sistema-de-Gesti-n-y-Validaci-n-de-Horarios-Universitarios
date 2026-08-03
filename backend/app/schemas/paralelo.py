from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Jornada(str, Enum):
    MATUTINA = "Matutina"
    VESPERTINA = "Vespertina"
    NOCTURNA = "Nocturna"


class ParaleloBase(BaseModel):
    codigo_paralelo_ext: str = Field(..., max_length=20)
    asignatura_id: int
    codigo_paralelo: str = Field(..., max_length=10)
    carrera: str = Field(..., max_length=100)
    nivel: int = Field(..., gt=0, le=12)
    jornada: Jornada
    numero_estudiantes: int = Field(..., gt=0)
    activo: bool = True


class ParaleloCrear(ParaleloBase):
    pass


class ParaleloActualizar(BaseModel):
    carrera: str | None = Field(None, max_length=100)
    nivel: int | None = Field(None, gt=0, le=12)
    jornada: Jornada | None = None
    numero_estudiantes: int | None = Field(None, gt=0)
    activo: bool | None = None


class ParaleloRespuesta(ParaleloBase):
    model_config = ConfigDict(from_attributes=True)

    paralelo_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
