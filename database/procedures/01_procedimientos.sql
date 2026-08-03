/* =====================================================================================
   Script: 01_procedimientos.sql
   Descripcion: Procedimientos almacenados de validacion de horarios.
   Este es el nucleo de negocio de la base de datos.
   ===================================================================================== */
USE HorariosUniversitarios;
GO

/* ---------------------------------------------------------------------------------
   sp_ValidarBloqueHorario
   Procedimiento principal: valida UN bloque de horario contra todas las reglas
   del dominio, limpia sus conflictos previos, inserta los conflictos vigentes y
   actualiza el estado del bloque (VALIDO | CONFLICTO). Devuelve el detalle.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.sp_ValidarBloqueHorario', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_ValidarBloqueHorario;
GO
CREATE PROCEDURE dbo.sp_ValidarBloqueHorario
    @bloque_id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @docente_id INT, @asignatura_id INT, @espacio_id INT;
    DECLARE @periodo_academico VARCHAR(20), @dia_semana VARCHAR(15);
    DECLARE @hora_inicio TIME(0), @hora_fin TIME(0);
    DECLARE @horas_max_semanales SMALLINT;
    DECLARE @carga_actual DECIMAL(6,2);

    SELECT
        @docente_id        = dist.docente_id,
        @asignatura_id     = dist.asignatura_id,
        @espacio_id        = b.espacio_id,
        @periodo_academico = b.periodo_academico,
        @dia_semana        = b.dia_semana,
        @hora_inicio       = b.hora_inicio,
        @hora_fin          = b.hora_fin
    FROM dbo.BloquesHorario b
    INNER JOIN dbo.Distributivo dist ON dist.distributivo_id = b.distributivo_id
    WHERE b.bloque_id = @bloque_id;

    IF @docente_id IS NULL
    BEGIN
        RAISERROR('El bloque de horario %d no existe.', 16, 1, @bloque_id);
        RETURN;
    END

    -- Recalcular desde cero: limpiar conflictos previos de este bloque
    DELETE FROM dbo.Conflictos WHERE bloque_id = @bloque_id;

    -- 1) Docente ocupado en la misma franja (otro bloque)
    IF dbo.fn_DocenteTieneTraslape(@docente_id, @periodo_academico, @dia_semana, @hora_inicio, @hora_fin, @bloque_id) = 1
        INSERT INTO dbo.Conflictos (bloque_id, tipo_conflicto, descripcion, severidad)
        VALUES (@bloque_id, 'DOCENTE_OCUPADO', 'El docente ya tiene otra clase asignada en esta franja horaria.', 'ALTA');

    -- 2) Aula / espacio ocupado en la misma franja
    IF dbo.fn_EspacioOcupado(@espacio_id, @periodo_academico, @dia_semana, @hora_inicio, @hora_fin, @bloque_id) = 1
        INSERT INTO dbo.Conflictos (bloque_id, tipo_conflicto, descripcion, severidad)
        VALUES (@bloque_id, 'AULA_OCUPADA', 'El espacio fisico ya esta asignado a otra clase en esta franja horaria.', 'ALTA');

    -- 3) Espacio no compatible (tipo o capacidad insuficiente)
    IF dbo.fn_EspacioCompatible(@asignatura_id, @espacio_id) = 0
        INSERT INTO dbo.Conflictos (bloque_id, tipo_conflicto, descripcion, severidad)
        VALUES (@bloque_id, 'ESPACIO_NO_COMPATIBLE', 'El espacio fisico no es compatible con el tipo o el cupo requerido por la asignatura.', 'ALTA');

    -- 4) Fuera de la disponibilidad declarada del docente
    IF dbo.fn_DocenteDentroDisponibilidad(@docente_id, @dia_semana, @hora_inicio, @hora_fin) = 0
        INSERT INTO dbo.Conflictos (bloque_id, tipo_conflicto, descripcion, severidad)
        VALUES (@bloque_id, 'FUERA_DISPONIBILIDAD', 'El horario propuesto esta fuera de la disponibilidad declarada del docente.', 'ALTA');

    -- 5) Exceso de carga horaria semanal
    SELECT @horas_max_semanales = horas_max_semanales FROM dbo.Docentes WHERE docente_id = @docente_id;
    SET @carga_actual = dbo.fn_CargaHorariaDocente(@docente_id, @periodo_academico);

    IF @carga_actual > @horas_max_semanales
        INSERT INTO dbo.Conflictos (bloque_id, tipo_conflicto, descripcion, severidad)
        VALUES (@bloque_id, 'EXCESO_CARGA_HORARIA',
                CONCAT('El docente supera su carga horaria maxima semanal (', @horas_max_semanales, 'h).'), 'MEDIA');

    -- Actualizar estado del bloque segun si quedaron conflictos vigentes
    UPDATE dbo.BloquesHorario
    SET estado = CASE WHEN EXISTS (SELECT 1 FROM dbo.Conflictos WHERE bloque_id = @bloque_id)
                       THEN 'CONFLICTO' ELSE 'VALIDO' END,
        fecha_validacion = SYSUTCDATETIME()
    WHERE bloque_id = @bloque_id;

    -- Resultado: estado general + detalle de conflictos
    SELECT
        @bloque_id AS bloque_id,
        (SELECT estado FROM dbo.BloquesHorario WHERE bloque_id = @bloque_id) AS estado_general,
        c.conflicto_id, c.tipo_conflicto, c.descripcion, c.severidad
    FROM dbo.Conflictos c
    WHERE c.bloque_id = @bloque_id;
END
GO

/* ---------------------------------------------------------------------------------
   sp_ValidarPeriodoAcademico
   Valida en lote todos los bloques de horario de un periodo academico.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.sp_ValidarPeriodoAcademico', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_ValidarPeriodoAcademico;
GO
CREATE PROCEDURE dbo.sp_ValidarPeriodoAcademico
    @periodo_academico VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @bloque_id INT;
    DECLARE cur CURSOR LOCAL FAST_FORWARD FOR
        SELECT bloque_id FROM dbo.BloquesHorario WHERE periodo_academico = @periodo_academico;

    OPEN cur;
    FETCH NEXT FROM cur INTO @bloque_id;
    WHILE @@FETCH_STATUS = 0
    BEGIN
        EXEC dbo.sp_ValidarBloqueHorario @bloque_id = @bloque_id;
        FETCH NEXT FROM cur INTO @bloque_id;
    END
    CLOSE cur;
    DEALLOCATE cur;

    SELECT
        b.bloque_id, b.estado, a.nombre_asignatura, p.codigo_paralelo,
        (doc.nombres + ' ' + doc.apellidos) AS docente,
        e.codigo_espacio, b.dia_semana, b.hora_inicio, b.hora_fin
    FROM dbo.BloquesHorario b
    INNER JOIN dbo.Distributivo dist ON dist.distributivo_id = b.distributivo_id
    INNER JOIN dbo.Asignaturas a ON a.asignatura_id = dist.asignatura_id
    INNER JOIN dbo.Paralelos p ON p.paralelo_id = dist.paralelo_id
    INNER JOIN dbo.Docentes doc ON doc.docente_id = dist.docente_id
    INNER JOIN dbo.Espacios e ON e.espacio_id = b.espacio_id
    WHERE b.periodo_academico = @periodo_academico
    ORDER BY b.dia_semana, b.hora_inicio;
END
GO

/* ---------------------------------------------------------------------------------
   sp_RegistrarYValidarBloque
   Inserta un nuevo bloque de horario (propuesta) a partir del distributivo y
   ejecuta de inmediato su validacion. Es el procedimiento que llama el backend
   cuando el usuario registra una propuesta desde el frontend.
   --------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.sp_RegistrarYValidarBloque', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_RegistrarYValidarBloque;
GO
CREATE PROCEDURE dbo.sp_RegistrarYValidarBloque
    @distributivo_id   INT,
    @espacio_id        INT,
    @dia_semana        VARCHAR(15),
    @hora_inicio       TIME(0),
    @hora_fin          TIME(0),
    @modalidad         VARCHAR(20),
    @periodo_academico VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @nuevo_bloque_id INT;

    INSERT INTO dbo.BloquesHorario
        (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico, estado)
    VALUES
        (@distributivo_id, @espacio_id, @dia_semana, @hora_inicio, @hora_fin, @modalidad, @periodo_academico, 'PENDIENTE');

    SET @nuevo_bloque_id = SCOPE_IDENTITY();

    EXEC dbo.sp_ValidarBloqueHorario @bloque_id = @nuevo_bloque_id;
END
GO
