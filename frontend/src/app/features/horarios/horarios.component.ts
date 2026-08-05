import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import {
  BloqueHorarioSemanal,
  DiaSemana,
  Distributivo,
  Espacio,
  Modalidad,
  ResultadoValidacionBloque,
} from '../../core/models/entidades';

const ORDEN_DIAS: DiaSemana[] = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO'];

@Component({
  selector: 'app-horarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './horarios.component.html',
})
export class HorariosComponent implements OnInit {
  private api = inject(ApiService);

  periodo = '2026A';
  diasSemana = ORDEN_DIAS;
  modalidades: Modalidad[] = ['PRESENCIAL', 'HIBRIDA', 'ONLINE'];

  // --- Catalogos para el formulario ---------------------------------
  espacios = signal<Espacio[]>([]);
  distributivos = signal<Distributivo[]>([]);
  cargandoCatalogos = signal(true);

  // --- Formulario de propuesta ---------------------------------------
  form = signal({
    distributivo_id: '',
    espacio_id: '',
    dia_semana: 'LUNES' as DiaSemana,
    hora_inicio: '07:00',
    hora_fin: '09:00',
    modalidad: 'PRESENCIAL' as Modalidad,
  });
  enviando = signal(false);
  resultado = signal<ResultadoValidacionBloque | null>(null);
  errorFormulario = signal<string | null>(null);

  // --- Matriz semanal --------------------------------------------------
  bloques = signal<BloqueHorarioSemanal[]>([]);
  cargandoMatriz = signal(true);
  errorMatriz = signal<string | null>(null);

  bloquesPorDia = computed(() => {
    const mapa = new Map<DiaSemana, BloqueHorarioSemanal[]>();
    for (const dia of this.diasSemana) mapa.set(dia, []);
    for (const b of this.bloques()) {
      mapa.get(b.dia_semana)?.push(b);
    }
    for (const lista of mapa.values()) {
      lista.sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
    }
    return mapa;
  });

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargarMatriz();
  }

  private cargarCatalogos(): void {
    this.cargandoCatalogos.set(true);
    Promise.all([this.api.listarEspacios().toPromise(), this.api.listarDistributivo().toPromise()])
      .then(([espacios, distributivos]) => {
        this.espacios.set(espacios ?? []);
        this.distributivos.set(distributivos ?? []);
      })
      .finally(() => this.cargandoCatalogos.set(false));
  }

  private cargarMatriz(): void {
    this.cargandoMatriz.set(true);
    this.errorMatriz.set(null);
    this.api.obtenerHorarioSemanal(this.periodo).subscribe({
      next: (datos) => {
        this.bloques.set(datos);
        this.cargandoMatriz.set(false);
      },
      error: (err) => {
        this.errorMatriz.set(err?.mensajeAmigable ?? 'No se pudo cargar el horario semanal.');
        this.cargandoMatriz.set(false);
      },
    });
  }

  actualizarCampo<K extends keyof ReturnType<HorariosComponent['form']>>(
    campo: K,
    valor: ReturnType<HorariosComponent['form']>[K],
  ): void {
    this.form.update((f) => ({ ...f, [campo]: valor }));
  }

  enviarPropuesta(): void {
    const datos = this.form();

    if (!datos.distributivo_id || !datos.espacio_id) {
      this.errorFormulario.set('Completa el registro del distributivo y el espacio físico.');
      return;
    }
    if (datos.hora_fin <= datos.hora_inicio) {
      this.errorFormulario.set('La hora de fin debe ser posterior a la hora de inicio.');
      return;
    }

    this.enviando.set(true);
    this.errorFormulario.set(null);
    this.resultado.set(null);

    this.api
      .proponerHorario({
        distributivo_id: datos.distributivo_id,
        espacio_id: datos.espacio_id,
        dia_semana: datos.dia_semana,
        hora_inicio: datos.hora_inicio,
        hora_fin: datos.hora_fin,
        modalidad: datos.modalidad,
        periodo_academico: this.periodo,
      })
      .subscribe({
        next: (resultado) => {
          this.resultado.set(resultado);
          this.enviando.set(false);
          this.cargarMatriz(); // refresca la matriz con el nuevo bloque
        },
        error: (err) => {
          this.enviando.set(false);
          this.errorFormulario.set(err?.mensajeAmigable ?? 'No se pudo registrar la propuesta.');
        },
      });
  }

  etiquetaTipo(tipo: string): string {
    const etiquetas: Record<string, string> = {
      DOCENTE_OCUPADO: 'Docente ocupado',
      AULA_OCUPADA: 'Aula ocupada',
      ESPACIO_NO_COMPATIBLE: 'Espacio no compatible',
      FUERA_DISPONIBILIDAD: 'Fuera de disponibilidad',
      EXCESO_CARGA_HORARIA: 'Exceso de carga horaria',
      CAPACIDAD_INSUFICIENTE: 'Capacidad insuficiente',
    };
    return etiquetas[tipo] ?? tipo;
  }
}
