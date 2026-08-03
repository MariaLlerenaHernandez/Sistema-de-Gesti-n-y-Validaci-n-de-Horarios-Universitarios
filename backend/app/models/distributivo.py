from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Distributivo(Base):
    __tablename__ = "Distributivo"

    distributivo_id: Mapped[int] = mapped_column(primary_key=True)
    codigo_distributivo_ext: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    docente_id: Mapped[int] = mapped_column(ForeignKey("Docentes.docente_id"), nullable=False)
    asignatura_id: Mapped[int] = mapped_column(ForeignKey("Asignaturas.asignatura_id"), nullable=False)
    paralelo_id: Mapped[int] = mapped_column(ForeignKey("Paralelos.paralelo_id"), nullable=False)
    periodo_academico: Mapped[str] = mapped_column(String(20), nullable=False)
    horas_asignadas: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    observacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    docente = relationship("Docente", back_populates="distributivos")
    asignatura = relationship("Asignatura", back_populates="distributivos")
    paralelo = relationship("Paralelo", back_populates="distributivos")
    bloques = relationship("BloqueHorario", back_populates="distributivo", cascade="all, delete-orphan")
