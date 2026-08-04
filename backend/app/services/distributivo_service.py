from sqlalchemy.orm import Session

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError, ReferenciaInvalidaError
from app.models.distributivo import Distributivo
from app.repositories.asignatura_repository import AsignaturaRepository
from app.repositories.distributivo_repository import DistributivoRepository
from app.repositories.docente_repository import DocenteRepository
from app.repositories.paralelo_repository import ParaleloRepository
from app.schemas.distributivo import DistributivoActualizar, DistributivoCrear


class DistributivoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DistributivoRepository(db)
        self.repo_docente = DocenteRepository(db)
        self.repo_asignatura = AsignaturaRepository(db)
        self.repo_paralelo = ParaleloRepository(db)

    def listar(self, skip: int = 0, limit: int = 200) -> list[Distributivo]:
        return self.repo.obtener_todos(skip=skip, limit=limit)

    def obtener(self, distributivo_id: int) -> Distributivo:
        distributivo = self.repo.obtener_por_id(distributivo_id)
        if not distributivo:
            raise EntidadNoEncontradaError("Distributivo", distributivo_id)
        return distributivo

    def _validar_referencias(self, datos: DistributivoCrear) -> None:
        if not self.repo_docente.obtener_por_id(datos.docente_id):
            raise ReferenciaInvalidaError(f"El docente_id {datos.docente_id} no existe.")
        if not self.repo_asignatura.obtener_por_id(datos.asignatura_id):
            raise ReferenciaInvalidaError(f"La asignatura_id {datos.asignatura_id} no existe.")
        if not self.repo_paralelo.obtener_por_id(datos.paralelo_id):
            raise ReferenciaInvalidaError(f"El paralelo_id {datos.paralelo_id} no existe.")

    def crear(self, datos: DistributivoCrear) -> Distributivo:
        if self.repo.obtener_por_codigo_ext(datos.codigo_distributivo_ext):
            raise EntidadDuplicadaError("un distributivo", "codigo_distributivo_ext", datos.codigo_distributivo_ext)
        self._validar_referencias(datos)

        distributivo = Distributivo(**datos.model_dump())
        distributivo = self.repo.crear(distributivo)
        self.db.commit()
        return distributivo

    def actualizar(self, distributivo_id: int, datos: DistributivoActualizar) -> Distributivo:
        distributivo = self.obtener(distributivo_id)
        cambios = datos.model_dump(exclude_unset=True)
        distributivo = self.repo.actualizar(distributivo, cambios)
        self.db.commit()
        return distributivo

    def eliminar(self, distributivo_id: int) -> None:
        distributivo = self.obtener(distributivo_id)
        self.repo.eliminar(distributivo)
        self.db.commit()
