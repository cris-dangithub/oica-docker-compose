# Estado actual — 2026-09-13

## Bloque G: implementación y validación local completadas

El usuario autorizó implementar el plan y después reconstruir las imágenes con
un presupuesto estimado de 2–4 GB. La aplicación nueva está activa y saludable en
**http://localhost**, proyecto Compose `oica-validation`. `.env` local (ignorado por
Git, sin secretos añadidos) conserva ese nombre y puerto 80 para los comandos habituales.
El usuario autorizó publicar esta entrega en una rama nueva y abrir PR hacia
`production`, reemplazando la petición de push directo. No fusionar el PR ni
desplegar sin nueva instrucción. La VPS no se operó directamente en esta sesión.

### Contrato aprobado

Solo 001/002 como corpus académico; AG; etapas sucesivas con reutilización acumulada
por diámetro; catálogo editable e inventario XLSX/CSV; exportación compatible;
pérdida por corte cero, sin mínimo reutilizable; desperdicio final ponderado por
masa de barras utilizadas una sola vez. 1–5 minutos como objetivo, sin aborto.
Título y objetivos reformulados por autorización del autor, pendientes del director.

### Implementado

- `backend/cutting/`: normalización, validador independiente, AG con evaluación de
  saldos agrupados, trazabilidad por barra y reportes acotados.
- API/worker con instantáneas, tarea activa, reimportación de inventario y estimación.
- Frontend con catálogo, inventario, progreso y descargas.
- Migración 003 aplicada a PostgreSQL local. Los volúmenes y dos versiones previas
  del archivo histórico id 2 permanecen intactos.
- Capítulos 1–4 y `docs/CORTE_SECUENCIAL.md` contrastados con el piloto y el E2E local.

### Evidencia verificada

- Build de las tres imágenes exitoso, incluyendo compilación/tipos/lint de frontend.
- 74 pruebas backend pasan dentro de la imagen nueva; 10 de scripts pasaron antes.
- 34 ensayos de motor válidos; 002 rápido 1,38–1,51 s, balanceado 3,13–3,79 s,
  profundo 5,65–9,15 s. Son tiempos de motor, no de aplicación.
- Chrome real Windows: 002 cargado, progreso y WebSocket, redirección a resultados,
  descargas Excel/PDF/PNG/inventario y reprocesamiento desde la tabla; sin errores JS.
- 002 id 36: v1 balanceado 9,76 s registrados, 7,995 %; v2 profundo 19,97 s,
  7,934 %. La espera medida en navegador para la primera carga fue 20,15 s.
- Ambas versiones pasan auditoría independiente desde JSON persistido y Excel:
  67.443 piezas, diámetros, etapas, capacidad, inventario y métricas exactos.
- 001 id 35 (nombre técnico smoke.xlsx): cinco versiones conservadas; HTTP, WS,
  descargas/reproceso y estimación empírica con cinco muestras (1,04–2,94 s).
- Control de reimportación id 37: consume una pieza #3 de 0,01 m del inventario
  exportado por 002 sin catálogo comercial y conserva exactamente los saldos.
  Es una prueba técnica; no un tercer caso académico ni validación física.

Evidencia: `tests/benchmarks/2026-09-13-integracion-local.json`, resultados de navegador,
series JSONL, captura, huellas de imágenes y freeze de dependencias. La serie anterior
`secuencial.jsonl` es diagnóstica incompleta; la serie final es `agrupado.jsonl`.
Auditoría reproducible: `scripts/verify_sequential_result.py`.

### Pendientes reales

Procedencia y permisos de redistribución de 001/002; licencia de distribución;
revisión bibliográfica y del director; reproducción en otra máquina. Sin certificado
de optimalidad ni validación física del modelo ideal. La captura evidencia mejoras
pendientes de contraste y ancho de tabla; no se amplió esta entrega con cosmética.
No hay una pregunta técnica de alta prioridad que bloquee el uso local actual.

### Almacenamiento y preservación

C: pasó de aproximadamente 8,0 a 7,5 GB libres; sigue al 99 %. No confundir la
capacidad virtual WSL con espacio físico. Se reutilizó caché; algunas capas Python
necesitaron completarse. Se registraron versiones instaladas para la reproducibilidad.
No hubo limpiezas globales, cambios de filesystem ni reinstalación del entorno.
Chrome de prueba cerrado y únicamente su perfil temporal retirado; contenedores
de la app siguen activos. El PostgreSQL antiguo `oica_postgres` sigue detenido.

