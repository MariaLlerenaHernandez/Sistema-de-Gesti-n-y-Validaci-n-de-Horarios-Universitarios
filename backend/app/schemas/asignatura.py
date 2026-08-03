from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.espacio import TipoEspacio


class Modalidad(str, Enum):
    PRESENCIAL = "PRESENCIAL"
    HIBRIDA = "HIBRIDA"
    ONLINE = "ONLINE"


class AsignaturaBase(BaseModel):
    codigo_asignatura: str = Field(..., max_length=20)
    nombre_asignatura: str = Field(..., max_length=150)
    modalidad: Modalidad
    requiere_laboratorio: bool = False
    tipo_espacio_requerido: TipoEspacio | None = None
    horas_semanales: int = Field(..., gt=0)
    cupo_estimado: int = Field(..., gt=0)
    activo: bool = True

    @model_validator(mode="after")
    def validar_laboratorio(self):
        if self.requiere_laboratorio and self.tipo_espacio_requerido is None:
            raise ValueError(
                "Si la asignatura requiere laboratorio, debe indicarse tipo_espacio_requerido."
            )
        return self


class AsignaturaCrear(AsignaturaBase):
    pass


class AsignaturaActualizar(BaseModel):
    nombre_asignatura: str | None = Field(None, max_length=150)
    modalidad: Modalidad | None = None
    requiere_laboratorio: bool | None = None
    tipo_espacio_requerido: TipoEspacio | None = None
    horas_semanales: int | None = Field(None, gt=0)
    cupo_estimado: int | None = Field(None, gt=0)
    activo: bool | None = None


class AsignaturaRespuesta(AsignaturaBase):
    model_config = ConfigDict(from_attributes=True)

    asignatura_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
