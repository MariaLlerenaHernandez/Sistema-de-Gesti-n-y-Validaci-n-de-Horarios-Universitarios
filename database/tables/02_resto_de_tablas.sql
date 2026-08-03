/* =====================================================================================
   Sistema de Horarios Universitarios
   Script: 02_resto_de_tablas.sql
   Descripcion: Resto de tablas del dominio, con PK, FK, CHECK, UNIQUE e indices.
   Requiere haber ejecutado antes: 01_base_datos_y_docentes.sql
   ===================================================================================== */
USE HorariosUniversitarios;
GO

/* -------------------------------------------------------------------------------------
   Tabla: Espacios (aulas, laboratorios, aulas de computo)
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.Espacios', 'U') IS NOT NULL DROP TABLE dbo.Espacios;
GO
CREATE TABLE dbo.Espacios (
    espacio_id              INT IDENTITY(1,1)  NOT NULL,
    codigo_espacio          VARCHAR(20)        NOT NULL,
    nombre_espacio          VARCHAR(100)       NOT NULL,
    tipo_espacio            VARCHAR(20)        NOT NULL,
    capacidad               SMALLINT           NOT NULL,
    edificio                VARCHAR(60)        NOT NULL,
    piso                    VARCHAR(10)        NULL,
    activo                  BIT                NOT NULL DEFAULT (1),
    fecha_creacion          DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),
    fecha_actualizacion     DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),

    CONSTRAINT PK_Espacios PRIMARY KEY CLUSTERED (espacio_id),
    CONSTRAINT UQ_Espacios_Codigo UNIQUE (codigo_espacio),
    CONSTRAINT CK_Espacios_Tipo CHECK (tipo_espacio IN ('AULA', 'LABORATORIO', 'AULA_COMPUTO')),
    CONSTRAINT CK_Espacios_Capacidad CHECK (capacidad > 0)
);
GO
CREATE NONCLUSTERED INDEX IX_Espacios_Tipo_Activo ON dbo.Espacios (tipo_espacio, activo);
GO

/* -------------------------------------------------------------------------------------
   Tabla: Asignaturas
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.Asignaturas', 'U') IS NOT NULL DROP TABLE dbo.Asignaturas;
GO
CREATE TABLE dbo.Asignaturas (
    asignatura_id           INT IDENTITY(1,1)  NOT NULL,
    codigo_asignatura       VARCHAR(20)        NOT NULL,
    nombre_asignatura       VARCHAR(150)       NOT NULL,
    modalidad               VARCHAR(20)        NOT NULL,
    requiere_laboratorio    BIT                NOT NULL DEFAULT (0),
    tipo_espacio_requerido  VARCHAR(20)        NULL,
    horas_semanales         SMALLINT           NOT NULL,
    cupo_estimado           SMALLINT           NOT NULL,
    activo                  BIT                NOT NULL DEFAULT (1),
    fecha_creacion          DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),
    fecha_actualizacion     DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),

    CONSTRAINT PK_Asignaturas PRIMARY KEY CLUSTERED (asignatura_id),
    CONSTRAINT UQ_Asignaturas_Codigo UNIQUE (codigo_asignatura),
    CONSTRAINT CK_Asignaturas_Modalidad CHECK (modalidad IN ('PRESENCIAL', 'HIBRIDA', 'ONLINE')),
    CONSTRAINT CK_Asignaturas_TipoEspacio CHECK (
        tipo_espacio_requerido IS NULL OR tipo_espacio_requerido IN ('AULA', 'LABORATORIO', 'AULA_COMPUTO')
    ),
    CONSTRAINT CK_Asignaturas_Horas CHECK (horas_semanales > 0),
    CONSTRAINT CK_Asignaturas_Cupo CHECK (cupo_estimado > 0),
    -- Si la asignatura requiere laboratorio, debe declarar que tipo de espacio necesita
    CONSTRAINT CK_Asignaturas_LabRequiereEspacio CHECK (
        requiere_laboratorio = 0 OR tipo_espacio_requerido IS NOT NULL
    )
);
GO
CREATE NONCLUSTERED INDEX IX_Asignaturas_Activo ON dbo.Asignaturas (activo);
GO

/* -------------------------------------------------------------------------------------
   Tabla: Paralelos
   Cada paralelo es una unidad independiente (no se agrupan por defecto).
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.Paralelos', 'U') IS NOT NULL DROP TABLE dbo.Paralelos;
GO
CREATE TABLE dbo.Paralelos (
    paralelo_id             INT IDENTITY(1,1)  NOT NULL,
    codigo_paralelo_ext     VARCHAR(20)        NOT NULL,   -- paralelo_id del Excel (ej. PAR001)
    asignatura_id           INT                NOT NULL,
    codigo_paralelo         VARCHAR(10)        NOT NULL,   -- A, B, C...
    carrera                 VARCHAR(100)       NOT NULL,
    nivel                   SMALLINT           NOT NULL,
    jornada                 VARCHAR(20)        NOT NULL,
    numero_estudiantes      SMALLINT           NOT NULL,
    activo                  BIT                NOT NULL DEFAULT (1),
    fecha_creacion          DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),
    fecha_actualizacion     DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),

    CONSTRAINT PK_Paralelos PRIMARY KEY CLUSTERED (paralelo_id),
    CONSTRAINT UQ_Paralelos_CodigoExt UNIQUE (codigo_paralelo_ext),
    CONSTRAINT UQ_Paralelos_Asignatura_Codigo UNIQUE (asignatura_id, codigo_paralelo),
    CONSTRAINT FK_Paralelos_Asignatura FOREIGN KEY (asignatura_id) REFERENCES dbo.Asignaturas (asignatura_id),
    CONSTRAINT CK_Paralelos_Jornada CHECK (jornada IN ('Matutina', 'Vespertina', 'Nocturna')),
    CONSTRAINT CK_Paralelos_Estudiantes CHECK (numero_estudiantes > 0),
    CONSTRAINT CK_Paralelos_Nivel CHECK (nivel > 0 AND nivel <= 12)
);
GO
CREATE NONCLUSTERED INDEX IX_Paralelos_Asignatura ON dbo.Paralelos (asignatura_id);
GO

/* -------------------------------------------------------------------------------------
   Tabla: Distributivo academico
   Vincula docente + asignatura + paralelo dentro de un periodo academico.
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.Distributivo', 'U') IS NOT NULL DROP TABLE dbo.Distributivo;
GO
CREATE TABLE dbo.Distributivo (
    distributivo_id          INT IDENTITY(1,1) NOT NULL,
    codigo_distributivo_ext  VARCHAR(20)       NOT NULL,
    docente_id               INT               NOT NULL,
    asignatura_id            INT               NOT NULL,
    paralelo_id              INT               NOT NULL,
    periodo_academico        VARCHAR(20)       NOT NULL,
    horas_asignadas          SMALLINT          NOT NULL,
    observacion              VARCHAR(255)      NULL,
    activo                   BIT               NOT NULL DEFAULT (1),
    fecha_creacion           DATETIME2         NOT NULL DEFAULT (SYSUTCDATETIME()),

    CONSTRAINT PK_Distributivo PRIMARY KEY CLUSTERED (distributivo_id),
    CONSTRAINT UQ_Distributivo_CodigoExt UNIQUE (codigo_distributivo_ext),
    -- Un paralelo, en un periodo dado, solo puede tener un registro de distributivo
    CONSTRAINT UQ_Distributivo_Paralelo_Periodo UNIQUE (paralelo_id, periodo_academico),
    CONSTRAINT FK_Distributivo_Docente FOREIGN KEY (docente_id) REFERENCES dbo.Docentes (docente_id),
    CONSTRAINT FK_Distributivo_Asignatura FOREIGN KEY (asignatura_id) REFERENCES dbo.Asignaturas (asignatura_id),
    CONSTRAINT FK_Distributivo_Paralelo FOREIGN KEY (paralelo_id) REFERENCES dbo.Paralelos (paralelo_id),
    CONSTRAINT CK_Distributivo_Horas CHECK (horas_asignadas > 0)
);
GO
CREATE NONCLUSTERED INDEX IX_Distributivo_Docente_Periodo ON dbo.Distributivo (docente_id, periodo_academico);
GO

/* -------------------------------------------------------------------------------------
   Tabla: Disponibilidad del docente
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.DisponibilidadDocente', 'U') IS NOT NULL DROP TABLE dbo.DisponibilidadDocente;
GO
CREATE TABLE dbo.DisponibilidadDocente (
    disponibilidad_id          INT IDENTITY(1,1) NOT NULL,
    codigo_disponibilidad_ext  VARCHAR(20)       NOT NULL,
    docente_id                 INT               NOT NULL,
    dia_semana                 VARCHAR(15)       NOT NULL,
    hora_inicio                TIME(0)           NOT NULL,
    hora_fin                   TIME(0)           NOT NULL,
    disponible                 BIT               NOT NULL DEFAULT (1),

    CONSTRAINT PK_DisponibilidadDocente PRIMARY KEY CLUSTERED (disponibilidad_id),
    CONSTRAINT UQ_Disponibilidad_CodigoExt UNIQUE (codigo_disponibilidad_ext),
    CONSTRAINT FK_Disponibilidad_Docente FOREIGN KEY (docente_id) REFERENCES dbo.Docentes (docente_id),
    CONSTRAINT CK_Disponibilidad_Dia CHECK (
        dia_semana IN ('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO')
    ),
    CONSTRAINT CK_Disponibilidad_Horas CHECK (hora_fin > hora_inicio)
);
GO
CREATE NONCLUSTERED INDEX IX_Disponibilidad_Docente_Dia ON dbo.DisponibilidadDocente (docente_id, dia_semana);
GO

/* -------------------------------------------------------------------------------------
   Tabla: Bloques de horario
   Es la "propuesta de horario": un bloque de clase concreto (dia + hora + espacio)
   asociado a un registro del distributivo.
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.BloquesHorario', 'U') IS NOT NULL DROP TABLE dbo.BloquesHorario;
GO
CREATE TABLE dbo.BloquesHorario (
    bloque_id               INT IDENTITY(1,1)  NOT NULL,
    distributivo_id         INT                NOT NULL,
    espacio_id              INT                NOT NULL,
    dia_semana              VARCHAR(15)        NOT NULL,
    hora_inicio              TIME(0)           NOT NULL,
    hora_fin                 TIME(0)           NOT NULL,
    modalidad                VARCHAR(20)       NOT NULL,
    periodo_academico         VARCHAR(20)       NOT NULL,
    estado                    VARCHAR(20)       NOT NULL DEFAULT ('PENDIENTE'),
    fecha_creacion            DATETIME2         NOT NULL DEFAULT (SYSUTCDATETIME()),
    fecha_validacion          DATETIME2         NULL,

    CONSTRAINT PK_BloquesHorario PRIMARY KEY CLUSTERED (bloque_id),
    CONSTRAINT FK_Bloques_Distributivo FOREIGN KEY (distributivo_id) REFERENCES dbo.Distributivo (distributivo_id),
    CONSTRAINT FK_Bloques_Espacio FOREIGN KEY (espacio_id) REFERENCES dbo.Espacios (espacio_id),
    CONSTRAINT CK_Bloques_Dia CHECK (
        dia_semana IN ('LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO')
    ),
    CONSTRAINT CK_Bloques_Horas CHECK (hora_fin > hora_inicio),
    CONSTRAINT CK_Bloques_Modalidad CHECK (modalidad IN ('PRESENCIAL', 'HIBRIDA', 'ONLINE')),
    CONSTRAINT CK_Bloques_Estado CHECK (estado IN ('PENDIENTE', 'VALIDO', 'CONFLICTO'))
);
GO
CREATE NONCLUSTERED INDEX IX_Bloques_Espacio_Dia ON dbo.BloquesHorario (espacio_id, dia_semana);
CREATE NONCLUSTERED INDEX IX_Bloques_Periodo ON dbo.BloquesHorario (periodo_academico, estado);
GO

/* -------------------------------------------------------------------------------------
   Tabla: Conflictos detectados
   ------------------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.Conflictos', 'U') IS NOT NULL DROP TABLE dbo.Conflictos;
GO
CREATE TABLE dbo.Conflictos (
    conflicto_id            INT IDENTITY(1,1)  NOT NULL,
    bloque_id               INT                NOT NULL,
    tipo_conflicto          VARCHAR(50)        NOT NULL,
    descripcion             VARCHAR(500)       NOT NULL,
    severidad               VARCHAR(20)        NOT NULL DEFAULT ('ALTA'),
    fecha_deteccion         DATETIME2          NOT NULL DEFAULT (SYSUTCDATETIME()),

    CONSTRAINT PK_Conflictos PRIMARY KEY CLUSTERED (conflicto_id),
    CONSTRAINT FK_Conflictos_Bloque FOREIGN KEY (bloque_id) REFERENCES dbo.BloquesHorario (bloque_id) ON DELETE CASCADE,
    CONSTRAINT CK_Conflictos_Tipo CHECK (tipo_conflicto IN (
        'DOCENTE_OCUPADO', 'AULA_OCUPADA', 'ESPACIO_NO_COMPATIBLE',
        'FUERA_DISPONIBILIDAD', 'EXCESO_CARGA_HORARIA', 'CAPACIDAD_INSUFICIENTE'
    )),
    CONSTRAINT CK_Conflictos_Severidad CHECK (severidad IN ('ALTA', 'MEDIA', 'BAJA'))
);
GO
CREATE NONCLUSTERED INDEX IX_Conflictos_Bloque ON dbo.Conflictos (bloque_id);
GO
