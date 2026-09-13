# Corte secuencial y evaluación de OICA

## Contrato aprobado el 13 de septiembre de 2026

Los casos académicos son `tests/data/001/001-pruebaInicial.xlsx` (92 piezas) y
`tests/data/002/002-ingeBigTest.xlsx` (67.443 piezas, 13 etapas). No se usan las
683 piezas de reportes históricos como evidencia de esta entrega.

El proyecto es de Ingeniería Civil, modalidad tesis. El autor autorizó reformular
título y objetivos con su director. Se conserva el algoritmo genético y se evalúa
su aporte, sin prometer optimalidad ni superioridad en todos los casos.

Los grupos son etapas sucesivas. Cada diámetro se planifica independientemente,
pero su cromosoma evalúa la secuencia completa de etapas: un sobrante permanece
disponible hasta consumirse o descartarse según los parámetros de esa ejecución.
El modelo ideal anterior se conserva desactivando ambos checks. Las condiciones
configurables son hipótesis, no prescripciones normativas ni garantía física.

El porcentaje principal es `100 × (pérdida de corte + descartado + reutilizable final) / masa original utilizada`, todo en masa.
Una barra original se cuenta una vez aunque se corte en varias etapas. El stock
intacto se exporta, pero no participa en ese porcentaje. Para demanda fija por
diámetro, minimizar longitud original utilizada equivale a minimizar ese porcentaje;
la agregación entre diámetros usa masa, no un promedio de porcentajes.

## Entradas e inventario

- La cartilla conserva los encabezados actuales; `Grupo de Ejecución` es opcional
  y su ausencia significa etapa 1. Una celda de grupo vacía en una columna presente
  es un error, no una asignación implícita.
- Cada fila tiene identidad propia aunque se repita `N° Orden`.
- El catálogo comercial inicial contiene 6, 9 y 12 m por diámetro; es editable antes
  de subir. `cantidad: null` significa ilimitado; una cantidad positiva es finita.
- Inventario adicional: XLSX/CSV, columnas `diametro`, `longitud_m`, `cantidad`.
  Todas las cantidades son enteras positivas. No se admiten valores infinitos.
- El inventario exportado contiene las existencias finitas intactas y todos los
  sobrantes elegibles. Puede importarse sin transformación en otro proyecto.
- El usuario confirma la disponibilidad física fuera de la aplicación. Reprocesar
  no consume inventario de otros proyectos ni convierte una simulación en stock real.

## Motor y reproducibilidad

`backend/cutting/` contiene entrada, validador, optimizador y reportes compartidos
por worker y comandos. El antiguo paquete `genetic_algorithm/` queda como referencia
histórica y no se invoca en el nuevo flujo de producción.

El AG usa dos genes por orden: prioridad de colocación y regla de selección de
longitud nueva. Ordena primero por etapa; nunca permite adelantar pedidos futuros.
Emplea selección por torneo, cruce uniforme, mutación de genes y elitismo. La
decodificación conserva información heredada y usa cantidades agrupadas. Cada
evaluación tiene inventario propio; solo el ganador se materializa como plan.

FFD y BFD son referencias adaptadas a stock de varias longitudes. Cada una compara
tres reglas de apertura: mayor longitud, menor longitud y menor residuo relativo
para la pieza actual. No se presentan como algoritmos exactos. El AG conserva una
solución al menos tan buena como estas referencias y su población inicial.

Perfiles `(población, generaciones máximas, generaciones sin mejora)`:
rápido `(20,30,8)`, balanceado `(50,100,15)`, profundo `(100,200,25)`.
No existe un aborto automático a los cinco minutos. El objetivo de duración se
evalúa experimentalmente. Una solución no encontrada con stock finito no constituye
una demostración matemática de inviabilidad.

```bash
python3 -B scripts/benchmark_cutting.py tests/data/002/002-ingeBigTest.xlsx --perfil rapido --semilla 0
python3 -B scripts/benchmark_cutting.py tests/data/002/002-ingeBigTest.xlsx --metodo bfd
python3 -B scripts/benchmark_cutting.py tests/data/001/001-pruebaInicial.xlsx --perfil profundo --semilla 2
```

Usar Python 3.12 con dependencias existentes. El comando no produce PDF, PNG ni
patrones serializados. `--salida ruta.json` crea exclusivamente un resumen nuevo;
no sobreescribe resultados. `--catalogo` recibe JSON y `--inventario` XLSX/CSV.

