# Análisis del Servicio Frontend — OICA

Documento de referencia con el análisis exhaustivo del frontend Next.js.
Generado para reutilización futura en documentación académica, agentes de IA, o desarrollo.

---

## 1. Estructura de Directorios

```
services/frontend/
├── .prettierrc                     # Prettier: 3 espacios, comillas simples
├── .vscode/settings.json           # VS Code: tabSize=3, Prettier como formatter
├── eslint.config.mjs               # ESLint 9 flat config (next/core-web-vitals + TS)
├── next.config.ts                  # ignoreDuringBuilds: ESLint + TypeScript
├── tsconfig.json                   # strict, baseUrl="src", alias @/* → src/*
├── tailwind.config.ts              # Solo 2 colores custom: background, foreground
├── postcss.config.mjs              # Solo plugin tailwindcss
├── package.json                    # next@15.1.4, react@19, socket.io-client@4.8.1
├── public/
│   ├── Plantilla_Cartilla.xlsx     # Plantilla descargable para usuarios
│   └── *.svg                       # Iconos default de create-next-app (sin usar)
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout (Server Component)
│   │   ├── globals.css             # Tailwind + CSS variables
│   │   ├── page.tsx                # / — Landing page
│   │   ├── subir-cartilla/page.tsx # /subir-cartilla — Carga de archivos
│   │   ├── archivos/page.tsx       # /archivos — Tabla de archivos procesados
│   │   ├── resultados/page.tsx     # /resultados — Descarga PDF (semi-legacy)
│   │   ├── tutorial/page.tsx       # /tutorial — Guía rápida
│   │   └── contact-us/page.tsx     # /contact-us — Contacto + formulario
│   ├── components/
│   │   ├── navbar.tsx              # Barra de navegación fija
│   │   ├── file-upload.tsx         # Componente de carga + progreso WebSocket
│   │   ├── FilesTable.tsx          # Tabla con filtros, paginación, descargas
│   │   ├── Resultados.js           # DEAD CODE — legacy, no importado
│   │   ├── tutorial/
│   │   │   └── TutorialGuide.tsx   # Guía paso a paso + glosario + FAQ
│   │   └── ui/
│   │       ├── button.tsx          # Componente Button (patrón shadcn/ui + CVA)
│   │       └── nav-button.tsx      # Botón de navegación con estado activo
│   └── lib/
│       ├── socket.ts               # Cliente Socket.IO singleton
│       ├── utils.ts                # Utilidad cn() (clsx + tailwind-merge)
│       ├── constants/services.tsx  # DEAD CODE — URLs de AWS Lambda
│       └── services/lambda.tsx     # DEAD CODE — Cliente AWS Lambda
```

---

## 2. Dependencias (package.json)

**Nombre:** `frontend` | **Versión:** `0.1.0` | **Private:** `true`

### Scripts

| Script | Comando | Descripción |
|--------|---------|-------------|
| `dev` | `next dev --turbopack` | Desarrollo con Turbopack |
| `build` | `next build` | Build de producción |
| `start` | `next start` | Servidor de producción (puerto 3000) |
| `lint` | `next lint` | ESLint |

### Dependencias de producción

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `next` | `15.1.4` | Framework |
| `react` / `react-dom` | `^19.0.0` | UI |
| `socket.io-client` | `^4.8.1` | WebSocket en tiempo real |
| `react-dropzone` | `^14.3.5` | Drag-and-drop de archivos |
| `lucide-react` | `^0.471.2` | Iconos SVG |
| `class-variance-authority` | `^0.7.1` | Variantes de componentes (shadcn) |
| `clsx` | `^2.1.1` | Clases condicionales |
| `tailwind-merge` | `^2.6.0` | Resolver conflictos Tailwind |
| `@radix-ui/react-slot` | `^1.1.1` | Composición con `asChild` en Button |

### Dependencias de desarrollo

| Paquete | Versión |
|---------|---------|
| `typescript` | `^5` |
| `tailwindcss` | `^3.4.1` |
| `eslint` | `^9` |
| `eslint-config-next` | `15.1.4` |
| `postcss` | `^8` |
| `@types/react` / `@types/react-dom` | `^19` |
| `@types/node` | `^20` |

---

## 3. Configuraciones

### next.config.ts

```ts
eslint: { ignoreDuringBuilds: true }
typescript: { ignoreBuildErrors: true }
```

**Implicación:** El build SIEMPRE tiene éxito, incluso con errores de tipo o lint.

