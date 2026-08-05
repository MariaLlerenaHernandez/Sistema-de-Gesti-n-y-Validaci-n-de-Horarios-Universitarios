import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import {
  Asignatura,
  BloqueHorarioSemanal,
  ConflictoDetalle,
  Distributivo,
  DisponibilidadDocente,
  Docente,
  Espacio,
  Paralelo,
  PropuestaHorario,
  ResultadoImportacion,
} from '../models/entidades';

/**
 * Punto unico de acceso a la API del backend. Cada entidad tiene su metodo
 * de listado y su metodo de importacion masiva; horarios y conflictos
 * exponen las operaciones de validacion.
 */
/**
 * IMPORTANTE: las rutas usadas aqui (ej. `/importacion/docentes`,
 * `/horarios/validar-periodo/...`) son las que definimos como referencia.
 * Antes de usar este servicio, abre `http://127.0.0.1:8000/docs` en tu
 * backend real y confirma que cada ruta coincide exactamente (metodo,
 * path y parametros). Si tu equipo nombro los endpoints distinto (por
 * ejemplo `/docentes/import` en vez de `/importacion/docentes`), ajusta
 * las rutas de este archivo — es el UNICO lugar del frontend donde hay
 * que tocarlo.
 */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private base = environment.apiUrl;

  // --- Catalogos --------------------------------------------------
  listarDocentes() {
    return this.http.get<Docente[]>(`${this.base}/docentes`);
  }
  listarEspacios() {
    return this.http.get<Espacio[]>(`${this.base}/espacios`);
  }
  listarAsignaturas() {
    return this.http.get<Asignatura[]>(`${this.base}/asignaturas`);
  }
  listarParalelos() {
    return this.http.get<Paralelo[]>(`${this.base}/paralelos`);
  }

  // --- Importacion masiva ------------------------------------------
  importarDocentes(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/importacion/docentes`, filas);
  }
  importarEspacios(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/importacion/espacios`, filas);
  }
  importarAsignaturas(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/importacion/asignaturas`, filas);
  }
  importarParalelos(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/importacion/paralelos`, filas);
  }
  importarDistributivo(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/importacion/distributivo`, filas);
  }
  importarDisponibilidad(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/importacion/disponibilidad`, filas);
  }

  // --- Horarios y validacion ----------------------------------------
  proponerHorario(propuesta: PropuestaHorario) {
    return this.http.post<ConflictoDetalle[]>(`${this.base}/horarios/validar`, propuesta);
  }
  obtenerHorarioSemanal(periodoAcademico: string) {
    return this.http.get<BloqueHorarioSemanal[]>(`${this.base}/horarios/semanal/${periodoAcademico}`);
  }
  obtenerConflictos(periodoAcademico: string) {
    return this.http.get<ConflictoDetalle[]>(`${this.base}/horarios/conflictos`, {
      params: { periodo_academico: periodoAcademico },
    });
  }
  revalidarPeriodo(periodoAcademico: string) {
    return this.http.post<BloqueHorarioSemanal[]>(
      `${this.base}/horarios/validar-periodo/${periodoAcademico}`,
      {},
    );
  }
}
