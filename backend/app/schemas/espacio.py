from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TipoEspacio(str, Enum):
    AULA = "AULA"
    LABORATORIO = "LABORATORIO"
    AULA_COMPUTO = "AULA_COMPUTO"


class EspacioBase(BaseModel):
    codigo_espacio: str = Field(..., max_length=20)
    nombre_espacio: str = Field(..., max_length=100)
    tipo_espacio: TipoEspacio
    capacidad: int = Field(..., gt=0)
    edificio: str = Field(..., max_length=60)
    piso: str | None = Field(None, max_length=10)
    activo: bool = True


class EspacioCrear(EspacioBase):
    pass


class EspacioActualizar(BaseModel):
    nombre_espacio: str | None = Field(None, max_length=100)
    tipo_espacio: TipoEspacio | None = None
    capacidad: int | None = Field(None, gt=0)
    edificio: str | None = Field(None, max_length=60)
    piso: str | None = Field(None, max_length=10)
    activo: bool | None = None


class EspacioRespuesta(EspacioBase):
    model_config = ConfigDict(from_attributes=True)

    espacio_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
