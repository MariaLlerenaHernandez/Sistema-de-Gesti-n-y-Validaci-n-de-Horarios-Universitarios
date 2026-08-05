// Modelos 1:1 con los schemas Pydantic del backend y las columnas del
// anexo de carga Excel. Mantener sincronizado si el backend cambia.
//
// NOTA sobre los identificadores: cada entidad tiene un ID interno
// numerico (docente_id, espacio_id, etc. — la clave primaria real de
// SQL Server, la que se usa en los payloads que el frontend envia al
// backend) y, ademas, un codigo de negocio en texto que viene del Excel
// (codigo_docente, codigo_paralelo_ext, etc. — solo para mostrarlo en
// pantalla). Los booleanos (activo, disponible, requiere_laboratorio)
// llegan como true/false de JSON, no como los strings 'SI'/'NO' del
// Excel — esa conversion la hace el backend al importar.

export type TipoContrato = 'TIEMPO_COMPLETO' | 'MEDIO_TIEMPO' | 'TIEMPO_PARCIAL';
export type TipoEspacio = 'AULA' | 'LABORATORIO' | 'AULA_COMPUTO';
export type Modalidad = 'PRESENCIAL' | 'HIBRIDA' | 'ONLINE';
export type DiaSemana = 'LUNES' | 'MARTES' | 'MIERCOLES' | 'JUEVES' | 'VIERNES' | 'SABADO';
export type EstadoBloque = 'PENDIENTE' | 'VALIDO' | 'CONFLICTO';
export type TipoConflicto =
  | 'DOCENTE_OCUPADO'
  | 'AULA_OCUPADA'
  | 'ESPACIO_NO_COMPATIBLE'
  | 'FUERA_DISPONIBILIDAD'
  | 'EXCESO_CARGA_HORARIA'
  | 'CAPACIDAD_INSUFICIENTE';

export interface Docente {
  docente_id: number;
  codigo_docente: string;
  cedula: string;
  nombres: string;
  apellidos: string;
  correo: string;
  tipo_contrato: TipoContrato;
  horas_max_semanales: number;
  activo: boolean;
}

export interface Espacio {
  espacio_id: number;
  codigo_espacio: string;
  nombre_espacio: string;
  tipo_espacio: TipoEspacio;
  capacidad: number;
  edificio: string;
  piso?: string | null;
  activo: boolean;
}

export interface Asignatura {
  asignatura_id: number;
  codigo_asignatura: string;
  codigo_asignatura_ext?: string | null;
  nombre_asignatura: string;
  modalidad: Modalidad;
  requiere_laboratorio: boolean;
  tipo_espacio_requerido?: TipoEspacio | null;
  horas_semanales: number;
  cupo_estimado: number;
  activo: boolean;
}

export interface Paralelo {
  paralelo_id: number;
  codigo_paralelo_ext: string;
  asignatura_id: number;
  codigo_paralelo: string;
  carrera: string;
  nivel: number;
  jornada: 'Matutina' | 'Vespertina' | 'Nocturna';
  numero_estudiantes: number;
  activo: boolean;
}

export interface Distributivo {
  distributivo_id: number;
  codigo_distributivo_ext: string;
  docente_id: number;
  asignatura_id: number;
  paralelo_id: number;
  periodo_academico: string;
  horas_asignadas: number;
  observacion?: string | null;
  activo: boolean;
}

export interface DisponibilidadDocente {
  disponibilidad_id: number;
  codigo_disponibilidad_ext: string;
  docente_id: number;
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  disponible: boolean;
}

export interface ConflictoDetalle {
  conflicto_id: number;
  bloque_id: number;
  tipo_conflicto: TipoConflicto;
  descripcion: string;
  severidad: 'ALTA' | 'MEDIA' | 'BAJA';
  fecha_deteccion: string;
  periodo_academico: string;
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  nombre_asignatura: string;
  codigo_paralelo: string;
  docente: string;
  codigo_espacio: string;
}

export interface BloqueHorarioSemanal {
  bloque_id: number;
  periodo_academico: string;
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  modalidad: Modalidad;
  estado: EstadoBloque;
  codigo_asignatura: string;
  nombre_asignatura: string;
  codigo_paralelo: string;
  carrera: string;
  docente: string;
  codigo_espacio: string;
  nombre_espacio: string;
}

export interface ConflictoResumen {
  conflicto_id: number;
  tipo_conflicto: TipoConflicto;
  descripcion: string;
  severidad: 'ALTA' | 'MEDIA' | 'BAJA';
}

export interface ResultadoValidacionBloque {
  bloque_id: number;
  estado_general: EstadoBloque;
  conflictos: ConflictoResumen[];
}

// Respuesta de POST /horarios/validar-periodo/{periodo}.
export interface ResultadoRevalidacionPeriodo {
  estado: string;
  periodo_academico: string;
  horario: BloqueHorarioSemanal[];
}

// Payload para POST /horarios/validar. distributivo_id y espacio_id son
// los ID INTERNOS (number) — no los codigos del Excel.
export interface PropuestaHorario {
  distributivo_id: number;
  espacio_id: number;
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  modalidad: Modalidad;
  periodo_academico: string;
}

// --- Resultado de importacion masiva --------------------------------
export interface ErrorFilaImportacion {
  fila: number;
  columna: string | null;
  detalle: string;
}

export interface ResultadoImportacion {
  entidad: string;
  total_filas: number;
  filas_procesadas: number;
  filas_con_error: number;
  errores: ErrorFilaImportacion[];
}

// Payload para PATCH /horarios/{bloque_id}/mover (arrastrar-y-soltar en
// el calendario). espacio_id es opcional: solo se envia si tambien
// cambio el aula, no solo el dia/hora.
export interface PropuestaMoverBloque {
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  espacio_id?: number;
}
