from sqlalchemy.orm import Session

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError
from app.models.espacio import Espacio
from app.repositories.espacio_repository import EspacioRepository
from app.schemas.espacio import EspacioActualizar, EspacioCrear


class EspacioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EspacioRepository(db)

    def listar(self, solo_activos: bool = False, skip: int = 0, limit: int = 200) -> list[Espacio]:
        return self.repo.obtener_todos(solo_activos=solo_activos, skip=skip, limit=limit)

    def obtener(self, espacio_id: int) -> Espacio:
        espacio = self.repo.obtener_por_id(espacio_id)
        if not espacio:
            raise EntidadNoEncontradaError("Espacio", espacio_id)
        return espacio

    def crear(self, datos: EspacioCrear) -> Espacio:
        if self.repo.obtener_por_codigo(datos.codigo_espacio):
            raise EntidadDuplicadaError("un espacio", "codigo_espacio", datos.codigo_espacio)
        espacio = Espacio(**datos.model_dump())
        espacio = self.repo.crear(espacio)
        self.db.commit()
        return espacio

    def actualizar(self, espacio_id: int, datos: EspacioActualizar) -> Espacio:
        espacio = self.obtener(espacio_id)
        cambios = datos.model_dump(exclude_unset=True)
        espacio = self.repo.actualizar(espacio, cambios)
        self.db.commit()
        return espacio

    def eliminar(self, espacio_id: int) -> None:
        espacio = self.obtener(espacio_id)
        self.repo.eliminar(espacio)
        self.db.commit()
