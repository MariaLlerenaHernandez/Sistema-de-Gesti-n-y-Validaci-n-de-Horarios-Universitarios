from fastapi import APIRouter, status

from app.api.deps import DBSession
from app.schemas.docente import DocenteActualizar, DocenteCrear, DocenteRespuesta
from app.services.docente_service import DocenteService

router = APIRouter(prefix="/docentes", tags=["Docentes"])


@router.get("", response_model=list[DocenteRespuesta])
def listar_docentes(db: DBSession, solo_activos: bool = False, skip: int = 0, limit: int = 200):
    return DocenteService(db).listar(solo_activos=solo_activos, skip=skip, limit=limit)


@router.get("/{docente_id}", response_model=DocenteRespuesta)
def obtener_docente(docente_id: int, db: DBSession):
    return DocenteService(db).obtener(docente_id)


@router.post("", response_model=DocenteRespuesta, status_code=status.HTTP_201_CREATED)
def crear_docente(datos: DocenteCrear, db: DBSession):
    return DocenteService(db).crear(datos)


@router.put("/{docente_id}", response_model=DocenteRespuesta)
def actualizar_docente(docente_id: int, datos: DocenteActualizar, db: DBSession):
    return DocenteService(db).actualizar(docente_id, datos)


@router.delete("/{docente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_docente(docente_id: int, db: DBSession):
    DocenteService(db).eliminar(docente_id)