### tsconfig.json

- `strict: true`, `target: ES2017`, `module: esnext`, `moduleResolution: bundler`
- `baseUrl: "src"` — imports absolutos desde `src/`
- `paths: { "@/*": ["src/*"] }` — alias para imports
- Plugin `next` para TypeScript

### tailwind.config.ts

Solo extiende 2 colores vía CSS variables: `background` y `foreground`. No hay customización de breakpoints, spacing, ni fonts.

### .prettierrc

```json
{ "tabWidth": 3, "useTabs": false, "semi": true, "singleQuote": true,
  "trailingComma": "es5", "bracketSpacing": true, "arrowParens": "avoid" }
```

### eslint.config.mjs

Flat config con `FlatCompat` para extender `next/core-web-vitals` y `next/typescript`.

---

## 4. Páginas (App Router)

### Layout raíz (`src/app/layout.tsx`) — Server Component

- Fuentes: **Geist** (sans) y **Geist Mono** vía `next/font/google`, asignadas a CSS variables
- Metadata: `"Create Next App"` (no personalizado)
- HTML: `lang="en"` (debería ser `"es"`)
- Body: `antialiased bg-white` + variables de fuente
- Renderiza `<Navbar />` fuera del `<main>`
- `<main className='mt-16'>` compensa el navbar fijo (h-16 = 64px)

### `/` — Landing page (Client Component)

- Hero de pantalla completa con imagen de fondo de Unsplash (barras de acero, `opacity-20`)
- Gradiente: `bg-gradient-to-br from-green-100 via-white to-green-200`
- Título: "Bienvenido a OICA Steel Cutting Optimizer"
- 2 CTAs: "Contactanos" → `/contact-us`, "Probar Optimizador" → `/subir-cartilla`
- Usa `<a href>` en vez de `<Link>` de Next.js (no prefetch)

### `/subir-cartilla` — Carga de archivos (Server Component wrapper)

Contenedor mínimo que renderiza `<FileUpload />`.

### `/archivos` — Archivos procesados (Server Component wrapper)

- Encabezado "Archivos Procesados"
- Renderiza `<FilesTable apiUrl={NEXT_PUBLIC_API_URL || 'http://localhost:5000'} />`

### `/resultados` — Descarga PDF (Client Component, semi-legacy)

- Lee `document_number` de query params y datos de `localStorage`
- POST a `http://localhost:5000/descargar-pdf` (**URL HARDCODEADA**)
- Descarga blob como PDF
- Envuelto en `<Suspense>` por uso de `useSearchParams()`

### `/tutorial` — Guía rápida (Server Component wrapper)

Renderiza `<TutorialGuide />`. Usa import relativo en vez del alias `@/`.

### `/contact-us` — Contacto (Client Component)

- 2 contactos: Lizeth Gasca y Cristian Muñoz (Neiva, Huila)
- Formulario HTML nativo con `action="https://formspree.io/f/xgvlrnje"` y `method="POST"`
- Sin manejo de estado del formulario

---

## 5. Componentes

### `navbar.tsx` — Navbar (Client Component)

- `usePathname()` para determinar ruta activa
- `console.log("PATHNAME:", pathname)` — **log de depuración en producción**
- Icono `<Heart>` verde como logo, navbar fijo `fixed top-0 w-full z-10 h-16 bg-gray-100`
- 5 NavButtons: INICIO, SUBIR CARTILLA, ARCHIVOS, GUÍA RÁPIDA, CONTACTANOS
- Código comentado: dropdowns de "CONVERTIR PDF" y botones "Acceder"/"Registro"

### `file-upload.tsx` — FileUpload (Client Component)

**Estado local (10 variables useState):**

| Estado | Tipo | Default | Propósito |
|--------|------|---------|-----------|
| `files` | `File[]` | `[]` | Archivos seleccionados |
| `loadingSendButton` | `boolean` | `false` | Indicador de procesamiento |
| `backendError` | `string \| null` | `null` | Error del backend |
| `perfil` | `string` | `'balanceado'` | Perfil de optimización |
| `taskId` | `string \| null` | `null` | ID de tarea Celery |
| `progress` | `number` | `0` | Progreso (0-100) |
| `statusMessage` | `string` | `''` | Mensaje descriptivo |
| `processingState` | `string` | `''` | Estado técnico |
| `isConnected` | `boolean` | `true` | Conectividad WebSocket |
| `isPulsing` | `boolean` | `false` | Efecto visual pulsante |

