# Inferencias de la Tesis OICA

> **Uso:** Registro central de suposiciones, decisiones inferidas e inconsistencias detectadas durante el trabajo de completar la aplicación y el documento académico.
>
> **Reglas de uso:**
> - Antes de agregar, verificar que no exista una inferencia similar. Si existe, consolidar.
> - Cambiar el estado en la misma sesión donde se resuelve.
> - Las inferencias `[OBSOLETA]` y `[CONSOLIDADA]` se archivan al final del archivo.
> - Ver plantilla en `.claude/templates/INFERENCE_TEMPLATE.md`.

---

## Índice rápido

| ID | Categoría | Prioridad | Estado | Descripción breve |
|----|-----------|-----------|--------|-------------------|
| INF-001 | Arquitectura | Alta | [VALIDADA] | ¿El AG debe agrupar por diámetro de barra? |
| INF-002 | Académica | Media | [VALIDADA] | Nombres canónicos de perfiles: rapido/balanceado/profundo |
| INF-003 | Arquitectura | Alta | [VALIDADA] | ¿La arquitectura final es Docker, no AWS? |
| INF-004 | Suposición técnica | Alta | [VALIDADA] | Bugs críticos en server.py |
| INF-005 | Académica | Media | [VALIDADA] | Cap. 4 basado en 34 ensayos; revisión del director pendiente |
| INF-006 | Datos | Alta | [CONSOLIDADA] | Consolidada con INF-001 |
| INF-007 | Suposición técnica | Baja | [VALIDADA] | Servicios Docker inactivos actualmente |
| INF-008 | Alcance | Media | [VALIDADA] | Etapas sucesivas e inventario importable/exportable |
| INF-009 | Técnica | Alta | [VALIDADA] | AG inviable para datasets reales por expansión de cantidades — BUG-003 corregido |
| INF-010 | Técnica | Alta | [VALIDADA] | Inicialización de población cuelga en datasets medianos por búsqueda exhaustiva O(N^k) — BUG-004 corregido |
| INF-012 | Datos y metodología | Alta | [VALIDADA] | Corpus 001/002, pérdida configurable y desperdicio final por masa |
| INF-013 | Arquitectura | Media | [VALIDADA] | Proxy seleccionable container/host; VPS en otro ambiente |
| INF-011 | Arquitectura | Alta | [VALIDADA] | Monorepo, producción VPS, CI/CD y desarrollo nativo |
| INF-014 | Académica | Alta | [VALIDADA] | Título fijo con IA/nesting/desperdicios admisibles; se alinea la app (spec 001) y los objetivos reales |
| INF-015 | Metodología | Alta | [PENDIENTE] | El umbral admisible se compara con el desperdicio de INF-012 (incluye saldo reutilizable) |
| INF-016 | Técnica | Media | [VALIDADA] | Cota Gilmore–Gomory con scipy/HiGHS, certificado lagrangiano y etapas relajadas |

---

## INF-001

### Categoría

Arquitectura

### Prioridad

Alta

### Pregunta inferida

¿El algoritmo genético debe optimizar cortes por separado según el diámetro de barra (`N° de Barra`), o puede optimizar todas las piezas juntas como si fueran del mismo material?

### Respuesta asumida

Debe optimizar **por grupo de diámetro**. Físicamente, no se puede cortar una pieza de diámetro #4 de una barra de diámetro #8; cada tipo de barra tiene sus propias longitudes comerciales.

### Justificación

