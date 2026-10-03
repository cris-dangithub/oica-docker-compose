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

Esperado: todas pasan, incluidas `test_report_presentacion`, `test_analisis` (`analisis-2`) y
`test_cutting_api`.

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
  - Cobertura de la tabla «136 de 136 patrones, 13.955 de 13.955 barras (100 %)» en la 002, y
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
   - La sección «Patrones de corte», con tabla y vista previa.
   - Los totales de compra.
   - La calidad sin la tarjeta de cota simple.
3. Descargar Excel, PDF, imagen e inventario. Reimportar el inventario en otro proyecto.
4. Abrir una versión histórica: sin errores, con «no disponible» donde corresponde.
