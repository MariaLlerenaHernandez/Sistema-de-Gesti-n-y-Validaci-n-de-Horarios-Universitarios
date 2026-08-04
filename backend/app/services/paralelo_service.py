from sqlalchemy.orm import Session

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError, ReferenciaInvalidaError
from app.models.paralelo import Paralelo
from app.repositories.asignatura_repository import AsignaturaRepository
from app.repositories.paralelo_repository import ParaleloRepository
from app.schemas.paralelo import ParaleloActualizar, ParaleloCrear


class ParaleloService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ParaleloRepository(db)
        self.repo_asignatura = AsignaturaRepository(db)

    def listar(self, solo_activos: bool = False, skip: int = 0, limit: int = 200) -> list[Paralelo]:
        return self.repo.obtener_todos(solo_activos=solo_activos, skip=skip, limit=limit)

    def obtener(self, paralelo_id: int) -> Paralelo:
        paralelo = self.repo.obtener_por_id(paralelo_id)
        if not paralelo:
            raise EntidadNoEncontradaError("Paralelo", paralelo_id)
        return paralelo

    def crear(self, datos: ParaleloCrear) -> Paralelo:
        if self.repo.obtener_por_codigo_ext(datos.codigo_paralelo_ext):
            raise EntidadDuplicadaError("un paralelo", "codigo_paralelo_ext", datos.codigo_paralelo_ext)
        if not self.repo_asignatura.obtener_por_id(datos.asignatura_id):
            raise ReferenciaInvalidaError(f"La asignatura_id {datos.asignatura_id} no existe.")

        paralelo = Paralelo(**datos.model_dump())
        paralelo = self.repo.crear(paralelo)
        self.db.commit()
        return paralelo

    def actualizar(self, paralelo_id: int, datos: ParaleloActualizar) -> Paralelo:
        paralelo = self.obtener(paralelo_id)
        cambios = datos.model_dump(exclude_unset=True)
        paralelo = self.repo.actualizar(paralelo, cambios)
        self.db.commit()
        return paralelo

    def eliminar(self, paralelo_id: int) -> None:
        paralelo = self.obtener(paralelo_id)
        self.repo.eliminar(paralelo)
        self.db.commit()
