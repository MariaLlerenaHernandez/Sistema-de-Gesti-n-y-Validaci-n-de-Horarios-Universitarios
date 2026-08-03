from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DistributivoBase(BaseModel):
    codigo_distributivo_ext: str = Field(..., max_length=20)
    docente_id: int
    asignatura_id: int
    paralelo_id: int
    periodo_academico: str = Field(..., max_length=20)
    horas_asignadas: int = Field(..., gt=0)
    observacion: str | None = Field(None, max_length=255)
    activo: bool = True


class DistributivoCrear(DistributivoBase):
    pass


class DistributivoActualizar(BaseModel):
    horas_asignadas: int | None = Field(None, gt=0)
    observacion: str | None = Field(None, max_length=255)
    activo: bool | None = None


class DistributivoRespuesta(DistributivoBase):
    model_config = ConfigDict(from_attributes=True)

    distributivo_id: int
    fecha_creacion: datetime
