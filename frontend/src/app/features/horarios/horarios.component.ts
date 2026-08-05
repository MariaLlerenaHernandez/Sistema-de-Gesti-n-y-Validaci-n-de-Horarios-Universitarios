import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import {
  Asignatura,
  BloqueHorarioSemanal,
  DiaSemana,
  Distributivo,
  Docente,
  Espacio,
  Modalidad,
  Paralelo,
  ResultadoValidacionBloque,
} from '../../core/models/entidades';

const ORDEN_DIAS: DiaSemana[] = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO'];

/** Calendario: filas de hora (07:00 a 19:00) y columnas de dia. */
const HORA_INICIO_CALENDARIO = 7;
const HORA_FIN_CALENDARIO = 19;
const ALTO_FILA_PX = 52;

interface OpcionDistributivo {
  distributivo_id: number;
  etiqueta: string;
}

interface BloquePosicionado extends BloqueHorarioSemanal {
  top: number;
  alto: number;
}

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

  readonly alturaFila = ALTO_FILA_PX;
  readonly horasCalendario = Array.from(
    { length: HORA_FIN_CALENDARIO - HORA_INICIO_CALENDARIO + 1 },
    (_, i) => HORA_INICIO_CALENDARIO + i,
  );
  readonly alturaCalendario = this.horasCalendario.length * ALTO_FILA_PX;

  // --- Catalogos para el formulario ---------------------------------
  espacios = signal<Espacio[]>([]);
  distributivos = signal<Distributivo[]>([]);
  docentes = signal<Docente[]>([]);
  asignaturas = signal<Asignatura[]>([]);
  paralelos = signal<Paralelo[]>([]);
  cargandoCatalogos = signal(true);

  /** Distributivo con nombres reales en vez de IDs sueltos, para el <select>. */
  opcionesDistributivo = computed<OpcionDistributivo[]>(() => {
    const docentesPorId = new Map(this.docentes().map((d) => [d.docente_id, d]));
    const asignaturasPorId = new Map(this.asignaturas().map((a) => [a.asignatura_id, a]));
    const paralelosPorId = new Map(this.paralelos().map((p) => [p.paralelo_id, p]));

    return this.distributivos()
      .filter((d) => d.periodo_academico === this.periodo)
      .map((d) => {
        const docente = docentesPorId.get(d.docente_id);
        const asignatura = asignaturasPorId.get(d.asignatura_id);
        const paralelo = paralelosPorId.get(d.paralelo_id);

        const nombreDocente = docente ? `${docente.nombres} ${docente.apellidos}` : `Docente #${d.docente_id}`;
        const nombreAsignatura = asignatura ? asignatura.nombre_asignatura : `Asignatura #${d.asignatura_id}`;
        const codigoParalelo = paralelo ? paralelo.codigo_paralelo : '';

        return {
          distributivo_id: d.distributivo_id,
          etiqueta: `${nombreAsignatura} (${codigoParalelo}) — ${nombreDocente}`,
        };
      })
      .sort((a, b) => a.etiqueta.localeCompare(b.etiqueta));
  });

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

  // --- Matriz semanal (calendario) ------------------------------------
  bloques = signal<BloqueHorarioSemanal[]>([]);
  cargandoMatriz = signal(true);
  errorMatriz = signal<string | null>(null);
  generando = signal(false);
  vaciando = signal(false);

  /** Bloques ya posicionados (top/alto en px) agrupados por dia, listos para pintar. */
  bloquesPorDia = computed(() => {
    const mapa = new Map<DiaSemana, BloquePosicionado[]>();
    for (const dia of this.diasSemana) mapa.set(dia, []);

    for (const b of this.bloques()) {
      const lista = mapa.get(b.dia_semana);
      if (!lista) continue;
      lista.push(this.posicionarBloque(b));
    }
    return mapa;
  });

  // --- Arrastrar y soltar ----------------------------------------------
  private arrastrando: { bloqueId: number; duracionMinutos: number } | null = null;
  celdaResaltada: { dia: DiaSemana } | null = null;
  moviendoBloqueId: number | null = null;

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargarMatriz();
  }

  private cargarCatalogos(): void {
    this.cargandoCatalogos.set(true);
    Promise.all([
      this.api.listarEspacios().toPromise(),
      this.api.listarDistributivo().toPromise(),
      this.api.listarDocentes().toPromise(),
      this.api.listarAsignaturas().toPromise(),
      this.api.listarParalelos().toPromise(),
    ])
      .then(([espacios, distributivos, docentes, asignaturas, paralelos]) => {
        this.espacios.set(espacios ?? []);
        this.distributivos.set(distributivos ?? []);
        this.docentes.set(docentes ?? []);
        this.asignaturas.set(asignaturas ?? []);
        this.paralelos.set(paralelos ?? []);
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

  /** Boton "Vaciar horario": borra todos los bloques del periodo, con confirmacion previa. */
  vaciarHorario(): void {
    if (this.bloques().length === 0) return;

    const confirmado = confirm(
      `¿Vaciar todo el horario del período ${this.periodo}? Se eliminarán los ${this.bloques().length} bloque(s) registrados. Esta acción no se puede deshacer.`,
    );
    if (!confirmado) return;

    this.vaciando.set(true);
    this.errorMatriz.set(null);
    this.api.vaciarPeriodo(this.periodo).subscribe({
      next: () => {
        this.bloques.set([]);
        this.vaciando.set(false);
      },
      error: (err) => {
        this.errorMatriz.set(err?.mensajeAmigable ?? 'No se pudo vaciar el horario.');
        this.vaciando.set(false);
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
        distributivo_id: datos.distributivo_id as unknown as number,
        espacio_id: datos.espacio_id as unknown as number,
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
          this.cargarMatriz(); // refresca el calendario con el nuevo bloque
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

  // --- Calculo de posicion (calendario tipo agenda) ---------------------

  private horaAMinutos(hora: string): number {
    const [h, m] = hora.split(':').map(Number);
    return h * 60 + (m ?? 0);
  }

  private minutosAHora(minutosDesdeMedianoche: number): string {
    const h = Math.floor(minutosDesdeMedianoche / 60);
    const m = minutosDesdeMedianoche % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00`;
  }

  private posicionarBloque(b: BloqueHorarioSemanal): BloquePosicionado {
    const inicioMin = this.horaAMinutos(b.hora_inicio) - HORA_INICIO_CALENDARIO * 60;
    const finMin = this.horaAMinutos(b.hora_fin) - HORA_INICIO_CALENDARIO * 60;
    const top = (inicioMin / 60) * ALTO_FILA_PX;
    const alto = Math.max(((finMin - inicioMin) / 60) * ALTO_FILA_PX - 2, 20);
    return { ...b, top, alto };
  }

  // --- Arrastrar y soltar (mover un bloque a otro dia/hora) -------------

  onDragStart(evento: DragEvent, bloque: BloqueHorarioSemanal): void {
    const duracionMinutos = this.horaAMinutos(bloque.hora_fin) - this.horaAMinutos(bloque.hora_inicio);
    this.arrastrando = { bloqueId: bloque.bloque_id, duracionMinutos };
    evento.dataTransfer?.setData('text/plain', String(bloque.bloque_id));
    if (evento.dataTransfer) evento.dataTransfer.effectAllowed = 'move';
  }

  onDragOverDia(evento: DragEvent, dia: DiaSemana): void {
    evento.preventDefault();
    if (evento.dataTransfer) evento.dataTransfer.dropEffect = 'move';
    this.celdaResaltada = { dia };
  }

  onDragLeaveDia(): void {
    this.celdaResaltada = null;
  }

  onDropEnDia(evento: DragEvent, dia: DiaSemana): void {
    evento.preventDefault();
    this.celdaResaltada = null;
    if (!this.arrastrando) return;

    const contenedor = evento.currentTarget as HTMLElement;
    const rect = contenedor.getBoundingClientRect();
    const offsetY = evento.clientY - rect.top;

    const minutosDesdeInicio = (offsetY / ALTO_FILA_PX) * 60;
    const horaSnapMin = Math.round(minutosDesdeInicio / 30) * 30; // ajusta a bloques de 30 min

    let nuevoInicioMin = HORA_INICIO_CALENDARIO * 60 + horaSnapMin;
    const { bloqueId, duracionMinutos } = this.arrastrando;

    // no dejar que el bloque se salga del calendario
    const maxInicio = HORA_FIN_CALENDARIO * 60 - duracionMinutos;
    nuevoInicioMin = Math.max(HORA_INICIO_CALENDARIO * 60, Math.min(nuevoInicioMin, maxInicio));
    const nuevoFinMin = nuevoInicioMin + duracionMinutos;

    this.moviendoBloqueId = bloqueId;
    this.api
      .moverBloque(bloqueId, {
        dia_semana: dia,
        hora_inicio: this.minutosAHora(nuevoInicioMin),
        hora_fin: this.minutosAHora(nuevoFinMin),
      })
      .subscribe({
        next: () => {
          this.moviendoBloqueId = null;
          this.cargarMatriz();
        },
        error: (err) => {
          this.moviendoBloqueId = null;
          this.errorMatriz.set(err?.mensajeAmigable ?? 'No se pudo mover el bloque.');
        },
      });

    this.arrastrando = null;
  }
}
