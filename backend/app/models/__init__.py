from app.models.docente import Docente
from app.models.espacio import Espacio
from app.models.asignatura import Asignatura
from app.models.paralelo import Paralelo
from app.models.distributivo import Distributivo
from app.models.disponibilidad_docente import DisponibilidadDocente
from app.models.bloque_horario import BloqueHorario, Conflicto

__all__ = [
    "Docente",
    "Espacio",
    "Asignatura",
    "Paralelo",
    "Distributivo",
    "DisponibilidadDocente",
    "BloqueHorario",
    "Conflicto",
]