El código actual ignora la columna `N° de Barra` al transformar el DataFrame para el AG (`celery_worker.py` líneas 398-401). La tesis dice explícitamente que se trabaja con "barras de 6, 9 y 12 metros para diferentes diámetros" y el archivo `barras_estandar.json` tiene 11 tipos de diámetros (#3 a #18).

### Impacto

- `services/backend/celery_worker.py` — función `process_file_task`, sección de transformación (líneas 396-402)
- `services/backend/genetic_algorithm/engine.py` — `ejecutar_algoritmo_genetico` (recibe todo junto)
- `services/backend/genetic_algorithm/output_formatter.py` — posiblemente requiere ajuste
- `docs/tesis-doc/03_Capitulo3.md` — sección 3.3.2.1 OICA

### Riesgo si la asunción es incorrecta

**Alto.** Si el diseño intencional es optimizar todo junto (ignorando diámetros), el modelo de datos y la UI deberían reflejar eso. Pero los resultados serían físicamente inválidos.

### Fecha

2026-05-06

### Inferencias relacionadas

- INF-006

### Puede consolidarse con

- INF-006 (mismo problema, diferente ángulo)

### Estado

[VALIDADA] — 2026-05-06

### Respuesta del usuario

Sí. El AG debe agrupar por `N° de Barra` antes de optimizar. Cada diámetro se procesa por separado con sus propias longitudes comerciales. Esto hace los resultados físicamente correctos y desbloquea Bloque B y Cap. 4.

---

## INF-002

### Categoría

Académica

### Prioridad

Media

### Pregunta inferida

¿Cuáles son los nombres canónicos de los perfiles de optimización: `rapido/balanceado/profundo` (código) o `economia/balanceado/velocidad` (INSTALLATION_AND_TESTING.md) o `rápido/balanceado/intensivo` (Capítulo 3)?

### Respuesta asumida

Los nombres canónicos son `rapido`, `balanceado`, `profundo` — que es lo que usa el backend (`server.py`, `celery_worker.py`) y el frontend (`file-upload.tsx`, `FilesTable.tsx`). Los otros nombres están en documentación desactualizada.

### Justificación

El código es la fuente de verdad funcional. Los tres archivos de código usan consistentemente `rapido/balanceado/profundo`. La documentación diverge porque fue escrita en iteraciones anteriores.

### Impacto

- `INSTALLATION_AND_TESTING.md` — sección de perfiles (nombres a actualizar)
- `docs/tesis-doc/03_Capitulo3.md` — sección 3.3.2.1 (nombres a actualizar)

### Riesgo si la asunción es incorrecta

**Bajo.** Si el usuario quiere cambiar los nombres en el código, es un cambio menor de string. Si quiere mantener los nombres del doc, se actualiza la doc.

### Fecha

2026-05-06

### Inferencias relacionadas

Ninguna

### Puede consolidarse con

Ninguna

### Estado

[VALIDADA] — 2026-05-06

### Respuesta del usuario

Los nombres canónicos son `rapido/balanceado/profundo`. El código, la BD, la API y el frontend son consistentes con estos nombres. La documentación del Cap. 3 que usa otros nombres se actualiza en el Bloque E.

---

## INF-003

### Categoría

Arquitectura

### Prioridad

Alta

### Pregunta inferida

¿La descripción de subida de archivos vía AWS S3 (presigned URLs, Lambda) del Capítulo 3 sección 3.3.3 del documento es obsoleta y debe reemplazarse por la arquitectura Docker actual?

### Respuesta asumida

Sí. La arquitectura final es Flask + Celery + PostgreSQL + Redis en Docker local. La arquitectura AWS fue descartada.

### Justificación

El repo completo es Docker Compose. No hay ninguna referencia a AWS en el código de producción. El Capítulo 3 describe una arquitectura que no existe en el repo.

### Impacto

- `docs/tesis-doc/03_Capitulo3.md` — toda la sección 3.3.3 (Desarrollo del Frontend)
- `docs/tesis-doc/02_Capitulo2.md` — notas pendientes sobre Docker

### Riesgo si la asunción es incorrecta

**Bajo.** La evidencia es concluyente.

### Fecha

2026-05-06

### Inferencias relacionadas

- INF-005

### Puede consolidarse con

Ninguna

### Estado

[VALIDADA]

### Respuesta del usuario

Confirmado por contexto del repo — la arquitectura final es Docker Compose, no AWS.

---

## INF-004

### Categoría

Suposición técnica

### Prioridad

Alta

### Pregunta inferida

¿Hay bugs críticos en `server.py` que impiden que los endpoints de filtrado, eliminación y reprocesamiento funcionen actualmente?

### Respuesta asumida

Sí. Se identificaron bugs de atributos incorrectos que causan `AttributeError` en runtime.

### Justificación

Análisis estático de `server.py` comparado con el modelo `UploadedFile` en `models/uploaded_file.py`:
- `UploadedFile.filename` no existe (es `file_name`)
- `UploadedFile.perfil` no existe en el modelo
- `uploaded_file.processing_results` no existe (la relación es `results`)
- `uploaded_file.uploaded_file_path` no existe (es `file_path`)

### Impacto

- `services/backend/server.py` — líneas 212, 222, 303, 311, 352, 360, 370, 371

### Riesgo si la asunción es incorrecta

**Bajo.** Los bugs son objetivamente verificables comparando el modelo con el servidor.

### Fecha

2026-05-06

### Inferencias relacionadas

Ninguna

### Puede consolidarse con

Ninguna

### Estado

[VALIDADA]

### Respuesta del usuario

Bugs confirmados por análisis estático — pendientes de corrección en Bloque A.

---

## INF-005

> Actualización 2026-09-13: la descripción que sigue es histórica. El capítulo 4 ahora presenta 34 ensayos verificables de 001/002 y distingue tiempos del motor de tiempos de la aplicación. La decisión de escribir resultados solo con evidencia queda satisfecha para este piloto; permanecen pendientes E2E real, procedencia de datos y revisión del director.

### Categoría

Académica

### Prioridad

Media

### Pregunta inferida

¿El Capítulo 4 (Resultados) del documento de tesis está casi vacío y debe llenarse solo después de que la aplicación esté funcionando y se hayan ejecutado pruebas reales?

### Respuesta asumida

Sí. El Cap. 4 actual solo tiene una imagen comparativa parcial. No tiene análisis cuantitativo. No se debe redactar hasta tener resultados reales de la aplicación corregida.

### Justificación

La revisión del archivo `docs/tesis-doc/04_Capitulo4.md` muestra que el capítulo tiene apenas 16 líneas de contenido real.

### Impacto

- `docs/tesis-doc/04_Capitulo4.md` — todo el capítulo

### Riesgo si la asunción es incorrecta

**Medio.** Si el usuario ya tiene resultados manuales que quiere incluir, se puede avanzar antes. Pero el riesgo de incluir resultados de una app con bugs es alto.

### Fecha

2026-05-06

### Inferencias relacionadas

- INF-003

### Puede consolidarse con

Ninguna

### Estado

[VALIDADA] — corpus y protocolo confirmados por el usuario; piloto ejecutado el 2026-09-13.

### Respuesta del usuario

Usar exclusivamente 001 y 002; continuar las pruebas y actualizar los capítulos según sus resultados.

---

## INF-006

### Categoría

Datos

### Prioridad

Alta

### Pregunta inferida

¿Es un bug de lógica de dominio que el AG procese todas las piezas juntas sin importar el diámetro (`N° de Barra`), o es un diseño intencional simplificado?

### Respuesta asumida

Es un bug. El `N° de Barra` representa el tipo de acero (diámetro), y mezclar piezas de diferentes diámetros en una misma barra es físicamente imposible.

### Justificación

El archivo `barras_estandar.json` tiene 11 tipos de barras con sus longitudes. La lógica de negocio implica que cada grupo de piezas del mismo diámetro se optimiza con las barras de ese diámetro. El código actual convierte todo a `df_ag` ignorando el diámetro.

### Impacto

- `services/backend/celery_worker.py` — líneas 396-402
- `services/backend/genetic_algorithm/engine.py` — estructura de entrada

### Riesgo si la asunción es incorrecta

**Alto.** Si el diseño intencional es "optimizar sin importar el diámetro" (simplificación del modelo), cambiar esto requeriría reestructurar el output también.

### Fecha

2026-05-06

### Inferencias relacionadas

- INF-001

### Puede consolidarse con

- INF-001

### Estado

[CONSOLIDADA] — 2026-05-06 — fusionada con INF-001

### Respuesta del usuario

Resuelta vía INF-001. El comportamiento es un bug, no una simplificación intencional. La corrección se aplica en el Bloque B.

---

## INF-007

### Categoría

Suposición técnica

### Prioridad

Baja

### Pregunta inferida

¿Los servicios Docker están actualmente inactivos?

### Respuesta asumida

Sí. Al ejecutar `docker compose ps`, no hay contenedores activos.

### Justificación

Salida de `docker compose ps` confirmó que no hay contenedores corriendo.

### Impacto

Entorno de desarrollo — se necesita `docker compose up -d --build` para validar.

### Riesgo si la asunción es incorrecta

**Bajo.** Solo afecta el momento de hacer pruebas de integración.

### Fecha

2026-05-06

### Inferencias relacionadas

Ninguna

### Puede consolidarse con

Ninguna

### Estado

[VALIDADA]

### Respuesta del usuario

Confirmado por comando directo.

---

## INF-008

### Categoría

Alcance

### Prioridad

Media

### Pregunta inferida

¿La reutilización de desperdicios de proyectos anteriores (`desperdicios_previos`) es parte del alcance final de la tesis, o se omite?

### Respuesta asumida

No confirmado. El Objetivo Específico 3 del Capítulo 1 menciona "registrar la reutilización de los desperdicios de barras de acero de proyectos anteriores", pero `celery_worker.py` siempre pasa `desperdicios_previos = []`.

### Justificación

El objetivo está en el documento, pero la implementación es un stub vacío. Puede ser intencional (simplificación de alcance) o un feature no terminado.

### Impacto

- `services/backend/celery_worker.py` — línea `desperdicios_previos = []`
- `docs/tesis-doc/01_Capitulo1.md` — Objetivo Específico 3
- `docs/tesis-doc/03_Capitulo3.md` — sección de OICA

### Riesgo si la asunción es incorrecta

**Medio.** Si está en el alcance y no se implementa, el Cap. 4 no puede mostrar resultados de reutilización.

### Fecha

2026-05-06

### Inferencias relacionadas

Ninguna

### Puede consolidarse con

Ninguna

### Estado

[VALIDADA]

### Respuesta del usuario

<!-- ¿La reutilización de desperdicios está en el alcance final de la tesis? -->

---

---

Actualización 2026-09-13: el usuario define etapas sucesivas e importación/exportación de stock físico por proyecto. No se reutilizan automáticamente resultados de una simulación anterior al reprocesar. Ver INF-012.

## INF-009

### Categoría

Técnica

### Prioridad

Alta

### Pregunta inferida

¿El algoritmo genético puede procesar datasets reales de construcción (>1000 piezas por diámetro) en tiempo razonable?

### Respuesta asumida

No, con la implementación original. Las funciones FFD/BFD/Aleatorio expandían cada orden de N piezas en N ítems individuales antes de procesarlos. Con 58,500 piezas de diámetro #3 (test 002), el AG tardó 26+ minutos de CPU sin completar con el perfil `rapido`.

### Justificación

Código antiguo (population.py líneas 41, 148, 259):
```python
for _ in range(int(cantidad_requerida)):  # 58,500 iteraciones
    piezas_individuales.append({...})
```
Complejidad: O(N_piezas × N_barras). Para el test 002: O(58,500 × 20,000) ≈ 10^9 operaciones.

### Corrección aplicada (2026-05-13)

Reescritura de `population.py` con representación agrupada:
- FFD y BFD operan directamente sobre tipos de pieza con su cantidad (17 tipos para #3, no 58,500 ítems)
- `reparar_cromosoma` pasa directamente `piezas_requeridas_df` a BFD (eliminada la re-expansión)
- `generar_individuo_aleatorio_con_reparacion` usa orden shuffled de tipos, no expansión individual
- Complejidad: O(R × B) donde R = tipos de pieza (17), B = barras usadas (~21,000)
- Timing post-fix: 58,700 piezas → 0.15s (era >26 min)

### Impacto

- `services/backend/genetic_algorithm/population.py` — reescritura completa de 4 funciones
- Cap. 4 de la tesis: los resultados del test 002 y comparación de perfiles ahora son alcanzables
- Los resultados del test 001 (16 piezas) no se ven afectados — la corrección es transparente

### Riesgo si la asunción es incorrecta

**Bajo.** La corrección fue verificada: 0 errores de demanda en todos los grupos, resultados idénticos para datasets pequeños (test 001).

### Fecha

2026-05-13

### Inferencias relacionadas

- INF-005 (Cap. 4 requiere resultados reales — ahora desbloqueado)

### Estado

[VALIDADA] — 2026-05-13

### Respuesta del usuario

Bug detectado en test 002 y corregido en la misma sesión.

---

## INF-010

### Categoría

Técnica

### Prioridad

Alta

### Pregunta inferida

¿La función `calcular_solucion_optima_homogenea` en `optimal_analyzer.py` puede colgar la inicialización de población para datasets medianos (>100 piezas de una longitud con múltiples tipos de barra)?

### Respuesta asumida

Sí. La función usa búsqueda exhaustiva `itertools.product` sobre todas las combinaciones posibles de barras. Para datasets medianos de construcción, el espacio de búsqueda crece exponencialmente con la cantidad de piezas.

### Justificación

Detectado al procesar test 002 (#5 con 2,774 piezas). El worker se colgó durante 8+ horas sin producir ningún log ni progreso después de iniciar el GA del grupo #5. El análisis muestra que para 2,774 piezas de 4.0m con barras de 6/9/12m: 926 × 1,388 × 2,775 ≈ 3,560 millones de combinaciones.

### Corrección aplicada (2026-05-13)

Guard en `calcular_solucion_optima_homogenea` (`optimal_analyzer.py` línea 57):
- Antes del loop `product`, calcular el tamaño total del espacio de búsqueda
- Si supera `MAX_COMBINACIONES = 500_000`, retornar solución greedy inmediata
- Greedy: elegir la barra con mejor ratio piezas/metro, calcular cantidad mínima necesaria
- Verificación: 2,774 piezas de 4.0m → 0.000s, eficiencia 100% (era >8 horas sin terminar)

### Impacto

- `services/backend/genetic_algorithm/optimal_analyzer.py` — guard de espacio de búsqueda
- `generar_individuo_con_analisis_optimo` en `population.py` — beneficiario directo
- Test 001 (16 piezas) — sin impacto, espacio pequeño usa búsqueda exhaustiva sin cambio

### Riesgo si la asunción es incorrecta

**Bajo.** El cuelgue fue verificado empíricamente (8+ horas sin output). La corrección es conservadora: solo activa el fallback cuando el espacio es demasiado grande para ser útil.

### Fecha

2026-05-13

### Inferencias relacionadas

- INF-009 (BUG-003, problema similar de rendimiento en inicialización)

### Estado

[VALIDADA] — 2026-05-13

### Respuesta del usuario

Bug detectado en test 002 (grupo #5) y corregido en la misma sesión.

---

## Archivo — Inferencias consolidadas u obsoletas

> Las inferencias que ya no son relevantes se mueven aquí.

*Vacío por ahora.*

## INF-011

### Categoría
Arquitectura

### Prioridad
Alta

### Pregunta inferida
¿Cómo desplegar y desarrollar OICA sin perder las correcciones locales ni mezclar despliegue con borrado de datos?

### Respuesta asumida
Monorepo con rama production, Docker Compose en VPS, GitHub Actions con imágenes por entrega, desarrollo nativo separado y reconstrucción manual con confirmación y respaldo configurable.

### Justificación
Decisiones explícitas del usuario durante la planificación del 2026-09-11/12. El código local contenía correcciones no publicadas y el instalador anterior borraba services/.

### Impacto
- Backend/frontend pasan a directorios versionados del monorepo.
- Se añade infraestructura de CI/CD, migraciones y recuperación.
- La aplicación permanece pública sin login por decisión explícita.

### Riesgo si la asunción es incorrecta
Alto: publicación de datos compartidos y pérdida de datos si se confunde actualización con reset.

### Fecha
2026-09-12

### Inferencias relacionadas
INF-003, INF-004, INF-009, INF-010.

### Puede consolidarse con
No duplica INF-003: concreta operación y publicación en VPS, sin cambiar Flask/Celery/PostgreSQL.

### Estado
[VALIDADA]

### Respuesta del usuario
Unificar este repositorio; acceso público sin login; puertos 80/443 libres en VPS; dominio oica.cris-munoz.me; desarrollo Linux/WSL mediante un script; actualizar inmediatamente; primera instalación vacía; reset con respaldo configurable.


## INF-012

### Categoría
Datos y metodología

### Prioridad
Alta

### Pregunta inferida
¿Qué casos, objetivo y supuestos gobiernan la nueva validación?

### Respuesta asumida
No es una suposición: decisiones explícitas del usuario. Usar 001 y 002, conservar
el AG, desperdicio final por masa y etapas sucesivas; duración 1–5 minutos deseable,
sin aborto a cinco minutos. La ampliación aprobada permite pérdida y mínimo
reutilizable configurables; ambos desactivados conservan el modelo ideal anterior.

### Justificación
Respuestas del usuario durante la planificación aprobada el 2026-09-13.

### Impacto
backend/cutting/, worker, API, frontend, tests y capítulos 1–4.

### Riesgo si la asunción es incorrecta
Alto. Un resultado rápido con grupos mezclados o desperdicio contado dos veces
no responde al problema definido. Los supuestos ideales no validan cortes en obra.

### Fecha
2026-09-13

### Inferencias relacionadas
INF-008, INF-005.

### Puede consolidarse con
INF-008 cubre inventario; esta entrada registra métrica y corpus.

### Estado
[VALIDADA]

### Respuesta del usuario
El desperdicio es todo lo que sobra al finalizar el proyecto respecto de las barras
utilizadas, tanto comerciales como adicionales. Medir por masa, con detalle en metros.
Los casos 001 y 002 son las bases experimentales. El título puede reformularse con el director.

Ampliación aprobada: ambos checks activos para nuevas cargas UI; disco nominal
1 mm o cizalla idealizada 0 mm, editables. Mínimo automático fijo igual a la menor
demanda de cada diámetro de toda la cartilla, o un mínimo manual común en metros.
Descarte inmediato tras cada operación por defecto, o al terminar la etapa.
Igualdad con el mínimo permite reutilizar. Inventario inicial inferior se excluye
y se informa aparte; con mínimo automático los diámetros sin demanda se conservan.
Se evalúa todo el proyecto conocido, sin premiar usos futuros hipotéticos.
La pérdida, el descarte y el saldo final forman el numerador; cada barra usada
entra al denominador una sola vez. En empate se reduce la pérdida irrecuperable.
Una pieza igual al saldo no necesita corte; en otro caso se exige el kerf completo.
No hay refrentado implícito, diseño estructural ni mínimo normativo universal validado.


### Evidencia de ejecución para INF-008 e INF-012 — 2026-09-13

La integración local verificó 002 desde Chrome y auditó ambas versiones en BD/Excel.
La reimportación real consumió inventario exportado sin catálogo comercial y mantuvo
el saldo esperado. No modifica las decisiones validadas ni sustituye revisión del
director o validación física. Evidencia: `tests/benchmarks/2026-09-13-integracion-local.json`.

Ampliación H: 136 ensayos de cuatro escenarios y 12 controles pasan; E2E de
secuencial-2 activado localmente con 002 id 38 y 001 id 39, dos versiones auditadas
por caso. Los parámetros y referencias persisten idénticos al reprocesar. Evidencia:
`tests/benchmarks/2026-09-13-fisico-integracion-local.json`. Esto valida la ejecución
del modelo configurable, no convierte sus defaults en parámetros medidos en obra.


## INF-013

### Categoría
Arquitectura
### Prioridad
Media
### Pregunta inferida
¿El modo sin Nginx Docker conserva los demás contenedores y utiliza Nginx del host?
### Respuesta asumida
Sí: dos modos seleccionables por env, sin cambiar el dominio ni la aplicación.
### Justificación
El usuario pidió activar/desactivar Nginx Docker y preparar el Nginx de la VPS;
luego separó explícitamente trabajo de repositorio y VPS y autorizó ejecutarlo.
### Impacto
- `compose.host-nginx.yaml`, `scripts/compose.sh`, `scripts/ops-common.sh`
- `scripts/deploy.sh`, `scripts/restore.sh`, scripts TLS y workflow CI
- `config/nginx/host.conf.example`, `docs/DEPLOYMENT.md`
### Riesgo si la asunción es incorrecta
Medio: el modo host necesita un proxy externo configurado y certificado válido.
### Fecha
2026-09-18
### Inferencias relacionadas
INF-011
### Puede consolidarse con
Ninguna: extiende el modo de operación de INF-011.
### Estado
[VALIDADA]
### Respuesta del usuario
«ejecuta entonces», con trabajo del VPS delegado al ambiente con acceso SSH.

---

## INF-014

### Categoría
Académica
### Prioridad
Alta
### Pregunta inferida
¿Es coherente con el proyecto el título «Diseño y desarrollo de una aplicación web con
Inteligencia Artificial para la distribución eficiente de barras de acero comercial de
6, 9 y 12 metros en Colombia, con desperdicios admisibles mediante el enfoque basado en
patrones de corte y nesting»?
### Respuesta asumida
No en su forma actual. Se recomienda:
*Desarrollo y evaluación de una aplicación web para la planificación por etapas del corte
de barras de acero de refuerzo mediante algoritmos genéticos y reutilización de sobrantes.*

Variantes:
- Si se exige mencionar IA: *Aplicación web basada en algoritmos genéticos para minimizar
  el desperdicio en el corte de barras de acero de refuerzo por etapas con reutilización
  de sobrantes.*
- Contexto colombiano defendible: añadir «, bajo la NSR-10»; y «: caso de estudio en
  [ciudad]» solo si las cartillas 001/002 provienen de una obra identificable.
- «Patrones de corte» puede usarse como producto («…que genera patrones de corte…»), no
  como método.
### Justificación
Contraste término por término con el código y el documento:

| Término | Respaldo | Evidencia |
|---|---|---|
| «aplicación web» | Sí | Next.js + Flask desplegado con HTTPS (INF-011). El título vigente dice «local». |
| falta «evaluación» | — | Objetivo específico 4 y Cap. 4 son de evaluación. |
| «con Inteligencia Artificial» | Débil | Cap. 2 §2.1: sin modelos generativos, aprendizaje supervisado ni redes neuronales; la técnica es un algoritmo genético. |
| «distribución eficiente» | Vago | El problema es corte unidimensional; el resumen niega garantía de optimalidad. |
| «6, 9 y 12 metros» | Parcial | Son longitudes por defecto; catálogo editable, inventario adicional y saldos reutilizados. |
| «en Colombia» | No | Dos cartillas; el resumen excluye generalización a otras obras. Solo la NSR-10 es colombiana. |
| «desperdicios admisibles» | No | El modelo minimiza desperdicio final por masa sin umbral admisible; Cap. 2 §2.5: el Tw de Benjaoran y Bhokha (2013) no se usa como mínimo universal. |
| «enfoque basado en patrones de corte» | Engañoso | En IO designa formulaciones por generación de patrones (Gilmore–Gomory); OICA usa un AG con representación por órdenes. |
| «nesting» | Contradictorio | Cap. 2 §2.1 excluye explícitamente la distribución bidimensional. |

Además: nombra dos métodos a la vez, omite la contribución distintiva (etapas y
reutilización de sobrantes) y tiene ~35 palabras.
### Impacto
- `docs/tesis-doc/01_Capitulo1.md` (título, resumen, objetivo general)
- `docs/tesis-doc/02_Capitulo2.md` §2.1 (aclaración sobre nesting e IA)
- Portada y registro institucional del título
### Riesgo si la asunción es incorrecta
Medio: si la institución exige conservar términos del título original («IA», «nesting»,
«desperdicios admisibles»), habría que ampliar el alcance o justificar explícitamente
cada término en el Cap. 2; de lo contrario el jurado puede señalar la incoherencia.
### Fecha
2026-09-29
### Inferencias relacionadas
INF-012 (autoriza reformular el título con el director), INF-011 (aplicación web).
### Puede consolidarse con
Ninguna: INF-012 solo deja abierta la reformulación; esta entrada evalúa la propuesta.
### Estado
[VALIDADA] — 2026-10-02. La respuesta asumida (reformular el título) quedó descartada: el título
es fijo y lo que se alinea es la aplicación y el documento.
### Respuesta del usuario
Solicitó registrar la evaluación y las alternativas (2026-09-29). El 2026-10-02 decidió:
- El título es **fijo palabra por palabra**; la app y la tesis deben respaldar cada término.
- Desperdicios admisibles: umbral porcentual opcional ingresado por el usuario, sin valor legal por
  defecto (no se encontró norma colombiana con un máximo; en INVIAS/IDU el desperdicio va dentro
  del precio unitario). Se reporta cumple/excede sin cambiar el motor.
- Patrones de corte: salida «patrón × repeticiones» y cota inferior Gilmore–Gomory como métrica.
- Nesting: nesting lineal (1D) con fuente; sin nesting 2D.
- Cartillas 001/002: obra colombiana, datos confidenciales y anonimizados.
- Objetivos vigentes aportados por el autor (distintos de los del 13 de septiembre). Aceptó ajustar
  su redacción: «reducir el desperdicio a niveles admisibles», OE1 resumen de compra por longitud,
  OE2 tiempo según cartilla y perfil, OE3 «sobrantes», OE4 planes verificados, OE5 con heurísticas
  y cota (sin datos de compra real por ahora; ver RIESGO-AC-009).
Cap. 1 §1.3 actualizado. Especificación: `specs/001-alineacion-titulo-tesis/spec.md`.
Referencias propuestas: se documentarán en `docs/tesis-doc/Referencias.md` (FR-021).

---

## INF-015

### Categoría
Metodología
### Prioridad
Alta
### Pregunta inferida
¿Contra qué porcentaje se compara el umbral de desperdicio admisible que ingresa el usuario?
### Respuesta asumida
Contra el desperdicio final por masa de INF-012: sobrante final + pérdida por corte +
descartes, sobre la masa de barras usadas. Ese valor incluye el saldo reutilizable. La pérdida
irrecuperable (corte + descartes) se informa aparte, sin juicio de cumplimiento.
### Justificación
Es la métrica ya validada en la matriz de 136 ensayos y la que reporta la app. Comparar contra
otra definición crearía dos «desperdicios» distintos. Spec 001, FR-003 y supuestos; plan R-05.
### Impacto
`backend/cutting/analysis.py` (nuevo), artefactos, `/archivos/[id]`, Cap. 3 y Cap. 4.
### Riesgo si la asunción es incorrecta
Medio. En los análisis de precios unitarios, el desperdicio suele entenderse como el material
que no se recupera. Si el director lo interpreta así, el estado «excede» sería demasiado
estricto con planes que dejan saldo reutilizable. Revertirlo solo cambia la evaluación, no el
plan.
### Fecha
2026-10-02
### Inferencias relacionadas
INF-012, INF-014
### Puede consolidarse con
Ninguna: INF-012 define la métrica, y esta entrada su uso frente al umbral.
### Estado
[PENDIENTE] — confirmar con el director qué desperdicio presupuesta un APU en Colombia.

---

## INF-016

### Categoría
Técnica
### Prioridad
Media
### Pregunta inferida
¿Cómo se calcula una cota Gilmore–Gomory válida sin convertirla en optimizador ni romper la
evidencia existente?
### Respuesta asumida
- Generación de columnas por diámetro sobre la relajación lineal, con `scipy.optimize.linprog`
  (HiGHS) y pricing por mochila exacta en enteros escalados.
- La validez se certifica con una cota lagrangiana (duales escalados), así que la cota es
  válida aunque el LP no converja.
- Se relajan el orden de etapas, los descartes y los saldos entre etapas. La pérdida por corte
  se modela como `Σ(l+e)·a ≤ L+e`, y se redondea al múltiplo del mcd de las longitudes de barra.
- Es solo una métrica: si el plan queda por debajo de la cota, se trata como error de dominio.
### Justificación
Decisión del usuario (2026-10-02): scipy frente a simplex propio. Constitución, Principios I y
IV. Spec 001, FR-012 a FR-017; plan R-01, R-02 y R-12.
### Impacto
`backend/cutting/bound.py` (nuevo), dependencia `scipy==1.18.1` (reconstrucción de imágenes con
aprobación) y `scripts/cota_ensayos.py`.
### Riesgo si la asunción es incorrecta
Bajo para la validez, gracias al certificado. Medio para la utilidad: al relajar las etapas, la
cota puede quedar holgada y la brecha resultar grande. Se declara en la tesis.
### Fecha
2026-10-02
### Inferencias relacionadas
INF-014
### Puede consolidarse con
Ninguna.
### Estado
[VALIDADA] — 2026-10-02, decisiones del usuario en `/speckit-plan`. Implementada y verificada el mismo día:
- pruebas de fuerza bruta y de certificados con duales aleatorios;
- cota calculada para los 148 registros, todos con desperdicio ≥ cota y cota «ajustada» (`tests/benchmarks/2026-10-02-cota-ensayos.jsonl`).
Presupuesto efectivo: 4 s por plan, en lugar de los 6 s previstos, para preservar SC-007.

