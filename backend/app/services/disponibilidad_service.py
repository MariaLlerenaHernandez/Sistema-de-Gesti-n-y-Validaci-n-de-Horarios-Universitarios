from sqlalchemy.orm import Session

from app.core.exceptions import EntidadDuplicadaError, EntidadNoEncontradaError, ReferenciaInvalidaError
from app.models.disponibilidad_docente import DisponibilidadDocente
from app.repositories.disponibilidad_repository import DisponibilidadRepository
from app.repositories.docente_repository import DocenteRepository
from app.schemas.disponibilidad_docente import DisponibilidadCrear


class DisponibilidadService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DisponibilidadRepository(db)
        self.repo_docente = DocenteRepository(db)

    def listar_por_docente(self, docente_id: int) -> list[DisponibilidadDocente]:
        return [d for d in self.repo.obtener_todos(limit=1000) if d.docente_id == docente_id]

    def listar(self, skip: int = 0, limit: int = 500) -> list[DisponibilidadDocente]:
        return self.repo.obtener_todos(skip=skip, limit=limit)

    def obtener(self, disponibilidad_id: int) -> DisponibilidadDocente:
        disponibilidad = self.repo.obtener_por_id(disponibilidad_id)
        if not disponibilidad:
            raise EntidadNoEncontradaError("Disponibilidad", disponibilidad_id)
        return disponibilidad

    def crear(self, datos: DisponibilidadCrear) -> DisponibilidadDocente:
        if self.repo.obtener_por_codigo_ext(datos.codigo_disponibilidad_ext):
            raise EntidadDuplicadaError("una disponibilidad", "codigo_disponibilidad_ext", datos.codigo_disponibilidad_ext)
        if not self.repo_docente.obtener_por_id(datos.docente_id):
            raise ReferenciaInvalidaError(f"El docente_id {datos.docente_id} no existe.")

        payload = datos.model_dump()
        payload["dia_semana"] = datos.dia_semana.value
        disponibilidad = DisponibilidadDocente(**payload)
        disponibilidad = self.repo.crear(disponibilidad)
        self.db.commit()
        return disponibilidad

    def eliminar(self, disponibilidad_id: int) -> None:
        disponibilidad = self.obtener(disponibilidad_id)
        self.repo.eliminar(disponibilidad)
        self.db.commit()
