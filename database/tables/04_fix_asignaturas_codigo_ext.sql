/* =====================================================================
   Script: 04_fix_asignaturas_codigo_ext.sql
   Descripcion: CORRECCION - la hoja 'asignaturas' del anexo de carga usa
   DOS identificadores distintos por fila: 'asignatura_id' (ej. ASI001,
   usado por las hojas 'paralelos' y 'distributivo' para referenciar la
   asignatura) y 'codigo_asignatura' (ej. SW101/INF101, el codigo propio
   de la materia). La tabla Asignaturas solo tenia una columna para el
   segundo. Este script agrega la columna que faltaba para el primero.

   Es seguro ejecutarlo sobre una base de datos ya creada: solo agrega
   una columna nueva (nullable) y un indice unico filtrado (permite
   multiples NULL, para no romper la creacion manual de asignaturas
   desde el CRUD del frontend, que no trae ese identificador externo).
   ===================================================================== */
USE HorariosUniversitarios;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('dbo.Asignaturas') AND name = 'codigo_asignatura_ext'
)
BEGIN
    ALTER TABLE dbo.Asignaturas ADD codigo_asignatura_ext VARCHAR(20) NULL;
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes WHERE name = 'UQ_Asignaturas_CodigoExt' AND object_id = OBJECT_ID('dbo.Asignaturas')
)
BEGIN
    CREATE UNIQUE NONCLUSTERED INDEX UQ_Asignaturas_CodigoExt
        ON dbo.Asignaturas(codigo_asignatura_ext)
        WHERE codigo_asignatura_ext IS NOT NULL;
END
GO
