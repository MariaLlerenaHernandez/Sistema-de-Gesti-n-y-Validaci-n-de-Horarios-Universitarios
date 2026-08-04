from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.paralelo import ParaleloActualizar, ParaleloCrear, ParaleloRespuesta
from app.services.paralelo_service import ParaleloService

router = APIRouter(prefix="/paralelos", tags=["Paralelos"])


@router.get("", response_model=list[ParaleloRespuesta])
def listar_paralelos(db: DBSession, solo_activos: bool = False, skip: int = 0, limit: int = 200):
    return ParaleloService(db).listar(solo_activos=solo_activos, skip=skip, limit=limit)


@router.get("/{paralelo_id}", response_model=ParaleloRespuesta)
def obtener_paralelo(paralelo_id: int, db: DBSession):
    return ParaleloService(db).obtener(paralelo_id)


@router.post("", response_model=ParaleloRespuesta, status_code=status.HTTP_201_CREATED)
def crear_paralelo(datos: ParaleloCrear, db: DBSession):
    return ParaleloService(db).crear(datos)


@router.put("/{paralelo_id}", response_model=ParaleloRespuesta)
def actualizar_paralelo(paralelo_id: int, datos: ParaleloActualizar, db: DBSession):
    return ParaleloService(db).actualizar(paralelo_id, datos)


@router.delete("/{paralelo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_paralelo(paralelo_id: int, db: DBSession):
    ParaleloService(db).eliminar(paralelo_id)
