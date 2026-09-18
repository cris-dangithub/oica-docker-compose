# Proxy host — validación pendiente

Configuración Compose y 16 pruebas simuladas pasan. No se ha intervenido la VPS
ni probado un Nginx externo real. El bootstrap protege shared y sus padres:
comprobar acceso del worker al marcador de mantenimiento antes de activar host,
sin exponer production.env. Comprobar certificados, renovación y todos los
sitios existentes. El cambio inicial requiere coordinar puertos 80/443. Rollback
solo a entregas compatibles con host mediante operador actual. Un archivo env
cambiado por sí solo no cambia contenedores en ejecución. No hay nuevos resultados
académicos ni cambios del motor de corte en este bloque.
