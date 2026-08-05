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
  PropuestaMoverBloque,
  ResultadoImportacion,
  ResultadoRevalidacionPeriodo,
  ResultadoValidacionBloque,
} from '../models/entidades';

/**
 * Punto unico de acceso a la API del backend. Cada entidad tiene su metodo
 * de listado y su metodo de importacion masiva; horarios y conflictos
 * exponen las operaciones de validacion.
 *
 * Rutas verificadas contra backend/app/api/router.py y
 * backend/app/api/routers/*.py — prefijo /api/v1 ya incluido en
 * environment.apiUrl.
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
  listarDistributivo() {
    return this.http.get<Distributivo[]>(`${this.base}/distributivo`);
  }
  listarDisponibilidad(docenteId?: number) {
    const params: Record<string, number> = {};
    if (docenteId !== undefined) {
      params['docente_id'] = docenteId;
    }
    return this.http.get<DisponibilidadDocente[]>(`${this.base}/disponibilidad`, { params });
  }

  // --- Importacion masiva ------------------------------------------
  // El prefijo real del backend es "/import" (no "/importacion"), y el
  // body esperado es {"filas": [...]}, no el array suelto.
  importarDocentes(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/import/docentes`, { filas });
  }
  importarEspacios(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/import/espacios`, { filas });
  }
  importarAsignaturas(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/import/asignaturas`, { filas });
  }
  importarParalelos(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/import/paralelos`, { filas });
  }
  importarDistributivo(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/import/distributivo`, { filas });
  }
  importarDisponibilidad(filas: Record<string, unknown>[]) {
    return this.http.post<ResultadoImportacion>(`${this.base}/import/disponibilidad`, { filas });
  }

  // --- Horarios y validacion ----------------------------------------
  proponerHorario(propuesta: PropuestaHorario) {
    return this.http.post<ResultadoValidacionBloque>(`${this.base}/horarios/validar`, propuesta);
  }
  moverBloque(bloqueId: number, datos: PropuestaMoverBloque) {
    return this.http.patch<ResultadoValidacionBloque>(`${this.base}/horarios/${bloqueId}/mover`, datos);
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
    return this.http.post<ResultadoRevalidacionPeriodo>(
      `${this.base}/horarios/validar-periodo/${periodoAcademico}`,
      {},
    );
  }
  vaciarPeriodo(periodoAcademico: string) {
    return this.http.delete<{ estado: string; periodo_academico: string; eliminados: number }>(
      `${this.base}/horarios/periodo/${periodoAcademico}`,
    );
  }
}
