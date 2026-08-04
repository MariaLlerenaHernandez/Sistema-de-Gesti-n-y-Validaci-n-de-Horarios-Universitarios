"""
Servicio de importacion inicial de datos. Recibe listas de filas ya
convertidas a JSON por el frontend (ver anexo de formatos de carga
Excel) y las valida y persiste fila por fila, acumulando errores sin
detener el proceso completo.
"""
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.asignatura import Asignatura
from app.models.disponibilidad_docente import DisponibilidadDocente
from app.models.distributivo import Distributivo
from app.models.docente import Docente
from app.models.espacio import Espacio
from app.models.paralelo import Paralelo
from app.repositories.asignatura_repository import AsignaturaRepository
from app.repositories.disponibilidad_repository import DisponibilidadRepository
from app.repositories.distributivo_repository import DistributivoRepository
from app.repositories.docente_repository import DocenteRepository
from app.repositories.espacio_repository import EspacioRepository
from app.repositories.paralelo_repository import ParaleloRepository
from app.schemas.common import ErrorFila, ResumenImportacion
from app.schemas.importacion import (
    FilaAsignaturaImport,
    FilaDisponibilidadImport,
    FilaDistributivoImport,
    FilaDocenteImport,
    FilaEspacioImport,
    FilaParaleloImport,
)


def _hora_a_time(valor: str):
    return datetime.strptime(valor, "%H:%M").time()


class ImportacionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo_docente = DocenteRepository(db)
        self.repo_espacio = EspacioRepository(db)
        self.repo_asignatura = AsignaturaRepository(db)
        self.repo_paralelo = ParaleloRepository(db)
        self.repo_distributivo = DistributivoRepository(db)
        self.repo_disponibilidad = DisponibilidadRepository(db)

    # ------------------------------------------------------------------
    def importar_docentes(self, filas: list[dict]) -> ResumenImportacion:
        errores: list[ErrorFila] = []
        procesadas = 0

        for i, fila_raw in enumerate(filas, start=1):
            try:
                fila = FilaDocenteImport(**fila_raw)
            except ValidationError as e:
                errores.append(ErrorFila(fila=i, detalle=str(e.errors()[0]["msg"])))
                continue

            existente = self.repo_docente.obtener_por_codigo(fila.docente_id)
            datos = dict(
                codigo_docente=fila.docente_id,
                cedula=fila.cedula,
                nombres=fila.nombres,
                apellidos=fila.apellidos,
                correo=fila.correo,
                tipo_contrato=fila.tipo_contrato.value,
                horas_max_semanales=fila.horas_max_semanales,
                activo=fila.a_bool_activo(),
            )
            if existente:
                self.repo_docente.actualizar(existente, datos)
            else:
                self.repo_docente.crear(Docente(**datos))
            procesadas += 1

        self.db.commit()
        return ResumenImportacion(
            entidad="docentes", total_filas=len(filas), filas_procesadas=procesadas,
            filas_con_error=len(errores), errores=errores,
        )

    # ------------------------------------------------------------------
    def importar_espacios(self, filas: list[dict]) -> ResumenImportacion:
        errores: list[ErrorFila] = []
        procesadas = 0

        for i, fila_raw in enumerate(filas, start=1):
            try:
                fila = FilaEspacioImport(**fila_raw)
            except ValidationError as e:
                errores.append(ErrorFila(fila=i, detalle=str(e.errors()[0]["msg"])))
                continue

            existente = self.repo_espacio.obtener_por_codigo(fila.codigo_espacio)
            datos = dict(
                codigo_espacio=fila.codigo_espacio,
                nombre_espacio=fila.nombre_espacio,
                tipo_espacio=fila.tipo_espacio.value,
                capacidad=fila.capacidad,
                edificio=fila.edificio,
                piso=fila.piso,
                activo=fila.a_bool_activo(),
            )
            if existente:
                self.repo_espacio.actualizar(existente, datos)
            else:
                self.repo_espacio.crear(Espacio(**datos))
            procesadas += 1

        self.db.commit()
        return ResumenImportacion(
            entidad="espacios", total_filas=len(filas), filas_procesadas=procesadas,
            filas_con_error=len(errores), errores=errores,
        )

    # ------------------------------------------------------------------
    def importar_asignaturas(self, filas: list[dict]) -> ResumenImportacion:
        errores: list[ErrorFila] = []
        procesadas = 0

        for i, fila_raw in enumerate(filas, start=1):
            try:
                fila = FilaAsignaturaImport(**fila_raw)
            except ValidationError as e:
                errores.append(ErrorFila(fila=i, detalle=str(e.errors()[0]["msg"])))
                continue

            existente = self.repo_asignatura.obtener_por_codigo(fila.codigo_asignatura)
            datos = dict(
                codigo_asignatura=fila.codigo_asignatura,
                nombre_asignatura=fila.nombre_asignatura,
                modalidad=fila.modalidad.value,
                requiere_laboratorio=fila.a_bool_requiere_lab(),
                tipo_espacio_requerido=fila.tipo_espacio_requerido.value if fila.tipo_espacio_requerido else None,
                horas_semanales=fila.horas_semanales,
                cupo_estimado=fila.cupo_estimado,
                activo=fila.a_bool_activo(),
            )
            if existente:
                self.repo_asignatura.actualizar(existente, datos)
            else:
                self.repo_asignatura.crear(Asignatura(**datos))
            procesadas += 1

        self.db.commit()
        return ResumenImportacion(
            entidad="asignaturas", total_filas=len(filas), filas_procesadas=procesadas,
            filas_con_error=len(errores), errores=errores,
        )

    # ------------------------------------------------------------------
    def importar_paralelos(self, filas: list[dict]) -> ResumenImportacion:
        errores: list[ErrorFila] = []
        procesadas = 0

        for i, fila_raw in enumerate(filas, start=1):
            try:
                fila = FilaParaleloImport(**fila_raw)
            except ValidationError as e:
                errores.append(ErrorFila(fila=i, detalle=str(e.errors()[0]["msg"])))
                continue

            asignatura = self.repo_asignatura.obtener_por_codigo(fila.asignatura_id)
            if not asignatura:
                errores.append(ErrorFila(fila=i, columna="asignatura_id", detalle=f"La asignatura '{fila.asignatura_id}' no existe."))
                continue

            existente = self.repo_paralelo.obtener_por_codigo_ext(fila.paralelo_id)
            datos = dict(
                codigo_paralelo_ext=fila.paralelo_id,
                asignatura_id=asignatura.asignatura_id,
                codigo_paralelo=fila.codigo_paralelo,
                carrera=fila.carrera,
                nivel=fila.nivel,
                jornada=fila.jornada.value,
                numero_estudiantes=fila.numero_estudiantes,
                activo=fila.a_bool_activo(),
            )
            if existente:
                self.repo_paralelo.actualizar(existente, datos)
            else:
                self.repo_paralelo.crear(Paralelo(**datos))
            procesadas += 1

        self.db.commit()
        return ResumenImportacion(
            entidad="paralelos", total_filas=len(filas), filas_procesadas=procesadas,
            filas_con_error=len(errores), errores=errores,
        )

    # ------------------------------------------------------------------
    def importar_distributivo(self, filas: list[dict]) -> ResumenImportacion:
        errores: list[ErrorFila] = []
        procesadas = 0

        for i, fila_raw in enumerate(filas, start=1):
            try:
                fila = FilaDistributivoImport(**fila_raw)
            except ValidationError as e:
                errores.append(ErrorFila(fila=i, detalle=str(e.errors()[0]["msg"])))
                continue

            docente = self.repo_docente.obtener_por_codigo(fila.docente_id)
            asignatura = self.repo_asignatura.obtener_por_codigo(fila.asignatura_id)
            paralelo = self.repo_paralelo.obtener_por_codigo_ext(fila.paralelo_id)

            if not docente:
                errores.append(ErrorFila(fila=i, columna="docente_id", detalle=f"El docente '{fila.docente_id}' no existe."))
                continue
            if not asignatura:
                errores.append(ErrorFila(fila=i, columna="asignatura_id", detalle=f"La asignatura '{fila.asignatura_id}' no existe."))
                continue
            if not paralelo:
                errores.append(ErrorFila(fila=i, columna="paralelo_id", detalle=f"El paralelo '{fila.paralelo_id}' no existe."))
                continue

            existente = self.repo_distributivo.obtener_por_codigo_ext(fila.distributivo_id)
            datos = dict(
                codigo_distributivo_ext=fila.distributivo_id,
                docente_id=docente.docente_id,
                asignatura_id=asignatura.asignatura_id,
                paralelo_id=paralelo.paralelo_id,
                periodo_academico=fila.periodo_academico,
                horas_asignadas=fila.horas_asignadas,
                observacion=fila.observacion,
            )
            if existente:
                self.repo_distributivo.actualizar(existente, datos)
            else:
                self.repo_distributivo.crear(Distributivo(**datos))
            procesadas += 1

        self.db.commit()
        return ResumenImportacion(
            entidad="distributivo", total_filas=len(filas), filas_procesadas=procesadas,
            filas_con_error=len(errores), errores=errores,
        )

    # ------------------------------------------------------------------
    def importar_disponibilidad(self, filas: list[dict]) -> ResumenImportacion:
        errores: list[ErrorFila] = []
        procesadas = 0

        for i, fila_raw in enumerate(filas, start=1):
            try:
                fila = FilaDisponibilidadImport(**fila_raw)
            except ValidationError as e:
                errores.append(ErrorFila(fila=i, detalle=str(e.errors()[0]["msg"])))
                continue

            docente = self.repo_docente.obtener_por_codigo(fila.docente_id)
            if not docente:
                errores.append(ErrorFila(fila=i, columna="docente_id", detalle=f"El docente '{fila.docente_id}' no existe."))
                continue

            try:
                hora_inicio = _hora_a_time(fila.hora_inicio)
                hora_fin = _hora_a_time(fila.hora_fin)
            except ValueError:
                errores.append(ErrorFila(fila=i, columna="hora_inicio/hora_fin", detalle="Formato de hora invalido, se espera HH:MM."))
                continue

            if hora_fin <= hora_inicio:
                errores.append(ErrorFila(fila=i, columna="hora_fin", detalle="hora_fin debe ser mayor que hora_inicio."))
                continue

            existente = self.repo_disponibilidad.obtener_por_codigo_ext(fila.disponibilidad_id)
            datos = dict(
                codigo_disponibilidad_ext=fila.disponibilidad_id,
                docente_id=docente.docente_id,
                dia_semana=fila.dia_semana.value,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                disponible=fila.a_bool_disponible(),
            )
            if existente:
                self.repo_disponibilidad.actualizar(existente, datos)
            else:
                self.repo_disponibilidad.crear(DisponibilidadDocente(**datos))
            procesadas += 1

        self.db.commit()
        return ResumenImportacion(
            entidad="disponibilidad_docente", total_filas=len(filas), filas_procesadas=procesadas,
            filas_con_error=len(errores), errores=errores,
        )
