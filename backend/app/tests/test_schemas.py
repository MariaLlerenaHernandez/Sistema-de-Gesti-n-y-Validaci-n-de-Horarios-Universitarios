import pytest
from pydantic import ValidationError

from app.schemas.asignatura import AsignaturaCrear, Modalidad
from app.schemas.disponibilidad_docente import DiaSemana, DisponibilidadCrear
from app.schemas.docente import DocenteCrear, TipoContrato
from app.schemas.espacio import TipoEspacio
from app.schemas.horario import BloqueHorarioCrear


def test_docente_valido():
    docente = DocenteCrear(
        codigo_docente="DOC001", cedula="0102030405", nombres="Ana", apellidos="Lopez",
        correo="ana.lopez@universidad.edu", tipo_contrato=TipoContrato.TIEMPO_COMPLETO,
        horas_max_semanales=40,
    )
    assert docente.horas_max_semanales == 40


def test_docente_horas_maximas_invalidas():
    with pytest.raises(ValidationError):
        DocenteCrear(
            codigo_docente="DOC001", cedula="0102030405", nombres="Ana", apellidos="Lopez",
            correo="ana.lopez@universidad.edu", tipo_contrato=TipoContrato.TIEMPO_COMPLETO,
            horas_max_semanales=0,
        )


def test_docente_correo_invalido():
    with pytest.raises(ValidationError):
        DocenteCrear(
            codigo_docente="DOC001", cedula="0102030405", nombres="Ana", apellidos="Lopez",
            correo="correo-invalido", tipo_contrato=TipoContrato.TIEMPO_COMPLETO,
            horas_max_semanales=10,
        )


def test_asignatura_requiere_laboratorio_sin_tipo_espacio_falla():
    with pytest.raises(ValidationError):
        AsignaturaCrear(
            codigo_asignatura="INF101", nombre_asignatura="Programacion I",
            modalidad=Modalidad.PRESENCIAL, requiere_laboratorio=True,
            tipo_espacio_requerido=None, horas_semanales=6, cupo_estimado=30,
        )


def test_asignatura_requiere_laboratorio_con_tipo_espacio_ok():
    asignatura = AsignaturaCrear(
        codigo_asignatura="INF101", nombre_asignatura="Programacion I",
        modalidad=Modalidad.PRESENCIAL, requiere_laboratorio=True,
        tipo_espacio_requerido=TipoEspacio.LABORATORIO, horas_semanales=6, cupo_estimado=30,
    )
    assert asignatura.tipo_espacio_requerido == TipoEspacio.LABORATORIO


def test_disponibilidad_hora_fin_menor_a_inicio_falla():
    with pytest.raises(ValidationError):
        DisponibilidadCrear(
            codigo_disponibilidad_ext="DISP001", docente_id=1, dia_semana=DiaSemana.LUNES,
            hora_inicio="11:00", hora_fin="07:00",
        )


def test_bloque_horario_horas_invalidas_falla():
    with pytest.raises(ValidationError):
        BloqueHorarioCrear(
            distributivo_id=1, espacio_id=1, dia_semana=DiaSemana.LUNES,
            hora_inicio="10:00", hora_fin="09:00", modalidad=Modalidad.PRESENCIAL,
            periodo_academico="2026A",
        )
