from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Docente(Base):
    __tablename__ = "Docentes"

    docente_id: Mapped[int] = mapped_column(primary_key=True)
    codigo_docente: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    cedula: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    tipo_contrato: Mapped[str] = mapped_column(String(20), nullable=False)
    horas_max_semanales: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.sysutcdatetime())

    disponibilidades = relationship("DisponibilidadDocente", back_populates="docente", cascade="all, delete-orphan")
    distributivos = relationship("Distributivo", back_populates="docente")

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"