Preservados `services/`, datasets, borrado previo de `docs/METODOLOGIA.md` y archivos
ajenos sin seguimiento, incluido `tests/data-tests.zip`. No hacer commits sin permiso.

## Registro anterior de producción (histórico, no describe el bloque activo)

# Estado actual del proyecto

> Actualizado: 2026-09-12, reanudación después de reparación de WSL con e2fsck.
> Bloque activo: F — Producción, CI/CD y desarrollo nativo.

## Objetivo y estado real

El código del monorepo, Compose, proxy, workflows y scripts de operación está implementado. **No declarar producción desplegada ni validación final completa**: falta el despliegue en la VPS. Los ensayos reales de recuperación pasaron en GitHub Actions 34691570574. El build final, los tests y el E2E pasaron en GitHub Actions (34686626604).

## Restricción urgente de almacenamiento

El usuario exige comprobar espacio antes de operaciones costosas y detenerse/avisar con una estimación antes de builds, instalaciones o generación significativa de datos. No ejecutar limpiezas destructivas, cambios de filesystem, mounts ni permisos globales sin autorización explícita.

Lecturas tras la reparación:

- WSL: disco virtual de 1007 GB, 37 GB usados, 920 GB disponibles.
- Windows C: 442 GB, 436 GB usados, **6 GB libres, 99 % ocupado**.
- Windows D: 26 GB, 19 GB usados, 7,8 GB libres.
- Docker: 10,75 GB en imágenes, 4,62 GB de caché de build, 255,8 MB de volúmenes. No sumar categorías como si no compartieran capas.
- Frontend local: 481 MB de node_modules y 152 MB de .next; se reutilizaron para verificaciones sin caché.

No se conoce aquí la ubicación física exacta del VHDX ni la causa del fallo. No inferir capacidad física a partir del espacio virtual. Desde la reanudación no se construyeron imágenes, instalaron dependencias, borraron datos ni cambiaron permisos/montajes de carpetas. actionlint se ejecutó con imagen existente, sin red ni bind mounts; las pruebas de scripts usaron archivos temporales pequeños.

## Trabajo implementado

- Código local migrado a `backend/` y `frontend/`, incluyendo correcciones anteriores sin commit. `services/` preservado intacto como copia histórica.
- Se retiraron solo los dos gitlinks del índice. Rama local: `production`, siguiendo `origin/production`.
- Fast-forward a e8fa70a incorporó dos commits remotos de documentación. Con aprobación del usuario se creó el commit 0330943 de implementación. El push falló por falta de credenciales HTTPS y el token de gh es inválido. Posteriormente se publicó por SSH y el usuario cambió la rama predeterminada a production, confirmado mediante API pública.
- Compose: Nginx, Next.js, Flask, Celery, PostgreSQL, Redis y migrador temporal. Puerto predeterminado 80; API relativa /api y Socket.IO /socket.io.
- Imágenes con código, sin montajes de fuentes; secretos externos, volúmenes persistentes y requisitos Python fijados. Dockerfiles finales eliminan compiladores temporales; su build se completó en GitHub Actions.
- Next.js 15.5.25 y overrides compatibles de seguridad. npm audit reportó cero vulnerabilidades antes del incidente.
- CI construye/verifica cada imagen una vez y publica exactamente esa imagen. Entregas SHA-RUN_ID, SSH, rollback, reset con confirmación y respaldo configurable.
- Desarrollo nativo Linux/WSL: setup-dev.sh y dev.sh. La instalación completa no se ejecutó: Python 3.12 no estaba en PATH; Node local predeterminado es 24, aunque los builds Docker usaron Node 22.
- Corrección pequeña del motor: rechazar entrada vacía con ValueError para cumplir su test existente. No se alteró la optimización de cartillas válidas.
- Página legacy /resultados redirige a /archivos. Polling revisa periódicamente pérdida de progreso; fallos de reset/restauración conservan mantenimiento.

## Verificación

Antes de la reparación:

- 58 tests del algoritmo: OK tras validar entrada vacía.
- Build Next.js: OK con Node 22; versiones intermedias de las imágenes arrancaron saludables.
- E2E: carga, progreso WebSocket, polling, filtros, Excel/PDF/PNG, reprocesamiento y borrado: OK.
- Se conservó la cartilla smoke (id 2, dos versiones) para comprobar persistencia.

Después de la reparación:

