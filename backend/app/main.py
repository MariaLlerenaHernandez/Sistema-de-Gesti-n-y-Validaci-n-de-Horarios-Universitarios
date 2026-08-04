import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.core.logging_config import setup_logging

settings = get_settings()
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST para la gestion, proyeccion y validacion de horarios "
        "academicos universitarios. Documentacion interactiva en /docs."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Salud"])
def raiz():
    return {"estado": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health", tags=["Salud"])
def health_check():
    return {"estado": "ok"}


@app.on_event("startup")
def evento_inicio():
    logger.info("%s v%s iniciado en modo %s", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