**Refs:** `lastUpdateTime` (timestamp), `pollingInterval` (intervalo HTTP)

**Flujo de datos:**
1. Usuario arrastra/selecciona archivo (.xlsx o .csv, máximo 1)
2. Selecciona perfil: rápido / balanceado / profundo
3. Click "Enviar" → POST `${NEXT_PUBLIC_API_URL}/upload` con FormData
4. Recibe `task_id` → suscripción WebSocket vía `subscribeToTask()`
5. Actualizaciones en tiempo real vía `handleTaskUpdate`:
   - Si completado: redirige a `/archivos` después de 2s
   - Si error: muestra mensaje y desactiva loading
6. **Fallback polling HTTP:** si no hay update WebSocket por 30s, GET `/status/${taskId}` cada 2s

**Mapeo de estados a mensajes (getStateLabel):**

| Estado técnico | Mensaje |
|----------------|---------|
| `uploaded` | Archivo cargado |
| `validating` | Validando contenido |
| `validated` | Validación completada |
| `processing` | Procesando con algoritmo genético |
| `generating_artifacts` | Generando archivos de resultados |
| `completed` | Procesamiento completado! |
| `error_validation` | Error en validación |
| `error_processing` | Error en procesamiento |
| `error_generation` | Error generando archivos |

### `FilesTable.tsx` — FilesTable (Client Component)

**Props:** `apiUrl?: string` (default: `'http://localhost:5000'`)

**Interfaces TypeScript:**

```ts
interface ProcessingResult {
   version_number: number;
   storage_uuid: string;
   status: string;
   excel_path?: string;
   pdf_path?: string;
   image_path?: string;
   created_at: string;
}

interface UploadedFile {
   id: number;
   filename: string;
   document_number: string;
   perfil: string;
   status: string;
   created_at: string;
   updated_at: string;
   processing_results?: ProcessingResult[];
   current_progress?: number;
   current_state?: string;
   current_message?: string;
}
```

**Funcionalidad:**
1. **Carga:** GET `/files?page=&per_page=&search=&status=&perfil=&date_from=&date_to=`
2. **4 filtros:** búsqueda textual, estado, perfil, rango de fechas + botón "Limpiar Filtros"
3. **WebSocket en tiempo real:** suscripción a archivos en procesamiento, barra de progreso
4. **3 tipos de descarga** por archivo completado: Excel, PDF, Imagen (vía `window.open`)
5. **Eliminar:** DELETE `/file/${fileId}` con `confirm()`
6. **Reprocesar:** `prompt()` para nuevo perfil → POST `/reprocess/${fileId}`
7. **Paginación:** 20 por página, botones Anterior/Siguiente

**Columnas de la tabla:** Archivo, Documento, Perfil (badge), Estado (badge + barra de progreso), Fecha, Acciones (descargas + reprocesar + eliminar)

**Constantes de mapeo:**
```ts
STATUS_LABELS: { uploaded: 'Cargado', validating: 'Validando', ... }
STATUS_COLORS: { uploaded: 'bg-blue-100 text-blue-800', completed: 'bg-green-500 text-white', ... }
```

### `Resultados.js` — DEAD CODE

JavaScript puro (no TypeScript). No importado. Lógica legacy: POST a `http://localhost:5000/descargar-pdf`, descarga blob. Supersedido por `resultados/page.tsx`.

### `tutorial/TutorialGuide.tsx` — TutorialGuide (Client Component)

- Layout de 2 columnas: guía paso a paso (izquierda) + glosario/FAQ (derecha)
- **5 pasos:** Ir a inicio → Subir cartilla → Esperar procesamiento → Consultar guía → Contactar soporte
- **11 términos de glosario:** Barras de acero, Diámetro, Peso, Patrón de corte, Método Búfalo/rápido/balanceado/intensivo, Cartilla, N° de orden, Elemento
- **2 FAQs:** Tipos de archivos aceptados (solo XLSX), Tiempo de procesamiento
- Link a descarga de plantilla `/Plantilla_Cartilla.xlsx`
- Gradientes CSS como color de texto, efecto hover scale en cards

### `ui/button.tsx` — Button (patrón shadcn/ui)

Componente con CVA. `React.forwardRef`. Props: `asChild`, `loading`, `loader`.

**Variantes de estilo:** default, destructive, outline, secondary, ghost, link
**Variantes de tamaño:** default (h-10), sm (h-9), lg (h-11), icon (h-10 w-10)

