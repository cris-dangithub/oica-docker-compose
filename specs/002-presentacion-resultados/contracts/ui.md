# Contrato de interfaz — detalle del proyecto (spec 002)

Sustituye a la sección `/archivos/[id]` de `specs/001-alineacion-titulo-tesis/contracts/ui.md`
en lo que aquí se indica. El resto del contrato de la spec 001 (`/subir-cartilla`, `/archivos`,
tutorial) sigue igual. **Enmienda 2026-10-04**: la §5 pasa a ser el explorador de patrones.

Reglas generales:

- Antes de implementar hay que leer `docs/oica-redesign/AI-DESIGN-RULES.md` y `STATE.md`.
- La interfaz va en español y con tres espacios de indentación.
- HTTP solo usa `API_URL` (`/api`).
- La interfaz MUST NOT introducir violaciones nuevas de axe.

**API**: `GET /api/file/<id>` no cambia y `analisis` conserva su versión vigente (sin
`analisis-2`). El explorador usa una única ruta nueva de solo lectura,
`GET /api/patrones/<storage_uuid>`, descrita en [api-patrones.md](api-patrones.md).

## `/archivos/[id]` — secciones, en orden

1. **Encabezado**: sin cambios.
2. **Verificación**: sin cambios.
3. **Desperdicio y admisibilidad**: sin cambios.
4. **Resumen de compra** (`PurchaseSummary.tsx`, FR-016):
   - La tabla actual por diámetro, longitud y origen.
   - Una fila de total por diámetro (solo compra) y la fila «Total comprado» (barras y kg).
   - Si hay inventario adicional, la fila «Total tomado del inventario» aparte.
   - En móvil, el total aparece en una tarjeta resumen al final de la lista.
5. **Patrones de corte — explorador** (nuevo, `patterns/PatternExplorer.tsx`; FR-015, FR-024 a
   FR-031):
   - **Carga diferida** (R-11):
     - Pide `${API_URL}/patrones/${storage_uuid}` cuando la sección entra en pantalla
       (`IntersectionObserver`) o al cambiar de versión.
     - Mientras carga, muestra un esqueleto con `aria-busy="true"`.
     - Si hay error de red o un 500, muestra un `Alert` de error con «Reintentar».
     - Si la respuesta trae `disponible: false`, muestra «Patrones: no disponible para esta
       versión» con el `motivo` (FR-030). El resto del detalle no se afecta.
   - **Encabezado de la sección**:
     - Título «Patrones de corte».
     - La frase «M patrones para T barras. Cada patrón es una forma de cortar que se repite».
     - La **línea de cobertura**, siempre visible y anunciada con `aria-live="polite"`: «Se
       muestran N de M patrones, que cubren B de T barras (x %)» (FR-027).
   - **Filtros** (`form-controls`, con etiquetas persistentes):
     - Diámetro, etapa y origen, como `select` con la opción «Todos».
     - Pedido: un `input` con `<datalist>` de `pedidos[]`, con la etiqueta «Pedido (N° Orden)».
       Se elige un pedido a la vez, y el valor tiene que existir en la lista para aplicarse.
     - «Quitar filtros».
     - Los filtros se combinan con Y.
     - Si no hay resultados: «Ningún patrón cumple los filtros» y el botón «Quitar filtros».
   - **Orden** (`select`, FR-031): «Como el Excel» (por defecto), «Repeticiones»,
     «Aprovechamiento» y «Saldo», todos de mayor a menor; los empates conservan el orden del
     Excel. Cambiar el orden no altera ni los filtros ni la cobertura.
   - **Leyenda**: etapas presentes («E1»… con su token `data/stage-n`), «Pérdida por corte»
     (separación), «Descarte» y «Saldo reutilizable».
   - **Lista de patrones** (R-17):
     - Se pinta por tramos de 50, con «Mostrar más patrones (quedan K)».
     - Cada fila es un `<button aria-expanded aria-controls>` con `aria-label`, por ejemplo
       «P-#4-001, barra #4 de 12 m, 230 repeticiones, aprovechamiento 99.20 %». Cuando hay un
       pedido filtrado, añade «, aporta P piezas del pedido X».
     - Contenido visible de la fila:
       - el identificador (mono);
       - el diámetro y la longitud de la barra;
       - `×repeticiones`;
       - el aprovechamiento;
       - la barra dibujada a escala común (`ancho = longitud_m / escala_m`; FR-026), con las
         piezas coloreadas por etapa, la medida dentro de la pieza cuando cabe, una separación
         por corte, el descarte y el saldo;
       - con un pedido filtrado, el aporte de piezas de ese pedido.
     - El dibujo lleva `aria-hidden="true"`. Un tooltip al pasar el ratón es solo una mejora.
     - **Móvil** (< 640 px): identificador y repeticiones arriba, y la barra a todo el ancho
       debajo, sin desplazamiento horizontal de la página (FR-018).
   - **Detalle del patrón** (se despliega bajo la fila; FR-028):
     - La secuencia legible por etapa.
     - Las piezas en orden: etapa, longitud (coma decimal), cantidad por barra y pedidos que
       atiende, con sus piezas totales.
     - Repeticiones, aprovechamiento, pérdida por corte, descarte y saldo, en metros.
     - **Barras que lo usan**:
       - el total, siempre visible;
       - los rangos (`#4:1 a #4:200 (200)`), con los primeros 100 rangos;
       - «Ver más (quedan K)» añade como máximo otros 100;
       - nunca se pintan todos los rangos de una vez (SC-012).
     - Una nota: «La lista completa está en la hoja Patrones y Barras del Excel».
     - Se cierra con el mismo botón de la fila. El foco vuelve a la fila.
   - **Descarga de la imagen**: no hay vista previa en la sección. La descarga del PNG sigue en
     `VersionsTable.tsx`.
