import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { ConflictoDetalle, TipoConflicto } from '../../core/models/entidades';

@Component({
  selector: 'app-conflictos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './conflictos.component.html',
})
export class ConflictosComponent implements OnInit {
  private api = inject(ApiService);

  periodo = '2026A';
  cargando = signal(true);
  revalidando = signal(false);
  error = signal<string | null>(null);
  conflictos = signal<ConflictoDetalle[]>([]);

  filtroTipo = signal<TipoConflicto | 'TODOS'>('TODOS');
  filtroSeveridad = signal<'TODAS' | 'ALTA' | 'MEDIA' | 'BAJA'>('TODAS');

  tiposDisponibles = computed(() => {
    const tipos = new Set(this.conflictos().map((c) => c.tipo_conflicto));
    return Array.from(tipos).sort();
  });

  conflictosFiltrados = computed(() => {
    return this.conflictos().filter((c) => {
      const pasaTipo = this.filtroTipo() === 'TODOS' || c.tipo_conflicto === this.filtroTipo();
      const pasaSeveridad = this.filtroSeveridad() === 'TODAS' || c.severidad === this.filtroSeveridad();
      return pasaTipo && pasaSeveridad;
    });
  });

  conteoPorTipo = computed(() => {
    const mapa = new Map<string, number>();
    for (const c of this.conflictos()) {
      mapa.set(c.tipo_conflicto, (mapa.get(c.tipo_conflicto) ?? 0) + 1);
    }
    return mapa;
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.api.obtenerConflictos(this.periodo).subscribe({
      next: (datos) => {
        this.conflictos.set(datos);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err?.mensajeAmigable ?? 'No se pudieron cargar los conflictos.');
        this.cargando.set(false);
      },
    });
  }

  revalidarPeriodo(): void {
    this.revalidando.set(true);
    this.api.revalidarPeriodo(this.periodo).subscribe({
      next: () => {
        this.revalidando.set(false);
        this.cargar();
      },
      error: (err) => {
        this.revalidando.set(false);
        this.error.set(err?.mensajeAmigable ?? 'No se pudo revalidar el periodo.');
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