**Nota:** Las CSS variables referenciadas (`--primary`, `--destructive`, etc.) NO están definidas en `globals.css`. Solo `--background` y `--foreground` existen.

### `ui/nav-button.tsx` — NavButton

Props: `content`, `to`, `status: 'all' | 'active' | 'inactive'`
Renderiza `<Link>` de Next.js. Estado `active` → `text-green-600 font-medium`.

---

## 6. Librería (src/lib/)

### `socket.ts` — Cliente Socket.IO (Singleton)

**Variables de módulo:**
- `socket: Socket | null`
- `taskCallbacks: Map<string, (data: any) => void>`
- `connectionStatusCallbacks: Set<(connected: boolean) => void>`
- `isConnected: boolean`
- `SOCKET_URL` — de `NEXT_PUBLIC_API_URL` o fallback `http://localhost:5000`

**Funciones exportadas:**

| Función | Firma | Descripción |
|---------|-------|-------------|
| `initializeSocket()` | `() → Socket` | Inicializa conexión si no existe |
| `subscribeToTask()` | `(taskId, callback) → void` | Guarda callback + emite `subscribe_task` |
| `unsubscribeFromTask()` | `(taskId) → void` | Elimina callback (NO emite unsubscribe) |
| `disconnectSocket()` | `() → void` | Cierra conexión y limpia todo |
| `onConnectionStatusChange()` | `(callback) → () => void` | Listener de conexión, retorna cleanup |
| `getConnectionStatus()` | `() → boolean` | Estado actual |

**Configuración:**
```ts
{ transports: ['websocket', 'polling'], reconnection: true,
  reconnectionAttempts: 5, reconnectionDelay: 1000 }
```

**Eventos:** `connect`, `disconnect`, `connected`, `task_update`, `connect_error`

**Interfaz TaskUpdate:**
```ts
interface TaskUpdate {
   task_id: string;
   state: 'uploaded' | 'validating' | 'validated' | 'processing' |
          'generating_artifacts' | 'completed' | 'SUCCESS' | 'FAILURE' |
          'VALIDATING' | 'VALIDATED' | 'PROCESSING' | 'GENERATING' |
          'error_validation' | 'error_processing' | 'error_generation';
   progress: number;
   message?: string;
   error?: string;
   result?: { version_number: number; storage_uuid: string;
              excel_path: string; pdf_path: string; image_path: string; };
}
```

### `utils.ts` — Utilidad cn()

```ts
export function cn(...inputs: ClassValue[]) {
   return twMerge(clsx(inputs));
}
```

### `constants/services.tsx` — DEAD CODE

URLs legacy de AWS Lambda (`RPESIGNED` — typo de `PRESIGNED`) y S3 bucket. No importado.

### `services/lambda.tsx` — DEAD CODE

Función `PresignedURLManagerService` para S3 presigned URLs. No importado.

---

## 7. Estilos y Sistema de Diseño

### `globals.css`

```css
@tailwind base; @tailwind components; @tailwind utilities;
:root { --background: #ffffff; --foreground: #171717; }
@media (prefers-color-scheme: dark) {
   :root { --background: #0a0a0a; --foreground: #ededed; }
}
body { color: var(--foreground); background: var(--background);
       font-family: Arial, Helvetica, sans-serif; }
```

**Observaciones:**
- Dark mode declarado en CSS pero **no funcional** (`bg-white` en layout + colores hardcodeados)
- `font-family: Arial` **sobreescribe** las fuentes Geist cargadas en layout.tsx
- Variables faltantes para shadcn/ui: `--primary`, `--secondary`, `--destructive`, `--accent`, etc.

### Paleta de colores (uso en componentes)

| Color | Uso |
|-------|-----|
| Green-500/600/700/900 | CTAs, botones envío, badges completado, logo Heart |
| Blue-600/800 | Botón "Enviar", barras de progreso, badge "Cargado" |
| Gray-50/100/200/300/500/600/700/900 | Fondos, bordes, texto secundario, navbar |
| Red-600 | Errores, badges de error |
| Yellow-100/800 | Badge "Validando" |
| Purple-100/800 | Badge "Procesando" |
| Indigo-100/800 | Badge "Generando" |
| Orange-600 | Advertencia WebSocket desconectado |

### Iconos

Lucide React: Heart, Upload, CheckCircle, AlertCircle, WifiOff, Download, Trash2, RefreshCw, Search, Filter, Home, Loader2, BookOpen, Mail

---

## 8. Endpoints del Backend Consumidos

