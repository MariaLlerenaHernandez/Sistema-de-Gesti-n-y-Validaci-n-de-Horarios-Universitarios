# Cómo levantar el backend (FastAPI)

Requisito previo: ya debiste completar `GUIA_INSTALACION_BD.md` y confirmar que
la consulta de verificación del paso 5 te devuelve los 5 tipos de conflicto y
al menos un bloque `VALIDO`. El backend asume que la base de datos ya existe
con todo su contenido (tablas, funciones, procedimientos, vistas y la
semilla de datos).

## 1. Ubicación de archivos

La carpeta `backend/` va en la **raíz** de tu proyecto, junto a `database/`:

```
horarios-universitarios/
├── docker-compose.yml
├── GUIA_INSTALACION_BD.md
├── GUIA_BACKEND.md          <- este archivo
├── database/
└── backend/                 <- aquí
    ├── app/
    ├── requirements.txt
    ├── .env.example
    └── Dockerfile
```

## 2. Opción A: correr el backend directo en tu maquina (recomendado para desarrollar)

Esta opción asume que ya tienes el contenedor de SQL Server corriendo
(`docker compose up -d sqlserver`, como en la guía de la BD) y que vas a
correr FastAPI directamente con Python, sin contenedor.

```powershell
cd backend
python -m venv venv
venv\Scripts\activate            # En Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # En Mac/Linux: cp .env.example .env
```

El archivo `.env.example` ya viene con los mismos valores que tu
`docker-compose.yml` (puerto **14330**, password `HorariosUni2026`), asi que
normalmente no necesitas cambiar nada. Si en algun momento cambias la
contraseña o el puerto en el compose, actualiza tambien el `.env`.

> **Requisito adicional en Windows**: necesitas el "ODBC Driver 18 for SQL
> Server" instalado en tu maquina (no solo en el contenedor). Descargalo de
> https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
> si aun no lo tienes — sin este driver, `pyodbc` no puede conectarse.

Luego arranca el servidor:

```powershell
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Documentación interactiva (Swagger): **http://localhost:8000/docs**
- Salud del servicio: http://localhost:8000/health

## 3. Opción B: todo en Docker Compose (backend + base de datos juntos)

Si prefieres no instalar Python ni el driver ODBC en tu máquina, el
`docker-compose.yml` ya incluye un servicio `backend` que se construye solo:

```powershell
docker compose up -d --build
```

Esto levanta `horarios_sqlserver` y `horarios_backend` juntos. El backend
espera automáticamente a que SQL Server esté `healthy` antes de arrancar
(`depends_on: condition: service_healthy`), y se conecta usando el nombre
del servicio (`sqlserver:1433`) en vez de `localhost:14330`, porque dentro
de la red de Docker Compose los contenedores se ven entre si por nombre.

Verifica que arrancó bien:

```powershell
docker logs horarios_backend -f
```

Deberías ver una línea como
`Sistema de Horarios Universitarios v1.0.0 iniciado en modo production`.

La API queda disponible igual en http://localhost:8000/docs.

## 4. Verificar que el backend ve los mismos datos que la base de datos

Con el backend arriba (Opción A o B), prueba estos tres endpoints desde
`/docs` o con `curl`:

```powershell
curl http://localhost:8000/api/v1/docentes
curl http://localhost:8000/api/v1/horarios/semanal/2026A
curl "http://localhost:8000/api/v1/horarios/conflictos?periodo_academico=2026A"
```

- El primero debe devolver los 3 docentes de la semilla (`DOC001`, `DOC002`, `DOC003`).
- El segundo debe devolver los bloques de horario del "Caso 0" en adelante.
- El tercero debe devolver los mismos 5 tipos de conflicto que viste en
  `vw_ConflictosDetalle` al validar la base de datos:
  `DOCENTE_OCUPADO`, `AULA_OCUPADA`, `ESPACIO_NO_COMPATIBLE`,
  `FUERA_DISPONIBILIDAD`, `EXCESO_CARGA_HORARIA`.

Si estos tres endpoints responden bien, el backend está correctamente
conectado y validado contra tu base de datos.

## 5. Qué incluye este backend

- **Arquitectura en capas**: `api/routers` (HTTP) → `services` (reglas de
  negocio de alto nivel: duplicados, referencias inexistentes) →
  `repositories` (acceso a datos con SQLAlchemy) → `models` (ORM).
- **CRUD completo** para Docentes, Espacios, Asignaturas, Paralelos,
  Distributivo y Disponibilidad Docente.
- **Importación** por hoja (`POST /api/v1/import/docentes`, `/espacios`,
  `/asignaturas`, `/paralelos`, `/distributivo`, `/disponibilidad`):
  valida cada fila con Pydantic, acumula errores sin detener el proceso, y
  hace *upsert* por código externo.
- **Construcción y validación de horarios**:
  - `POST /api/v1/horarios/validar` — registra un bloque y ejecuta de
    inmediato `sp_ValidarBloqueHorario`.
  - `POST /api/v1/horarios/{bloque_id}/revalidar` — revalida un bloque puntual.
  - `POST /api/v1/horarios/validar-periodo/{periodo}` — revalida todo un
    periodo académico de una sola vez (equivalente a
    `sp_ValidarPeriodoAcademico`).
  - `GET /api/v1/horarios/semanal/{periodo}` — matriz semanal (para el
    calendario del frontend), leyendo `vw_HorarioSemanal`.
  - `GET /api/v1/horarios/conflictos?periodo_academico=...` — listado de
    conflictos, leyendo `vw_ConflictosDetalle`.
- **Manejo global de errores**: cualquier error de negocio, de validación
  de payload, o de integridad de base de datos responde con un JSON
  consistente (`estado`, `codigo`, `mensaje`, `detalles`).
- **Pruebas unitarias** (`pytest`) sobre los schemas de validación y la
  lógica de los servicios de Docentes e Importación, usando *mocks* del
  repositorio (no requieren la base de datos real corriendo).

## 6. Correr las pruebas unitarias

```powershell
cd backend
pip install -r requirements.txt
pytest
```

## 7. Errores comunes

**`pyodbc.InterfaceError` / "Data source name not found"** → falta instalar
el ODBC Driver 18 en tu máquina (ver sección 2), o el nombre del driver en
`.env` no coincide exactamente con el instalado. Verifica los drivers
disponibles con:

```powershell
python -c "import pyodbc; print(pyodbc.drivers())"
```

**`Login failed for user 'sa'`** → mismo motivo que en la guía de la BD:
revisa la contraseña en `.env` contra la de `docker-compose.yml`.

**El backend arranca pero `/docentes` devuelve `[]` vacío** → probablemente
no ejecutaste `database/seed/01_seed.sql`, o lo ejecutaste contra otra base
de datos. Verifica con Azure Data Studio que `SELECT * FROM dbo.Docentes`
devuelva las 3 filas de la semilla.

**CORS bloqueado desde el frontend** → confirma que `CORS_ORIGINS` en tu
`.env` incluya exactamente `http://localhost:4200` (el puerto por defecto
de `ng serve`).

---

Con esto el backend queda listo y validado contra la base de datos que ya
armaste. El siguiente paso natural es el frontend en Angular (importación
de Excel, construcción de horarios, matriz semanal y tabla de conflictos)
— avísame y seguimos con eso.
