'use client';
import { API_URL } from '@/lib/api';

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Upload, CheckCircle, AlertCircle, WifiOff } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { subscribeToTask, unsubscribeFromTask, TaskUpdate, onConnectionStatusChange } from '@/lib/socket';

export function FileUpload() {
   const [files, setFiles] = useState<File[]>([]);
   const [loadingSendButton, setLoadingSendButton] = useState(false);
   const [backendError, setBackendError] = useState<string | null>(null);
   const [perfil, setPerfil] = useState<string>('balanceado');
   
   // Estados para WebSocket
   const [taskId, setTaskId] = useState<string | null>(null);
   const [progress, setProgress] = useState<number>(0);
   const [statusMessage, setStatusMessage] = useState<string>('');
   const [processingState, setProcessingState] = useState<string>('');
   const [isConnected, setIsConnected] = useState<boolean>(true);
   const [isPulsing, setIsPulsing] = useState<boolean>(false);
   
   // Refs para polling fallback
   const lastUpdateTime = useRef<number>(Date.now());
   const pollingInterval = useRef<NodeJS.Timeout | null>(null);

   const router = useRouter();

   const onDrop = useCallback(async (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
         setFiles(acceptedFiles);
      }
   }, []);

   const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop,
      accept: {
         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
         'text/csv': ['.csv'],
      },
      maxFiles: 1,
      multiple: false,
   });

   // Limpieza al desmontar
   useEffect(() => {
      // Monitorear estado de conexión
      const unsubscribe = onConnectionStatusChange((connected) => {
         setIsConnected(connected);
         if (!connected) {
            console.log('[FileUpload] WebSocket desconectado, esperando reconexión...');
         } else {
            console.log('[FileUpload] WebSocket reconectado');
         }
      });
      
      return () => {
         unsubscribe();
         if (taskId) {
            unsubscribeFromTask(taskId);
         }
         if (pollingInterval.current) {
            clearInterval(pollingInterval.current);
         }
      };
   }, [taskId]);
   
   // Polling fallback si no hay actualizaciones de WebSocket
   useEffect(() => {
      if (!taskId || !loadingSendButton) return;
      
      const startPolling = () => {
         if (pollingInterval.current) return;
      
         pollingInterval.current = setInterval(async () => {
            if (!taskId) return;
         
            try {
               const apiUrl = API_URL;
               const response = await fetch(`${apiUrl}/status/${taskId}`);
            
               if (response.ok) {
                  const data = await response.json();
                  console.log('[FileUpload] Polling update:', data);
               
                  // Actualizar estado desde polling
                  if (data.progress !== undefined) {
                     setProgress(data.progress);
                  }
                  if (data.message) {
                     setStatusMessage(data.message);
                  }
                  if (data.state) {
                     setProcessingState(data.state);
                  
                     // Detener polling si completado o error
                     if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
                        stopPolling();
                        setLoadingSendButton(false);
                        if (data.state === 'FAILURE') setBackendError(data.message || 'Procesamiento interrumpido');
                        if (data.state === 'SUCCESS') {
                           setTimeout(() => {
                              router.push('/archivos');
                           }, 2000);
                        }
                     }
                  }
               }
            } catch (error) {
               console.error('[FileUpload] Polling error:', error);
            }
         }, 2000);
      };
      // Revisar periódicamente: también cubre desconexiones durante el trabajo.
      const checkInterval = setInterval(() => {
         const timeSinceLastUpdate = Date.now() - lastUpdateTime.current;
         if (timeSinceLastUpdate > 30000) {
            console.log('[FileUpload] Sin actualizaciones WebSocket por 30s, iniciando polling...');
            startPolling();
         }
      }, 5000);
      
      return () => {
         clearInterval(checkInterval);
         if (pollingInterval.current) {
            clearInterval(pollingInterval.current);
            pollingInterval.current = null;
         }
      };
   }, [taskId, loadingSendButton, router]);
   

   
   const stopPolling = () => {
      if (pollingInterval.current) {
         clearInterval(pollingInterval.current);
         pollingInterval.current = null;
      }
   };

   const handleTaskUpdate = useCallback((data: TaskUpdate) => {
      console.log('[FileUpload] Actualización de tarea:', data);
      
      lastUpdateTime.current = Date.now();  // Actualizar timestamp
      stopPolling();  // Detener polling si WebSocket funciona
      
      // Activar parpadeo por 300ms
      setIsPulsing(true);
      setTimeout(() => setIsPulsing(false), 300);
      
      setProgress(data.progress || 0);
      setProcessingState(data.state);
      setStatusMessage(data.message || '');

      if (data.state === 'completed' || data.state === 'SUCCESS') {
         // Procesamiento completado
         setTimeout(() => {
            router.push('/archivos');
         }, 2000);
      }

      if (data.state.startsWith('error_') || data.state === 'FAILURE') {
         // Error en procesamiento
         setBackendError(data.error || 'Error en el procesamiento');
         setLoadingSendButton(false);
      }
   }, [router]);

   const handleSend = async () => {
      console.log('CLICK ENVIAR');
      setBackendError(null);

      if (files.length === 0) {
         setBackendError('No hay archivos para enviar');
         return;
      }

      const file = files[0];

      try {
         setLoadingSendButton(true);
         setProgress(0);
         setStatusMessage('Subiendo archivo...');

         const formData = new FormData();
         formData.append('file', file);
         formData.append('perfil', perfil);

         const apiUrl = API_URL;
         const response = await fetch(`${apiUrl}/upload`, {
            method: 'POST',
            body: formData,
         });

         let data = null;
         try {
            data = await response.json();
            console.log('Respuesta del backend:', data);
         } catch {
            setBackendError('El backend no devolvió una respuesta válida.');
            setLoadingSendButton(false);
            return;
         }

         if (!response.ok || !data || !data.task_id) {
            setBackendError(data?.error || `Error al subir el archivo: ${response.statusText}`);
            setLoadingSendButton(false);
            return;
         }

         // Suscribirse a actualizaciones de WebSocket
         const newTaskId = data.task_id;
         setTaskId(newTaskId);
         subscribeToTask(newTaskId, handleTaskUpdate);

         setStatusMessage('Archivo en cola de procesamiento...');
         setProgress(5);

      } catch (error: unknown) {
         const errorMessage = error instanceof Error ? error.message : String(error);
         setBackendError('Error manejando el archivo: ' + errorMessage);
         console.error('Error manejando el archivo:', error);
         setLoadingSendButton(false);
      }
   };

   // Mapeo de estados a mensajes amigables
   const getStateLabel = (state: string): string => {
      const labels: Record<string, string> = {
         uploaded: 'Archivo cargado',
         validating: 'Validando contenido',
         validated: 'Validación completada',
         processing: 'Procesando con algoritmo genético',
         generating_artifacts: 'Generando archivos de resultados',
         completed: '¡Procesamiento completado!',
         error_validation: 'Error en validación',
         error_processing: 'Error en procesamiento',
         error_generation: 'Error generando archivos',
      };
      return labels[state] || state;
   };

   return (
      <div className="container mx-auto px-4 py-16 max-w-3xl">
         <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4 text-black">
               Análisis Geométrico de aceros
            </h1>
            <p className="text-gray-600 text-lg">
               Optimiza los patrones de corte aplicando el método Búfalo para
               reducir el desperdicio de material. ¡Rápido y fácil!
            </p>
         </div>

         <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center transition-colors ${
               isDragActive
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-300 hover:border-green-500'
            }`}
         >
            <input {...getInputProps()} />

            <Button
               size="lg"
               className="bg-green-700 hover:bg-green-900 mb-4 text-lg px-8 py-6 h-auto rounded-2xl"
            >
               <Upload className="mr-2 h-5 w-5" />
               Seleccionar archivo XLSX/CSV
            </Button>

            <p className="text-gray-500">o arrastra y suelta el archivo aquí</p>

            {files.length > 0 && (
               <div className="mt-6 w-full">
                  <h3 className="font-medium mb-2 text-gray-400">
                     Archivo seleccionado:
                  </h3>
                  <ul className="space-y-2">
                     {files.map((file, index) => (
                        <li
                           key={index}
                           className="bg-gray-200 text-gray-400 p-3 rounded-lg text-sm flex items-center"
                        >
                           {file.name}
                        </li>
                     ))}
                  </ul>
               </div>
            )}
         </div>

         <div className="mt-8 text-center">
            {/* Mostrar nombre de archivo seleccionado como identificador */}
            {files.length > 0 && (
               <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Archivo seleccionado:</p>
                  <p className="text-lg font-semibold text-blue-700">
                     {files[0].name}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                     Este nombre se usará como identificador
                  </p>
               </div>
            )}

            {/* Selector de perfil */}
            <div className="mb-4">
               <label className="block mb-2 font-semibold text-gray-700">
                  Perfil de optimización
               </label>
               <select
                  value={perfil}
                  onChange={e => setPerfil(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-black"
                  disabled={loadingSendButton}
               >
                  <option value="rapido">Rápido (procesamiento rápido)</option>
                  <option value="balanceado">Balanceado (recomendado)</option>
                  <option value="profundo">Profundo (más ahorro de material)</option>
               </select>
            </div>

            <Button
               size="lg"
               onClick={handleSend}
               className="bg-blue-600 hover:bg-blue-800 text-lg px-8 py-4 rounded-lg"
               disabled={
                  files.length === 0 || loadingSendButton
               }
            >
               {loadingSendButton ? 'Procesando...' : 'Enviar'}
            </Button>

            {/* Barra de progreso */}
            {loadingSendButton && (
               <div className="mt-6 w-full">
                  {/* Indicador de conexión WebSocket */}
                  {!isConnected && (
                     <div className="mb-3 flex items-center justify-center text-orange-600 text-sm">
                        <WifiOff className="w-4 h-4 mr-2" />
                        <span>WebSocket desconectado - usando polling de respaldo</span>
                     </div>
                  )}
                  
                  <div className="flex items-center justify-between mb-2">
                     <span className="text-sm font-medium text-gray-700">
                        {getStateLabel(processingState)}
                     </span>
                     <span className="text-sm font-medium text-gray-700">
                        {progress}%
                     </span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                     <div
                        className="bg-blue-600 h-3 transition-all ease-out"
                        style={{ 
                           width: `${progress}%`,
                           opacity: isPulsing ? 0.5 : 1,
                           transition: 'width 0.5s ease-out, opacity 0.15s ease-in-out'
                        }}
                     />
                  </div>

                  {statusMessage && (
                     <p className="mt-2 text-sm text-gray-600">
                        {statusMessage}
                     </p>
                  )}

                  {(processingState === 'completed' || processingState === 'SUCCESS') && (
                     <div className="mt-4 flex items-center justify-center text-green-600">
                        <CheckCircle className="w-5 h-5 mr-2" />
                        <span>Redirigiendo a resultados...</span>
                     </div>
                  )}
               </div>
            )}

            {backendError && (
               <div className="mt-4 flex items-center justify-center text-red-600 font-semibold">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  {backendError}
               </div>
            )}
         </div>
      </div>
   );
}