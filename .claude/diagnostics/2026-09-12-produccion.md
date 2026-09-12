# Revisión de preparación para producción — 2026-09-12

## Decisiones explícitas del usuario

Unificar repositorios; app pública sin login; VPS compartida Linux 6 CPU/12 GB, pero 80/443 libres; dominio oica.cris-munoz.me; primera base vacía; desarrollo nativo Linux/WSL con un script; despliegues interrumpen trabajos activos; reset manual con respaldo configurable.

## Hallazgos y tratamiento

- Copias `services/` contenían correcciones sin commit. Se copiaron a `backend/` y `frontend/`, sin borrar originales; se retiraron únicamente los gitlinks del índice.
- Se incorporaron por fast-forward dos commits remotos ya presentes en origin/main (documentación), sin crear commits. Rama local renombrada a production. El cambio remoto/push está pendiente.
- URL de túnel, puertos de datos expuestos y código montado: sustituidos por Nginx, rutas relativas, imágenes con código y redes internas.
- SQL inicial tenía ON CONFLICT sin UNIQUE: corregido; no se inventa una restricción que impida reprocesar archivos.
- Test existente del motor esperaba rechazo de cartilla vacía; fallaba. Se añadió ValueError antes de inicializar el AG. No cambia cartillas válidas.
- Next.js y dependencias transitivas: actualizados a 15.5.25 y parches compatibles; npm audit reportó 0 vulnerabilidades tras los overrides de PostCSS/brace-expansion.
- La página histórica /resultados usaba un endpoint POST eliminado. Ahora redirige a /archivos, donde las descargas versionadas funcionan.
- Backend/worker conservan dependencia y funcionamiento gevent/eventlet según los entornos anteriores; worker utiliza prefork con concurrencia 1 para trabajo de CPU.

## Riesgos y pendientes reales

- Sin autenticación por decisión del usuario: cualquier visitante puede leer/borrar archivos compartidos. Rate limits y límites de recursos no reemplazan permisos por usuario.
- Actualización inmediata implica pérdida del trabajo en curso; se conserva el original y se marca error para reprocesar. No hay reanudación automática.
- Backups están en la misma VPS; no protegen ante pérdida del disco/servidor. Se documenta copia externa.
- VPS aún no inspeccionada ni desplegada: faltan SSH/secretos GitHub, comprobar arquitectura x86_64, distribución, espacio y puertos.
- No se ha emitido un certificado real en esta sesión; el bootstrap requiere correo del administrador y DNS correcto.
- BUG-002 y BUG-006 permanecen; la decisión académica INF-008 no cambia.
- El entorno local usa Node 24 por defecto y no tiene Python 3.12 nativo en PATH. Builds verificados dentro de Docker con Node 22/Python 3.12; la instalación nativa completa requiere esos prerequisitos.


## Reanudación después de e2fsck

El usuario reportó un fallo crítico de WSL y reparación del filesystem. No se determinó su causa. Se verificó C: al 99 %, con 6 GB libres, frente a 920 GB virtuales en WSL. Docker reportó 10,75 GB de imágenes y 4,62 GB de caché; no se eliminó nada. Los logs temporales anteriores de /tmp ya no estaban disponibles.

Se suspendieron builds/instalaciones. Se corrigió mantenimiento tras error de reset y se eliminó el segundo build redundante del pipeline. Diez pruebas de scripts, TypeScript/ESLint sin caché y actionlint pasaron. La consulta de dos resultados almacenados confirmó demanda, diámetros, longitud y archivos intactos. No se volvió a ejecutar una prueba destructiva real.

Pendiente: build final (estimado 1–3 GB de almacenamiento transitorio adicional, dependiente de caché), recuperación real en entorno desechable y VPS. Requiere resolver margen físico o usar GitHub; no ejecutar limpiezas ni mounts ni cambios de permisos globales sin autorización.

Los 58 tests del motor se repitieron tras la reparación, usando la imagen existente y la corrección en memoria: OK. Se preparó test_operations_ci.sh para ensayar operaciones reales en GitHub; no se ejecutó localmente.
