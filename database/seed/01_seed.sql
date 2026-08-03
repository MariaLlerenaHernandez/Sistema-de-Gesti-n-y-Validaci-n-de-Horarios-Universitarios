/* =====================================================================================
   Script: 01_seed.sql
   Descripcion: Datos de ejemplo para poder probar el sistema sin necesidad de
   importar un archivo Excel. Coincide con el anexo de formatos de carga.

   IMPORTANTE PARA LA DEMO: al final de este script se registran bloques de horario
   que generan a proposito varios tipos de conflicto (docente ocupado, aula ocupada,
   espacio no compatible, fuera de disponibilidad, exceso de carga), para que puedan
   mostrarlos en vivo sin tener que improvisar el dia de la exposicion.
   ===================================================================================== */
USE HorariosUniversitarios;
GO

/* ---------------------------- Docentes ---------------------------- */
SET IDENTITY_INSERT dbo.Docentes ON;
INSERT INTO dbo.Docentes (docente_id, codigo_docente, cedula, nombres, apellidos, correo, tipo_contrato, horas_max_semanales, activo)
VALUES
(1, 'DOC001', '0102030405', 'Ana',    'Lopez', 'ana.lopez@universidad.edu',    'TIEMPO_COMPLETO', 40, 1),
(2, 'DOC002', '0102030406', 'Carlos', 'Perez', 'carlos.perez@universidad.edu', 'MEDIO_TIEMPO',    20, 1),
(3, 'DOC003', '0102030407', 'Luisa',  'Mora',  'luisa.mora@universidad.edu',   'TIEMPO_PARCIAL',  12, 1);
SET IDENTITY_INSERT dbo.Docentes OFF;
GO

/* ---------------------------- Espacios ---------------------------- */
SET IDENTITY_INSERT dbo.Espacios ON;
INSERT INTO dbo.Espacios (espacio_id, codigo_espacio, nombre_espacio, tipo_espacio, capacidad, edificio, piso, activo)
VALUES
(1, 'A101',   'Aula 101',            'AULA',         40, 'Bloque A', '1', 1),
(2, 'LAB201', 'Laboratorio Redes',   'LABORATORIO',  32, 'Bloque B', '2', 1),
(3, 'C303',   'Aula Computo 303',    'AULA_COMPUTO', 30, 'Bloque C', '3', 1);
SET IDENTITY_INSERT dbo.Espacios OFF;
GO

/* ---------------------------- Asignaturas ---------------------------- */
SET IDENTITY_INSERT dbo.Asignaturas ON;
INSERT INTO dbo.Asignaturas (asignatura_id, codigo_asignatura, nombre_asignatura, modalidad, requiere_laboratorio, tipo_espacio_requerido, horas_semanales, cupo_estimado, activo)
VALUES
(1, 'INF101', 'Programacion I',                  'PRESENCIAL', 1, 'LABORATORIO', 6, 30, 1),
(2, 'MAT201', 'Calculo II',                       'PRESENCIAL', 0, 'AULA',        4, 35, 1),
(3, 'ADM110', 'Metodologia de la Investigacion',  'HIBRIDA',    0, 'AULA',        3, 40, 1);
SET IDENTITY_INSERT dbo.Asignaturas OFF;
GO

/* ---------------------------- Paralelos ---------------------------- */
SET IDENTITY_INSERT dbo.Paralelos ON;
INSERT INTO dbo.Paralelos (paralelo_id, codigo_paralelo_ext, asignatura_id, codigo_paralelo, carrera, nivel, jornada, numero_estudiantes, activo)
VALUES
(1, 'PAR001', 1, 'A', 'Sistemas',       1, 'Matutina',   28, 1),
(2, 'PAR002', 2, 'B', 'Industrial',     2, 'Vespertina', 35, 1),
(3, 'PAR003', 3, 'A', 'Administracion', 3, 'Nocturna',   32, 1),
(4, 'PAR004', 1, 'B', 'Sistemas',       1, 'Matutina',   30, 1);   -- paralelo extra para forzar conflictos
SET IDENTITY_INSERT dbo.Paralelos OFF;
GO

/* ---------------------------- Distributivo ---------------------------- */
SET IDENTITY_INSERT dbo.Distributivo ON;
INSERT INTO dbo.Distributivo (distributivo_id, codigo_distributivo_ext, docente_id, asignatura_id, paralelo_id, periodo_academico, horas_asignadas, observacion, activo)
VALUES
(1, 'DIS001', 1, 1, 1, '2026A', 6, 'Asignacion regular',              1),
(2, 'DIS002', 2, 2, 2, '2026A', 4, 'Asignacion regular',              1),
(3, 'DIS003', 3, 3, 3, '2026A', 3, 'Asignacion regular',              1),
(4, 'DIS004', 1, 1, 4, '2026A', 6, 'Mismo docente para forzar choque',1);  -- DOC001 tambien aqui
SET IDENTITY_INSERT dbo.Distributivo OFF;
GO