- 58 tests del algoritmo: repetidos con éxito en el contenedor existente, cargando la validación del motor en memoria y sin modificar sus fuentes/datos.
- Diez tests de seguridad de scripts: OK (Docker simulado, sin tocar contenedores reales).
- TypeScript sin emisión/incremental, ESLint sin caché, sintaxis Bash y AST Python: OK.
- Workflows revisados con actionlint usando imagen existente.
- Stack `oica-validation` activo y saludable en **http://localhost:8088**. El stack antiguo `oica-app` quedó detenido tras el incidente; sus contenedores y volúmenes se conservan.
- Lectura de la BD y los archivos: dos versiones conservan demanda, separación por diámetro, conservación de longitud y firmas de los tres artefactos.

Las imágenes Python activas no deben considerarse la validación del código final de Dockerfiles/constraints. No se migró aún el stack al puerto 80. No se hicieron ensayos destructivos reales de reset/restauración ni se emitió certificado público.

## Pendiente para cerrar F

Seguimiento: 34691155372 confirmó arranque de Nginx y E2E, pero falló la comprobación de interrupción de un reprocesamiento en cola. server.py conservaba completed al encolar; interrupt_jobs.py no podía reconocer la tarea pendiente. Corregido en f2a6692: persistir pending antes de publicar en Celery y recuperar estado anterior si falla el envío. Dos comprobaciones aisladas en memoria confirmaron ambos casos. CI 34691570574 completó correctamente toda la validación y recuperación. El job deploy falló en Transferir y actualizar; falta preparar VPS según último estado del usuario y obtener diagnóstico de transferencia si persiste. Los diagnósticos de CI ahora se emiten por servicio en anotaciones cortas.

Datos confirmados por el usuario para la VPS 169.58.196.25: Ubuntu 24.04.4, x86_64, Compose v5.5.0, 172 GB libres, sin contenedores activos y puertos 80/443 libres. No se ejecutó bootstrap. Correo TLS autorizado: cristiandaniel8080@gmail.com. DNS del dominio resuelve a la IP esperada. El acceso SSH a la VPS está en otra instancia de WSL. CI 34690720017 pasó build y pruebas, pero falló en el arranque de Nginx del ensayo de recuperación; anotación pública truncada, se solicitó al usuario el final del log. No hubo despliegue ni cambios en la VPS.

El usuario autorizó commit y push. La publicación se completó usando Git por SSH: origin ahora es git@github.com:cris-dangithub/oica-docker-compose.git y production se publicó con los commits 0330943 y 7b77062. El token de gh sigue inválido, pero no impide operar Git por SSH. El usuario informa que configuró los secretos; falta comprobar la ejecución del pipeline y el despliegue. La rama predeterminada remota ya es production. La ejecución 34686626604 pasó build, tests, arranque, migraciones, E2E y publicación GHCR; falló el ensayo de recuperación y no desplegó. Se corrige la herencia de HTTP_PORT=8080 del runner para que el ensayo use 8081 y se añaden anotaciones públicas del diagnóstico. Se corrigió `.gitignore` para excluir solo `/app/` en la raíz y conservar `frontend/src/app/` en la entrega.

1. Continuar las validaciones en GitHub; compilación final completada allí. No construir localmente.
2. Imágenes finales, migraciones repetibles y recuperación validadas en el runner desechable (34691570574). No repetir localmente.
3. Configurar SSH, GHCR y secrets/environment GitHub; comprobar arquitectura x86_64, distribución, espacio y puertos reales de la VPS.
4. Publicación y rama predeterminada production completadas; commits y push autorizados por el usuario.
5. Preparar HTTPS para oica.cris-munoz.me y efectuar el primer despliegue vacío.

## Contexto académico preservado

Bloques A/B/C completados. Test 002 completó rápido, balanceado y profundo; balanceado obtuvo mejor eficiencia, y profundo sigue afectado por BUG-006. BUG-002 y BUG-006 continúan pendientes. D depende de INF-008 (reutilización de desperdicios). INF-011 valida el cambio a monorepo y operación en VPS.

Los commits incorporados ampliaron Cap. 4 a 212 líneas; la antigua afirmación «Cap. 4 vacío» está desactualizada. Su revisión académica queda fuera de este bloque, sin inventar completitud ni validar resultados por inferencia.

Guía operativa: `docs/DEPLOYMENT.md`. Diagnóstico y riesgos: `.claude/diagnostics/2026-09-12-produccion.md`.
