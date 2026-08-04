from unittest.mock import MagicMock, patch

from app.services.importacion_service import ImportacionService


def _servicio_con_repos_mock():
    db = MagicMock()
    with patch("app.services.importacion_service.DocenteRepository") as docente_repo_cls, \
         patch("app.services.importacion_service.EspacioRepository") as espacio_repo_cls, \
         patch("app.services.importacion_service.AsignaturaRepository") as asignatura_repo_cls, \
         patch("app.services.importacion_service.ParaleloRepository") as paralelo_repo_cls, \
         patch("app.services.importacion_service.DistributivoRepository") as distributivo_repo_cls, \
         patch("app.services.importacion_service.DisponibilidadRepository") as disponibilidad_repo_cls:

        servicio = ImportacionService(db)
        # obtener_por_* devuelven None por defecto -> se tratan como fila nueva
        servicio.repo_docente.obtener_por_codigo.return_value = None
        servicio.repo_espacio.obtener_por_codigo.return_value = None
        servicio.repo_asignatura.obtener_por_codigo.return_value = None
        servicio.repo_paralelo.obtener_por_codigo_ext.return_value = None
        servicio.repo_distributivo.obtener_por_codigo_ext.return_value = None
        servicio.repo_disponibilidad.obtener_por_codigo_ext.return_value = None
        return servicio


def test_importar_docentes_fila_valida_se_procesa():
    servicio = _servicio_con_repos_mock()
    filas = [{
        "docente_id": "DOC001", "cedula": "0102030405", "nombres": "Ana", "apellidos": "Lopez",
        "correo": "ana.lopez@universidad.edu", "tipo_contrato": "TIEMPO_COMPLETO",
        "horas_max_semanales": 40, "activo": "SI",
    }]

    resumen = servicio.importar_docentes(filas)

    assert resumen.filas_procesadas == 1
    assert resumen.filas_con_error == 0


def test_importar_docentes_fila_invalida_no_detiene_el_proceso():
    servicio = _servicio_con_repos_mock()
    filas = [
        {  # valida
            "docente_id": "DOC001", "cedula": "0102030405", "nombres": "Ana", "apellidos": "Lopez",
            "correo": "ana.lopez@universidad.edu", "tipo_contrato": "TIEMPO_COMPLETO",
            "horas_max_semanales": 40, "activo": "SI",
        },
        {  # tipo_contrato invalido
            "docente_id": "DOC002", "cedula": "0102030406", "nombres": "Carlos", "apellidos": "Perez",
            "correo": "carlos.perez@universidad.edu", "tipo_contrato": "CONTRATO_INEXISTENTE",
            "horas_max_semanales": 20, "activo": "SI",
        },
    ]

    resumen = servicio.importar_docentes(filas)

    assert resumen.total_filas == 2
    assert resumen.filas_procesadas == 1
    assert resumen.filas_con_error == 1
    assert resumen.errores[0].fila == 2


def test_importar_paralelos_con_asignatura_inexistente_reporta_error():
    servicio = _servicio_con_repos_mock()
    servicio.repo_asignatura.obtener_por_codigo.return_value = None  # asignatura no existe

    filas = [{
        "paralelo_id": "PAR001", "asignatura_id": "ASI999", "codigo_paralelo": "A",
        "carrera": "Sistemas", "nivel": 1, "jornada": "Matutina",
        "numero_estudiantes": 28, "activo": "SI",
    }]

    resumen = servicio.importar_paralelos(filas)

    assert resumen.filas_procesadas == 0
    assert resumen.filas_con_error == 1
    assert "no existe" in resumen.errores[0].detalle