| Método | Endpoint | Usado en |
|--------|----------|----------|
| POST | `/upload` | FileUpload |
| GET | `/status/${taskId}` | FileUpload (polling fallback) |
| GET | `/files?page=&per_page=&search=&status=&perfil=&date_from=&date_to=` | FilesTable |
| DELETE | `/file/${fileId}` | FilesTable |
| POST | `/reprocess/${fileId}` | FilesTable |
| GET | `/descargar-excel/${uuid}` | FilesTable |
| GET | `/descargar-pdf/${uuid}` | FilesTable |
| GET | `/descargar-imagen/${uuid}` | FilesTable |
| POST | `/descargar-pdf` (body JSON) | Resultados (legacy, hardcodeado) |

---

## 9. Patrones de Código

### Manejo de Estado

- **No hay estado global.** Todo con `useState`/`useEffect`/`useRef`
- **Inter-página:** `localStorage` en `/resultados` (frágil, semi-legacy)
- **No hay custom hooks**, no hay context providers
- Props drilling mínimo (solo `apiUrl` en FilesTable)

### Data Fetching

- `fetch` nativo. No SWR, no React Query, no wrapper
- No hay interceptors, no retry logic (excepto polling fallback)

### Error Handling

- Try/catch en operaciones async
- Errores vía estado + UI (`AlertCircle`), `alert()` nativo, o `console.error`
- **No hay error boundary** de React
- **No hay logging centralizado**

### Comunicación en Tiempo Real

1. **Primaria:** Socket.IO singleton (`lib/socket.ts`)
2. **Fallback:** HTTP polling cada 2s si no hay update WebSocket por 30s
3. Polling se detiene automáticamente al recibir update WebSocket

---

## 10. Convenciones de Nombrado

| Elemento | Convención | Ejemplos |
|----------|------------|----------|
| Archivos de componentes | kebab-case o PascalCase (inconsistente) | `file-upload.tsx`, `FilesTable.tsx` |
| Componentes React | PascalCase | `FileUpload`, `FilesTable`, `Navbar` |
| Funciones | camelCase | `subscribeToTask`, `handleDownloadPDF` |
| Variables de estado | camelCase | `loadingSendButton`, `processingState` |
| Interfaces | PascalCase (prefijo I solo en NavButton) | `INavButtonProps`, `ButtonProps` |
| Constantes | UPPER_SNAKE_CASE | `STATUS_LABELS`, `SOCKET_URL` |
| Texto UI | Español | "Archivos Procesados", "Enviar" |
| Comentarios | Mezcla español/inglés | |
| Variables/funciones | Mezcla español/inglés | `perfil`, `handleSend`, `loadFiles` |

---

## 11. Indentación y Estilo

### Reglas formales (.prettierrc)

3 espacios, comillas simples, punto y coma, trailing commas ES5, sin paréntesis en arrows de 1 parámetro.

### Consistencia real

| Archivos que cumplen (3 espacios) | Archivos que NO cumplen (2 espacios) |
|-------------------------------------|--------------------------------------|
| layout.tsx, navbar.tsx, file-upload.tsx, button.tsx, nav-button.tsx | page.tsx (inicio), contact-us/page.tsx, archivos/page.tsx, resultados/page.tsx, FilesTable.tsx, TutorialGuide.tsx, socket.ts, globals.css |

~50% de archivos no cumple con la regla de 3 espacios.

### Otras inconsistencias

- Comillas: mezcla de simples y dobles
- Imports: mezcla de alias `@/` e imports relativos
- Exports: mezcla de `export default function`, `export function`, `export { X }`

---

## 12. Hallazgos Clave

1. **Dead code:** `Resultados.js`, `lib/constants/services.tsx`, `lib/services/lambda.tsx`
2. **URL hardcodeada:** `resultados/page.tsx` → `http://localhost:5000`
3. **Dark mode roto:** CSS variables existen pero `bg-white` y colores hardcodeados lo anulan
4. **CSS variables faltantes:** Button (shadcn) referencia `--primary`, `--destructive` etc. que no existen
5. **Fuentes Geist infrautilizadas:** `font-family: Arial` en body las sobreescribe
6. **console.log en producción:** `navbar.tsx` → `console.log("PATHNAME:", pathname)`
7. **Metadata no personalizada:** Título "Create Next App"
8. **HTML lang incorrecto:** `lang="en"` con UI en español
9. **Indentación inconsistente:** ~50% no cumple .prettierrc
10. **Sin tests, sin CI, sin error boundaries**
