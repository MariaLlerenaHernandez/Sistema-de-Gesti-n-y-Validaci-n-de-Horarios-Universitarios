from sqlalchemy.orm import Session

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError
from app.models.asignatura import Asignatura
from app.repositories.asignatura_repository import AsignaturaRepository
from app.schemas.asignatura import AsignaturaActualizar, AsignaturaCrear


class AsignaturaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AsignaturaRepository(db)

    def listar(self, solo_activos: bool = False, skip: int = 0, limit: int = 200) -> list[Asignatura]:
        return self.repo.obtener_todos(solo_activos=solo_activos, skip=skip, limit=limit)

    def obtener(self, asignatura_id: int) -> Asignatura:
        asignatura = self.repo.obtener_por_id(asignatura_id)
        if not asignatura:
            raise EntidadNoEncontradaError("Asignatura", asignatura_id)
        return asignatura

    def crear(self, datos: AsignaturaCrear) -> Asignatura:
        if self.repo.obtener_por_codigo(datos.codigo_asignatura):
            raise EntidadDuplicadaError("una asignatura", "codigo_asignatura", datos.codigo_asignatura)
        asignatura = Asignatura(**datos.model_dump())
        asignatura = self.repo.crear(asignatura)
        self.db.commit()
        return asignatura

    def actualizar(self, asignatura_id: int, datos: AsignaturaActualizar) -> Asignatura:
        asignatura = self.obtener(asignatura_id)
        cambios = datos.model_dump(exclude_unset=True)
        asignatura = self.repo.actualizar(asignatura, cambios)
        self.db.commit()
        return asignatura

    def eliminar(self, asignatura_id: int) -> None:
        asignatura = self.obtener(asignatura_id)
        self.repo.eliminar(asignatura)
        self.db.commit()
