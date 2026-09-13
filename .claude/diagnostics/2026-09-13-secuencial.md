# Diagnóstico de cierre del piloto secuencial — 2026-09-13

## Cambio de dirección autorizado

El núcleo activo pasa a `backend/cutting/`: grupos como etapas sucesivas, inventario
finito adicional y catálogo editable, reutilización por diámetro y desperdicio
final ponderado por masa. Se conserva el AG y se compara con FFD/BFD adaptados.
Las decisiones del autor constan en INF-008 e INF-012. `services/` y el motor
anterior se preservan como historia; sus resultados no certifican esta versión.

## Evidencia técnica

- `tests/benchmarks/2026-09-13-agrupado.jsonl`: 34 resultados válidos, dos cartillas,
  cinco semillas por perfil. 002: rápido 1,379–1,510 s; balanceado 3,129–3,793 s;
  profundo 5,648–9,150 s. Tiempos exclusivamente del motor.
- 74 pruebas de backend en Python 3.12; incluyen 11 nuevas pruebas de dominio
  (60 comparaciones agrupado/individual) y cinco de integración aislada.
- TypeScript sin emisión/incremental y ESLint sin caché: pasan con Node 22.
- Diez pruebas de scripts de despliegue: pasan; no operan la VPS real.
- Migración 003: cinco columnas verificadas en PostgreSQL mediante tablas
  temporales y rollback. No aplicada a las tablas reales de la aplicación.
- `2026-09-13-artefactos-002.jsonl`: salida 002 completa verificada, 969.077 bytes
  temporales, 13,11 s de generación/verificación más 1,64 s de motor; demanda
  exacta en Excel e inventario reimportado consistente. No mide HTTP/cola/BD.
- Regresión 002 incorporada a CI; todavía no publicada ni ejecutada en GitHub.

## Riesgos y condiciones pendientes

| Prioridad | Hallazgo | Cierre necesario |
|---|---|---|
| P0 académico | Modelo ideal: pérdida cero, cualquier sobrante positivo reutilizable; compatibilidad del material asumida por diámetro | Revisar supuestos con ingeniero civil/director y declarar las limitaciones; no presentarlo como plan certificado para obra |
| Resuelto | Stack local actualizado con autorización explícita | Build, migración, 74 pruebas y Chrome/HTTP/Redis/Celery/WS/descargas completos; dos versiones 002 auditadas |
| P1 académico | Dos casos y cinco semillas; sin óptimo certificado | Mantener conclusiones descriptivas, completar procedencia de cartillas y repetir en otro entorno |
| P1 documental | Antecedentes de capítulo 1 heredados, fuentes/resúmenes no verificados | Revisar bibliografía original antes de presentación; no usar esas reseñas para justificar superioridad |
| P1 académico | Título/objetivos reformulados con permiso del autor | Revisión formal con el director; no afirmar aprobación institucional |
| P1 distribución | Objetivo de software abierto | Confirmar licencia y autorización de redistribución de datasets antes de publicar una entrega académica |
| P2 técnico | Estimación exige cinco muestras comparables; huella no identifica carga instantánea ni todos los componentes físicos | Explicar rango empírico, no prometer duración; calibrar tras instalación y observar cambios de entorno |
| P2 técnico | Stock finito puede dejar sin solución al decodificador heurístico aun existiendo una | Mensaje de solución no encontrada; evitar presentar esto como prueba de inviabilidad matemática |
| P2 técnico | Persistencia conserva JSON de compatibilidad expandido una vez para el ganador | E2E 002 medido y correcto; vigilar crecimiento con futuras cartillas, no extrapolar tiempos de motor |
| P2 interfaz | Captura muestra bajo contraste en filtros y tabla con desplazamiento horizontal | Revisar estilos y legibilidad en otro bloque; las operaciones probadas funcionan |
| P1 reproducibilidad | Algunas dependencias transitivas se resolvieron al construir | Se registraron freeze e identificadores de imágenes; cerrar bloqueo completo de dependencias para reproducción externa |

No se identificaron violaciones de demanda, separación de diámetros, capacidad o
conservación de inventario en las ejecuciones verificadas. Esto es evidencia del
modelo y de estos casos, no una demostración universal de corrección física.

## Operación y preservación

Con autorización explícita de 2–4 GB, se construyeron las tres imágenes usando
caché y se aplicó 003 en el mismo stack. C: pasó de ~8,0 a ~7,5 GB libres, sigue al
99 %. No hubo limpiezas globales ni cambios de filesystem. El perfil temporal de
Chrome se retiró después de cerrar únicamente el navegador de prueba.

Evidencia integrada: `tests/benchmarks/2026-09-13-integracion-local.json`. 002 pasó
carga y reprocesamiento desde Chrome, con 9,76/19,97 s registrados para balanceado/
profundo y auditoría física del modelo desde JSON/Excel. 001 pasó HTTP/WS y calibró
ETA con cinco muestras. La carga técnica id 37 verificó reimportación de inventario.
No se hicieron commits, push ni cambios en VPS. Datos anteriores preservados.
