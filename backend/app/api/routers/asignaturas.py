from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.asignatura import AsignaturaActualizar, AsignaturaCrear, AsignaturaRespuesta
from app.services.asignatura_service import AsignaturaService

router = APIRouter(prefix="/asignaturas", tags=["Asignaturas"])


@router.get("", response_model=list[AsignaturaRespuesta])
def listar_asignaturas(db: DBSession, solo_activos: bool = False, skip: int = 0, limit: int = 200):
    return AsignaturaService(db).listar(solo_activos=solo_activos, skip=skip, limit=limit)


@router.get("/{asignatura_id}", response_model=AsignaturaRespuesta)
def obtener_asignatura(asignatura_id: int, db: DBSession):
    return AsignaturaService(db).obtener(asignatura_id)


@router.post("", response_model=AsignaturaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_asignatura(datos: AsignaturaCrear, db: DBSession):
    return AsignaturaService(db).crear(datos)


@router.put("/{asignatura_id}", response_model=AsignaturaRespuesta)
def actualizar_asignatura(asignatura_id: int, datos: AsignaturaActualizar, db: DBSession):
    return AsignaturaService(db).actualizar(asignatura_id, datos)


@router.delete("/{asignatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asignatura(asignatura_id: int, db: DBSession):
    AsignaturaService(db).eliminar(asignatura_id)