6. **Calidad del plan** (`QualitySection.tsx`, FR-017):
   - Cifras destacadas: «Cota por patrones» y «Brecha del plan».
   - **Se elimina la tarjeta «Cota simple».** Se añade, si existe, una frase en el texto
     explicativo: «Con aprovechamiento perfecto, el desperdicio sería x %».
   - El resto (marca de ajuste, motivo y detalle por diámetro) sigue igual.
7. **Avisos de masa nominal NSR-10**: sin cambios.
8. **Versiones**: sin cambios.

## Formato numérico en toda la app (enmiendas 2 y 3; FR-032 a FR-035; research R-20)

Aplica a todas las pantallas (`/`, `/subir-cartilla`, `/archivos`, `/archivos/[id]`, `/tutorial`
y `/contact-us`).

- **Presentación** (enmienda 3): punto decimal, sin separador de miles y con un espacio antes de
  la unidad («8.86 %», «152039.57 kg», «13955 barras», «+1.264 pp»).
- **Decimales (FR-033)**:
  - porcentajes: 2;
  - cota y brecha: 3;
  - pp frente al umbral: 2;
  - kg: 2;
  - kg/m: 3;
  - metros y mm: hasta 3, sin ceros finales;
  - segundos medidos: 1;
  - rangos estimados: enteros;
  - conteos: enteros sin separador de miles.
- **Ayudantes obligatorios**: `decimal`, `entero`, `pct`, `pp` y `kg` de
  `file-detail/types.ts`, y `numero` y `metros` de `file-detail/patterns/filtros.ts`. No se usan
  `toFixed` ni `toLocaleString` sueltos para texto visible.
- **Entradas decimales**: `Input` con `type="text"` e `inputMode="decimal"`. Se interpretan con
  `leerDecimal` (acepta coma o punto) y se envían a la API con punto.

## Tokens de color nuevos (R-17)

`color/data/stage-1` a `stage-6`, como alias de primitivos existentes, que se repiten en ciclo
a partir de la etapa 7. Se registran en `docs/oica-redesign/DESIGN-SYSTEM.md` y en
`frontend/src/app/globals.css` (y en Tailwind, si los tokens se exponen allí). El texto de la
medida sobre cada color MUST cumplir un contraste AA; si no, la medida no se escribe dentro de
la pieza.

## Tipos (`file-detail/types.ts`)

```text
PatronResumen    sin cambios (no se añade `secuencia`)

PedidoPiezas     { pedido: string; piezas: number }
PiezaPatron      { etapa: number; longitud_m: number; cantidad: number; pedidos: PedidoPiezas[] }
RangoBarras      { desde: string; hasta: string; n: number }
PatronExplorable { patron_id: string; diametro: string; origen: string; longitud_m: number;
                   secuencia: string; repeticiones: number; aprovechamiento_pct: number;
                   perdida_corte_m: number; descartado_m: number; saldo_m: number;
                   etapas: number[]; piezas: PiezaPatron[];
                   barras: { total: number; rangos: RangoBarras[] } }
VistaPatrones    = { disponible: true; storage_uuid: string; version_number: number; motor: string;
                     escala_m: number; totales: { patrones: number; barras: number };
                     diametros: string[]; etapas: number[]; origenes: string[];
                     pedidos: PedidoPiezas[]; patrones: PatronExplorable[] }
                 | { disponible: false; storage_uuid: string; version_number: number;
                     motor: string | null; motivo: string }
```

## Lógica pura (testeable sin DOM)

`patterns/filtros.ts` contiene funciones puras para filtrar, ordenar, calcular la cobertura y
calcular el aporte de un pedido. Sus invariantes son las de data-model §8. El proyecto no tiene
un runner de pruebas del frontend, así que las invariantes se verifican en el backend (la misma
respuesta) y con `typecheck` y `build`. Si se añade un runner, requiere aprobación (dependencia
nueva).
