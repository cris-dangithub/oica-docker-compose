# Bloque H — riesgos y límites

- Disco 1 mm es espesor nominal de referencia, no medición del kerf efectivo.
  Cizalla 0 mm es idealización editable. Hace falta calibración con un equipo real.
- El mínimo automático es un criterio de planificación sobre demanda conocida,
  no una longitud estructural ni mínimo legal. La regla no certifica anclajes,
  traslapos, ganchos o condición física del material.
- Un aumento del porcentaje respecto del modelo ideal no significa un fallo:
  cambian restricciones y material necesario. Comparar algoritmos dentro del mismo
  escenario. El AG puede variar entre semillas y no certifica optimalidad.
- Los ensayos iniciales `fisico-ideal`, `fisico-solo-perdida`, `fisico-solo-minimo`
  y `fisico-ambos` son comprobaciones de desarrollo; parte se ejecutó mientras
  había otras pruebas. No usarlos como comparación temporal controlada final.
- La memoria máxima del runner es acumulada para el proceso y sus librerías.
  No describirla como incremento aislado por semilla.
- La ampliación ya está activa y probada en contenedores locales; no se publicó
  en producción. El E2E con imágenes coordinadas complementó las pruebas aisladas.
- C: 7,7 GB libres al inicio, **2,0 GB** en lectura posterior; causa no determinada.
  Se avisó al usuario y no se construyeron imágenes ni instalaron dependencias.
  En el reintento autorizado había 8,3 GB y el build completó reutilizando caché;
  no usar el espacio virtual de WSL como evidencia de capacidad física disponible.

## Cierre de pruebas

La matriz final en serie terminó con salida 0 y 136 resultados válidos y únicos;
12 controles adicionales pasan. Los reportes finales de 001/002 se generaron y
releyeron con éxito. El JSON de nuevas condiciones pasó roundtrip y validación
en SQLite, y las dos versiones antiguas de 002 en PostgreSQL se auditaron mediante
lecturas. El E2E nuevo se completó: 002 id 38 desde Chrome y 001 id 39 por HTTP/WS,
dos versiones por caso auditadas desde las imágenes nuevas. Estado real registrado
en CURRENT_STATE.md. Se conserva la revisión física y académica como límite.
