"""
Schemas de las filas que llegan desde el frontend (ya convertidas de
Excel/CSV a JSON) para cada hoja de importacion definida en el anexo
de formatos de carga.
"""
from pydantic import BaseModel, Field

from app.schemas.asignatura import Modalidad
from app.schemas.disponibilidad_docente import DiaSemana
from app.schemas.docente import TipoContrato
from app.schemas.espacio import TipoEspacio
from app.schemas.paralelo import Jornada


def _si_no_a_bool(valor) -> bool:
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().upper() == "SI"


class FilaDocenteImport(BaseModel):
    docente_id: str
    cedula: str
    nombres: str
    apellidos: str
    correo: str
    tipo_contrato: TipoContrato
    horas_max_semanales: int
    activo: str | bool = "SI"

    def a_bool_activo(self) -> bool:
        return _si_no_a_bool(self.activo)


class FilaEspacioImport(BaseModel):
    espacio_id: str
    codigo_espacio: str
    nombre_espacio: str
    tipo_espacio: TipoEspacio
    capacidad: int
    edificio: str
    piso: str | None = None
    activo: str | bool = "SI"

    def a_bool_activo(self) -> bool:
        return _si_no_a_bool(self.activo)


class FilaAsignaturaImport(BaseModel):
    asignatura_id: str
    codigo_asignatura: str
    nombre_asignatura: str
    modalidad: Modalidad
    requiere_laboratorio: str | bool = "NO"
    tipo_espacio_requerido: TipoEspacio | None = None
    horas_semanales: int
    cupo_estimado: int
    activo: str | bool = "SI"

    def a_bool_requiere_lab(self) -> bool:
        return _si_no_a_bool(self.requiere_laboratorio)

    def a_bool_activo(self) -> bool:
        return _si_no_a_bool(self.activo)


class FilaParaleloImport(BaseModel):
    paralelo_id: str
    asignatura_id: str
    codigo_paralelo: str
    carrera: str
    nivel: int
    jornada: Jornada
    numero_estudiantes: int
    activo: str | bool = "SI"

    def a_bool_activo(self) -> bool:
        return _si_no_a_bool(self.activo)


class FilaDistributivoImport(BaseModel):
    distributivo_id: str
    docente_id: str
    asignatura_id: str
    paralelo_id: str
    periodo_academico: str
    horas_asignadas: int
    observacion: str | None = None


class FilaDisponibilidadImport(BaseModel):
    disponibilidad_id: str
    docente_id: str
    dia_semana: DiaSemana
    hora_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    hora_fin: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    disponible: str | bool = "SI"

    def a_bool_disponible(self) -> bool:
        return _si_no_a_bool(self.disponible)


class SolicitudImportacion(BaseModel):
    """Envoltorio generico: lista de filas ya parseadas por el frontend."""
    filas: list[dict]
