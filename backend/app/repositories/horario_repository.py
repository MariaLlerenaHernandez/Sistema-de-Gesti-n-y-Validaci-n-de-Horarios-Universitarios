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
        Inserta el bloque de horario y a continuacion ejecuta
        sp_ValidarBloqueHorario sobre el bloque recien creado. Retorna el
        bloque_id.

        Nota de diseno: se separan a proposito el INSERT (que solo produce
        el resultset de SCOPE_IDENTITY) de la llamada al procedimiento
        (que produce su propio resultset de conflictos). Si se combinan en
        un unico batch de texto, SQLAlchemy solo lee el PRIMER resultset
        que llega, y como el procedimiento tambien devuelve una columna
        llamada bloque_id, el bug queda oculto en vez de fallar: bastaria
        con que alguien reordene una columna en el SP para que el codigo
        empiece a leer datos equivocados sin ningun error visible.
        """
        resultado = self.db.execute(
            text(
                """
                INSERT INTO dbo.BloquesHorario
                    (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico, estado)
                VALUES
                    (:distributivo_id, :espacio_id, :dia_semana, :hora_inicio, :hora_fin, :modalidad, :periodo_academico, 'PENDIENTE');
                SELECT CAST(SCOPE_IDENTITY() AS INT) AS bloque_id;
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
        nuevo_id = resultado.mappings().first()["bloque_id"]

        # Se ejecuta como paso independiente y se consume su resultset por
        # completo (aunque no se use aqui), para no dejar un cursor con
        # resultados pendientes antes del commit.
        self.db.execute(
            text("EXEC dbo.sp_ValidarBloqueHorario @bloque_id = :bloque_id"),
            {"bloque_id": nuevo_id},
        ).mappings().all()

        self.db.commit()
        return nuevo_id

    def revalidar_bloque(self, bloque_id: int) -> None:
        self.db.execute(text("EXEC dbo.sp_ValidarBloqueHorario @bloque_id = :bloque_id"), {"bloque_id": bloque_id})
        self.db.commit()

    def validar_periodo(self, periodo_academico: str) -> None:
        self.db.execute(
            text("EXEC dbo.sp_ValidarPeriodoAcademico @periodo_academico = :periodo"),
            {"periodo": periodo_academico},
        )
        self.db.commit()

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
