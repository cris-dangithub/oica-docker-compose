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
disponible hasta consumirse. No hay pérdida por corte ni mínimo de sobrante.
Son hipótesis ideales, no prescripciones normativas ni garantía de ejecución física.

El porcentaje principal es `100 × masa sobrante final / masa original utilizada`.
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
  sobrantes positivos. Puede importarse sin transformación en otro proyecto.
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

Excel contiene `Barras`, `Cortes`, `Inventario`, `Metricas`; el saldo final de la
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
