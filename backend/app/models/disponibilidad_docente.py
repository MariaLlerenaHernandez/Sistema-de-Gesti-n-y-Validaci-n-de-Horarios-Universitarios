from sqlalchemy import Boolean, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class DisponibilidadDocente(Base):
    __tablename__ = "DisponibilidadDocente"

    disponibilidad_id: Mapped[int] = mapped_column(primary_key=True)
    codigo_disponibilidad_ext: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    docente_id: Mapped[int] = mapped_column(ForeignKey("Docentes.docente_id"), nullable=False)
    dia_semana: Mapped[str] = mapped_column(String(15), nullable=False)
    hora_inicio: Mapped[str] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[str] = mapped_column(Time, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    docente = relationship("Docente", back_populates="disponibilidades")
