/* =====================================================================================
   Script: 03_triggers.sql
   Descripcion: Triggers de auditoria (fecha_actualizacion automatica) y de proteccion
   de integridad de negocio.
   ===================================================================================== */
USE HorariosUniversitarios;
GO

IF OBJECT_ID('dbo.trg_Docentes_Update', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_Docentes_Update;
GO
CREATE TRIGGER dbo.trg_Docentes_Update ON dbo.Docentes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE d SET fecha_actualizacion = SYSUTCDATETIME()
    FROM dbo.Docentes d INNER JOIN inserted i ON d.docente_id = i.docente_id;
END
GO

IF OBJECT_ID('dbo.trg_Espacios_Update', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_Espacios_Update;
GO
CREATE TRIGGER dbo.trg_Espacios_Update ON dbo.Espacios
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE e SET fecha_actualizacion = SYSUTCDATETIME()
    FROM dbo.Espacios e INNER JOIN inserted i ON e.espacio_id = i.espacio_id;
END
GO

IF OBJECT_ID('dbo.trg_Asignaturas_Update', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_Asignaturas_Update;
GO
CREATE TRIGGER dbo.trg_Asignaturas_Update ON dbo.Asignaturas
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE a SET fecha_actualizacion = SYSUTCDATETIME()
    FROM dbo.Asignaturas a INNER JOIN inserted i ON a.asignatura_id = i.asignatura_id;
END
GO

-- Regla de negocio: un bloque en estado VALIDO no se puede borrar directamente,
-- debe volver a PENDIENTE o CONFLICTO antes (evita perder trazabilidad de un horario
-- ya validado por error de interfaz).
IF OBJECT_ID('dbo.trg_BloquesHorario_Delete', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_BloquesHorario_Delete;
GO
CREATE TRIGGER dbo.trg_BloquesHorario_Delete ON dbo.BloquesHorario
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS (SELECT 1 FROM deleted WHERE estado = 'VALIDO')
    BEGIN
        RAISERROR('No se puede eliminar un bloque de horario en estado VALIDO. Debe re-planificarse primero.', 16, 1);
        RETURN;
    END
    DELETE FROM dbo.Conflictos WHERE bloque_id IN (SELECT bloque_id FROM deleted);
    DELETE FROM dbo.BloquesHorario WHERE bloque_id IN (SELECT bloque_id FROM deleted);
END
GO
