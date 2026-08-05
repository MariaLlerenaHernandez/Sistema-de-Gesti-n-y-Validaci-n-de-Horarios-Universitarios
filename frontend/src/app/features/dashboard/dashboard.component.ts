import { Component, OnInit, inject, signal } from '@angular/core';
import { ApiService } from '../../core/services/api.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  private api = inject(ApiService);

  periodo = '2026A';
  cargando = signal(true);
  error = signal<string | null>(null);

  totalDocentes = signal(0);
  totalEspacios = signal(0);
  totalAsignaturas = signal(0);
  totalConflictos = signal(0);
  totalValidos = signal(0);

  ngOnInit(): void {
    this.cargarResumen();
  }

  private cargarResumen(): void {
    this.cargando.set(true);
    this.error.set(null);

    Promise.all([
      this.api.listarDocentes().toPromise(),
      this.api.listarEspacios().toPromise(),
      this.api.listarAsignaturas().toPromise(),
      this.api.obtenerConflictos(this.periodo).toPromise(),
      this.api.obtenerHorarioSemanal(this.periodo).toPromise(),
    ])
      .then(([docentes, espacios, asignaturas, conflictos, horario]) => {
        this.totalDocentes.set(docentes?.length ?? 0);
        this.totalEspacios.set(espacios?.length ?? 0);
        this.totalAsignaturas.set(asignaturas?.length ?? 0);
        this.totalConflictos.set(conflictos?.length ?? 0);
        this.totalValidos.set((horario ?? []).filter((b) => b.estado === 'VALIDO').length);
      })
      .catch((err) => {
        this.error.set(err?.mensajeAmigable ?? 'No se pudo cargar el resumen.');
      })
      .finally(() => this.cargando.set(false));
  }
}
