# Cómo levantar la base de datos (Windows + Docker)

## 1. Ubicación de archivos

Coloca `docker-compose.yml` en la **raíz** de tu carpeta de proyecto:

```
horarios-universitarios/
├── docker-compose.yml          <- aquí
└── database/
    ├── tables/
    ├── functions/
    ├── procedures/
    ├── views/
    └── seed/
```

## 2. Levantar el contenedor

Abre una terminal (PowerShell o la terminal integrada de VS Code) **en la carpeta raíz del proyecto** y ejecuta:

```powershell
docker compose up -d
```

Espera unos 20-30 segundos (SQL Server tarda un poco en arrancar la primera vez). Verifica que esté sano con:

```powershell
docker ps
```

Debe aparecer `horarios_sqlserver` con estado `healthy`. Si dice `starting`, espera un poco más y vuelve a correr el comando.

## 3. Conectarte a la base de datos

Recomiendo **Azure Data Studio** (gratuito, multiplataforma, más liviano que SSMS): https://azure.microsoft.com/products/data-studio

Datos de conexión:
- **Server**: `localhost,14330`
- **Authentication type**: SQL Login
- **User**: `sa`
- **Password**: `HorariosUni2026`
- Marca "Trust server certificate" en Advanced (necesario porque el contenedor usa un certificado autofirmado)

> **¿Por qué el puerto 14330 y no el 1433 estándar?** Muchas máquinas ya tienen instalado un SQL Server nativo (no en Docker) que usa el puerto 1433 por defecto. Si Docker también intentara usar ese mismo puerto, las conexiones podrían mezclarse entre el SQL Server nativo y el de Docker, causando errores de login confusos. Por eso el contenedor de este proyecto expone su SQL Server en el puerto **14330** del lado de Windows — así conviven sin problema con cualquier otro SQL Server que ya tengas instalado. Puertos "internos" de SQL Server dentro del contenedor siguen siendo 1433, solo cambia el puerto que ve Windows.

Si prefieres SSMS, funciona igual con los mismos datos.

## 4. Ejecutar los scripts EN ESTE ORDEN

Abre cada archivo dentro de Azure Data Studio (o SSMS) y ejecútalo (F5 o botón "Run") en este orden exacto — cada uno depende del anterior:

1. `database/tables/01_base_datos_y_docentes.sql`
2. `database/tables/02_resto_de_tablas.sql`
3. `database/tables/03_triggers.sql`
4. `database/functions/01_funciones.sql`
5. `database/procedures/01_procedimientos.sql`
6. `database/views/01_vistas.sql`
7. `database/seed/01_seed.sql` *(opcional, pero recomendado para tener datos de prueba)*

## 5. Verificar que todo funcionó

Corre esta consulta:

```sql
USE HorariosUniversitarios;
SELECT * FROM dbo.vw_ConflictosDetalle ORDER BY tipo_conflicto;
```

Deberías ver **5 filas o más**, con estos `tipo_conflicto` distintos:
- `DOCENTE_OCUPADO`
- `AULA_OCUPADA`
- `ESPACIO_NO_COMPATIBLE`
- `FUERA_DISPONIBILIDAD`
- `EXCESO_CARGA_HORARIA`

Y confirma que también hay al menos un bloque válido:

```sql
SELECT * FROM dbo.vw_HorarioSemanal WHERE estado = 'VALIDO';
```

Debería aparecer 1 fila (el "Caso 0" de control).

## 6. Errores comunes

**"Login failed for user 'sa'"** → revisa que copiaste bien la contraseña, incluyendo el signo `!` al final.

**El contenedor no queda "healthy"** → revisa los logs con `docker logs horarios_sqlserver` y busca líneas de error. Lo más común es RAM insuficiente asignada a Docker Desktop (dale al menos 2 GB en Settings > Resources).

**"Login failed for user 'sa'" con el puerto 14330 y contraseña correcta** → verifica que no tengas otro SQL Server (nativo o de otro contenedor) también publicado en el puerto 14330. Corre `docker ps` y confirma que solo `horarios_sqlserver` usa ese puerto, y con `Get-Service | Where-Object {$_.DisplayName -like "*SQL Server*"}` en PowerShell confirma que tu SQL Server nativo sigue en el 1433 (no interfiere).

## 7. Comandos útiles

```powershell
docker compose down          # apaga el contenedor (los datos persisten en el volumen)
docker compose down -v       # apaga y BORRA todos los datos (para empezar de cero)
docker compose up -d         # vuelve a levantarlo
docker logs horarios_sqlserver -f   # ver logs en vivo
```

Una vez que confirmes que la consulta del paso 5 te devuelve los 5 tipos de conflicto, avísame y seguimos con el backend en FastAPI.
