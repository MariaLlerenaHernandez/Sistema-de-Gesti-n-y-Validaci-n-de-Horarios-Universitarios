from sqlalchemy.orm import Session

from app.models.distributivo import Distributivo
from app.repositories.base_repository import BaseRepository


class DistributivoRepository(BaseRepository[Distributivo]):
    def __init__(self, db: Session):
        super().__init__(Distributivo, db)

    def obtener_por_codigo_ext(self, codigo_distributivo_ext: str) -> Distributivo | None:
        return self.obtener_por_campo("codigo_distributivo_ext", codigo_distributivo_ext)
