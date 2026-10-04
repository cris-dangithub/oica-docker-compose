# Quickstart — validar la presentación de resultados (spec 002)

Guía de validación. Los detalles de formato están en [contracts/artefactos.md](contracts/artefactos.md)
y [contracts/ui.md](contracts/ui.md).

## Prerrequisitos

- Stack local en marcha (`bash scripts/compose.sh up -d --wait`), con los contenedores
  `oica-validation-backend-1` y `oica-validation-celery_worker-1`.
- No hace falta reconstruir imágenes para los pasos 1–4: el arnés carga el código del árbol de
  trabajo en memoria.
- El paso 6 (E2E) **sí** requiere reconstruir imágenes. Antes hay que avisar con una estimación de
  espacio en C: y esperar aprobación.

## 1. Pruebas del backend

```bash
python3 scripts/check_cutting_container.py --all-tests --container oica-validation-backend-1
```

Esperado: todas pasan, incluidas:

- `test_report_presentacion`.
- `test_vista_patrones` (enmienda): la reconstrucción coincide con `agrupar` y con la hoja
  «Patrones», y se cumplen las invariantes de data-model §8.3.
- `test_cutting_api`, con la ruta `GET /patrones/<uuid>` sobre la base SQLite en memoria de las
  pruebas.
- `test_analisis`, que **sigue** esperando `analisis-1`: no hay `analisis-2`.

## 2. Regresión del plan (FR-021, SC-004)

```bash
python3 scripts/check_cutting_container.py \
  --comparar tests/benchmarks/2026-09-13-fisico-matriz-final.jsonl \
  --comparar tests/benchmarks/2026-09-13-fisico-control-cizalla.jsonl \
  --comparar tests/benchmarks/2026-09-13-fisico-control-fin-etapa.jsonl \
  --output tests/benchmarks/<fecha>-regresion-presentacion.jsonl
```

Esperado: 148 registros y 0 diferencias.

## 3. Artefactos de 001 y 002, y tiempo (SC-003, SC-007)

```bash
python3 scripts/check_cutting_container.py --artifacts-smoke --dataset 002-ingeBigTest.xlsx \
  --profiles balanceado --seeds 1 --output tests/benchmarks/<fecha>-presentacion-002.jsonl
```

Esperado:
- Artefactos verificados.
- Para la medición de tiempo, cinco repeticiones antes y después (research R-15); la mediana
  total no supera 26,75 s × 1,10 ≈ 29,4 s.
- Para inspeccionar los archivos a mano, generarlos en un directorio temporal del contenedor y
  copiarlos con `docker cp`, sin versionarlos.

Revisión manual:
- **Excel**:
  - Las 13 hojas en orden.
  - «Resumen» con indicadores legibles y los totales de compra.
  - Barras sin `stock_id`.
  - «Parámetros» legible.
  - «Trazabilidad» con el JSON de parámetros.
- **PDF**:
  - Encabezado con versión, perfil y fecha.
  - Compra con totales en la primera página.
  - Cobertura de la tabla «136 de 136 patrones, 13955 de 13955 barras (100 %)» en la 002, y
    cobertura de las imágenes «60 de 136 patrones…».
  - Nesting en páginas de hasta 18 patrones, legible al imprimir en A4.
  - Coma decimal; datos técnicos al final.
- **PNG**:
  - Medidas legibles al 100 %, leyenda de etapas, 200 dpi, máximo 9 MP.
  - Cobertura «60 de 136 patrones…».

## 4. Frontend

```bash
cd frontend && npm run typecheck && npm run lint && npm run build
```

Más axe en 1440, 820 y 390 px sobre `/archivos/<id>`: sin violaciones nuevas.

## 5. Auditoría

```bash
docker compose exec -T backend python - <ID> < scripts/verify_sequential_result.py
```

Ejecutarla sobre una versión nueva y una histórica: ambas pasan.

## 6. E2E local (tras una reconstrucción aprobada)

1. Subir la 001 desde `/subir-cartilla`, con y sin umbral.
2. En `/archivos/<id>`:
   - La sección «Patrones de corte» con el explorador (§7).
   - Los totales de compra.
   - La calidad sin la tarjeta de cota simple.
3. Descargar Excel, PDF, imagen e inventario. Reimportar el inventario en otro proyecto.
4. Abrir una versión histórica: sin errores, con «no disponible» donde corresponde.

## 7. Explorador de patrones (enmienda 2026-10-04; FR-024 a FR-031, SC-009 a SC-012)

Requisitos: la ruta nueva y el frontend necesitan las imágenes reconstruidas, así que esta
sección se hace junto con el §6, con aprobación previa. Las invariantes del backend ya se cubren
en el §1, sin reconstruir.

1. **Endpoint** (versiones reales de la 001 y la 002):

   ```bash
   curl -s -o /tmp/patrones-002.json -w '%{http_code} %{time_total}s\n' \
     http://localhost/api/patrones/<storage_uuid_002>
   ```

   Antes del E2E, SC-009 ya se puede medir sin reconstruir con `scripts/medir_vista_patrones.py`
   (tasks T025).

   Esperado:
   - `200`, `disponible: true`, `totales.patrones = 136` y `totales.barras = 13955`.
   - Tiempo ≤ 2 s (SC-009); la primera llamada, sin caché.
   - Con una versión `secuencial-1` o del motor histórico: `200` con `disponible: false` y su
     `motivo`.
   - Con un uuid inexistente: `404`.
2. **Coherencia con el Excel** (SC-010): con la misma versión, comparar `patrones[]` (`patron_id`,
   `repeticiones`, `secuencia`, `aprovechamiento_pct`, `saldo_m`) con la hoja «Patrones» de su
   Excel. Se puede usar pandas dentro del contenedor, en un directorio temporal, sin versionar
   nada. Esperado: 0 diferencias.
3. **Pantalla** `/archivos/<id>` de la versión de la 002:
   - La sección carga al hacer scroll hasta ella, no al abrir la página.
   - La cobertura dice «Se muestran 136 de 136 patrones, que cubren 13955 de 13955 barras
     (100 %)».
   - Filtrar solo por un pedido: cada fila muestra el aporte del pedido, y la suma de los aportes
     es igual a la cantidad del pedido en la cartilla (FR-027).
   - Añadir un filtro de diámetro: la cobertura cambia y la suma de los aportes pasa a ser solo
     la parte del pedido de ese diámetro.
   - Cambiar el orden: los filtros y la cobertura no cambian.
   - Abrir el patrón con más repeticiones: muestra el total, los rangos (como máximo 100) y
     «Ver más». La respuesta es inmediata (SC-012; medirla con el panel Performance del
     navegador si hay dudas).
   - Las barras de 6 m ocupan la mitad del ancho que las de 12 m, también al filtrar (FR-026).
4. **Teclado y lector de pantalla** (SC-011): Tab hasta un patrón, Enter abre el detalle y Enter
   lo cierra (el foco vuelve a la fila), y los filtros tienen su etiqueta.
5. **axe** en 1440, 820 y 390 px con la sección abierta y un detalle desplegado: sin violaciones
   nuevas. A 390 px, sin desplazamiento horizontal de la página.
6. **Versión histórica**: la sección dice «Patrones: no disponible para esta versión» y el resto
   del detalle funciona.
7. **Confidencialidad** (supuesto de la spec): antes de capturas o demostraciones, comprobar que
   los pedidos («N° Orden») y el nombre de archivo de la versión que se muestra no identifican la
   obra. Si la identifican, usar una copia anonimizada de la cartilla.
