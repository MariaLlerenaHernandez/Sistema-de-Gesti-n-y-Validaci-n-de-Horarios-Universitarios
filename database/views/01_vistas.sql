/* =====================================================================================
   Script: 01_vistas.sql
   Descripcion: Vistas de lectura para el frontend (matriz semanal y detalle de
   conflictos). El backend consulta estas vistas en vez de hacer los JOIN a mano.
   ===================================================================================== */
USE HorariosUniversitarios;
GO

IF OBJECT_ID('dbo.vw_HorarioSemanal', 'V') IS NOT NULL DROP VIEW dbo.vw_HorarioSemanal;
GO
CREATE VIEW dbo.vw_HorarioSemanal
AS
SELECT
    b.bloque_id, b.periodo_academico, b.dia_semana, b.hora_inicio, b.hora_fin,
    b.modalidad, b.estado,
    a.asignatura_id, a.codigo_asignatura, a.nombre_asignatura,
    p.paralelo_id, p.codigo_paralelo, p.carrera,
    doc.docente_id, doc.codigo_docente, (doc.nombres + ' ' + doc.apellidos) AS docente,
    e.espacio_id, e.codigo_espacio, e.nombre_espacio
FROM dbo.BloquesHorario b
INNER JOIN dbo.Distributivo dist ON dist.distributivo_id = b.distributivo_id
INNER JOIN dbo.Asignaturas a ON a.asignatura_id = dist.asignatura_id
INNER JOIN dbo.Paralelos p ON p.paralelo_id = dist.paralelo_id
INNER JOIN dbo.Docentes doc ON doc.docente_id = dist.docente_id
INNER JOIN dbo.Espacios e ON e.espacio_id = b.espacio_id;
GO

IF OBJECT_ID('dbo.vw_ConflictosDetalle', 'V') IS NOT NULL DROP VIEW dbo.vw_ConflictosDetalle;
GO
CREATE VIEW dbo.vw_ConflictosDetalle
AS
SELECT
    c.conflicto_id, c.bloque_id, c.tipo_conflicto, c.descripcion, c.severidad, c.fecha_deteccion,
    b.periodo_academico, b.dia_semana, b.hora_inicio, b.hora_fin,
    a.nombre_asignatura, p.codigo_paralelo,
    (doc.nombres + ' ' + doc.apellidos) AS docente,
    e.codigo_espacio
FROM dbo.Conflictos c
INNER JOIN dbo.BloquesHorario b ON b.bloque_id = c.bloque_id
INNER JOIN dbo.Distributivo dist ON dist.distributivo_id = b.distributivo_id
INNER JOIN dbo.Asignaturas a ON a.asignatura_id = dist.asignatura_id
INNER JOIN dbo.Paralelos p ON p.paralelo_id = dist.paralelo_id
INNER JOIN dbo.Docentes doc ON doc.docente_id = dist.docente_id
INNER JOIN dbo.Espacios e ON e.espacio_id = b.espacio_id;
GO
