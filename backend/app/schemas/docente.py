from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class TipoContrato(str, Enum):
    TIEMPO_COMPLETO = "TIEMPO_COMPLETO"
    MEDIO_TIEMPO = "MEDIO_TIEMPO"
    TIEMPO_PARCIAL = "TIEMPO_PARCIAL"


class DocenteBase(BaseModel):
    codigo_docente: str = Field(..., max_length=20)
    cedula: str = Field(..., max_length=20)
    nombres: str = Field(..., max_length=100)
    apellidos: str = Field(..., max_length=100)
    correo: EmailStr
    tipo_contrato: TipoContrato
    horas_max_semanales: int = Field(..., gt=0, le=60)
    activo: bool = True

    @field_validator("codigo_docente", "cedula")
    @classmethod
    def sin_espacios(cls, v: str) -> str:
        return v.strip()


class DocenteCrear(DocenteBase):
    pass


class DocenteActualizar(BaseModel):
    nombres: str | None = Field(None, max_length=100)
    apellidos: str | None = Field(None, max_length=100)
    correo: EmailStr | None = None
    tipo_contrato: TipoContrato | None = None
    horas_max_semanales: int | None = Field(None, gt=0, le=60)
    activo: bool | None = None


class DocenteRespuesta(DocenteBase):
    model_config = ConfigDict(from_attributes=True)

    docente_id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
