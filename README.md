# Sistema de Gestion y Validacion de Horarios Universitarios

Proyecto academico: sistema web para la gestion, proyeccion y validacion de
horarios academicos universitarios, con arquitectura desacoplada en tres
capas (base de datos / backend / frontend).

## Stack tecnologico

| Capa | Tecnologia |
|---|---|
| Frontend | Angular 17+ (standalone components), PrimeNG, RxJS, xlsx, papaparse |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic |
| Base de datos | Microsoft SQL Server (tablas, funciones, stored procedures, triggers) |

## Estructura del repositorio

```text
.
├── database/               Tablas, funciones, procedimientos, vistas y seed (SQL Server)
├── backend/                API REST (FastAPI + SQLAlchemy + Pydantic)
├── frontend/                Interfaz web (Angular + PrimeNG)
├── docker-compose.yml        Orquesta los 3 servicios: sqlserver, backend, frontend
├── GUIA_INSTALACION_BD.md    Paso 1: levantar y verificar la base de datos
├── GUIA_BACKEND.md            Paso 2: levantar y verificar el backend
└── GUIA_FRONTEND.md            Paso 3: levantar y verificar el frontend
```

## Puesta en marcha

Sigue las tres guias **en orden**, cada una verifica que el paso anterior
quedo bien antes de continuar:

1. **[`GUIA_INSTALACION_BD.md`](GUIA_INSTALACION_BD.md)** — levanta SQL Server
   con Docker (puerto `14330`), ejecuta los scripts de `database/` en orden,
   y confirma que `vw_ConflictosDetalle` devuelve los 5 tipos de conflicto
   de la semilla.
   > **Importante:** despues de `03_triggers.sql` y antes de las funciones,
   > ejecuta tambien **`database/tables/04_fix_asignaturas_codigo_ext.sql`**
   > (corrige el mapeo entre `asignatura_id` y `codigo_asignatura` que usan
   > `paralelos` y `distributivo` al importar — ver detalle en
   > `docs/CORRECCION_IMPORTACION_ASIGNATURAS.md`). Es seguro ejecutarlo
   > aunque ya hayas corrido los scripts antes: solo agrega una columna.
2. **[`GUIA_BACKEND.md`](GUIA_BACKEND.md)** — instala y arranca la API
   FastAPI (local con `uvicorn` o en Docker), y confirma que
   `/api/v1/docentes`, `/api/v1/horarios/semanal/2026A` y
   `/api/v1/horarios/conflictos?periodo_academico=2026A` devuelven los
   datos de la semilla.
3. **[`GUIA_FRONTEND.md`](GUIA_FRONTEND.md)** — instala y arranca Angular
   (local con `npm start` o en Docker), y recorre el flujo completo:
   Dashboard → CRUDs → Importar Excel → Construir/Validar horarios.

### Atajo: todo con Docker Compose

Si ya tienes Docker Desktop, puedes levantar los tres servicios de una sola vez:

```powershell
docker compose up -d --build
```

- Base de datos: `localhost,14330` (usuario `sa`, password `HorariosUni2026`)
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:4200

Dale unos 30-60 segundos a que SQL Server quede `healthy` antes de que el
backend termine de arrancar (el `docker-compose.yml` ya encadena la
dependencia). Los scripts de `database/` **no se ejecutan automaticamente**
— siempre debes correrlos manualmente la primera vez, tal como indica
`GUIA_INSTALACION_BD.md`.

## Reglas de negocio implementadas

| Regla | Donde se implementa |
|---|---|
| Docente no puede dictar 2 clases al mismo tiempo | `fn_DocenteTieneTraslape` (SQL) |
| Espacio no puede asignarse dos veces en la misma franja | `fn_EspacioOcupado` (SQL) |
| Espacio debe ser compatible (tipo + capacidad) | `fn_EspacioCompatible` (SQL) |
| Horario debe respetar disponibilidad del docente | `fn_DocenteDentroDisponibilidad` (SQL) |
| No exceder carga horaria maxima semanal | `fn_CargaHorariaDocente` (SQL) |
| Asignatura con laboratorio exige tipo de espacio | Constraint SQL + validacion Pydantic |
| Paralelos se planifican de forma independiente | Diseno del modelo de datos (sin agrupacion por defecto) |

Todas las reglas anteriores se evaluan en un unico lugar —
`sp_ValidarBloqueHorario` — sin importar si el bloque de horario se crea
desde la importacion, desde la pantalla "Construir/Validar", o desde
cualquier otro cliente futuro.

## Pruebas unitarias

```powershell
cd backend
pip install -r requirements.txt
pytest
```

## Documentacion tecnica adicional

- **[`docs/Documento-Tecnico.docx`](docs/Documento-Tecnico.docx)** — documento
  tecnico de entrega (arquitectura, modelo de datos, reglas de negocio,
  endpoints y pruebas unitarias), listo para Word.
- **[`docs/GUION_DEMOSTRACION.md`](docs/GUION_DEMOSTRACION.md)** — guion
  paso a paso para la demostracion en vivo, cubriendo las 5 evidencias
  minimas exigidas por la especificacion (carga Excel, registro de
  propuesta, deteccion de al menos 3 conflictos, visualizacion del
  horario y ejecucion de pruebas unitarias).
