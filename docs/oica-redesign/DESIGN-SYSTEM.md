# OICA Design System v1

Estado: **dirección aprobada; alcance v1 fijado; creación en Figma bloqueada
temporalmente por cuota MCP**.

Dirección: B — Industrial Clarity, con numerales monoespaciados y geometría
precisa heredados de A.

## Arquitectura

1. Primitivos de color.
2. Tokens semánticos con alias a primitivos.
3. Spacing, sizing, radius y motion.
4. Estilos de tipografía y elevación.
5. Componentes base.
6. Compuestos y patrones de producto.
7. Pantallas.

Los componentes no dependen directamente de colores primitivos. El alcance de
componentes se mantiene en `COMPONENT-MAP.md`.

## Foundations v1

### Color primitives

Los nombres de primitivos describen valor, no uso. Se ocultan de los selectores
de propiedades en Figma (`scopes: []`).

| Familia | Escala v1 |
|---|---|
| Neutral cálido | `white #FFFFFF`, `50 #FAFAF7`, `100 #F3F2ED`, `200 #E3E1DA`, `300 #CDCAC1`, `500 #747A80`, `600 #596168`, `700 #424A52`, `900 #20272E`, `950 #151A1F` |
| Cobalto | `50 #EEF5FF`, `100 #DCEAFE`, `300 #8DB4EF`, `600 #2D63B8`, `700 #234F95`, `800 #193A70` |
| Teal | `50 #EAF8F5`, `100 #D2EEE8`, `600 #117765`, `700 #0C5F52` |
| Ámbar | `50 #FFF7E6`, `200 #F4D18A`, `700 #8A4B08` |
| Rojo | `50 #FFF0F0`, `200 #F2B8B8`, `700 #A12A2A` |

### Semantic colors

Todos son alias a primitivos. La sintaxis web usa el nombre CSS exacto indicado.

| Grupo | Tokens |
|---|---|
| Background | `color/background/default`, `elevated`, `subtle`, `interactive`, `inverse` |
| Text | `color/text/default`, `muted`, `subtle`, `inverse`, `brand`, `success`, `warning`, `error` |
| Border | `color/border/default`, `strong`, `focus`, `success`, `warning`, `error` |
| Action | `color/action/primary`, `primary-hover`, `primary-active`, `primary-text`, `secondary`, `secondary-hover`, `danger`, `danger-hover` |
| Status | `color/status/success-background`, `warning-background`, `error-background`, `info-background` y sus pares `*-text`/`*-border` |
| Data | `color/data/primary`, `efficient`, `warning`, `grid`, `remaining-material`, `stage-1` … `stage-6` |

Etapas de ejecución (spec 002, explorador de patrones): `color/data/stage-1` … `stage-6` son
categóricas y se repiten en ciclo desde la etapa 7. Alias: 1 cobalto 600, 2 ámbar 700, 3 teal
600, 4 neutral 700, 5 ámbar 200 y 6 neutral 300. Llevan texto blanco en 1–4 (5,45–9,0:1) y
`color/text/default` en 5–6 (10,3 y 9,21:1). No se usan cobalto 300 (saldo reutilizable) ni rojo
(descarte), para que las etapas no se confundan con esos tramos. El color nunca es el único canal:
la etapa se nombra «E1», «E2»… en la leyenda, en el nombre accesible y en el detalle.

Pares de contraste base validados: texto default/background 14.44:1; texto
muted/background 6.02:1; blanco/acción primaria 5.85:1; success text/background
6.94:1; warning 6.37:1; error 6.59:1.

Regla: `color/text/subtle` (neutral-500) solo se usa en placeholders y estados
deshabilitados. Sobre `background/subtle` baja a ~3,9:1 y no cumple AA para
texto informativo; para texto secundario se usa `color/text/muted`.

### Typography

- UI y contenido: Geist; fallback `Inter, ui-sans-serif, system-ui, sans-serif`.
- Datos, métricas, medidas, IDs y fragmentos técnicos: Geist Mono; fallback
  `ui-monospace, SFMono-Regular, Consolas, monospace`.
