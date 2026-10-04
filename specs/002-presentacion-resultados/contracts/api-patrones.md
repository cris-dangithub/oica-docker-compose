# Contrato HTTP — patrones de una versión (spec 002, enmienda 2026-10-04)

Es la única ruta nueva de la spec 002, de solo lectura (FR-024). El resto de la API no cambia.
La ruta se registra sin el prefijo `/api`, igual que las demás de `backend/server.py`: Nginx
elimina el prefijo y el frontend la llama como `${API_URL}/patrones/<storage_uuid>`.

## `GET /patrones/<storage_uuid>`

- **Parámetros**: `storage_uuid` de la versión (`ProcessingResult.storage_uuid`, el mismo que
  usan `/descargar-*`).
- **Efectos**: ninguno. No escribe en la base ni en el sistema de archivos (FR-024).
- **Fuente**: `resultados` y `metricas` de la versión, reconstruidos con
  `cutting.vista_patrones` (research R-16). No ejecuta el AG.

### 200 — patrones disponibles

```json
{
  "disponible": true,
  "storage_uuid": "…",
  "version_number": 1,
  "motor": "secuencial-2",
  "escala_m": 12.0,
  "totales": { "patrones": 136, "barras": 13955 },
  "diametros": ["#3", "#4", "#5"],
  "etapas": [1, 2, 3],
  "origenes": ["comercial", "adicional"],
  "pedidos": [ { "pedido": "12", "piezas": 480 } ],
  "patrones": [
    {
      "patron_id": "P-#4-001",
      "diametro": "#4",
      "origen": "comercial",
      "longitud_m": 12.0,
      "secuencia": "E1: 2×4.2 m + 1×3.5 m",
      "repeticiones": 230,
      "aprovechamiento_pct": 99.2,
      "perdida_corte_m": 0.003,
      "descartado_m": 0.0,
      "saldo_m": 0.097,
      "etapas": [1],
      "piezas": [
        { "etapa": 1, "longitud_m": 4.2, "cantidad": 2,
          "pedidos": [ { "pedido": "12", "piezas": 300 }, { "pedido": "15", "piezas": 160 } ] },
        { "etapa": 1, "longitud_m": 3.5, "cantidad": 1,
          "pedidos": [ { "pedido": "18", "piezas": 230 } ] }
      ],
      "barras": {
        "total": 230,
        "rangos": [ { "desde": "#4:1", "hasta": "#4:200", "n": 200 },
                    { "desde": "#4:450", "hasta": "#4:479", "n": 30 } ]
      }
    }
  ]
}
```

Reglas:

- **Campos del patrón**: `patron_id` a `saldo_m` salen de `report.patrones_rows`, el mismo código
  que genera la hoja «Patrones» del Excel (FR-025, SC-010). `etapas`, `piezas` y `barras` son
  campos añadidos.
- **Orden**: `patrones` viene en el orden de la hoja «Patrones», es decir, el de
  `patterns.agrupar` (FR-031).
- **`escala_m`**: la `longitud_m` máxima entre todos los patrones de la versión. No depende de
  ningún filtro (FR-026).
- **`piezas`**: una entrada por elemento de la secuencia, en orden de corte. Se cumple
  `Σ pedidos.piezas = cantidad × repeticiones` (R-19).
- **`barras.rangos`**: identificadores consecutivos del mismo diámetro, con el formato `#d:n` de
  la hoja «Barras». Se cumple `Σ n = total = repeticiones` (R-18).
- **`pedidos`**: el índice global, con `piezas` igual al total entregado de ese pedido. Se ordena
  numéricamente si todos los pedidos son números y, si no, como texto.
- **`totales.barras`**: igual a `Σ repeticiones` y al número de registros de `resultados`.
- **Unidades**: los números van en metros y porcentaje, con punto decimal JSON. La coma decimal
  se aplica al mostrarlos.

### 200 — patrones no disponibles (FR-030)

```json
{ "disponible": false, "storage_uuid": "…", "version_number": 1, "motor": "secuencial-1",
  "motivo": "La versión no guarda la trazabilidad de cortes necesaria para reconstruir los patrones" }
```

Aplica, en este orden de comprobación, a:

1. versiones sin plan terminado: `result_status` distinto de `completed` y de
   `error_generation`. Esta última conserva un plan guardado aunque fallaran los artefactos, y
   el explorador no depende de ellos;
2. versiones cuyo plan no consta como verificado: `metricas.valido` distinto de `true` (FR-030;
   constitución, Principio I). El motivo es «El plan de esta versión no pasó la verificación
   independiente» si es `false`, y «La versión es anterior a la verificación independiente del
   plan» si no existe (motor histórico);
3. versiones sin `resultados`, sin `metricas.escala_longitudes` o sin `trazabilidad_cortes`
   (motor histórico o `secuencial-1`).

### 404

`storage_uuid` inexistente: `{"error": "Versión no encontrada"}`.

### 500 — inconsistencia (FR-025)

`{"error": "Patrones inconsistentes: <detalle>"}` cuando se viola alguna invariante de R-16:

- `Σ repeticiones ≠ número de registros de resultados`;
- discrepancia con `analisis.patrones` (total, barras o repeticiones del `top`);
- una invariante de pedidos de R-19.

La ruta registra el error en el log y **nunca** devuelve datos parciales.

## Rendimiento (SC-009, R-18)

- Carga solo `resultados` y `metricas`.
- Usa una caché en memoria del proceso, con `lru_cache(maxsize=8)` y la clave `storage_uuid`.
  La caché guarda solo la vista calculada. La respuesta se arma en cada llamada como un
  diccionario **nuevo** (`{**vista, 'storage_uuid': …}`), para que nada modifique el objeto
  cacheado.
- Meta: responder en ≤ 2 s con la cartilla 002 en el entorno local. Medición exploratoria: unos
  0,5 s sin caché.
