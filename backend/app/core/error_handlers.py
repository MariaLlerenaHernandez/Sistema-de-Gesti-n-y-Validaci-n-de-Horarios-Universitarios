"""
Manejo global de errores para respuestas JSON consistentes en toda la API.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import DomainError, EntidadNoEncontradaError

logger = logging.getLogger(__name__)


def _error_body(code: str, message: str, details=None) -> dict:
    return {
        "estado": "error",
        "codigo": code,
        "mensaje": message,
        "detalles": details,
    }


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(EntidadNoEncontradaError)
    async def entidad_no_encontrada_handler(request: Request, exc: EntidadNoEncontradaError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error_body(exc.code, exc.message),
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body("ERROR_VALIDACION_PAYLOAD", "Los datos enviados no cumplen el formato esperado.", exc.errors()),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.error("Error de integridad en base de datos: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_body("ERROR_INTEGRIDAD_BD", "La operacion viola una restriccion de integridad (duplicado o referencia invalida)."),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Error inesperado de base de datos")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("ERROR_BASE_DATOS", "Ocurrio un error inesperado al acceder a la base de datos."),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Error no controlado")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("ERROR_INTERNO", "Ocurrio un error interno inesperado."),
        )
