from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Espacio(Base):
    __tablename__ = "Espacios"

    espacio_id: Mapped[int] = mapped_column(primary_key=True)
    codigo_espacio: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre_espacio: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_espacio: Mapped[str] = mapped_column(String(20), nullable=False)
    capacidad: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    edificio: Mapped[str] = mapped_column(String(60), nullable=False)
    piso: Mapped[str | None] = mapped_column(String(10), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    bloques = relationship("BloqueHorario", back_populates="espacio")
