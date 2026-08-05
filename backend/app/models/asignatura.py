from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Asignatura(Base):
    __tablename__ = "Asignaturas"

    asignatura_id: Mapped[int] = mapped_column(primary_key=True)
    codigo_asignatura: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    codigo_asignatura_ext: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    nombre_asignatura: Mapped[str] = mapped_column(String(150), nullable=False)
    modalidad: Mapped[str] = mapped_column(String(20), nullable=False)
    requiere_laboratorio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tipo_espacio_requerido: Mapped[str | None] = mapped_column(String(20), nullable=True)
    horas_semanales: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cupo_estimado: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    paralelos = relationship("Paralelo", back_populates="asignatura")
    distributivos = relationship("Distributivo", back_populates="asignatura")
