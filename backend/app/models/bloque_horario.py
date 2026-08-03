from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BloqueHorario(Base):
    __tablename__ = "BloquesHorario"

    bloque_id: Mapped[int] = mapped_column(primary_key=True)
    distributivo_id: Mapped[int] = mapped_column(ForeignKey("Distributivo.distributivo_id"), nullable=False)
    espacio_id: Mapped[int] = mapped_column(ForeignKey("Espacios.espacio_id"), nullable=False)
    dia_semana: Mapped[str] = mapped_column(String(15), nullable=False)
    hora_inicio: Mapped[str] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[str] = mapped_column(Time, nullable=False)
    modalidad: Mapped[str] = mapped_column(String(20), nullable=False)
    periodo_academico: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE", nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())
    fecha_validacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    distributivo = relationship("Distributivo", back_populates="bloques")
    espacio = relationship("Espacio", back_populates="bloques")
    conflictos = relationship("Conflicto", back_populates="bloque", cascade="all, delete-orphan")


class Conflicto(Base):
    __tablename__ = "Conflictos"

    conflicto_id: Mapped[int] = mapped_column(primary_key=True)
    bloque_id: Mapped[int] = mapped_column(ForeignKey("BloquesHorario.bloque_id"), nullable=False)
    tipo_conflicto: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    severidad: Mapped[str] = mapped_column(String(20), default="ALTA", nullable=False)
    fecha_deteccion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    bloque = relationship("BloqueHorario", back_populates="conflictos")
