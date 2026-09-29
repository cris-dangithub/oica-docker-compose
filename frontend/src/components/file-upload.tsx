'use client';
import { API_URL } from '@/lib/api';
import { CuttingOptions, initialCatalog, StockRow, Timing, TimingInfo } from './cutting-options';
import { PhysicalOptions, PhysicalParameters, ParameterMetadata } from './physical-options';

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Field, Select } from '@/components/ui/form-controls';
import { Progress } from '@/components/ui/progress';
import { ArrowRight, CheckCircle2, Clock3, FileSpreadsheet, Layers3, Upload } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { subscribeToTask, unsubscribeFromTask, TaskUpdate, onConnectionStatusChange } from '@/lib/socket';

export function FileUpload() {
   const [files, setFiles] = useState<File[]>([]);
   const [loadingSendButton, setLoadingSendButton] = useState(false);
   const [backendError, setBackendError] = useState<string | null>(null);
   const [perfil, setPerfil] = useState<string>('balanceado');
   const [catalog, setCatalog] = useState<StockRow[]>(initialCatalog);
   const [inventory, setInventory] = useState<File | null>(null);
   const [visuals, setVisuals] = useState(true);
   const [timing, setTiming] = useState<Timing | null>(null);
   const [estimating, setEstimating] = useState(false);
   const [metadata, setMetadata] = useState<ParameterMetadata | null>(null);
   const [parameters, setParameters] = useState<PhysicalParameters | null>(null);

   useEffect(() => {
      let active = true;
      fetch(`${API_URL}/parametros-corte`).then(async response => {
         if (!response.ok) throw new Error('No fue posible cargar los parámetros de corte. Recarga la página para reintentar.');
         const data: ParameterMetadata = await response.json();
         if (active) { setMetadata(data); setParameters(data.defaults); }
      }).catch(error => { if (active) setBackendError(String(error)); });
      return () => { active = false; };
   }, []);
   
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
   const estimateRevision = useRef(0);

   useEffect(() => {
      estimateRevision.current += 1;
      setTiming(null);
   }, [files, perfil, catalog, inventory, visuals, parameters]);

   const router = useRouter();

   const onDrop = useCallback(async (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
         setFiles(acceptedFiles);
      }
   }, []);

   const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
      onDrop,
      accept: {
         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
         'text/csv': ['.csv'],
      },
      maxFiles: 1,
      multiple: false,
      // El foco va al botón interno; el contenedor queda como zona de clic/arrastre.
      noKeyboard: true,
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
                  setTiming(data);
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
                     if (data.state === 'SUCCESS' || data.state === 'FAILURE' || data.state.startsWith('error_')) {
                        stopPolling();
                        setLoadingSendButton(false);
                        if (data.state === 'FAILURE' || data.state.startsWith('error_')) setBackendError(data.message || 'Procesamiento interrumpido');
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
      setTiming(data);
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

   const makeForm = () => {
      const form = new FormData();
      if (files[0]) form.append('file', files[0]);
      form.append('perfil', perfil);
      form.append('catalogo', JSON.stringify(catalog));
      form.append('visuales', String(visuals));
      if (!parameters) throw new Error('Espera a que carguen los parámetros de corte');
      form.append('parametros_corte', JSON.stringify(parameters));
      if (inventory) form.append('inventario', inventory);
      return form;
   };

   const estimateTime = async () => {
      const revision = estimateRevision.current;
      setEstimating(true);
      setBackendError(null);
      try {
         const response = await fetch(`${API_URL}/estimate`, { method: 'POST', body: makeForm() });
         const data = await response.json();
         if (!response.ok) throw new Error(data.error || 'No fue posible estimar');
         if (revision === estimateRevision.current) setTiming(data);
      } catch (error) {
         setBackendError(error instanceof Error ? error.message : String(error));
      } finally { setEstimating(false); }
   };

   const handleSend = async () => {
      console.log('CLICK ENVIAR');
      setBackendError(null);

      if (files.length === 0) {
         setBackendError('No hay archivos para enviar');
         return;
      }

      try {
         setLoadingSendButton(true);
         estimateRevision.current += 1;
         setTiming(null);
         setProgress(0);
         setStatusMessage('Subiendo archivo...');

         const formData = makeForm();

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
         // Estados en mayúscula emitidos por el worker (celery_worker.publish_progress) y por Celery.
         PENDING: 'En cola',
         STARTED: 'Iniciando',
         VALIDATING: 'Validando contenido',
         VALIDATED: 'Validación completada',
         PROCESSING: 'Procesando con algoritmo genético',
         GENERATING: 'Generando archivos de resultados',
         SUCCESS: '¡Procesamiento completado!',
         FAILURE: 'Procesamiento interrumpido',
      };
      return labels[state] || state;
   };

   const diameterCount = new Set(catalog.map(row => row.diametro).filter(Boolean)).size;

   return (
      <div className="mx-auto w-full max-w-wide px-4 py-10 sm:px-6 sm:py-12 lg:px-8">
         <header className="mb-8 max-w-narrow">
            <p className="mb-2 font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">
               Nueva optimización
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-content sm:text-4xl">
               Configurar optimización
            </h1>
            <p className="mt-3 text-base leading-7 text-content-muted sm:text-lg">
               Planifica cortes por etapas, reutiliza los sobrantes disponibles y conserva
               la trazabilidad de cada decisión del modelo.
            </p>
         </header>

         <div className="grid gap-6 lg:grid-cols-3 lg:items-start">
            <section className="space-y-6 lg:col-span-2" aria-label="Configuración de optimización">
               <Card
                  {...getRootProps()}
                  className={`flex min-h-56 cursor-pointer flex-col items-center justify-center border-2 border-dashed p-6 text-center transition-colors duration-standard sm:p-10 ${
                     isDragActive
                        ? 'border-line-focus bg-surface-interactive'
                        : 'border-line-strong hover:border-line-focus hover:bg-surface-interactive'
                  }`}
               >
                  <input {...getInputProps({ 'aria-label': 'Archivo de cartilla (XLSX o CSV)' })} />
                  <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-surface-interactive text-content-brand">
                     <Upload className="h-6 w-6" aria-hidden="true" />
                  </span>
                  <p className="font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">
                     Cartilla de trabajo
                  </p>
                  <h2 className="mt-2 text-lg font-semibold text-content">
                     {files.length ? 'Archivo listo para configurar' : 'Arrastra la cartilla o selecciona un archivo'}
                  </h2>
                  <p className="mt-2 text-sm text-content-muted">Formatos XLSX o CSV · un archivo por proyecto</p>
                  <Button
                     type="button"
                     variant="outline"
                     className="mt-5"
                     disabled={loadingSendButton}
                     onClick={event => { event.stopPropagation(); open(); }}
                  >
                     <FileSpreadsheet className="h-4 w-4" aria-hidden="true" />
                     {files.length ? 'Cambiar cartilla' : 'Seleccionar cartilla'}
                  </Button>
               </Card>

               {files.length > 0 && (
                  <Alert tone="info" title="Cartilla seleccionada">
                     <p className="break-all font-medium">{files[0].name}</p>
                     <p className="mt-1 text-xs">El nombre identificará este proyecto en el historial.</p>
                  </Alert>
               )}

               <Card className="p-5 sm:p-6">
                  <Field
                     label="Perfil de optimización"
                     htmlFor="optimization-profile"
                     description="Balanceado ofrece la mejor relación entre tiempo y exploración para la mayoría de cartillas."
                  >
                     <Select
                        id="optimization-profile"
                        value={perfil}
                        onChange={event => setPerfil(event.target.value)}
                        disabled={loadingSendButton}
                        aria-describedby="optimization-profile-description"
                     >
                        <option value="rapido">Rápido — menor tiempo de procesamiento</option>
                        <option value="balanceado">Balanceado — recomendado</option>
                        <option value="profundo">Profundo — mayor búsqueda, sin garantía de mejora</option>
                     </Select>
                  </Field>
               </Card>

               <CuttingOptions
                  catalog={catalog}
                  onCatalog={setCatalog}
                  onInventory={setInventory}
                  visuals={visuals}
                  onVisuals={setVisuals}
                  disabled={loadingSendButton || estimating}
               />

               {parameters && metadata ? (
                  <PhysicalOptions
                     value={parameters}
                     metadata={metadata}
                     onChange={setParameters}
                     disabled={loadingSendButton || estimating}
                  />
               ) : (
                  <Card className="p-5 text-sm text-content-muted">Cargando condiciones físicas…</Card>
               )}

               {backendError && <Alert tone="error" title="No fue posible continuar">{backendError}</Alert>}

               {timing && !loadingSendButton && <TimingInfo timing={timing} />}

               {loadingSendButton && (
                  <Card className={`p-5 sm:p-6 ${isPulsing ? 'opacity-80' : 'opacity-100'} transition-opacity duration-fast`}>
                     {!isConnected && (
                        <Alert tone="warning" className="mb-5">
                           WebSocket desconectado; OICA está usando el sondeo de respaldo.
                        </Alert>
                     )}
                     <Progress
                        value={progress}
                        label={getStateLabel(processingState) || 'Preparando procesamiento'}
                        detail={statusMessage || undefined}
                     />
                     <TimingInfo timing={timing} />
                     {(processingState === 'completed' || processingState === 'SUCCESS') && (
                        <div className="mt-4 flex items-center gap-2 text-sm font-semibold text-content-success">
                           <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
                           Redirigiendo a resultados…
                        </div>
                     )}
                  </Card>
               )}

               <div className="flex flex-col-reverse gap-3 border-t border-line pt-6 sm:flex-row sm:justify-end">
                  <Button
                     variant="outline"
                     disabled={!parameters || !files.length || loadingSendButton || estimating}
                     onClick={estimateTime}
                  >
                     <Clock3 className="h-4 w-4" aria-hidden="true" />
                     {estimating ? 'Consultando…' : 'Estimar tiempo'}
                  </Button>
                  <Button
                     size="lg"
                     onClick={handleSend}
                     disabled={!parameters || files.length === 0 || loadingSendButton}
                  >
                     {loadingSendButton ? 'Procesando…' : 'Iniciar optimización'}
                     {!loadingSendButton && <ArrowRight className="h-4 w-4" aria-hidden="true" />}
                  </Button>
               </div>
            </section>

            <aside className="lg:sticky lg:top-24" aria-label="Resumen de ejecución">
               <Card className="overflow-hidden">
                  <div className="border-b border-line p-5 sm:p-6">
                     <p className="font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">
                        Antes de comenzar
                     </p>
                     <div className="mt-2 flex items-start justify-between gap-4">
                        <h2 className="text-xl font-semibold text-content">Resumen de ejecución</h2>
                        <Badge tone={files.length ? 'success' : 'neutral'}>
                           {files.length ? 'Configurando' : 'Borrador'}
                        </Badge>
                     </div>
                     <p className="mt-3 text-sm leading-6 text-content-muted">
                        OICA procesará los grupos en orden y conservará los saldos reutilizables.
                     </p>
                  </div>

                  <div className="grid grid-cols-3 gap-2 border-b border-line p-5 sm:p-6">
                     {[
                        { value: String(diameterCount).padStart(2, '0'), label: 'diámetros' },
                        { value: String(catalog.length).padStart(2, '0'), label: 'longitudes' },
                        { value: visuals ? 'ON' : 'OFF', label: 'visuales' },
                     ].map(metric => (
                        <div key={metric.label} className="rounded-md border border-line bg-surface-interactive p-3">
                           <p className="font-mono text-lg font-semibold tabular-nums text-content-brand">{metric.value}</p>
                           <p className="mt-1 text-xs text-content-muted">{metric.label}</p>
                        </div>
                     ))}
                  </div>

                  <div className="p-5 sm:p-6">
                     <p className="mb-4 font-mono text-xs font-semibold uppercase tracking-widest text-content-muted">
                        Secuencia de trabajo
                     </p>
                     <ol className="space-y-3">
                        {[
                           ['01', 'Validar cartilla', 'estructura y demanda'],
                           ['02', 'Optimizar cortes', 'por diámetro y etapa'],
                           ['03', 'Generar resultados', 'Excel, PDF e inventario'],
                        ].map(([number, title, detail]) => (
                           <li key={number} className="flex gap-3 rounded-md bg-surface-subtle p-3">
                              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-status-info-border bg-status-info-bg font-mono text-xs font-semibold text-status-info-text">
                                 {number}
                              </span>
                              <div>
                                 <p className="text-sm font-semibold text-content">{title}</p>
                                 <p className="mt-1 font-mono text-xs text-content-muted">{detail}</p>
                              </div>
                           </li>
                        ))}
                     </ol>
                     <div className="mt-5 flex items-start gap-3 border-t border-line pt-5 text-xs leading-5 text-content-muted">
                        <Layers3 className="mt-0.5 h-4 w-4 shrink-0 text-content-brand" aria-hidden="true" />
                        Los parámetros quedan guardados con cada versión para asegurar trazabilidad.
                     </div>
                  </div>
               </Card>
            </aside>
         </div>
      </div>
   );
}
