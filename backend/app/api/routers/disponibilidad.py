from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.disponibilidad_docente import DisponibilidadCrear, DisponibilidadRespuesta
from app.services.disponibilidad_service import DisponibilidadService

router = APIRouter(prefix="/disponibilidad", tags=["Disponibilidad Docente"])


@router.get("", response_model=list[DisponibilidadRespuesta])
def listar_disponibilidad(db: DBSession, docente_id: int | None = None, skip: int = 0, limit: int = 500):
    servicio = DisponibilidadService(db)
    if docente_id is not None:
        return servicio.listar_por_docente(docente_id)
    return servicio.listar(skip=skip, limit=limit)


@router.get("/{disponibilidad_id}", response_model=DisponibilidadRespuesta)
def obtener_disponibilidad(disponibilidad_id: int, db: DBSession):
    return DisponibilidadService(db).obtener(disponibilidad_id)


@router.post("", response_model=DisponibilidadRespuesta, status_code=status.HTTP_201_CREATED)
def crear_disponibilidad(datos: DisponibilidadCrear, db: DBSession):
    return DisponibilidadService(db).crear(datos)


@router.delete("/{disponibilidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_disponibilidad(disponibilidad_id: int, db: DBSession):
    DisponibilidadService(db).eliminar(disponibilidad_id)
