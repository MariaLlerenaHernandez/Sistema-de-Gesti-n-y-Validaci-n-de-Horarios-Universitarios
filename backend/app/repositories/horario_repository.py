from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.bloque_horario import BloqueHorario, Conflicto
from app.repositories.base_repository import BaseRepository


class HorarioRepository(BaseRepository[BloqueHorario]):
    """
    Repositorio de bloques de horario. Ademas del CRUD generico, expone
    los metodos que invocan los procedimientos almacenados de SQL Server
    responsables de la validacion real de reglas de negocio.
    """

    def __init__(self, db: Session):
        super().__init__(BloqueHorario, db)

    def crear_y_validar(
        self,
        distributivo_id: int,
        espacio_id: int,
        dia_semana: str,
        hora_inicio,
        hora_fin,
        modalidad: str,
        periodo_academico: str,
    ) -> int:
        """
        Inserta el bloque (usando OUTPUT para obtener el ID generado en
        la MISMA sentencia, evitando el problema de multiples result sets
        de pyodbc con lotes INSERT;SELECT) y luego ejecuta, en una
        llamada aparte, el procedimiento que valida las reglas de negocio.
        """
        resultado = self.db.execute(
            text(
                """
                INSERT INTO dbo.BloquesHorario
                    (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico, estado)
                OUTPUT inserted.bloque_id
                VALUES
                    (:distributivo_id, :espacio_id, :dia_semana, :hora_inicio, :hora_fin, :modalidad, :periodo_academico, 'PENDIENTE')
                """
            ),
            {
                "distributivo_id": distributivo_id,
                "espacio_id": espacio_id,
                "dia_semana": dia_semana,
                "hora_inicio": hora_inicio,
                "hora_fin": hora_fin,
                "modalidad": modalidad,
                "periodo_academico": periodo_academico,
            },
        )
        nuevo_id = resultado.scalar_one()

        self.db.execute(text("EXEC dbo.sp_ValidarBloqueHorario @bloque_id = :bloque_id"), {"bloque_id": nuevo_id})
        self.db.commit()
        return nuevo_id

    def mover_bloque(
        self,
        bloque_id: int,
        dia_semana: str,
        hora_inicio,
        hora_fin,
        espacio_id: int | None = None,
    ) -> None:
        """
        Reubica un bloque ya existente (usado por arrastrar-y-soltar en
        el calendario del frontend) y vuelve a validarlo. Deja el estado
        en PENDIENTE antes de revalidar para que, si el nuevo horario ya
        no tiene conflicto, sp_ValidarBloqueHorario lo pueda marcar VALIDO
        limpiamente (y no arrastre un estado CONFLICTO viejo).
        """
        if espacio_id is not None:
            self.db.execute(
                text(
                    """
                    UPDATE dbo.BloquesHorario
                    SET dia_semana = :dia_semana,
                        hora_inicio = :hora_inicio,
                        hora_fin = :hora_fin,
                        espacio_id = :espacio_id,
                        estado = 'PENDIENTE'
                    WHERE bloque_id = :bloque_id
                    """
                ),
                {
                    "dia_semana": dia_semana,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "espacio_id": espacio_id,
                    "bloque_id": bloque_id,
                },
            )
        else:
            self.db.execute(
                text(
                    """
                    UPDATE dbo.BloquesHorario
                    SET dia_semana = :dia_semana,
                        hora_inicio = :hora_inicio,
                        hora_fin = :hora_fin,
                        estado = 'PENDIENTE'
                    WHERE bloque_id = :bloque_id
                    """
                ),
                {
                    "dia_semana": dia_semana,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "bloque_id": bloque_id,
                },
            )

        self.db.execute(text("EXEC dbo.sp_ValidarBloqueHorario @bloque_id = :bloque_id"), {"bloque_id": bloque_id})
        self.db.commit()

    def revalidar_bloque(self, bloque_id: int) -> None:
        self.db.execute(text("EXEC dbo.sp_ValidarBloqueHorario @bloque_id = :bloque_id"), {"bloque_id": bloque_id})
        self.db.commit()

    def validar_periodo(self, periodo_academico: str) -> None:
        self.db.execute(
            text("EXEC dbo.sp_ValidarPeriodoAcademico @periodo_academico = :periodo"),
            {"periodo": periodo_academico},
        )
        self.db.commit()

    def vaciar_periodo(self, periodo_academico: str) -> int:
        """
        Elimina todos los bloques de horario (y sus conflictos asociados,
        via ON DELETE CASCADE) de un periodo academico.

        La tabla tiene un trigger (trg_BloquesHorario_Delete) que impide
        borrar directamente un bloque en estado VALIDO, para evitar
        borrados accidentales. Por eso primero se "des-valida" (estado ->
        PENDIENTE) todo el periodo y luego se borra — asi el trigger no
        bloquea nada, y sigue protegiendo los borrados individuales
        normales del resto del sistema.
        """
        total = self.db.execute(
            text("SELECT COUNT(*) FROM dbo.BloquesHorario WHERE periodo_academico = :periodo"),
            {"periodo": periodo_academico},
        ).scalar_one()

        if total == 0:
            return 0

        self.db.execute(
            text("UPDATE dbo.BloquesHorario SET estado = 'PENDIENTE' WHERE periodo_academico = :periodo"),
            {"periodo": periodo_academico},
        )
        self.db.execute(
            text("DELETE FROM dbo.BloquesHorario WHERE periodo_academico = :periodo"),
            {"periodo": periodo_academico},
        )
        self.db.commit()
        return total

    def obtener_conflictos_de_bloque(self, bloque_id: int) -> list[Conflicto]:
        return list(
            self.db.query(Conflicto).filter(Conflicto.bloque_id == bloque_id).all()
        )

    def obtener_horario_semanal(self, periodo_academico: str) -> list[dict]:
        resultado = self.db.execute(
            text("SELECT * FROM dbo.vw_HorarioSemanal WHERE periodo_academico = :periodo ORDER BY dia_semana, hora_inicio"),
            {"periodo": periodo_academico},
        )
        return [dict(fila) for fila in resultado.mappings().all()]

    def obtener_conflictos_periodo(self, periodo_academico: str) -> list[dict]:
        resultado = self.db.execute(
            text("SELECT * FROM dbo.vw_ConflictosDetalle WHERE periodo_academico = :periodo ORDER BY fecha_deteccion DESC"),
            {"periodo": periodo_academico},
        )
        return [dict(fila) for fila in resultado.mappings().all()]
