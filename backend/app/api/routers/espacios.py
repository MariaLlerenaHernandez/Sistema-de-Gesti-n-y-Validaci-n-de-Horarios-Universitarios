from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.espacio import EspacioActualizar, EspacioCrear, EspacioRespuesta
from app.services.espacio_service import EspacioService

router = APIRouter(prefix="/espacios", tags=["Espacios"])


@router.get("", response_model=list[EspacioRespuesta])
def listar_espacios(db: DBSession, solo_activos: bool = False, skip: int = 0, limit: int = 200):
    return EspacioService(db).listar(solo_activos=solo_activos, skip=skip, limit=limit)


@router.get("/{espacio_id}", response_model=EspacioRespuesta)
def obtener_espacio(espacio_id: int, db: DBSession):
    return EspacioService(db).obtener(espacio_id)


@router.post("", response_model=EspacioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_espacio(datos: EspacioCrear, db: DBSession):
    return EspacioService(db).crear(datos)


@router.put("/{espacio_id}", response_model=EspacioRespuesta)
def actualizar_espacio(espacio_id: int, datos: EspacioActualizar, db: DBSession):
    return EspacioService(db).actualizar(espacio_id, datos)


@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(espacio_id: int, db: DBSession):
    EspacioService(db).eliminar(espacio_id)
