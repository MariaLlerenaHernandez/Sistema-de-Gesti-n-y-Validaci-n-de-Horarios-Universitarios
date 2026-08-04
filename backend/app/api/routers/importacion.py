from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.common import ResumenImportacion
from app.schemas.importacion import SolicitudImportacion
from app.services.importacion_service import ImportacionService

router = APIRouter(prefix="/import", tags=["Importacion"])


@router.post("/docentes", response_model=ResumenImportacion, status_code=status.HTTP_201_CREATED)
def importar_docentes(solicitud: SolicitudImportacion, db: DBSession):
    return ImportacionService(db).importar_docentes(solicitud.filas)


@router.post("/espacios", response_model=ResumenImportacion, status_code=status.HTTP_201_CREATED)
def importar_espacios(solicitud: SolicitudImportacion, db: DBSession):
    return ImportacionService(db).importar_espacios(solicitud.filas)


@router.post("/asignaturas", response_model=ResumenImportacion, status_code=status.HTTP_201_CREATED)
def importar_asignaturas(solicitud: SolicitudImportacion, db: DBSession):
    return ImportacionService(db).importar_asignaturas(solicitud.filas)


@router.post("/paralelos", response_model=ResumenImportacion, status_code=status.HTTP_201_CREATED)
def importar_paralelos(solicitud: SolicitudImportacion, db: DBSession):
    return ImportacionService(db).importar_paralelos(solicitud.filas)


@router.post("/distributivo", response_model=ResumenImportacion, status_code=status.HTTP_201_CREATED)
def importar_distributivo(solicitud: SolicitudImportacion, db: DBSession):
    return ImportacionService(db).importar_distributivo(solicitud.filas)


@router.post("/disponibilidad", response_model=ResumenImportacion, status_code=status.HTTP_201_CREATED)
def importar_disponibilidad(solicitud: SolicitudImportacion, db: DBSession):
    return ImportacionService(db).importar_disponibilidad(solicitud.filas)
