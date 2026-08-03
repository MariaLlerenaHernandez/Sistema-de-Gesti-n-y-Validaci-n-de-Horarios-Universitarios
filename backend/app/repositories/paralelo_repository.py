from sqlalchemy.orm import Session

from app.models.paralelo import Paralelo
from app.repositories.base_repository import BaseRepository


class ParaleloRepository(BaseRepository[Paralelo]):
    def __init__(self, db: Session):
        super().__init__(Paralelo, db)

    def obtener_por_codigo_ext(self, codigo_paralelo_ext: str) -> Paralelo | None:
        return self.obtener_por_campo("codigo_paralelo_ext", codigo_paralelo_ext)
