from sqlalchemy.orm import Session

from app.models.espacio import Espacio
from app.repositories.base_repository import BaseRepository


class EspacioRepository(BaseRepository[Espacio]):
    def __init__(self, db: Session):
        super().__init__(Espacio, db)

    def obtener_por_codigo(self, codigo_espacio: str) -> Espacio | None:
        return self.obtener_por_campo("codigo_espacio", codigo_espacio)
