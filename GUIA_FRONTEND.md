# Cómo levantar el frontend (Angular + PrimeNG)

Requisito previo: backend corriendo y verificado según `GUIA_BACKEND.md`
(los tres endpoints de prueba de esa guía deben responder con datos).

## 1. Ubicación de archivos

```
horarios-universitarios/
├── docker-compose.yml
├── GUIA_INSTALACION_BD.md
├── GUIA_BACKEND.md
├── GUIA_FRONTEND.md         <- este archivo
├── database/
├── backend/
└── frontend/                 <- aquí
    ├── src/
    ├── package.json
    ├── angular.json
    └── Dockerfile
```

## 2. Opción A: correr el frontend directo en tu maquina (recomendado para desarrollar)

```powershell
cd frontend
npm install
npm start
```

Esto levanta Angular en modo desarrollo en **http://localhost:4200**, con
recarga automática al guardar cambios. El frontend está configurado para
hablar con el backend en `http://localhost:8000/api/v1` (archivo
`src/app/core/api-config.ts`) — si cambias el puerto del backend, actualiza
esa constante.

> `npm install` puede tardar unos minutos la primera vez (PrimeNG, Angular
> CLI y el resto de dependencias). Necesitas **Node.js 18 o superior**.

## 3. Opción B: todo en Docker Compose (base de datos + backend + frontend)

```powershell
docker compose up -d --build
```

Esto construye y levanta los tres servicios: `horarios_sqlserver`,
`horarios_backend` y `horarios_frontend`. El frontend se sirve como
archivos estáticos compilados (build de producción) detrás de nginx, en
**http://localhost:4200** — el mapeo de puertos es `4200:80` (el 80 es el
puerto interno de nginx dentro del contenedor).

Verifica que los tres estén sanos:

```powershell
docker ps
```

## 4. Recorrido funcional (para probar que todo esta conectado)

1. Abre **http://localhost:4200**. Deberías ver el Dashboard con los
   indicadores (3 docentes, 3 espacios, 3 asignaturas, 4 paralelos — los de
   la semilla).
2. Entra a **Docentes / Espacios / Asignaturas / Paralelos / Distributivo**
   y confirma que la tabla muestra los datos de `database/seed/01_seed.sql`.
   Prueba crear, editar y eliminar un registro de prueba.
3. Entra a **Construir / Validar** y escribe `2026A` en el campo de
   periodo (o déjalo por defecto). La matriz semanal debe mostrar los
   bloques de la semilla, coloreados: **verde** el "Caso 0" (válido) y
   **rojo** los que generan conflicto a propósito. La tabla de conflictos
   de abajo debe listar los 5 tipos: `DOCENTE_OCUPADO`, `AULA_OCUPADA`,
   `ESPACIO_NO_COMPATIBLE`, `FUERA_DISPONIBILIDAD`, `EXCESO_CARGA_HORARIA`.
4. Registra una propuesta nueva de horario (formulario de la misma
   pantalla) y confirma que el sistema te dice de inmediato si quedó
   válida o con conflicto, con el detalle de cada regla violada.
5. Entra a **Importar Excel** y sube un archivo `.xlsx` con las hojas del
   anexo de formatos (`docentes`, `espacios`, `asignaturas`, `paralelos`,
   `distributivo`, `disponibilidad_docente`). Revisa la vista previa por
   pestaña y envía cada hoja al backend.

Si los 5 pasos funcionan, tienes el flujo completo end-to-end demostrable:
importación → insumos → construcción de horario → detección de
conflictos → visualización.

## 5. Qué incluye este frontend

- **Angular 17+ standalone**, sin NgModules, con lazy loading por ruta.
- **PrimeNG** para tablas (`p-table`), diálogos de formulario
  (`p-dialog` + Reactive Forms), dropdowns, calendario de horas,
  confirmaciones de borrado y notificaciones Toast.
- **Interceptor HTTP global** (`error.interceptor.ts`) que centraliza el
  manejo de errores de la API y los muestra como Toast, sin repetir
  codigo en cada componente.
- **`ExcelReaderService`**: lee el archivo `.xlsx`/`.csv` enteramente en
  el navegador (con `xlsx` y `papaparse`), una hoja por pestaña del
  libro, antes de enviar nada al backend — cumpliendo el flujo exacto
  del anexo de formatos de carga.
- **CRUD completo** (tabla + formulario en diálogo) para Docentes,
  Espacios, Asignaturas, Paralelos, Distributivo y Disponibilidad.
- **Página de Horarios**: formulario de registro de propuesta, matriz
  semanal por colores (válido / conflicto / pendiente) y tabla de
  conflictos detectados, ambas leyendo directamente `vw_HorarioSemanal`
  y `vw_ConflictosDetalle` a través del backend.

## 6. Errores comunes

**La app carga pero las tablas quedan vacías / Toast rojo de error** →
el backend no está corriendo o `CORS_ORIGINS` en el `.env` del backend no
incluye `http://localhost:4200`. Revisa la consola del navegador (F12) para
ver el detalle exacto del error HTTP.

**`npm install` falla por versiones de Node** → confirma `node -v` (debe
ser 18+); si tienes una version vieja, instala Node 20 LTS.

**El Excel se lee pero ninguna pestaña se reconoce como "hoja destino
detectada"** → revisa que los nombres de las hojas del archivo coincidan
con los del anexo (`docentes`, `espacios`, `asignaturas`, `paralelos`,
`distributivo`, `disponibilidad_docente`), sin tildes ni espacios extra.

---

Con esto el sistema queda completo de punta a punta: base de datos,
backend y frontend, cumpliendo el flujo descrito en la especificación
(`[ Frontend Angular ] -> Excel/CSV -> JSON -> API FastAPI -> SQLAlchemy ->
SQL Server con funciones y stored procedures`). Lo que sigue, si quieres,
es preparar el documento técnico y los datos para la demostración en vivo.
