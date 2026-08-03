from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class RespuestaExitosa(BaseModel, Generic[T]):
    estado: str = "ok"
    mensaje: str | None = None
    data: T | None = None


class ErrorFila(BaseModel):
    fila: int
    columna: str | None = None
    detalle: str


class ResumenImportacion(BaseModel):
    entidad: str
    total_filas: int
    filas_procesadas: int
    filas_con_error: int
    errores: list[ErrorFila] = []
