import { Component, inject, signal } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { ExcelReaderService, HojaLeida } from '../../core/services/excel-reader.service';
import { ResultadoImportacion } from '../../core/models/entidades';

interface EstadoEntidad {
  clave: string;
  etiqueta: string;
  columnas: string[];
  hoja: HojaLeida | null;
  resultado: ResultadoImportacion | null;
  importando: boolean;
}

@Component({
  selector: 'app-importacion',
  standalone: true,
  templateUrl: './importacion.component.html',
})
export class ImportacionComponent {
  private excelReader = inject(ExcelReaderService);
  private api = inject(ApiService);

  nombreArchivo = signal<string | null>(null);
  leyendo = signal(false);
  errorLectura = signal<string | null>(null);
  pestanaActiva = signal<string>('docentes');

  entidades = signal<EstadoEntidad[]>(
    Object.keys(ExcelReaderService.COLUMNAS).map((clave) => ({
      clave,
      etiqueta: ExcelReaderService.ETIQUETAS[clave],
      columnas: ExcelReaderService.COLUMNAS[clave],
      hoja: null,
      resultado: null,
      importando: false,
    })),
  );

  get entidadActiva(): EstadoEntidad | undefined {
    return this.entidades().find((e) => e.clave === this.pestanaActiva());
  }

  async onArchivoSeleccionado(evento: Event): Promise<void> {
    const input = evento.target as HTMLInputElement;
    const archivo = input.files?.[0];
    if (!archivo) return;

    this.leyendo.set(true);
    this.errorLectura.set(null);
    this.nombreArchivo.set(archivo.name);

    try {
      const hojas = await this.excelReader.leerArchivo(archivo);

      this.entidades.update((lista) =>
        lista.map((e) => ({
          ...e,
          hoja: hojas.get(e.clave) ?? null,
          resultado: null,
        })),
      );

      // Salta automaticamente a la primera pestana que si trajo datos
      const primeraConDatos = this.entidades().find((e) => e.hoja && e.hoja.filas.length > 0);
      if (primeraConDatos) this.pestanaActiva.set(primeraConDatos.clave);
    } catch (err) {
      this.errorLectura.set(
        'No se pudo leer el archivo. Verifica que sea un .xlsx valido y que no este danado.',
      );
      console.error(err);
    } finally {
      this.leyendo.set(false);
      input.value = ''; // permite volver a seleccionar el mismo archivo si se corrige
    }
  }

  seleccionarPestana(clave: string): void {
    this.pestanaActiva.set(clave);
  }

  importar(entidad: EstadoEntidad): void {
    if (!entidad.hoja || entidad.hoja.filas.length === 0) return;

    this.actualizarEntidad(entidad.clave, { importando: true, resultado: null });

    const llamada = this.llamadaImportacion(entidad.clave, entidad.hoja.filas);
    if (!llamada) {
      this.actualizarEntidad(entidad.clave, { importando: false });
      return;
    }

    llamada.subscribe({
      next: (resultado) => this.actualizarEntidad(entidad.clave, { importando: false, resultado }),
      error: (err) => {
        this.actualizarEntidad(entidad.clave, { importando: false });
        this.errorLectura.set(
          err?.mensajeAmigable ?? `No se pudo importar la hoja "${entidad.etiqueta}".`,
        );
      },
    });
  }

  private llamadaImportacion(clave: string, filas: Record<string, unknown>[]) {
    switch (clave) {
      case 'docentes':
        return this.api.importarDocentes(filas);
      case 'espacios':
        return this.api.importarEspacios(filas);
      case 'asignaturas':
        return this.api.importarAsignaturas(filas);
      case 'paralelos':
        return this.api.importarParalelos(filas);
      case 'distributivo':
        return this.api.importarDistributivo(filas);
      case 'disponibilidad_docente':
        return this.api.importarDisponibilidad(filas);
      default:
        return null;
    }
  }

  private actualizarEntidad(clave: string, cambios: Partial<EstadoEntidad>): void {
    this.entidades.update((lista) =>
      lista.map((e) => (e.clave === clave ? { ...e, ...cambios } : e)),
    );
  }

  filasPreview(entidad: EstadoEntidad): Record<string, unknown>[] {
    return entidad.hoja?.filas.slice(0, 8) ?? [];
  }
}
