# Mapa de componentes

## Inventario AS-IS

| Elemento actual | Clasificación | Destino propuesto |
|---|---|---|
| `Navbar` | REPLACE | `AppHeader` + navegación desktop + menú móvil accesible |
| `NavButton` | MERGE | Variante/estado de `NavItem` |
| `Button` | REFACTOR | API consistente `variant`, `size`, `loading`, `disabled`; tokens reales |
| Inputs/selects/textarea ad hoc | MERGE | `Field`, `Input`, `Select`, `Textarea` |
| Checkboxes nativos dispersos | MERGE | `CheckboxField` |
| Dropzone de `FileUpload` | REFACTOR | `FileUpload` con vacío, drag, archivo, error, disabled |
| `FileUpload` (flujo completo) | REFACTOR | patrón `OptimizationSetup` compuesto |
| `CuttingOptions` | REFACTOR | `CatalogEditor`, `InventoryUpload`, `OutputOptions` |
| `PhysicalOptions` | REFACTOR | `CuttingConditions` con grupos de campos consistentes |
| `TimingInfo` | REFACTOR | `EstimateSummary`/`ProcessingSummary` |
| Barras de progreso | MERGE | `Progress` común con label, valor y estado |
| Estados de error inline | MERGE | `Alert` + `FieldMessage` |
| Filtros de archivos | REFACTOR | `FilterPanel` responsive |
| `FilesTable` | REFACTOR | `ResultsTable` desktop + `ResultCardList` mobile |
| Badges de estado/perfil | MERGE | `Badge` semántico |
| Paginación | REFACTOR | `Pagination` responsive |
| `TutorialGuide` | REFACTOR | `GuideStep`, navegación interna y disclosure móvil |
| Tarjetas de contacto | REFACTOR | `ContactCard` sobre `Card` |
| Formulario contacto | REFACTOR | primitives de formulario + labels persistentes |
| `Resultados.js` | REMOVE | Legacy no usado; eliminar solo tras demostrar ausencia de imports/ruta |
| `/resultados` | KEEP | Redirección de compatibilidad |

## Componentes v1 necesarios

- Button, IconButton.
- Input, Textarea, Select, CheckboxField, FileUpload.
- Card, Badge, Alert, Tooltip.
- AppHeader, MobileNavigation, PageHeader.
- Progress, Spinner y Skeleton limitado a tablas/paneles.
- Table, responsive ResultCard, Pagination.
- Dialog de confirmación y Dialog de reprocesamiento. ✅ (`ui/dialog.tsx`)
- EmptyState, ErrorState, LoadingState.
- Disclosure/Accordion para catálogo, condiciones y guía.

## Alcance Figma v1 fijado

| Familia | API/variantes necesarias | Límite de alcance |
|---|---|---|
| Button | `style=primary/secondary/ghost`, `size=md/lg`, `state=default/hover/active/focus/disabled`; loading como propiedad | 30 variantes; peligro separado |
| DangerButton | `size=md/lg`, mismos cinco estados | 10 variantes |
| IconButton | `style=secondary/ghost/danger`, `size=sm/md/lg`, estados esenciales | Icono por `INSTANCE_SWAP`, no por variante |
| Form controls | Input, Select y Textarea; default/focus/disabled/error | Un tamaño principal; no duplicar Field |
| CheckboxField | unchecked/checked/indeterminate × default/focus/disabled/error cuando aplique | Label y helper como propiedades |
| FileUpload | empty/drag/selected/uploading/error/disabled | Componente compuesto específico |
| Feedback | Badge, Alert, Progress, Spinner, Skeleton, Tooltip | Tonos solo donde OICA los usa |
| Containers | Card y Disclosure | Sin variantes decorativas sin caso real |
| Navigation | AppHeader, NavItem, MobileNavigation, PageHeader | Desktop/mobile como composiciones |
| Results | Table primitives, ResultCard, Pagination, Empty/Error/LoadingState | Tabla desktop; tarjetas mobile |
| Overlays | Dialog base + confirmación/reprocesamiento | Sin Drawer hasta que exista caso real |

La matriz se mantiene deliberadamente acotada. `Button` y `DangerButton` se
separan en Figma para no superar 30 combinaciones; en código conservarán una API
única mediante `variant="destructive"`.

## Patrones de producto

- OptimizationSetup.
- CatalogEditor.
- CuttingConditions.
- ProcessingStatus.
- OptimizationSummary.
- ResultsExplorer.
- ResultDownloads.

No convertir en componente cada bloque de layout; los patrones usarán primitives y componentes compuestos.
