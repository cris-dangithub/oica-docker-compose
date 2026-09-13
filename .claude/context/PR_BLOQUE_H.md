# Pérdida por corte y mínimo reutilizable configurables

Las cargas nuevas permiten reservar material por separación y decidir cuándo un
sobrante deja de estar disponible. Ambos checks están activos por defecto en la
interfaz: disco nominal de 1 mm y mínimo automático por diámetro. Se pueden elegir
cizalla, valores personalizados y descarte al cierre de etapa. Los valores se
presentan como supuestos editables, sin atribuirlos a una obligación legal.

El motor secuencial-2 evalúa estas condiciones durante la búsqueda agrupada y un
validador independiente reconstruye cada operación. Excel, PDF, gráfica y resultados
distinguen piezas, pérdida, descartado y reutilizable final; el inventario inicial
excluido se informa aparte. Las instantáneas conservan condiciones y referencias,
y el reproceso mantiene las de la carga original. Clientes sin parámetros y ambos
checks desactivados conservan el modelo ideal. No requiere migración SQL.

Validación: 83 pruebas backend con fuentes en memoria/Python 3.12; tipos/lint frontend;
136 ensayos completos de 001/002, 12 controles y generación/relectura de artefactos.
Auditoría de dos versiones antiguas de 002 desde PostgreSQL sin modificarlas.
Build de las tres imágenes, tipos/lint y 83 pruebas en la imagen nueva pasan.
E2E local: Chrome 002 con carga y reproceso, ocho descargas y cero errores JS;
001 con HTTP/WS, filtros, artefactos y reproceso. Las cuatro versiones nuevas pasan
auditoría independiente desde JSON/Excel y conservan exactamente sus instantáneas.
Activo en localhost:80; publicación en VPS no realizada para esta ampliación.
Destino de revisión: production. No fusionar ni desplegar automáticamente.
