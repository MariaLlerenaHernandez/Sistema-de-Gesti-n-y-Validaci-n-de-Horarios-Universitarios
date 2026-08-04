from sqlalchemy.orm import Session

from app.core.exceptions import EntidadNoEncontradaError, ReferenciaInvalidaError
from app.models.bloque_horario import BloqueHorario
from app.repositories.distributivo_repository import DistributivoRepository
from app.repositories.espacio_repository import EspacioRepository
from app.repositories.horario_repository import HorarioRepository
from app.schemas.horario import BloqueHorarioCrear, ConflictoRespuesta, ResultadoValidacion


class HorarioService:
    """
    Orquesta el registro de propuestas de horario (bloques) y delega la
    validacion real de las reglas del dominio en la base de datos
    (funciones + procedimiento almacenado sp_ValidarBloqueHorario),
    que es la fuente de verdad de las reglas de negocio.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = HorarioRepository(db)
        self.repo_distributivo = DistributivoRepository(db)
        self.repo_espacio = EspacioRepository(db)

    def registrar_y_validar(self, datos: BloqueHorarioCrear) -> ResultadoValidacion:
        if not self.repo_distributivo.obtener_por_id(datos.distributivo_id):
            raise ReferenciaInvalidaError(f"El distributivo_id {datos.distributivo_id} no existe.")
        if not self.repo_espacio.obtener_por_id(datos.espacio_id):
            raise ReferenciaInvalidaError(f"El espacio_id {datos.espacio_id} no existe.")

        bloque_id = self.repo.crear_y_validar(
            distributivo_id=datos.distributivo_id,
            espacio_id=datos.espacio_id,
            dia_semana=datos.dia_semana.value,
            hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin,
            modalidad=datos.modalidad.value,
            periodo_academico=datos.periodo_academico,
        )
        return self._construir_resultado(bloque_id)

    def revalidar(self, bloque_id: int) -> ResultadoValidacion:
        bloque = self.repo.obtener_por_id(bloque_id)
        if not bloque:
            raise EntidadNoEncontradaError("Bloque de horario", bloque_id)
        self.repo.revalidar_bloque(bloque_id)
        return self._construir_resultado(bloque_id)

    def validar_periodo(self, periodo_academico: str) -> list[dict]:
        self.repo.validar_periodo(periodo_academico)
        return self.repo.obtener_horario_semanal(periodo_academico)

    def obtener_bloque(self, bloque_id: int) -> BloqueHorario:
        bloque = self.repo.obtener_por_id(bloque_id)
        if not bloque:
            raise EntidadNoEncontradaError("Bloque de horario", bloque_id)
        return bloque

    def obtener_horario_semanal(self, periodo_academico: str) -> list[dict]:
        return self.repo.obtener_horario_semanal(periodo_academico)

    def obtener_conflictos(self, periodo_academico: str) -> list[dict]:
        return self.repo.obtener_conflictos_periodo(periodo_academico)

    def _construir_resultado(self, bloque_id: int) -> ResultadoValidacion:
        bloque = self.obtener_bloque(bloque_id)
        conflictos = self.repo.obtener_conflictos_de_bloque(bloque_id)
        return ResultadoValidacion(
            bloque_id=bloque_id,
            estado_general=bloque.estado,
            conflictos=[ConflictoRespuesta.model_validate(c) for c in conflictos],
        )
