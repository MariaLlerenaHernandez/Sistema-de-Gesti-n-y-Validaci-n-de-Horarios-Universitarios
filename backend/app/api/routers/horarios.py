from fastapi import APIRouter

from app.api.deps import DBSession
from app.schemas.horario import BloqueHorarioCrear, BloqueHorarioMover, ResultadoValidacion
from app.services.horario_service import HorarioService

router = APIRouter(prefix="/horarios", tags=["Horarios"])


@router.post("/validar", response_model=ResultadoValidacion, status_code=201)
def registrar_y_validar_propuesta(datos: BloqueHorarioCrear, db: DBSession):
    """
    Registra un bloque de horario (propuesta) y ejecuta de inmediato la
    validacion de reglas de negocio en base de datos. Devuelve el
    estado general y el detalle de los conflictos encontrados, si los hay.
    """
    return HorarioService(db).registrar_y_validar(datos)


@router.patch("/{bloque_id}/mover", response_model=ResultadoValidacion)
def mover_bloque(bloque_id: int, datos: BloqueHorarioMover, db: DBSession):
    """
    Reubica un bloque ya registrado (dia/hora y, opcionalmente, espacio) —
    usado por el calendario semanal del frontend al arrastrar y soltar un
    bloque a otra celda. Vuelve a validar las reglas de negocio despues
    de moverlo.
    """
    return HorarioService(db).mover(bloque_id, datos)


@router.post("/{bloque_id}/revalidar", response_model=ResultadoValidacion)
def revalidar_bloque(bloque_id: int, db: DBSession):
    return HorarioService(db).revalidar(bloque_id)


@router.post("/validar-periodo/{periodo_academico}")
def validar_periodo_completo(periodo_academico: str, db: DBSession):
    """Revalida en lote todos los bloques de un periodo academico."""
    filas = HorarioService(db).validar_periodo(periodo_academico)
    return {"estado": "ok", "periodo_academico": periodo_academico, "horario": filas}


@router.get("/semanal/{periodo_academico}")
def obtener_horario_semanal(periodo_academico: str, db: DBSession):
    """Matriz semanal de bloques (para el calendario del frontend)."""
    return HorarioService(db).obtener_horario_semanal(periodo_academico)


@router.get("/conflictos")
def obtener_conflictos(periodo_academico: str, db: DBSession):
    """Listado de conflictos detectados para un periodo academico."""
    return HorarioService(db).obtener_conflictos(periodo_academico)
