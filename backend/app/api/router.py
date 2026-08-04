from fastapi import APIRouter

from app.api.routers import (
    asignaturas,
    distributivo,
    disponibilidad,
    docentes,
    espacios,
    horarios,
    importacion,
    paralelos,
)

api_router = APIRouter()

api_router.include_router(docentes.router)
api_router.include_router(espacios.router)
api_router.include_router(asignaturas.router)
api_router.include_router(paralelos.router)
api_router.include_router(distributivo.router)
api_router.include_router(disponibilidad.router)
api_router.include_router(importacion.router)
api_router.include_router(horarios.router)