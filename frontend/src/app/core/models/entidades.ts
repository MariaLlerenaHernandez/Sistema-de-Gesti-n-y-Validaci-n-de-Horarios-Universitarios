// Modelos 1:1 con los schemas Pydantic del backend y las columnas del
// anexo de carga Excel. Mantener sincronizado si el backend cambia.

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
  docente_id: string;
  cedula: string;
  nombres: string;
  apellidos: string;
  correo: string;
  tipo_contrato: TipoContrato;
  horas_max_semanales: number;
  activo: 'SI' | 'NO';
}

export interface Espacio {
  espacio_id: string;
  codigo_espacio: string;
  nombre_espacio: string;
  tipo_espacio: TipoEspacio;
  capacidad: number;
  edificio: string;
  piso?: string;
  activo: 'SI' | 'NO';
}

export interface Asignatura {
  asignatura_id: string;
  codigo_asignatura: string;
  nombre_asignatura: string;
  modalidad: Modalidad;
  requiere_laboratorio: 'SI' | 'NO';
  tipo_espacio_requerido?: TipoEspacio | '';
  horas_semanales: number;
  cupo_estimado: number;
  activo: 'SI' | 'NO';
}

export interface Paralelo {
  paralelo_id: string;
  asignatura_id: string;
  codigo_paralelo: string;
  carrera: string;
  nivel: number;
  jornada: 'Matutina' | 'Vespertina' | 'Nocturna';
  numero_estudiantes: number;
  activo: 'SI' | 'NO';
}

export interface Distributivo {
  distributivo_id: string;
  docente_id: string;
  asignatura_id: string;
  paralelo_id: string;
  periodo_academico: string;
  horas_asignadas: number;
  observacion?: string;
}

export interface DisponibilidadDocente {
  disponibilidad_id: string;
  docente_id: string;
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  disponible: 'SI' | 'NO';
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

export interface PropuestaHorario {
  distributivo_id: string;
  espacio_id: string;
  dia_semana: DiaSemana;
  hora_inicio: string;
  hora_fin: string;
  modalidad: Modalidad;
  periodo_academico: string;
}

// --- Resultado de importacion masiva --------------------------------
export interface ErrorFilaImportacion {
  fila: number;
  identificador: string | null;
  error: string;
}

export interface ResultadoImportacion {
  entidad: string;
  filas_recibidas: number;
  filas_insertadas: number;
  filas_actualizadas: number;
  filas_con_error: number;
  errores: ErrorFilaImportacion[];
}
