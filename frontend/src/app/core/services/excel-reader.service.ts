import { Injectable } from '@angular/core';
import * as XLSX from 'xlsx';

export interface HojaLeida {
  nombreDetectado: string;
  filas: Record<string, unknown>[];
}

/**
 * Lee un archivo .xlsx en el navegador y devuelve sus hojas como JSON,
 * sin tocar el backend. Sigue el anexo de formatos de carga: intenta
 * emparejar cada hoja esperada por nombre, aceptando variantes comunes
 * de mayusculas/tildes para no ser fragil ante pequenas diferencias.
 */
@Injectable({ providedIn: 'root' })
export class ExcelReaderService {
  private static ALIAS: Record<string, string[]> = {
    docentes: ['docentes', 'Docentes', 'DOCENTES'],
    espacios: ['espacios', 'Espacios', 'ESPACIOS'],
    asignaturas: ['asignaturas', 'Asignaturas', 'ASIGNATURAS'],
    paralelos: ['paralelos', 'Paralelos', 'PARALELOS'],
    distributivo: ['distributivo', 'Distributivo', 'DISTRIBUTIVO'],
    disponibilidad_docente: [
      'disponibilidad_docente',
      'Disponibilidad_Docente',
      'disponibilidad',
      'Disponibilidad',
    ],
  };

  async leerArchivo(archivo: File): Promise<Map<string, HojaLeida>> {
    const buffer = await archivo.arrayBuffer();
    const libro = XLSX.read(buffer, { type: 'array', cellDates: false });

    const resultado = new Map<string, HojaLeida>();

    for (const [clave, alias] of Object.entries(ExcelReaderService.ALIAS)) {
      const nombreHoja = libro.SheetNames.find((n) => alias.includes(n));
      if (!nombreHoja) continue;

      const hoja = libro.Sheets[nombreHoja];
      const filas = XLSX.utils.sheet_to_json<Record<string, unknown>>(hoja, {
        defval: '',
        raw: false, // fuerza texto/numeros consistentes en vez de tipos mixtos de Excel
      });

      resultado.set(clave, { nombreDetectado: nombreHoja, filas: this.limpiarFilas(filas) });
    }

    return resultado;
  }

  /** Elimina filas completamente vacias y recorta espacios en los valores de texto. */
  private limpiarFilas(filas: Record<string, unknown>[]): Record<string, unknown>[] {
    return filas
      .map((fila) => {
        const limpia: Record<string, unknown> = {};
        for (const [clave, valor] of Object.entries(fila)) {
          limpia[clave.trim()] = typeof valor === 'string' ? valor.trim() : valor;
        }
        return limpia;
      })
      .filter((fila) => Object.values(fila).some((v) => v !== '' && v !== null && v !== undefined));
  }

  /** Nombres de columna esperados por entidad, usados para armar la vista previa. */
  static readonly COLUMNAS: Record<string, string[]> = {
    docentes: [
      'docente_id',
      'cedula',
      'nombres',
      'apellidos',
      'correo',
      'tipo_contrato',
      'horas_max_semanales',
      'activo',
    ],
    espacios: [
      'espacio_id',
      'codigo_espacio',
      'nombre_espacio',
      'tipo_espacio',
      'capacidad',
      'edificio',
      'piso',
      'activo',
    ],
    asignaturas: [
      'asignatura_id',
      'codigo_asignatura',
      'nombre_asignatura',
      'modalidad',
      'requiere_laboratorio',
      'tipo_espacio_requerido',
      'horas_semanales',
      'cupo_estimado',
      'activo',
    ],
    paralelos: [
      'paralelo_id',
      'asignatura_id',
      'codigo_paralelo',
      'carrera',
      'nivel',
      'jornada',
      'numero_estudiantes',
      'activo',
    ],
    distributivo: [
      'distributivo_id',
      'docente_id',
      'asignatura_id',
      'paralelo_id',
      'periodo_academico',
      'horas_asignadas',
      'observacion',
    ],
    disponibilidad_docente: [
      'disponibilidad_id',
      'docente_id',
      'dia_semana',
      'hora_inicio',
      'hora_fin',
      'disponible',
    ],
  };

  static readonly ETIQUETAS: Record<string, string> = {
    docentes: 'Docentes',
    espacios: 'Espacios físicos',
    asignaturas: 'Asignaturas',
    paralelos: 'Paralelos',
    distributivo: 'Distributivo académico',
    disponibilidad_docente: 'Disponibilidad docente',
  };
}
