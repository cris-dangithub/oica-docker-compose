# Contrato de interfaz — frontend Next.js

> **Sustituido en parte por `specs/002-presentacion-resultados/contracts/` (2026-10-04).** Lo que la spec 002 cambia rige desde allí; el resto de este contrato sigue vigente.

Antes de implementar hay que leer `docs/oica-redesign/AI-DESIGN-RULES.md` y `STATE.md`. La
interfaz va en español y con tres espacios de indentación. HTTP solo usa `API_URL` (`/api`).
La interfaz MUST NOT introducir violaciones nuevas de axe.

## `/subir-cartilla` (`components/file-upload.tsx`)

- **Campo**: numérico opcional, «Desperdicio admisible (%)», sin valor por defecto.
- **Ayuda fija** (FR-002): «Opcional. No identificamos una norma colombiana que fije un
  porcentaje máximo de desperdicio de acero; usa el que asumiste en tu análisis de precios
  unitarios o el que exige tu contrato». Solo después de que T003 verifique las fuentes podrá
  nombrar las normas consultadas.
- **Validación local**: `0 < v < 100`. El backend valida de nuevo.
- **Envío**: `makeForm()` envía `umbral_desperdicio_pct` solo si el campo tiene valor.

## `/archivos` (`components/FilesTable.tsx`)

- **Insignia** de la última versión, en tabla y tarjetas:
  - «Dentro de lo admisible» o «Excede», según el estado;
  - «Sin evaluar» si no hay umbral;
  - nada si el campo es `null` (versión histórica).
- **Enlace** «Ver detalle» a `/archivos/<id>`.
- **Diálogo de reproceso**: añade el campo de umbral precargado con el vigente, editable y que
  se puede vaciar. Envía `umbral_desperdicio_pct`: el número, `null` si se vació o la clave
  ausente si no se tocó.

## `/archivos/[id]` (nueva)

Es una página cliente que llama a `GET /api/file/<id>` y tiene estas secciones:

1. **Encabezado**: nombre del archivo, versión seleccionada (por defecto la última) y umbral
   vigente.
2. **Verificación**: «Plan verificado» o el motivo del error.
3. **Admisibilidad**:
   - estado del proyecto y diferencia en puntos porcentuales;
   - tabla por diámetro;
   - pérdida irrecuperable frente a saldo reutilizable, en kg y %;
   - aprovechamiento.
4. **Resumen de compra**: tabla por diámetro, longitud y origen, con las barras de inventario
   separadas.
5. **Calidad del plan**: cota por patrones, cota simple y brecha, con la marca «no ajustada» o
   «no disponible» si aplica.
6. **Avisos de masa nominal NSR-10**: solo aparece si los hay. La fuente se rotula
   «masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)», verificada en T003 (ficha REF-NSR10-TABLA).
7. **Versiones** (FR-028): tabla con versión, perfil, tiempo de procesamiento, desperdicio,
   umbral, estado de admisibilidad, verificación y descargas.
   - Si hay umbrales distintos entre versiones, se indica «umbrales distintos».
   - Los datos que faltan se muestran como «no disponible».

Las tablas son responsive (tarjetas en móvil), siguiendo el patrón de `FilesTable`.

## Tutorial (`components/tutorial/TutorialGuide.tsx`, arreglo `glosario`)

Debe definir, sin prometer optimalidad (FR-020):

- **«Algoritmo genético»**: técnica de Inteligencia Artificial de la familia de la computación
  evolutiva. Se reencuadra la definición existente.
- **«Patrón de corte»**: se amplía la existente con las repeticiones.
- **«Nesting lineal»**: acomodo unidimensional de piezas sobre barras.
- **«Cota inferior»**: desperdicio por debajo del cual ningún plan puede bajar; mide la calidad
  del plan, no lo construye.
- **«Desperdicio admisible»**: límite que define el usuario; no se identificó un máximo
  normativo.
