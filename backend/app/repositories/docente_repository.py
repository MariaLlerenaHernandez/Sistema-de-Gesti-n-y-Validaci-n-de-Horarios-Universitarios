from sqlalchemy.orm import Session

from app.models.docente import Docente
from app.repositories.base_repository import BaseRepository


class DocenteRepository(BaseRepository[Docente]):
    def __init__(self, db: Session):
        super().__init__(Docente, db)

    def obtener_por_codigo(self, codigo_docente: str) -> Docente | None:
        return self.obtener_por_campo("codigo_docente", codigo_docente)

    def obtener_por_cedula(self, cedula: str) -> Docente | None:
        return self.obtener_por_campo("cedula", cedula)

    def obtener_por_correo(self, correo: str) -> Docente | None:
        return self.obtener_por_campo("correo", correo)
