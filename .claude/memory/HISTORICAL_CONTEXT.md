# Contexto Histórico del Proyecto

> Este archivo registra decisiones importantes, cambios de dirección y contexto histórico que no es obvio desde el código o el documento actual.

---

## Historial de arquitectura

### Pre-Docker (arquitectura descartada)

La primera versión del frontend intentó subir archivos a **AWS S3** usando **presigned URLs** generadas por un backend en **AWS Lambda**. Esta arquitectura fue completamente descartada.

El Capítulo 3 del documento de tesis todavía describe esta arquitectura (sección 3.3.3). Esta es una contradicción activa registrada como INF-003.

**Decisión tomada:** La arquitectura final es Docker Compose (Flask + Celery + PostgreSQL + Redis + Next.js). No hay componentes AWS en producción.

### Migración a PostgreSQL

El proyecto migró de `localStorage` (browser) a PostgreSQL para persistencia. Esta migración introdujo el modelo de versionamiento: 1 `UploadedFile` → N `ProcessingResult`.

El campo `document_number` en `UploadedFile` está marcado como `[DEPRECATED]` en el código — era relevante cuando el usuario debía ingresar un número de documento manualmente. Ahora se auto-rellena desde el nombre del archivo.

---

## Decisiones de diseño conocidas

### Perfiles de optimización

Los perfiles de optimización han tenido al menos 3 conjuntos de nombres en la historia del proyecto:
- `economia / balanceado / velocidad` — referenciado en `INSTALLATION_AND_TESTING.md`
- `rapido / balanceado / intensivo` — referenciado en Capítulo 3 del documento
- `rapido / balanceado / profundo` — en el código actual (fuente de verdad)

**Decisión actual:** El código usa `rapido/balanceado/profundo`. La documentación debe actualizarse. Pendiente confirmación del usuario (INF-002).

### Reutilización de desperdicios

El Objetivo Específico 3 del Cap. 1 menciona reutilizar desperdicios de proyectos anteriores. El código tiene la estructura para ello (`desperdicios_previos` como parámetro del AG) pero siempre pasa una lista vacía.

El algoritmo genético `engine.py` acepta `desperdicios_reutilizables_previos` como parámetro. La infraestructura existe pero no se usa.

**Estado:** Pendiente decisión del usuario sobre alcance (INF-008).

---

## Problemas históricos conocidos

### Duplicación de requirements.txt

El `requirements.txt` de producción tiene dos fuentes: `config/backend/requirements.txt` y `services/backend/requirements.txt`. Solo la primera se edita manualmente. La segunda se debe sincronizar antes de cada build. Si no se sincroniza, el Docker build usa dependencias desactualizadas.

### Python 3.12 y psycopg2

`psycopg2-binary 2.9.9` no es compatible con Python 3.13. La imagen base está fijada en `python:3.12-alpine`. No actualizar sin verificar compatibilidad de psycopg2.

### backend vs celery_worker

Usan el mismo código fuente (`services/backend/`) pero diferentes Dockerfiles. La diferencia crítica es el servidor async: backend usa `gevent`, worker usa `eventlet`. Los requirements.txt son diferentes en esta dependencia.

---

## Sesiones de trabajo

### Sesión 1 — 2026-05-06

**Trabajo realizado:**
- Diagnóstico completo del repositorio.
- Identificación de 5 bugs críticos en `server.py`.
- Identificación de bug de lógica de dominio en AG (INF-001/006).
- Creación de infraestructura `.claude/` completa.
- Creación de 6 agentes especializados.
- Actualización de `INFERENCIAS_TESIS.md` con formato mejorado.
- Creación de `PLAN_TRABAJO.md`.

**Decisiones tomadas:**
- Prioridad: funcionalidad > coherencia académica > UI > documento.
- El Bloque A (corrección de bugs) no requiere validación del usuario y puede ejecutarse inmediatamente.
- El Bloque B (agrupación por diámetro) está bloqueado hasta que el usuario responda INF-001.

**Preguntas abiertas al usuario:**
- INF-001: ¿Agrupar por diámetro?
- INF-002: ¿Nombres de perfiles?
- INF-008: ¿Alcance de desperdicios?


### 2026-09-12 — Monorepo, producción y reparación de WSL

El usuario aprobó unificar backend/frontend en este repositorio y preparar producción por GitHub Actions, desarrollo nativo y reset con respaldo configurable. Se conservaron services/ y sus cambios; se incorporó origin/main por fast-forward y se renombró la rama local a production, sin commits/push nuevos.

Tras un incidente de WSL reparado por el usuario con e2fsck, se suspendieron builds e instalaciones. C: reportó 6 GB libres aunque WSL mostraba 920 GB virtuales. Desde la reanudación solo se hicieron cambios pequeños y verificaciones que reutilizan archivos/imágenes existentes, sin limpiezas ni nuevos montajes de carpetas. El usuario exige aviso y estimación antes de consumos significativos.

Código de infraestructura implementado; build final y activación real de la VPS siguen pendientes. El smoke de dos versiones sobrevivió al reinicio y pasó verificación de demanda, diámetro y artefactos. No confundir pruebas de imágenes intermedias con validación final. Consultar CURRENT_STATE.md.


## 2026-09-13 — Giro al modelo secuencial y corpus 001/002

El usuario descartó el caso 683 de la evaluación y aprobó implementar el plan con
002 como caso crítico. Grupos son etapas sucesivas; el stock adicional y sobrantes
se importan/exportan por proyecto. No hay pérdida de corte ni mínimo de sobrante.
Se conserva el AG y se mide desperdicio final por masa. Se creó un núcleo separado
del paquete genético histórico porque la reparación anterior borraba la herencia
y no existía trazabilidad de inventario. El piloto nuevo consta de 34 ensayos válidos;
la evaluación agrupada redujo el tiempo de 002 a menos de 10 s de motor en el entorno
ensayado. No implica E2E desplegado ni validación física. Ver CURRENT_STATE.md.


## 2026-09-13 — Entrega secuencial activada localmente

Con autorización explícita para 2–4 GB de reconstrucción, se construyeron las tres
imágenes usando caché, se aplicó 003 y se llevó el stack existente oica-validation
de 8088 a localhost:80 conservando volúmenes. Chrome verificó 002 y reprocesamiento;
la BD/Excel de ambas versiones pasó auditoría independiente. 001 calibró la ETA y
el inventario de 002 se reimportó mediante HTTP. C: quedó con ~7,5 GB libres.
No hubo commits, push ni modificaciones de VPS. No confundir este cierre técnico
local con aprobación de tesis, licencia o validación de ejecución física.
