from sqlalchemy.orm import Session

from app.models.disponibilidad_docente import DisponibilidadDocente
from app.repositories.base_repository import BaseRepository


class DisponibilidadRepository(BaseRepository[DisponibilidadDocente]):
    def __init__(self, db: Session):
        super().__init__(DisponibilidadDocente, db)

    def obtener_por_codigo_ext(self, codigo: str) -> DisponibilidadDocente | None:
        return self.obtener_por_campo("codigo_disponibilidad_ext", codigo)
