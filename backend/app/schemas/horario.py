from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.asignatura import Modalidad
from app.schemas.disponibilidad_docente import DiaSemana


class BloqueHorarioCrear(BaseModel):
    """Payload para registrar una propuesta de horario (un bloque)."""

    distributivo_id: int
    espacio_id: int
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fin: time
    modalidad: Modalidad
    periodo_academico: str = Field(..., max_length=20)

    @model_validator(mode="after")
    def validar_horas(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValueError("hora_fin debe ser mayor que hora_inicio.")
        return self


class ConflictoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conflicto_id: int
    tipo_conflicto: str
    descripcion: str
    severidad: str


class BloqueHorarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bloque_id: int
    distributivo_id: int
    espacio_id: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    modalidad: str
    periodo_academico: str
    estado: str


class ResultadoValidacion(BaseModel):
    bloque_id: int
    estado_general: str
    conflictos: list[ConflictoRespuesta] = []


class BloqueHorarioDetalle(BaseModel):
    """Fila enriquecida para la matriz semanal / listado de conflictos en el frontend."""

    bloque_id: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    modalidad: str
    estado: str
    periodo_academico: str
    asignatura_id: int
    codigo_asignatura: str
    nombre_asignatura: str
    paralelo_id: int
    codigo_paralelo: str
    carrera: str
    docente_id: int
    codigo_docente: str
    docente: str
    espacio_id: int
    codigo_espacio: str
    nombre_espacio: str
