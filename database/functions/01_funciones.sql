/* =====================================================================================
   Script: 01_funciones.sql
   Descripcion: Funciones escalares de validacion de reglas del dominio.
   Cada funcion resuelve UNA regla de negocio y es reutilizada por los stored procedures.
   ===================================================================================== */
USE HorariosUniversitarios;
GO

/* ---------------------------------------------------------------------------------
   fn_DocenteTieneTraslape
   1 si el docente ya tiene un bloque que se traslapa con el horario indicado,
   en el mismo periodo academico (excluye el propio bloque al revalidar).
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.fn_DocenteTieneTraslape', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_DocenteTieneTraslape;
GO
CREATE FUNCTION dbo.fn_DocenteTieneTraslape (
    @docente_id         INT,
    @periodo_academico  VARCHAR(20),
    @dia_semana         VARCHAR(15),
    @hora_inicio        TIME(0),
    @hora_fin           TIME(0),
    @bloque_id_excluir  INT = NULL
)
RETURNS BIT
AS
BEGIN
    DECLARE @resultado BIT = 0;
    IF EXISTS (
        SELECT 1
        FROM dbo.BloquesHorario b
        INNER JOIN dbo.Distributivo d ON d.distributivo_id = b.distributivo_id
        WHERE d.docente_id = @docente_id
          AND b.periodo_academico = @periodo_academico
          AND b.dia_semana = @dia_semana
          AND b.estado <> 'CONFLICTO'
          AND (@bloque_id_excluir IS NULL OR b.bloque_id <> @bloque_id_excluir)
          AND @hora_inicio < b.hora_fin
          AND @hora_fin > b.hora_inicio
    )
        SET @resultado = 1;
    RETURN @resultado;
END
GO

/* ---------------------------------------------------------------------------------
   fn_EspacioOcupado
   1 si el espacio fisico ya esta ocupado en la franja indicada.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.fn_EspacioOcupado', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_EspacioOcupado;
GO
CREATE FUNCTION dbo.fn_EspacioOcupado (
    @espacio_id         INT,
    @periodo_academico  VARCHAR(20),
    @dia_semana         VARCHAR(15),
    @hora_inicio        TIME(0),
    @hora_fin           TIME(0),
    @bloque_id_excluir  INT = NULL
)
RETURNS BIT
AS
BEGIN
    DECLARE @resultado BIT = 0;
    IF EXISTS (
        SELECT 1
        FROM dbo.BloquesHorario b
        WHERE b.espacio_id = @espacio_id
          AND b.periodo_academico = @periodo_academico
          AND b.dia_semana = @dia_semana
          AND b.estado <> 'CONFLICTO'
          AND (@bloque_id_excluir IS NULL OR b.bloque_id <> @bloque_id_excluir)
          AND @hora_inicio < b.hora_fin
          AND @hora_fin > b.hora_inicio
    )
        SET @resultado = 1;
    RETURN @resultado;
END
GO

/* ---------------------------------------------------------------------------------
   fn_DocenteDentroDisponibilidad
   1 si el horario propuesto cae DENTRO de un rango de disponibilidad declarado
   (disponible = 1) para ese docente y dia.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.fn_DocenteDentroDisponibilidad', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_DocenteDentroDisponibilidad;
GO
CREATE FUNCTION dbo.fn_DocenteDentroDisponibilidad (
    @docente_id     INT,
    @dia_semana     VARCHAR(15),
    @hora_inicio    TIME(0),
    @hora_fin       TIME(0)
)
RETURNS BIT
AS
BEGIN
    DECLARE @resultado BIT = 0;
    IF EXISTS (
        SELECT 1
        FROM dbo.DisponibilidadDocente dd
        WHERE dd.docente_id = @docente_id
          AND dd.dia_semana = @dia_semana
          AND dd.disponible = 1
          AND dd.hora_inicio <= @hora_inicio
          AND dd.hora_fin >= @hora_fin
    )
        SET @resultado = 1;
    RETURN @resultado;
END
GO

/* ---------------------------------------------------------------------------------
   fn_EspacioCompatible
   1 si el espacio es compatible con el tipo y el cupo requerido por la asignatura.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.fn_EspacioCompatible', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_EspacioCompatible;
GO
CREATE FUNCTION dbo.fn_EspacioCompatible (
    @asignatura_id  INT,
    @espacio_id     INT
)
RETURNS BIT
AS
BEGIN
    DECLARE @resultado BIT = 0;
    DECLARE @tipo_requerido VARCHAR(20);
    DECLARE @tipo_espacio VARCHAR(20);
    DECLARE @capacidad_espacio SMALLINT;
    DECLARE @cupo_estimado SMALLINT;

    SELECT @tipo_requerido = tipo_espacio_requerido, @cupo_estimado = cupo_estimado
    FROM dbo.Asignaturas WHERE asignatura_id = @asignatura_id;

    SELECT @tipo_espacio = tipo_espacio, @capacidad_espacio = capacidad
    FROM dbo.Espacios WHERE espacio_id = @espacio_id;

    IF (@tipo_requerido IS NULL OR @tipo_requerido = @tipo_espacio)
       AND (@capacidad_espacio >= @cupo_estimado)
        SET @resultado = 1;

    RETURN @resultado;
END
GO

/* ---------------------------------------------------------------------------------
   fn_CargaHorariaDocente
   Suma de horas ya asignadas (bloques de horario) a un docente en un periodo
   academico, considerando solo bloques que no estan en estado CONFLICTO.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.fn_CargaHorariaDocente', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_CargaHorariaDocente;
GO
CREATE FUNCTION dbo.fn_CargaHorariaDocente (
    @docente_id         INT,
    @periodo_academico  VARCHAR(20)
)
RETURNS DECIMAL(6,2)
AS
BEGIN
    DECLARE @total DECIMAL(6,2) = 0;
    SELECT @total = ISNULL(SUM(DATEDIFF(MINUTE, b.hora_inicio, b.hora_fin)) / 60.0, 0)
    FROM dbo.BloquesHorario b
    INNER JOIN dbo.Distributivo d ON d.distributivo_id = b.distributivo_id
    WHERE d.docente_id = @docente_id
      AND b.periodo_academico = @periodo_academico
      AND b.estado <> 'CONFLICTO';
    RETURN @total;
END
GO
