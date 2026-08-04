from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.distributivo import DistributivoActualizar, DistributivoCrear, DistributivoRespuesta
from app.services.distributivo_service import DistributivoService

router = APIRouter(prefix="/distributivo", tags=["Distributivo"])


@router.get("", response_model=list[DistributivoRespuesta])
def listar_distributivo(db: DBSession, skip: int = 0, limit: int = 200):
    return DistributivoService(db).listar(skip=skip, limit=limit)


@router.get("/{distributivo_id}", response_model=DistributivoRespuesta)
def obtener_distributivo(distributivo_id: int, db: DBSession):
    return DistributivoService(db).obtener(distributivo_id)


@router.post("", response_model=DistributivoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_distributivo(datos: DistributivoCrear, db: DBSession):
    return DistributivoService(db).crear(datos)


@router.put("/{distributivo_id}", response_model=DistributivoRespuesta)
def actualizar_distributivo(distributivo_id: int, datos: DistributivoActualizar, db: DBSession):
    return DistributivoService(db).actualizar(distributivo_id, datos)


@router.delete("/{distributivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_distributivo(distributivo_id: int, db: DBSession):
    DistributivoService(db).eliminar(distributivo_id)
