/* =====================================================================================
   Sistema de Horarios Universitarios
   Script: 01_base_datos_y_docentes.sql
   Descripcion: Creacion de la base de datos y de la tabla Docentes.
   Motor: Microsoft SQL Server 2019 o superior.
   Orden de ejecucion: este es el PRIMER script del proyecto.
   ===================================================================================== */

IF DB_ID(N'HorariosUniversitarios') IS NULL
BEGIN
    CREATE DATABASE HorariosUniversitarios;
END
GO

USE HorariosUniversitarios;
GO

/* -------------------------------------------------------------------------------------
   Tabla: Docentes
   Corresponde a la hoja "docentes" del anexo de carga inicial.
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.Docentes', 'U') IS NOT NULL DROP TABLE dbo.Docentes;
GO

CREATE TABLE dbo.Docentes (
    docente_id              INT IDENTITY(1,1)  NOT NULL,
    codigo_docente          VARCHAR(20)        NOT NULL,   -- docente_id del Excel (ej. DOC001)
    cedula                  VARCHAR(20)        NOT NULL,
    nombres                 VARCHAR(100)       NOT NULL,
    apellidos               VARCHAR(100)       NOT NULL,
    correo                  VARCHAR(150)       NOT NULL,
    tipo_contrato           VARCHAR(20)        NOT NULL,
    horas_max_semanales     SMALLINT           NOT NULL,
    activo                  BIT                NOT NULL DEFAULT (1),
    fecha_creacion          DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),
    fecha_actualizacion     DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),

    CONSTRAINT PK_Docentes PRIMARY KEY CLUSTERED (docente_id),
    CONSTRAINT UQ_Docentes_Codigo UNIQUE (codigo_docente),
    CONSTRAINT UQ_Docentes_Cedula UNIQUE (cedula),
    CONSTRAINT UQ_Docentes_Correo UNIQUE (correo),
    CONSTRAINT CK_Docentes_TipoContrato CHECK (
        tipo_contrato IN ('TIEMPO_COMPLETO', 'MEDIO_TIEMPO', 'TIEMPO_PARCIAL')
    ),
    CONSTRAINT CK_Docentes_HorasMax CHECK (
        horas_max_semanales > 0 AND horas_max_semanales <= 60
    )
);
GO

CREATE NONCLUSTERED INDEX IX_Docentes_Activo
    ON dbo.Docentes (activo) INCLUDE (codigo_docente, nombres, apellidos);
GO