Para reutilizar Python 3.12 de un contenedor existente sin construir imágenes:

```bash
python3 -B scripts/check_cutting_container.py --tests
python3 -B scripts/check_cutting_container.py --api-tests --container oica-validation-backend-1
```

El segundo comando usa SQLite en memoria, broker simulado y temporales pequeños.
No reemplaza la comprobación E2E con PostgreSQL, Celery y WebSocket reales.

Para comprobar una sola salida completa de 002 sin construir imágenes, revisar
primero el espacio físico y ejecutar:

```bash
python3 -B scripts/check_cutting_container.py --dataset tests/data/002/002-ingeBigTest.xlsx --artifacts-smoke
```

Genera Excel, inventario, PDF y PNG en un directorio temporal que se retira al
terminar. Comprueba la demanda de la hoja Cortes, el inventario reimportado y los
formatos de los reportes. No escribe resultados en la base de datos de la app.

## API y operación

- `GET /catalogo`: catálogo inicial.
- `POST /estimate`: multipart igual a la carga; valida en memoria y consulta
  duraciones previas, sin guardar archivos ni encolar.
- `POST /upload`: añade `catalogo` (JSON), `inventario` (archivo opcional),
  `semilla` (entero, 0 por defecto) y `visuales` (`true` por defecto).
- `POST /reprocess/<id>` conserva las entradas originales y permite cambiar perfil.
- `GET /descargar-inventario/<uuid>`: inventario final de esa versión.
- HTTP de estado y WebSocket incluyen `elapsed_seconds`, `calibration`,
  `estimated_total_seconds`, `remaining_seconds`. Los rangos pueden ser `null`.

Se requieren cinco ejecuciones comparables del mismo problema, perfil, modalidad
de artefactos y entorno para emitir una estimación. Se muestra un rango empírico
con margen del 20 %, no un intervalo de confianza estadística ni garantía temporal.
Si se supera, se informa y se deja de prometer un tiempo restante. La cola se excluye.

La migración nueva es `003_sequential_inputs.sql`. La ejecuta el migrador habitual;
no modificar migraciones aplicadas. Los registros anteriores conservan metadatos
nulos y etiqueta histórica. La actualización de backend y worker debe coordinarse
como una entrega normal, sin mezclar código anterior con esquema sin migrar.

Excel contiene `Barras`, `Cortes`, `Inventario`, `Metricas`, `Descartados`,
`Inventario excluido` y `Parametros`; el saldo final de la
barra raíz aparece una vez. PDF muestra como máximo 150 registros y PNG 60 barras,
identificados explícitamente como muestras. El Excel conserva el plan completo.

## Límites y verificaciones pendientes

El objetivo de menos de un minuto se refiere al motor, no al tiempo de cola, carga
o generación de reportes. Los ensayos de rendimiento no certifican la instalación
completa en otra máquina ni la aplicación de las migraciones en la VPS.

Antes de repetir ensayos con artefactos o construir imágenes, comprobar espacio
físico disponible y estimar escrituras. No borrar los originales de `services/`,
los datasets ni los resultados históricos. No usar limpiezas globales de Docker.


## Estado local verificado el 13 de septiembre de 2026

El registro de id 36 de esta sección corresponde a `secuencial-1`. La ampliación
`secuencial-2` también completó reconstrucción y E2E; véase el cierre al final.

La entrega está activa en `http://localhost`. En esta máquina, `.env` conserva
`COMPOSE_PROJECT_NAME=oica-validation` y `HTTP_PORT=80` para reutilizar los volúmenes.
Desde la raíz, `docker compose up -d --no-build --wait` arranca las imágenes locales
ya construidas. Para reconstruir tras cambiar código, comprobar primero espacio
físico y presupuesto de almacenamiento.

002 completó carga y reprocesamiento en Chrome, descargas y auditoría de ambas
versiones desde base de datos y Excel. Se conserva como archivo id 36. Para repetir
únicamente la auditoría, sin generar archivos ni modificar datos:

```bash
docker compose exec -T backend python - 36 < scripts/verify_sequential_result.py
```

Los ID son propios de esta instalación. No son constantes para otras máquinas.
La evidencia completa está en `tests/benchmarks/2026-09-13-integracion-local.json`.

