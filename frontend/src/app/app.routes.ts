import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'panel',
  },
  {
    path: 'panel',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    title: 'Panel general — Sistema de Horarios',
  },
  {
    path: 'importacion',
    loadComponent: () =>
      import('./features/importacion/importacion.component').then((m) => m.ImportacionComponent),
    title: 'Carga inicial de datos — Sistema de Horarios',
  },
  {
    path: 'horarios',
    loadComponent: () =>
      import('./features/horarios/horarios.component').then((m) => m.HorariosComponent),
    title: 'Horarios y propuestas — Sistema de Horarios',
  },
  {
    path: 'conflictos',
    loadComponent: () =>
      import('./features/conflictos/conflictos.component').then((m) => m.ConflictosComponent),
    title: 'Conflictos detectados — Sistema de Horarios',
  },
  {
    path: '**',
    redirectTo: 'panel',
  },
];