/* ---------------------------- Disponibilidad docente ---------------------------- */
SET IDENTITY_INSERT dbo.DisponibilidadDocente ON;
INSERT INTO dbo.DisponibilidadDocente (disponibilidad_id, codigo_disponibilidad_ext, docente_id, dia_semana, hora_inicio, hora_fin, disponible)
VALUES
(1, 'DISP001', 1, 'LUNES',     '07:00', '11:00', 1),
(2, 'DISP002', 1, 'MIERCOLES', '07:00', '11:00', 1),
(3, 'DISP003', 2, 'MARTES',    '18:00', '22:00', 1),
(4, 'DISP004', 3, 'SABADO',    '08:00', '12:00', 0),
(5, 'DISP005', 2, 'LUNES',     '07:00', '11:00', 1),   -- ventana extra para aislar el caso AULA_OCUPADA
(6, 'DISP006', 3, 'LUNES',     '07:00', '11:00', 1),   -- idem, y da a DOC003 una franja util normal
(7, 'DISP007', 3, 'JUEVES',    '08:00', '18:00', 1);   -- franja normal de DOC003 entre semana
SET IDENTITY_INSERT dbo.DisponibilidadDocente OFF;
GO

/* =====================================================================================
   Bloques de horario: casos deliberados para la demostracion en vivo.
   Se insertan "en limpio" (sin validar todavia) y luego se corre la validacion masiva,
   para que puedan ver el "antes y despues" en la matriz semanal y en /horarios/conflictos.
   ===================================================================================== */

-- Caso 0: bloque VALIDO de control (DOC001, INF101-PAR001, miercoles 07:00-09:00,
--   LAB201) -> dentro de disponibilidad, laboratorio compatible, sin choques con
--   ningun otro bloque. Este es el unico que debe quedar en estado VALIDO; sirve
--   para mostrar en la demo que el sistema tambien reconoce lo que SI esta bien.
INSERT INTO dbo.BloquesHorario (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico)
VALUES (1, 2, 'MIERCOLES', '07:00', '09:00', 'PRESENCIAL', '2026A');

-- Caso 1 + Caso 2: DOCENTE_OCUPADO -> el mismo docente (DOC001) queda asignado a dos
--   paralelos distintos (PAR001 y PAR004) el mismo dia (lunes) en horas que se
--   traslapan. Ambos bloques quedaran marcados en conflicto (es un choque mutuo).
INSERT INTO dbo.BloquesHorario (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico)
VALUES (1, 2, 'LUNES', '07:00', '09:00', 'PRESENCIAL', '2026A'),
       (4, 3, 'LUNES', '08:00', '10:00', 'PRESENCIAL', '2026A');

-- Caso 3: AULA_OCUPADA -> dos distributivos distintos (DOC002 y DOC003, ambos con
--   disponibilidad valida el lunes en la manana) compitiendo por la MISMA aula (A101)
--   en horario que se traslapa. Aislado a proposito para que este caso muestre
--   unicamente el conflicto de aula, sin mezclarse con otros.
INSERT INTO dbo.BloquesHorario (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico)
VALUES (2, 1, 'LUNES', '08:00', '10:00', 'PRESENCIAL', '2026A'),
       (3, 1, 'LUNES', '09:00', '11:00', 'PRESENCIAL', '2026A');

-- Caso 4: ESPACIO_NO_COMPATIBLE -> INF101 requiere LABORATORIO, aqui se asigna al aula
--   comun A101 (tipo AULA), que no es compatible con el tipo requerido.
INSERT INTO dbo.BloquesHorario (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico)
VALUES (1, 1, 'MIERCOLES', '09:00', '11:00', 'PRESENCIAL', '2026A');

-- Caso 5: FUERA_DISPONIBILIDAD -> DOC002 solo esta disponible MARTES 18:00-22:00,
--   pero aqui se le asigna VIERNES en la manana.
INSERT INTO dbo.BloquesHorario (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico)
VALUES (2, 1, 'VIERNES', '08:00', '10:00', 'PRESENCIAL', '2026A');

-- Caso 6: EXCESO_CARGA_HORARIA -> DOC003 tiene un maximo de 12h semanales; estos
--   dos bloques (4h sabado + 10h jueves = 14h) superan ese limite. El bloque del
--   jueves cae dentro de su disponibilidad normal (DISP007), asi que muestra
--   UNICAMENTE exceso de carga; el del sabado ademas cae fuera de su disponibilidad
--   (DISP004 = no disponible), asi que ese muestra los dos conflictos a la vez.
INSERT INTO dbo.BloquesHorario (distributivo_id, espacio_id, dia_semana, hora_inicio, hora_fin, modalidad, periodo_academico)
VALUES (3, 1, 'SABADO', '08:00', '12:00', 'ONLINE', '2026A'),
       (3, 1, 'JUEVES', '08:00', '18:00', 'ONLINE', '2026A');
GO

-- Ejecutar la validacion masiva del periodo para que los conflictos queden
-- registrados de una sola vez (sin tener que llamar bloque por bloque desde la API).
EXEC dbo.sp_ValidarPeriodoAcademico @periodo_academico = '2026A';
GO
