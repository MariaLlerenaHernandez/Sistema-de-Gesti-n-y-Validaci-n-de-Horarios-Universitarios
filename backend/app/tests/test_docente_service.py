from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError
from app.models.docente import Docente
from app.schemas.docente import DocenteCrear, TipoContrato
from app.services.docente_service import DocenteService


def _datos_docente(**overrides):
    base = dict(
        codigo_docente="DOC001", cedula="0102030405", nombres="Ana", apellidos="Lopez",
        correo="ana.lopez@universidad.edu", tipo_contrato=TipoContrato.TIEMPO_COMPLETO,
        horas_max_semanales=40,
    )
    base.update(overrides)
    return DocenteCrear(**base)


@patch("app.services.docente_service.DocenteRepository")
def test_crear_docente_codigo_duplicado_lanza_error(mock_repo_cls):
    mock_repo = MagicMock()
    mock_repo.obtener_por_codigo.return_value = Docente(docente_id=1, codigo_docente="DOC001")
    mock_repo_cls.return_value = mock_repo

    servicio = DocenteService(db=MagicMock())

    with pytest.raises(EntidadDuplicadaError):
        servicio.crear(_datos_docente())


@patch("app.services.docente_service.DocenteRepository")
def test_crear_docente_correo_duplicado_lanza_error(mock_repo_cls):
    mock_repo = MagicMock()
    mock_repo.obtener_por_codigo.return_value = None
    mock_repo.obtener_por_cedula.return_value = None
    mock_repo.obtener_por_correo.return_value = Docente(docente_id=2, correo="ana.lopez@universidad.edu")
    mock_repo_cls.return_value = mock_repo

    servicio = DocenteService(db=MagicMock())

    with pytest.raises(EntidadDuplicadaError):
        servicio.crear(_datos_docente())


@patch("app.services.docente_service.DocenteRepository")
def test_obtener_docente_inexistente_lanza_error(mock_repo_cls):
    mock_repo = MagicMock()
    mock_repo.obtener_por_id.return_value = None
    mock_repo_cls.return_value = mock_repo

    servicio = DocenteService(db=MagicMock())

    with pytest.raises(EntidadNoEncontradaError):
        servicio.obtener(999)


@patch("app.services.docente_service.DocenteRepository")
def test_crear_docente_exitoso(mock_repo_cls):
    mock_repo = MagicMock()
    mock_repo.obtener_por_codigo.return_value = None
    mock_repo.obtener_por_cedula.return_value = None
    mock_repo.obtener_por_correo.return_value = None
    mock_repo.crear.side_effect = lambda instancia: instancia
    mock_repo_cls.return_value = mock_repo

    db = MagicMock()
    servicio = DocenteService(db=db)

    resultado = servicio.crear(_datos_docente())

    assert resultado.codigo_docente == "DOC001"
    db.commit.assert_called_once()
