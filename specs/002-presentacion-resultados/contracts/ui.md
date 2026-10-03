# Contrato de interfaz — detalle del proyecto (spec 002)

Sustituye a la sección `/archivos/[id]` de `specs/001-alineacion-titulo-tesis/contracts/ui.md`
en lo que aquí se indica. El resto del contrato de la spec 001 (`/subir-cartilla`, `/archivos`,
tutorial) sigue igual.

Antes de implementar hay que leer `docs/oica-redesign/AI-DESIGN-RULES.md` y `STATE.md`. La
interfaz va en español y con tres espacios de indentación. HTTP solo usa `API_URL` (`/api`).
La interfaz MUST NOT introducir violaciones nuevas de axe.

**No hay cambios de API.** `GET /api/file/<id>` ya devuelve `analisis` completo. En `analisis-2`,
`analisis.patrones.top[]` incluye además `secuencia`.

## `/archivos/[id]` — secciones, en orden

1. **Encabezado**: sin cambios.
2. **Verificación**: sin cambios.
3. **Desperdicio y admisibilidad**: sin cambios.
4. **Resumen de compra** (`PurchaseSummary.tsx`, FR-016):
   - La tabla actual por diámetro, longitud y origen.
   - Una fila de total por diámetro (solo compra) y la fila «Total comprado» (barras y kg).
   - Si hay inventario adicional, la fila «Total tomado del inventario» aparte.
   - En móvil, el total aparece en una tarjeta resumen al final de la lista.
5. **Patrones de corte** (nuevo, `PatternsSection.tsx`, FR-015):
   - Título «Patrones de corte» y la frase «N patrones para T barras. Cada patrón es una forma de
     cortar que se repite».
   - Tabla con los 10 más repetidos: Patrón, Diámetro, Barra (longitud y origen), Secuencia por
     etapa, Repeticiones y Aprovechamiento. Si falta `secuencia`, la celda dice «no disponible».
   - Vista previa: `<img>` con `${API_URL}/descargar-imagen/${storage_uuid}`, `loading="lazy"`,
     ancho completo de la tarjeta y alto automático. Texto alternativo: «Nesting lineal de los
     patrones más repetidos (ver cobertura en la imagen)». Si no carga o la versión no tiene
     imagen, aparece un aviso neutro: «Imagen no disponible para esta versión».
   - Una nota que remite al Excel (hoja «Patrones») para la lista completa.
   - Móvil (FR-018): tarjetas por patrón, sin desplazamiento horizontal de la página.
   - Si la versión no tiene `analisis.patrones`: «Patrones: no disponible (versión procesada antes
     de este análisis)».
6. **Calidad del plan** (`QualitySection.tsx`, FR-017):
   - Cifras destacadas: «Cota por patrones» y «Brecha del plan».
   - **Se elimina la tarjeta «Cota simple».** Se añade, si existe, una frase en el texto
     explicativo: «Con aprovechamiento perfecto, el desperdicio sería x %».
   - El resto (marca de ajuste, motivo y detalle por diámetro) sigue igual.
7. **Avisos de masa nominal NSR-10**: sin cambios.
8. **Versiones**: sin cambios.

## Tipos (`file-detail/types.ts`)

```text
PatronResumen   + secuencia?: string
ResumenPatrones { total: number; barras: number; max_repeticiones: number; top: PatronResumen[] }
Analisis        + patrones?: ResumenPatrones   (si aún no está tipado)
```

Todos los campos nuevos son opcionales, para las versiones históricas.