- Estilos: `display/lg` 40/48/650, `heading/xl` 32/40/650, `heading/lg`
  24/32/650, `heading/md` 20/28/600, `body/lg` 18/28/400, `body/md`
  16/24/400, `body/sm` 14/20/400, `label/md` 14/20/600, `label/sm`
  12/16/600 y `metric/md` 20/24/600 mono.
- No usar mayúsculas sostenidas para navegación o párrafos. Se reservan para
  microetiquetas técnicas de hasta tres palabras con tracking positivo.

### Formato numérico

Estándar único de la app (spec 002, enmienda 2: FR-032 a FR-035; research R-20). Aplica a todo
lo que lee el usuario: pantallas, PDF, imagen, textos legibles del Excel y mensajes.

- **Separadores** (enmienda 3, como la plantilla USCO de la tesis): punto decimal y sin separador
  de miles, con un espacio entre la cifra y la unidad, también en el porcentaje: «8.86 %»,
  «152039.57 kg», «13955 barras». Las diferencias llevan signo explícito: «+1.264 pp».
- **Decimales por tipo de cifra**:
  - porcentajes: 2;
  - cota y brecha: 3;
  - pp frente al umbral: 2;
  - kg: 2;
  - kg/m: 3;
  - m y mm: hasta 3, sin ceros finales;
  - segundos medidos: 1;
  - rangos estimados: enteros;
  - conteos: enteros sin separador de miles.
- **Ayudantes**:
  - Frontend: `decimal`, `entero`, `pct`, `pp`, `kg` y `leerDecimal` en
    `components/file-detail/types.ts`; `numero` y `metros` en
    `components/file-detail/patterns/filtros.ts`; `DecimalInput` en `components/ui/`.
  - Backend: `cutting/formato.py`.
- **Entradas**: los campos decimales aceptan coma o punto, conservan lo escrito y viajan a la API
  con punto.
- **Datos para máquinas**: API, JSON, celdas numéricas del Excel e inventario conservan números
  nativos.

### Dimensions

- Spacing: `0, 1=4, 2=8, 3=12, 4=16, 5=20, 6=24, 8=32, 10=40,
  12=48, 16=64` px.
- Radius: `none=0`, `sm=4`, `md=8`, `lg=12`, `xl=16`, `full=999` px.
- Control: `sm=32`, `md=40`, `lg=48` px.
- Icon: `sm=16`, `md=20`, `lg=24` px.
- Border: `default=1`, `strong=2` px.
- Contenido: `content/narrow=768`, `content/default=1120`,
  `content/wide=1280` px.

### Elevation and motion

- `elevation/raised`: `0 1px 2px rgba(21,26,31,.08)`.
- `elevation/overlay`: `0 12px 32px rgba(21,26,31,.16)`.
- Motion: `fast=100`, `standard=160`, `slow=240` ms; easing estándar
  `cubic-bezier(.2,0,0,1)`. Respetar `prefers-reduced-motion`.

### Responsive

- Mobile: `<640 px`; tablet: `640–1023 px`; desktop: `1024–1439 px`;
  wide: `≥1440 px`.
- Son reglas de comportamiento, no variables de estilo: navegación colapsa,
  formularios se apilan, tablas se transforman en tarjetas y diagramas admiten
  scroll/zoom controlado.

## Alcance de componentes v1

El alcance exacto y sus variantes está en `COMPONENT-MAP.md`. Los componentes se
construyen en dependencia ascendente: iconografía → controles → feedback →
contenedores → navegación/datos → patrones de producto.

No se incluye un tema oscuro, date picker, avatar, breadcrumb, menú contextual ni
editor genérico: OICA no los usa.

## Sincronización Figma ↔ código

- Los nombres CSS serán la sintaxis web de las variables de Figma.
- Figma conservará variables semánticas y estados visuales.
- Código conservará la implementación, accesibilidad y comportamiento.
- Una primitive nueva deberá añadirse en ambos lados y documentarse antes de
  usarse en componentes.
- El ledger de IDs de Figma vive en `FIGMA-STATE.json`; los IDs nunca se
  reconstruyen ni se adivinan.
