# Auditoría UI AS-IS

> Fecha: 2026-09-29. Fuente funcional: frontend local y API local. Producción se usó como contraste visual.

## Stack y estructura

- Next.js 15.5.25, React 19 y TypeScript.
- Tailwind CSS 3.4.1; no hay librería de componentes completa.
- CVA, Radix Slot, `clsx` y `tailwind-merge` solo sostienen el componente `Button`.
- Lucide React para iconos.
- Geist y Geist Mono se cargan, pero `globals.css` fuerza Arial en `body`; la tipografía efectiva no coincide con la intención del layout.
- Solo existen `--background` y `--foreground`. No hay tokens semánticos de acción, estado, borde, spacing, radius o elevación.
- Existe una media query oscura global, pero múltiples `bg-white` y colores Tailwind hardcoded impiden un tema coherente.

## Rutas reales

| Ruta | Propósito | Estados relevantes |
|---|---|---|
| `/` | Inicio/entrada | imagen remota, CTAs |
| `/subir-cartilla` | Configuración y carga | vacío, archivo seleccionado, estimación, procesamiento, progreso, WebSocket degradado, éxito, error |
| `/archivos` | Proyectos/resultados | loading, error, vacío, tabla, filtros, progreso, paginación, descargas |
| `/tutorial` | Guía, glosario y FAQ | contenido largo |
| `/contact-us` | Equipo y formulario externo | formulario normal/validación nativa |
| `/resultados` | Compatibilidad legacy | redirección a `/archivos` |

## Hallazgos críticos y altos

1. **Navegación móvil no adaptada.** La barra mantiene todos los destinos horizontalmente; varios quedan fuera del viewport sin control de expansión.
2. **Resultados móviles incompletos.** La tabla se recorta dentro de `overflow-x-auto`; en la captura solo se ve la primera columna y no existe indicación de desplazamiento o alternativa por tarjetas.
3. **Accesibilidad de formularios.** axe-core detecta controles sin nombre accesible en carga y archivos. En contacto se depende de placeholders en vez de labels persistentes.
4. **Identidad y semántica global incorrectas.** Todas las páginas anuncian `Create Next App`, usan `lang="en"` y el logo es un enlace sin nombre discernible.
5. **Contraste.** Todas las rutas registran fallos serios de contraste; los textos grises del archivo seleccionado y algunos acentos/estados son especialmente débiles.
6. **Asset roto.** La imagen remota de la landing devuelve 400 y aparece el icono de imagen rota.

## Hallazgos medios

- La landing mezcla español e inglés en el nombre principal y usa un corazón como marca sin relación con optimización/corte.
- Radios de 4, 6, 8, 12 y 16+ px, sombras y colores aparecen sin escala compartida.
- Verde, azul, índigo, ámbar, rosa, rojo y gradientes compiten sin semántica consistente.
- `Button` declara tokens de estilo tipo shadcn (`primary`, `ring`, `destructive`) que no están definidos en Tailwind; cada pantalla lo sobreescribe con clases ad hoc.
- Carga concentra demasiadas decisiones en una columna larga y mezcla controles nativos sin normalización visual.
- El catálogo expandido contiene una tabla editable de 33 filas sin estrategia móvil.
- Los resultados usan `prompt`, `alert` y `confirm`; son visualmente ajenos al producto y limitan accesibilidad/control.
- Loading, vacío y error son texto centrado sin estructura ni acciones de recuperación.
- Tutorial no tiene `h1`; usa gradientes y colores de iconos sin sistema.
- Fechas se muestran con formato de locale no fijado (`9/13/2026`) en una interfaz española.
- Hay logs de consola de navegación y procesamiento en código cliente.

## Jerarquía y densidad

- La landing tiene mucho espacio sin información y una promesa genérica; no comunica de inmediato el flujo técnico.
- `subir-cartilla` tiene buena secuencia funcional, pero la jerarquía se diluye entre textos explicativos, fieldsets y controles nativos.
- `archivos` funciona en desktop, aunque las acciones exceden el ancho y se recortan incluso en 1440 px.
- Tutorial es legible en desktop, pero demasiado largo y denso en móvil; necesita navegación interna o disclosure progresivo.

## Responsive AS-IS

- Desktop: usable, con recortes en acciones de la tabla.
- Tablet: layouts se contraen, pero navegación y tablas carecen de comportamiento específico.
- Mobile: contenido principal apila correctamente en varias vistas; navegación, tablas, catálogo y acciones no están resueltos.

## Baseline visual

Las capturas están en [`baseline/`](./baseline/):

- Inicio: desktop/mobile.
- Carga: desktop/tablet/mobile.
- Archivos: loading y cargado, desktop/tablet/mobile.
- Tutorial: desktop/tablet/mobile.
- Contacto: desktop/mobile.
- Producción: inicio y archivos desktop.

## Auditoría automatizada

Comando reproducible: `scripts/audit-ui-baseline.cjs` con Playwright y axe-core.

- Todas las rutas: `color-contrast`, `link-name`, metadata genérica y `lang="en"`.
- Carga: `label` y `select-name` críticos.
- Archivos: dos inputs y dos selects reportados por axe; cinco controles detectados sin asociación programática.
- Tutorial: sin `h1`.
- Contacto: nombre, correo y mensaje sin label programático persistente.

