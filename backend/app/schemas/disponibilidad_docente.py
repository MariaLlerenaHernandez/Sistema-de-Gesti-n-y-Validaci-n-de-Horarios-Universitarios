from datetime import time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DiaSemana(str, Enum):
    LUNES = "LUNES"
    MARTES = "MARTES"
    MIERCOLES = "MIERCOLES"
    JUEVES = "JUEVES"
    VIERNES = "VIERNES"
    SABADO = "SABADO"


class DisponibilidadBase(BaseModel):
    codigo_disponibilidad_ext: str = Field(..., max_length=20)
    docente_id: int
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fin: time
    disponible: bool = True

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValueError("hora_fin debe ser mayor que hora_inicio.")
        return self


class DisponibilidadCrear(DisponibilidadBase):
    pass


class DisponibilidadRespuesta(DisponibilidadBase):
    model_config = ConfigDict(from_attributes=True)

    disponibilidad_id: int
