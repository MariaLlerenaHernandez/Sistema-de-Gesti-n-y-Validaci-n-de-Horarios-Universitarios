from sqlalchemy.orm import Session

from app.models.asignatura import Asignatura
from app.repositories.base_repository import BaseRepository


class AsignaturaRepository(BaseRepository[Asignatura]):
    def __init__(self, db: Session):
        super().__init__(Asignatura, db)

    def obtener_por_codigo(self, codigo_asignatura: str) -> Asignatura | None:
        return self.obtener_por_campo("codigo_asignatura", codigo_asignatura)
