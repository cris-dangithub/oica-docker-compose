# Migración visual

Estado: en curso. Pasos 1–7 completados el 2026-09-29; siguiente: paso 8 (limpieza legacy).

## Orden incremental

1. ✅ Foundations/tokens en CSS y Tailwind.
2. ✅ Primitives de formulario, Button, Card, Badge, Alert y Progress.
3. ✅ Navegación responsive y shell de páginas.
4. ✅ `subir-cartilla` como primera pantalla representativa.
5. ✅ `archivos`, incluida adaptación móvil real.
6. ✅ Inicio, tutorial y contacto.
7. ✅ Sustitución de diálogos nativos de reproceso/eliminación.
8. Limpieza demostrable de CSS/componentes legacy.

## Reglas

- Mantener contratos HTTP, Socket.IO, estados y validaciones.
- No cambiar el significado de perfiles ni parámetros físicos.
- No alterar el flujo de descarga por UUID.
- Cambiar presentación responsive sin ocultar acciones funcionales.
- Cada migración debe pasar typecheck/lint y comparación visual antes de avanzar.


## Registro

### `/subir-cartilla` (2026-09-29)

- El catálogo pasó de `<table>` ancha a una lista con rejilla de 4 columnas
  (encabezados visibles en todos los tamaños). Página móvil: 10.934 → 5.852 px.
- Dropzone con el patrón accesible de react-dropzone: `noKeyboard`, contenedor
  como zona de clic/arrastre y `<button>` real que llama a `open()`. Evita el
  control anidado (`nested-interactive`).
- Inventario: input nativo oculto (`sr-only`) + label estilizado en español y
  nombre del archivo en `aria-live`. Sin cambios en `onInventory`.
- `text-subtle` quedó reservado para placeholders y deshabilitados (3,9:1 sobre
  `background-subtle`, no cumple AA para texto informativo); el texto
  informativo usa `text-muted`.
- `FileUpload` ya no renderiza `<main>`; el landmark vive en `layout.tsx` para
  todas las rutas.
- Sin cambios en requests, estados, WebSocket, polling ni redirección a `/archivos`.

### `/archivos` (2026-09-29)

- `FilesTable`: tabla en `lg+` y lista de tarjetas en mobile/tablet con la misma
  información y todas las acciones visibles. La fecha pasó a la línea
  secundaria del proyecto para que las acciones quepan en una fila desde 1440 px.
- `confirm/prompt/alert` sustituidos por `Dialog` (eliminar, reprocesar con
  `Select` de perfil) y avisos `Alert` descartables. Los endpoints, el cuerpo
  `{ perfil }` y las recargas posteriores no cambian. El perfil ya no se escribe
  a mano, así que desaparece el caso "perfil inválido".
- Filtros con `Field`/`Input`/`Select` y labels asociadas; badge de filtros activos.
- Estados vacío (con y sin filtros), carga y error con "Reintentar".
- Eliminar/Reprocesar se desactivan si el proyecto está activo (el backend responde
  409); los mensajes de error del backend se muestran en el diálogo.
- `FileUpload` traduce también los estados en mayúscula del worker
  (`PROCESSING`, `GENERATING`, `SUCCESS`, `FAILURE`); antes aparecían crudos.
- `Dialog` debe renderizarse fuera de contenedores `space-y-*`: sus márgenes
  anulan el `m-auto` del modal.

### Inicio, tutorial y contacto (2026-09-29)

- Inicio: se retiró la imagen de Unsplash (respondía 400) y el título mixto
  "OICA Steel Cutting Optimizer". El diagrama de barra es un ejemplo
  ilustrativo rotulado como tal; no hay cifras de desempeño inventadas.
- Tutorial: contenido corregido contra plantilla, UI y Cap. 3 (ver
  RIESGO-AC-007). Perfiles con los parámetros del Cap. 3.
- Contacto: mismo `action` de Formspree, `method` y nombres `nombre`/`correo`/`mensaje`.
- Las tres páginas son server components (sin `"use client"`), con `metadata`.

## Código legacy detectado (no eliminado)

- `frontend/src/components/ui/nav-button.tsx`: sin importaciones desde que
  `Navbar` se rediseñó. Candidato a eliminar en el paso 8 (limpieza legacy).
- `frontend/src/components/Resultados.js`: sin importaciones; contiene el último
  `alert()` nativo del frontend. Clasificado REMOVE en `COMPONENT-MAP.md`.
- `frontend/public/{next,vercel,file,globe,window}.svg`: assets de create-next-app sin
  referencias en `src/`.
