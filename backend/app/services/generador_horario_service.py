"""
Generador automatico de horarios: toma todo el distributivo cargado (via
Excel) que todavia no tiene un bloque de horario en el periodo, y le
asigna dia/hora/espacio automaticamente, respetando:

  - la disponibilidad declarada del docente (DisponibilidadDocente);
  - que el espacio sea compatible (tipo y capacidad) con la asignatura;
  - que ni el docente ni el espacio queden doblemente ocupados, ni con
    bloques ya existentes en la base de datos ni con los que el propio
    generador va creando en la misma corrida.

Cada bloque que el generador logra ubicar se inserta con
HorarioRepository.crear_y_validar(), que a su vez ejecuta
sp_ValidarBloqueHorario en SQL Server — es decir, la base de datos sigue
siendo la fuente de verdad final de si el bloque quedo VALIDO o no; el
generador solo intenta, de entrada, proponer horarios sin choques
obvios para minimizar conflictos.
"""
from datetime import time
from typing import NamedTuple

from sqlalchemy.orm import Session

from app.repositories.asignatura_repository import AsignaturaRepository
from app.repositories.disponibilidad_repository import DisponibilidadRepository
from app.repositories.distributivo_repository import DistributivoRepository
from app.repositories.docente_repository import DocenteRepository
from app.repositories.espacio_repository import EspacioRepository
from app.repositories.horario_repository import HorarioRepository

INCREMENTO_MINUTOS = 30


class ResultadoGeneracion(NamedTuple):
    programados: int
    ya_existian: int
    sin_agendar: list[dict]


def _a_minutos(t: time) -> int:
    return t.hour * 60 + t.minute


def _a_time(minutos: int) -> time:
    return time(hour=minutos // 60, minute=minutos % 60)


def _se_solapan(dia_a: str, ini_a: int, fin_a: int, dia_b: str, ini_b: int, fin_b: int) -> bool:
    return dia_a == dia_b and ini_a < fin_b and fin_a > ini_b


class GeneradorHorarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo_horario = HorarioRepository(db)
        self.repo_distributivo = DistributivoRepository(db)
        self.repo_docente = DocenteRepository(db)
        self.repo_espacio = EspacioRepository(db)
        self.repo_asignatura = AsignaturaRepository(db)
        self.repo_disponibilidad = DisponibilidadRepository(db)

    def generar(self, periodo_academico: str) -> ResultadoGeneracion:
        distributivos = [
            d for d in self.repo_distributivo.obtener_todos(limit=1000)
            if d.periodo_academico == periodo_academico
        ]
        if not distributivos:
            return ResultadoGeneracion(programados=0, ya_existian=0, sin_agendar=[])

        distributivo_por_id = {d.distributivo_id: d for d in distributivos}
        bloques_existentes = self.repo_horario.obtener_bloques_periodo_orm(periodo_academico)
        ids_con_bloque = {b.distributivo_id for b in bloques_existentes}

        espacios = self.repo_espacio.obtener_todos(solo_activos=True, limit=1000)
        docentes = {d.docente_id: d for d in self.repo_docente.obtener_todos(limit=1000)}
        asignaturas = {a.asignatura_id: a for a in self.repo_asignatura.obtener_todos(limit=1000)}
        disponibilidad_todas = self.repo_disponibilidad.obtener_todos(limit=1000)

        disponibilidad_por_docente: dict[int, list] = {}
        for disp in disponibilidad_todas:
            if not disp.disponible:
                continue
            disponibilidad_por_docente.setdefault(disp.docente_id, []).append(disp)

        # Ocupacion ya existente (bloques previos + los que el generador va creando)
        docente_ocupado: dict[int, list[tuple[str, int, int]]] = {}
        espacio_ocupado: dict[int, list[tuple[str, int, int]]] = {}
        for b in bloques_existentes:
            dist = distributivo_por_id.get(b.distributivo_id)
            if dist is None:
                continue
            docente_ocupado.setdefault(dist.docente_id, []).append(
                (b.dia_semana, _a_minutos(b.hora_inicio), _a_minutos(b.hora_fin))
            )
            espacio_ocupado.setdefault(b.espacio_id, []).append(
                (b.dia_semana, _a_minutos(b.hora_inicio), _a_minutos(b.hora_fin))
            )

        pendientes = [d for d in distributivos if d.distributivo_id not in ids_con_bloque]

        programados = 0
        sin_agendar: list[dict] = []

        for dist in pendientes:
            docente = docentes.get(dist.docente_id)
            asignatura = asignaturas.get(dist.asignatura_id)
            if not docente or not asignatura:
                sin_agendar.append({
                    "codigo_distributivo_ext": dist.codigo_distributivo_ext,
                    "motivo": "El docente o la asignatura de este distributivo ya no existen.",
                })
                continue

            duracion_min = int(asignatura.horas_semanales) * 60
            ventanas = disponibilidad_por_docente.get(dist.docente_id, [])

            espacios_compatibles = [
                e for e in espacios
                if (asignatura.tipo_espacio_requerido is None or e.tipo_espacio == asignatura.tipo_espacio_requerido)
                and e.capacidad >= asignatura.cupo_estimado
            ]

            asignado = False
            for ventana in ventanas:
                if asignado:
                    break
                inicio_ventana = _a_minutos(ventana.hora_inicio)
                fin_ventana = _a_minutos(ventana.hora_fin)
                dia = ventana.dia_semana

                t = inicio_ventana
                while t + duracion_min <= fin_ventana and not asignado:
                    ocupado_docente = any(
                        _se_solapan(dia, t, t + duracion_min, d2, i2, f2)
                        for d2, i2, f2 in docente_ocupado.get(dist.docente_id, [])
                    )
                    if not ocupado_docente:
                        for espacio in espacios_compatibles:
                            libre_espacio = not any(
                                _se_solapan(dia, t, t + duracion_min, d2, i2, f2)
                                for d2, i2, f2 in espacio_ocupado.get(espacio.espacio_id, [])
                            )
                            if libre_espacio:
                                self.repo_horario.crear_y_validar(
                                    distributivo_id=dist.distributivo_id,
                                    espacio_id=espacio.espacio_id,
                                    dia_semana=dia,
                                    hora_inicio=_a_time(t),
                                    hora_fin=_a_time(t + duracion_min),
                                    modalidad=asignatura.modalidad,
                                    periodo_academico=periodo_academico,
                                )
                                docente_ocupado.setdefault(dist.docente_id, []).append((dia, t, t + duracion_min))
                                espacio_ocupado.setdefault(espacio.espacio_id, []).append((dia, t, t + duracion_min))
                                programados += 1
                                asignado = True
                                break
                    t += INCREMENTO_MINUTOS

            if not asignado:
                nombre_docente = f"{docente.nombres} {docente.apellidos}"
                sin_agendar.append({
                    "codigo_distributivo_ext": dist.codigo_distributivo_ext,
                    "motivo": (
                        f"No se encontro un horario y espacio libres para {nombre_docente} "
                        f"({asignatura.nombre_asignatura}) dentro de su disponibilidad declarada."
                    ),
                })

        return ResultadoGeneracion(
            programados=programados,
            ya_existian=len(ids_con_bloque),
            sin_agendar=sin_agendar,
        )
