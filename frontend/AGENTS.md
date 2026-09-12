# Frontend OICA

Leer primero `../AGENTS.md`. Este directorio es fuente versionada del monorepo; no editar `../services/frontend/`.

- Next.js 15, React 19, Node **22**. Tres espacios de indentación.
- `npm run dev`, `npm run typecheck`, `npm run lint`, `npm run build`.
- Compilación standalone; TypeScript y ESLint bloquean errores.
- HTTP usa `src/lib/api.ts` (`/api`); Socket.IO usa el origen del navegador y `/socket.io/`. No hardcodear dominios, puertos ni URLs de túneles.
- Mantener las directivas `use client` antes de los imports.
- Interfaz española, perfiles `rapido`, `balanceado`, `profundo`.
- `/resultados` redirige a `/archivos`: las descargas utilizan el UUID de cada versión, no localStorage.
- Las versiones forzadas de PostCSS/brace-expansion corrigen avisos de seguridad en dependencias transitivas; revisar `npm audit` al actualizarlas.
