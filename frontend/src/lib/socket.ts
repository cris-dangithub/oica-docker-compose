/**
 * Cliente Socket.IO para actualizaciones en tiempo real de tareas.
 * 
 * Uso:
 *   import { subscribeToTask, unsubscribeFromTask } from '@/lib/socket';
 *   
 *   subscribeToTask(taskId, (data) => {
 *     console.log('Estado:', data.state, 'Progreso:', data.progress);
 *   });
 */
import { io, Socket } from 'socket.io-client';

// URL del servidor backend
const SOCKET_URL = undefined; // Socket.IO utiliza el origen de la página.

let socket: Socket | null = null;
const taskCallbacks: Map<string, (data: TaskUpdate) => void> = new Map();
const connectionStatusCallbacks: Set<(connected: boolean) => void> = new Set();
let isConnected = false;

/**
 * Inicializa la conexión Socket.IO.
 * Se conecta automáticamente al servidor backend.
 */
export function initializeSocket(): Socket {
  if (socket) {
    return socket;
  }

  socket = io(SOCKET_URL, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
  });

  socket.on('connect', () => {
    console.log('[Socket.IO] Conectado al servidor');
    isConnected = true;
    notifyConnectionStatus(true);
    
    // Re-suscribirse a todas las tareas activas al reconectar
    taskCallbacks.forEach((callback, taskId) => {
      socket?.emit('subscribe_task', { task_id: taskId });
      console.log(`[Socket.IO] Re-suscrito a tarea: ${taskId}`);
    });
  });

  socket.on('disconnect', (reason) => {
    console.log('[Socket.IO] Desconectado:', reason);
    isConnected = false;
    notifyConnectionStatus(false);
  });

  socket.on('connected', (data) => {
    console.log('[Socket.IO] Confirmación de conexión:', data);
  });

  socket.on('task_update', (data) => {
    console.log('[Socket.IO] Actualización de tarea:', data);
    
    const { task_id } = data;
    const callback = taskCallbacks.get(task_id);
    
    if (callback) {
      callback(data);
    }
  });

  socket.on('connect_error', (error) => {
    console.error('[Socket.IO] Error de conexión:', error);
  });

  return socket;
}

/**
 * Notifica a todos los listeners del estado de conexión.
 */
function notifyConnectionStatus(connected: boolean): void {
  connectionStatusCallbacks.forEach(callback => callback(connected));
}

/**
 * Registra un callback para recibir notificaciones de estado de conexión.
 * 
 * @param callback - Función que recibe true cuando conectado, false cuando desconectado
 * @returns Función para des-registrar el callback
 */
export function onConnectionStatusChange(
  callback: (connected: boolean) => void
): () => void {
  connectionStatusCallbacks.add(callback);
  // Notificar estado actual inmediatamente
  callback(isConnected);
  
  return () => {
    connectionStatusCallbacks.delete(callback);
  };
}

/**
 * Obtiene el estado de conexión actual.
 */
export function getConnectionStatus(): boolean {
  return isConnected;
}

/**
 * Se suscribe a actualizaciones de una tarea específica.
 * 
 * @param taskId - ID de la tarea Celery
 * @param callback - Función que recibe los datos de actualización
 * 
 * @example
 * subscribeToTask('process_123', (data) => {
 *   console.log(`Estado: ${data.state}, Progreso: ${data.progress}%`);
 *   if (data.state === 'completed') {
 *     console.log('Tarea completada!');
 *   }
 * });
 */
export function subscribeToTask(
  taskId: string,
  callback: (data: TaskUpdate) => void
): void {
  const sock = socket || initializeSocket();
  
  // Guardar callback
  taskCallbacks.set(taskId, callback);
  
  // Suscribirse en el servidor
  sock.emit('subscribe_task', { task_id: taskId });
  
  console.log(`[Socket.IO] Suscrito a tarea: ${taskId}`);
}

/**
 * Cancela la suscripción a actualizaciones de una tarea.
 * 
 * @param taskId - ID de la tarea Celery
 */
export function unsubscribeFromTask(taskId: string): void {
  taskCallbacks.delete(taskId);
  console.log(`[Socket.IO] Desuscrito de tarea: ${taskId}`);
}

/**
 * Cierra la conexión Socket.IO.
 * Útil para limpiar al desmontar componentes o al cerrar la aplicación.
 */
export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
    taskCallbacks.clear();
    console.log('[Socket.IO] Conexión cerrada');
  }
}

/**
 * Tipo de datos de actualización de tarea.
 */
export interface TaskUpdate {
  elapsed_seconds?: number;
  estimated_total_seconds?: [number, number] | null;
  remaining_seconds?: [number, number] | null;
  calibration?: string;
  task_id: string;
  state: 'uploaded' | 'validating' | 'validated' | 'processing' | 
         'generating_artifacts' | 'completed' | 'SUCCESS' | 'FAILURE' |
         'VALIDATING' | 'VALIDATED' | 'PROCESSING' | 'GENERATING' |
         'error_validation' | 'error_processing' | 'error_generation';
  progress: number;
  message?: string;
  error?: string;
  result?: {
    version_number: number;
    storage_uuid: string;
    excel_path: string;
    pdf_path: string;
    image_path: string;
  };
}
