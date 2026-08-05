# Parche: calendario semanal visual + nombres reales en "Nueva propuesta"

## 1. Dropdown de "Nueva propuesta" — ya no muestra IDs

Antes, el `<select>` de Distributivo mostraba literalmente los IDs
internos: `3 — 1 / 3 / 3`. Ahora carga también docentes, asignaturas y
paralelos, y arma una etiqueta legible:

```
Cálculo de una Variable (A) — Ana López
```

El valor que se envía al backend sigue siendo el ID interno (eso no
cambia, es lo que la API espera) — solo cambió lo que el usuario *ve*.

## 2. Calendario semanal real (día × hora), con arrastrar y soltar

La "matriz semanal" ahora es un calendario tipo agenda (como el de tu
captura de SGA-UPSE):

- **Columnas** = días (Lunes a Sábado).
- **Filas** = horas, de 07:00 a 19:00.
- Cada clase aparece como una tarjeta de color (verde = válido, rojo =
  conflicto, ámbar = pendiente) posicionada y dimensionada según su
  hora de inicio/fin.
- **Botón "Generar horario"** — revalida todos los bloques del período
  contra las reglas de negocio y refresca el calendario.
- **Arrastrar y soltar** — toma cualquier tarjeta y suéltala en otro
  día/hora; el sistema:
  1. Calcula el nuevo día y hora según dónde soltaste (ajustado a
     bloques de 30 minutos).
  2. Llama al backend para mover el bloque **y revalidarlo** contra
     las mismas reglas (disponibilidad, choques de aula, etc.).
  3. Refresca el calendario con el resultado — si el nuevo horario
     genera un conflicto, la tarjeta se pinta de rojo automáticamente.

## Archivos nuevos/modificados

**Backend** (agrega la capacidad de "mover" un bloque — no existía):
- `backend/app/schemas/horario.py` — nuevo `BloqueHorarioMover`.
- `backend/app/repositories/horario_repository.py` — nuevo `mover_bloque()`
  (incluye también el fix de `crear_y_validar` de la ronda anterior, por
  si todavía no lo habías aplicado).
- `backend/app/services/horario_service.py` — nuevo método `mover()`.
- `backend/app/api/routers/horarios.py` — nuevo endpoint
  `PATCH /horarios/{bloque_id}/mover`.

**Frontend**:
- `frontend/src/app/core/models/entidades.ts` — nueva interfaz
  `PropuestaMoverBloque`.
- `frontend/src/app/core/services/api.service.ts` — nuevo método
  `moverBloque()`.
- `frontend/src/app/features/horarios/horarios.component.ts` — reescrito:
  carga docentes/asignaturas/paralelos para las etiquetas, calcula la
  posición de cada bloque en el calendario, y maneja los eventos de
  arrastrar-y-soltar.
- `frontend/src/app/features/horarios/horarios.component.html` —
  reescrito: calendario en cuadrícula en vez de listas por día.
- `frontend/src/styles/main.scss` — se agregaron los estilos del
  calendario al final del archivo (reutiliza tus mismas variables de
  color: `$english-green`, `$burgundy`, `$brass`), todo lo demás del
  archivo queda intacto.

## Cómo aplicarlo

Reemplaza los 8 archivos de arriba en las mismas rutas dentro de tu
proyecto, y reinicia backend (`Ctrl+C` + `uvicorn app.main:app --reload`)
y frontend (Angular recarga solo, pero si no ves cambios, `Ctrl+C` +
`npm start` de nuevo).

## Nota de diseño

El calendario va de 07:00 a 19:00 porque es el rango que cubre toda la
disponibilidad declarada en tu Excel (mañana + tarde + sábado). Si más
adelante cargan disponibilidad fuera de ese rango, avísame para ajustar
las constantes `HORA_INICIO_CALENDARIO` / `HORA_FIN_CALENDARIO` en
`horarios.component.ts`.
