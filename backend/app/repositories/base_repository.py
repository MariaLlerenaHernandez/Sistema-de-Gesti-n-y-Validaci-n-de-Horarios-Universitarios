"""
Repositorio generico: encapsula el acceso a datos via SQLAlchemy para
evitar duplicar codigo CRUD en cada repositorio concreto.
"""
from typing import Generic, TypeVar

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def obtener_por_id(self, id_valor: int) -> ModelType | None:
        return self.db.get(self.model, id_valor)

    def obtener_todos(self, *, solo_activos: bool = False, skip: int = 0, limit: int = 200) -> list[ModelType]:
        stmt = select(self.model)
        if solo_activos and hasattr(self.model, "activo"):
            stmt = stmt.where(self.model.activo == True)  # noqa: E712
        # SQL Server exige un ORDER BY explicito para poder usar OFFSET/LIMIT
        # (a diferencia de PostgreSQL/MySQL/SQLite, que lo permiten sin el).
        # Se ordena de forma generica por la(s) columna(s) de clave primaria
        # del modelo, para que este repositorio siga sirviendo para
        # cualquier entidad sin tener que conocer sus columnas especificas.
        columnas_pk = inspect(self.model).primary_key
        stmt = stmt.order_by(*columnas_pk).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def obtener_por_campo(self, campo: str, valor) -> ModelType | None:
        stmt = select(self.model).where(getattr(self.model, campo) == valor)
        return self.db.execute(stmt).scalars().first()

    def crear(self, instancia: ModelType) -> ModelType:
        self.db.add(instancia)
        self.db.flush()
        self.db.refresh(instancia)
        return instancia

    def actualizar(self, instancia: ModelType, datos: dict) -> ModelType:
        for campo, valor in datos.items():
            setattr(instancia, campo, valor)
        self.db.flush()
        self.db.refresh(instancia)
        return instancia

    def eliminar(self, instancia: ModelType) -> None:
        self.db.delete(instancia)
        self.db.flush()