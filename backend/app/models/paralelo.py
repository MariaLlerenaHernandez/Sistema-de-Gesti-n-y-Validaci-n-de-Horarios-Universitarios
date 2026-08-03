from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Paralelo(Base):
    __tablename__ = "Paralelos"

    paralelo_id: Mapped[int] = mapped_column(primary_key=True)
    codigo_paralelo_ext: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    asignatura_id: Mapped[int] = mapped_column(ForeignKey("Asignaturas.asignatura_id"), nullable=False)
    codigo_paralelo: Mapped[str] = mapped_column(String(10), nullable=False)
    carrera: Mapped[str] = mapped_column(String(100), nullable=False)
    nivel: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    jornada: Mapped[str] = mapped_column(String(20), nullable=False)
    numero_estudiantes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    asignatura = relationship("Asignatura", back_populates="paralelos")
    distributivos = relationship("Distributivo", back_populates="paralelo")