## Condiciones de corte — secuencial-2

`GET /parametros-corte` entrega defaults y referencias canónicas. La interfaz los
carga antes de habilitar el envío. `/upload` y `/estimate` reciben el campo multipart
`parametros_corte`, un objeto JSON:

```json
{"perdida_activa":true,"proceso":"disco","perdida_mm":"1","minimo_activo":true,"modo_minimo":"automatico","minimo_m":"0.5","descarte":"inmediato"}
```

`minimo_m` solo se aplica en modo `manual`; 0,5 es una propuesta editable para ese
campo, no el default automático ni una recomendación normativa. `proceso` admite
`disco` y `cizalla`; al elegirlos la UI propone respectivamente 1 y 0 mm.
`descarte` admite `inmediato` y `fin_etapa`. Omitir el objeto preserva el contrato
ideal de clientes antiguos. Cambiar condiciones invalida la estimación anterior.
El reprocesamiento conserva las condiciones originales; para compararlas se crea
otra carga. Las instantáneas JSON existentes bastan: no se añade una migración.

El mínimo automático se resuelve una vez por diámetro con toda la cartilla y
se devuelve en `/estimate`. Los diámetros sin demanda no tienen mínimo automático.
El modo manual aplica a todos los diámetros. El inventario adicional inferior al
mínimo se excluye antes de buscar y no es desperdicio generado por el proyecto.

Cada operación obtiene una pieza entera. Si coincide exactamente con el saldo,
no se necesita separación. En otro caso se exige pieza más pérdida completa; no
se permite pérdida parcial de borde ni se añade refrentado implícito. El descarte
inmediato se aplica tras **cada pieza**, incluso dentro de una fila con cantidad.
Al final de etapa se descartan los saldos inferiores al mínimo antes de la siguiente.
La igualdad permite reutilizar. El balance por barra raíz es:

`longitud original = piezas + pérdida + descartado + saldo reutilizable`.

La puntuación considera todas las etapas conocidas. Primero minimiza material
original utilizado; después pérdida irrecuperable, material comercial y número
de barras. No descuenta créditos por demanda futura desconocida. La evaluación
agrupada usa capacidad cerrada por lote; el validador recorre independientemente
las operaciones del ganador y reconstruye pérdida y descarte.

Referencias y límites: disco de espesor nominal 1 mm, [Hilti AC-D](https://www.hilti.com.ph/c/CLS_POWER_TOOL_INSERT_7126/CLS_ABRASIVES_7126/r6473822);
criterio de sobrante al menos igual a la menor longitud demandada,
[Benjaoran y Bhokha (2013)](https://www.joams.com/uploadfile/2013/1024/20131024100240137.pdf),
DOI 10.12720/joams.1.3.313-316. El parámetro de trim loss `Tw` del artículo no es
un mínimo reutilizable universal. Cizalla 0 mm es una idealización que debe
calibrarse. No se verificó una ley que imponga estos valores.

Ensayo de las cuatro combinaciones, en serie y sin reportes:

```bash
python3 -B scripts/check_cutting_container.py --matrix --dataset tests/data/001/001-pruebaInicial.xlsx --dataset tests/data/002/002-ingeBigTest.xlsx --output resumen-nuevo.jsonl
```

Para un escenario: `--parametros-corte '{"descarte":"fin_etapa"}'`. El comando
nativo `benchmark_cutting.py` recibe `--parametros-corte archivo.json`.

## Cierre local de secuencial-2

La ampliación está activa en `http://localhost`, con seis servicios saludables.
El build reutilizó dependencias; C: tenía aproximadamente 8,3 GB libres antes y
después. Los 83 tests pasan en la imagen nueva; frontend pasa build, tipos y lint.
002 se conserva con id 38 (balanceado y profundo) y 001 con id 39 (dos versiones,
nombre técnico smoke.xlsx). El primero pasó carga y reproceso desde Chrome, ocho
descargas y 33 frames WebSocket, sin excepciones JavaScript. Las cuatro versiones
se auditaron desde JSON/Excel y conservan las instantáneas originales.

Evidencia: `tests/benchmarks/2026-09-13-fisico-integracion-local.json`.
La auditoría de lectura se puede repetir sustituyendo el ID por 38 o 39 en el
comando anterior. No hay migración nueva ni publicación en VPS de esta ampliación.
