from sqlalchemy.orm import Session

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError
from app.repositories.docente_repository import DocenteRepository
from app.models.docente import Docente
from app.schemas.docente import DocenteActualizar, DocenteCrear


class DocenteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocenteRepository(db)

    def listar(self, solo_activos: bool = False, skip: int = 0, limit: int = 200) -> list[Docente]:
        return self.repo.obtener_todos(solo_activos=solo_activos, skip=skip, limit=limit)

    def obtener(self, docente_id: int) -> Docente:
        docente = self.repo.obtener_por_id(docente_id)
        if not docente:
            raise EntidadNoEncontradaError("Docente", docente_id)
        return docente

    def crear(self, datos: DocenteCrear) -> Docente:
        if self.repo.obtener_por_codigo(datos.codigo_docente):
            raise EntidadDuplicadaError("un docente", "codigo_docente", datos.codigo_docente)
        if self.repo.obtener_por_cedula(datos.cedula):
            raise EntidadDuplicadaError("un docente", "cedula", datos.cedula)
        if self.repo.obtener_por_correo(datos.correo):
            raise EntidadDuplicadaError("un docente", "correo", datos.correo)

        docente = Docente(**datos.model_dump())
        docente = self.repo.crear(docente)
        self.db.commit()
        return docente

    def actualizar(self, docente_id: int, datos: DocenteActualizar) -> Docente:
        docente = self.obtener(docente_id)
        cambios = datos.model_dump(exclude_unset=True)
        docente = self.repo.actualizar(docente, cambios)
        self.db.commit()
        return docente

    def eliminar(self, docente_id: int) -> None:
        docente = self.obtener(docente_id)
        self.repo.eliminar(docente)
        self.db.commit()
