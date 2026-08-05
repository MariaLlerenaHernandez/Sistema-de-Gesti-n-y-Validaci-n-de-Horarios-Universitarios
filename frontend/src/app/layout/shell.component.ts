import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

interface ItemNav {
  ruta: string;
  etiqueta: string;
  icono: string;
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="d-flex" style="min-height: 100vh;">
      <!-- ============================== Barra lateral ============================== -->
      <aside class="app-sidebar d-none d-lg-flex flex-column">
        <div class="px-4 pt-4 pb-3 d-flex align-items-center gap-3 hairline-bottom">
          <span class="sello sello-sm">SH</span>
          <div class="lh-sm">
            <div class="eyebrow">Sistema de</div>
            <div class="text-white fw-semibold" style="font-family: 'Fraunces', serif; font-size: 1.05rem;">
              Horarios
            </div>
          </div>
        </div>

        <nav class="flex-grow-1 px-3 py-4 d-flex flex-column gap-1">
          @for (item of navegacion; track item.ruta) {
            <a
              [routerLink]="item.ruta"
              routerLinkActive="activo"
              class="nav-item-lujo"
            >
              <i class="bi" [class]="item.icono"></i>
              <span>{{ item.etiqueta }}</span>
            </a>
          }
        </nav>

        <div class="px-4 py-3 hairline-top">
          <div class="eyebrow mb-1">Periodo academico</div>
          <div class="text-white-50" style="font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;">
            2026A
          </div>
        </div>
      </aside>

      <!-- ============================== Contenido ============================== -->
      <div class="flex-grow-1 d-flex flex-column" style="min-width: 0;">
        <!-- Barra superior movil -->
        <header class="d-lg-none d-flex align-items-center gap-3 px-3 py-3 hairline-bottom bg-white">
          <span class="sello sello-sm">SH</span>
          <span class="fw-semibold" style="font-family: 'Fraunces', serif;">Sistema de Horarios</span>
        </header>

        <main class="flex-grow-1 app-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [
    `
      .app-sidebar {
        width: 260px;
        background: #0b1b33;
        flex-shrink: 0;
      }

      .nav-item-lujo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.65rem 1rem;
        border-radius: 0.2rem;
        color: rgba(255, 255, 255, 0.65);
        text-decoration: none;
        font-size: 0.9rem;
        transition: background-color 0.15s ease, color 0.15s ease;
      }

      .nav-item-lujo i {
        font-size: 1rem;
        width: 1.25rem;
        text-align: center;
      }

      .nav-item-lujo:hover {
        background: rgba(255, 255, 255, 0.06);
        color: #ffffff;
      }

      .nav-item-lujo.activo {
        background: rgba(176, 141, 87, 0.15);
        color: #d4b888;
        font-weight: 500;
      }

      .app-content {
        background: #f7f5f0;
        min-height: 100vh;
      }
    `,
  ],
})
export class ShellComponent {
  navegacion: ItemNav[] = [
    { ruta: '/panel', etiqueta: 'Panel general', icono: 'bi-grid-1x2' },
    { ruta: '/importacion', etiqueta: 'Carga de datos', icono: 'bi-file-earmark-spreadsheet' },
    { ruta: '/horarios', etiqueta: 'Horarios', icono: 'bi-calendar3' },
    { ruta: '/conflictos', etiqueta: 'Conflictos', icono: 'bi-exclamation-diamond' },
  ];
}
