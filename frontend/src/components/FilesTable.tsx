'use client';
import { API_URL } from '@/lib/api';
/**
 * Componente de tabla de archivos procesados con filtros y acciones.
 * 
 * Features:
 * - 4 filtros: búsqueda, estado, perfil, rango de fechas
 * - 3 botones de descarga por archivo (Excel, PDF, Imagen)
 * - Botón de eliminar
 * - Botón de reprocesar
 * - Paginación
 * - Actualizaciones en tiempo real vía WebSocket para archivos en procesamiento
 */


import React, { useState, useEffect, useCallback } from 'react';
import { Download, Trash2, RefreshCw, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { subscribeToTask, unsubscribeFromTask, TaskUpdate } from '@/lib/socket';

interface ProcessingResult {
  inventory_path?: string;
  motor?: string;
  desperdicio_porcentaje?: number;
  perdida_corte_kg?: number;
  descartado_kg?: number;
  sobrante_final_kg?: number;
  version_number: number;
  storage_uuid: string;
  status: string;
  excel_path?: string;
  pdf_path?: string;
  image_path?: string;
  graph_image_path?: string;
  created_at: string;
}

interface UploadedFile {
  task_id?: string;
  id: number;
  filename: string;
  document_number: string;
  perfil: string;
  status: string;
  created_at: string;
  updated_at: string;
  processing_results?: ProcessingResult[];
  current_progress?: number;  // Progreso actual de Redis (0-100)
  current_state?: string;      // Estado actual del worker
  current_message?: string;    // Mensaje descriptivo del progreso
}

interface FilesTableProps {
  apiUrl?: string;
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'En cola',
  uploaded: 'Cargado',
  validating: 'Validando',
  validated: 'Validado',
  processing: 'Procesando',
  generating_artifacts: 'Generando',
  completed: 'Completado',
  error_validation: 'Error: Validación',
  error_processing: 'Error: Procesamiento',
  error_generation: 'Error: Generación',
};

const STATUS_COLORS: Record<string, string> = {
  uploaded: 'bg-blue-100 text-blue-800',
  validating: 'bg-yellow-100 text-yellow-800',
  validated: 'bg-green-100 text-green-800',
  processing: 'bg-purple-100 text-purple-800',
  generating_artifacts: 'bg-indigo-100 text-indigo-800',
  completed: 'bg-green-500 text-white',
  error_validation: 'bg-red-100 text-red-800',
  error_processing: 'bg-red-100 text-red-800',
  error_generation: 'bg-red-100 text-red-800',
};

export default function FilesTable({ apiUrl = API_URL }: FilesTableProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Map para rastrear progreso en tiempo real de archivos en procesamiento
  const [fileProgress, setFileProgress] = useState<Map<number, number>>(new Map());
  const [pulsing, setPulsing] = useState<Set<number>>(new Set());
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [perfilFilter, setPerfilFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  
  // Paginación
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  const loadFiles = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
      });

      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);
      if (perfilFilter) params.append('perfil', perfilFilter);
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const response = await fetch(`${apiUrl}/files?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setFiles(data.files);
      setTotal(data.total);
      setTotalPages(data.pages);
      
      // Inicializar fileProgress con el progreso actual del backend
      const progressMap = new Map<number, number>();
      data.files.forEach((file: UploadedFile) => {
        if (file.current_progress !== undefined) {
          progressMap.set(file.id, file.current_progress);
        }
      });
      setFileProgress(progressMap);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar archivos');
      console.error('Error loading files:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, page, searchTerm, statusFilter, perfilFilter, dateFrom, dateTo]);


  // Cargar archivos
  useEffect(() => {
    loadFiles();
  }, [loadFiles]);
  
  // Suscribirse a actualizaciones en tiempo real de archivos en procesamiento
  useEffect(() => {
    const processingFiles = files.filter(file => 
      file.status === 'pending' || file.status === 'processing' ||
      file.status === 'validating' ||
      file.status === 'generating_artifacts'
    );
    
    // Suscribirse a cada archivo en procesamiento
    processingFiles.forEach(file => {
      const taskId = file.task_id || `process_${file.id}`;
      subscribeToTask(taskId, (data: TaskUpdate) => {
        console.log(`[FilesTable] Update para file ${file.id}:`, data);
        
        // Activar parpadeo
        setPulsing(prev => new Set(prev).add(file.id));
        setTimeout(() => {
          setPulsing(prev => {
            const newSet = new Set(prev);
            newSet.delete(file.id);
            return newSet;
          });
        }, 300);
        
        // Actualizar progreso
        setFileProgress(prev => new Map(prev).set(file.id, data.progress || 0));
        
        // Si completó o falló, recargar tabla después de 2 segundos
        if (data.state === 'SUCCESS' || data.state === 'FAILURE' || 
            data.state === 'completed' || data.state.startsWith('error_')) {
          setTimeout(() => {
            loadFiles();
          }, 2000);
        }
      });
    });
    
    // Cleanup: desuscribirse al cambiar la lista
    return () => {
      processingFiles.forEach(file => {
        unsubscribeFromTask(file.task_id || `process_${file.id}`);
      });
    };
  }, [files, loadFiles]);

  const handleDelete = async (fileId: number) => {
    if (!confirm('¿Estás seguro de eliminar este archivo y todas sus versiones?')) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/file/${fileId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Error al eliminar archivo');
      }

      // Recargar lista
      loadFiles();
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Error inesperado'}`);
    }
  };

  const handleReprocess = async (fileId: number, currentPerfil: string) => {
    const newPerfil = prompt(
      `Selecciona nuevo perfil (actual: ${currentPerfil || 'ninguno'}):\n\nOpciones: rapido, balanceado, profundo`,
      currentPerfil || 'balanceado'
    );

    if (!newPerfil || !['rapido', 'balanceado', 'profundo'].includes(newPerfil)) {
      alert('Perfil inválido. Opciones válidas: rapido, balanceado, profundo');
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/reprocess/${fileId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ perfil: newPerfil }),
      });

      if (!response.ok) {
        throw new Error('Error al reprocesar archivo');
      }

      const data = await response.json();
      alert(`Archivo encolado para reprocesamiento. Task ID: ${data.task_id}`);
      
      // Recargar después de 2 segundos
      setTimeout(() => loadFiles(), 2000);
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Error inesperado'}`);
    }
  };

  const handleDownload = (uuid: string, type: 'excel' | 'pdf' | 'imagen' | 'inventario') => {
    const url = `${apiUrl}/descargar-${type}/${uuid}`;
    window.open(url, '_blank');
  };

  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setPerfilFilter('');
    setDateFrom('');
    setDateTo('');
    setPage(1);
  };

  return (
    <div className="w-full space-y-6">
      {/* Filtros */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Filtros</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Búsqueda */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Buscar
            </label>
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(1);
                }}
                placeholder="Nombre o documento..."
                className="w-full px-3 py-2 border rounded-md pl-10"
              />
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
            </div>
          </div>

          {/* Estado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado
            </label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="">Todos</option>
              <option value="uploaded">Cargado</option>
              <option value="validating">Validando</option>
              <option value="processing">Procesando</option>
              <option value="completed">Completado</option>
              <option value="error_validation">Error Validación</option>
              <option value="error_processing">Error Procesamiento</option>
            </select>
          </div>

          {/* Perfil */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Perfil
            </label>
            <select
              value={perfilFilter}
              onChange={(e) => {
                setPerfilFilter(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="">Todos</option>
              <option value="rapido">Rápido</option>
              <option value="balanceado">Balanceado</option>
              <option value="profundo">Profundo</option>
            </select>
          </div>

          {/* Fecha Desde */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Desde
            </label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          {/* Fecha Hasta */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Hasta
            </label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          {/* Botón Limpiar */}
          <div className="flex items-end">
            <Button
              onClick={resetFilters}
              variant="outline"
              className="w-full"
            >
              Limpiar Filtros
            </Button>
          </div>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">
            Cargando archivos...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">
            Error: {error}
          </div>
        ) : files.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No se encontraron archivos
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Archivo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Documento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Perfil
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {files.map((file) => {
                    const latestResult = file.processing_results?.[0];
                    const hasResults = Boolean(latestResult);

                    return (
                      <tr key={file.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {file.filename}
                          {latestResult && <div className="text-xs text-gray-500">
                            {latestResult.motor?.startsWith('secuencial-') ? latestResult.motor : 'Histórico'}
                            {latestResult.desperdicio_porcentaje != null && ` · Desperdicio: ${latestResult.desperdicio_porcentaje.toFixed(3)}% en masa`}
                            {latestResult.motor === 'secuencial-2' && <div>
                              Corte: {latestResult.perdida_corte_kg?.toFixed(3)} kg · Descartado: {latestResult.descartado_kg?.toFixed(3)} kg · Reutilizable final: {latestResult.sobrante_final_kg?.toFixed(3)} kg
                            </div>}
                          </div>}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {file.document_number || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {file.perfil ? (
                            <span className="capitalize px-2 py-1 bg-blue-50 text-blue-700 rounded-md">
                              {file.perfil}
                            </span>
                          ) : (
                            <span className="text-gray-400 italic">Sin procesar</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="space-y-1">
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              STATUS_COLORS[file.status] || 'bg-gray-100 text-gray-800'
                            }`}>
                              {STATUS_LABELS[file.status] || file.status}
                            </span>
                            
                            {/* Barra de progreso en tiempo real para archivos en procesamiento */}
                            {(file.status === 'processing' || file.status === 'validating' || file.status === 'generating_artifacts') && (
                              <div className="mt-2 w-full">
                                <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                                  <span>Progreso</span>
                                  <span>{fileProgress.get(file.id) || 0}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                  <div
                                    className="bg-blue-600 h-2 transition-all ease-out"
                                    style={{ 
                                      width: `${fileProgress.get(file.id) || 0}%`,
                                      opacity: pulsing.has(file.id) ? 0.5 : 1,
                                      transitionDuration: '500ms, 150ms',
                                      transitionProperty: 'width, opacity'
                                    }}
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(file.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          {hasResults && latestResult && (
                            <>
                              {latestResult.inventory_path && <Button size="sm" variant="outline"
                                onClick={() => handleDownload(latestResult.storage_uuid, 'inventario')}>
                                Inventario final
                              </Button>}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDownload(latestResult.storage_uuid, 'excel')}
                                title="Descargar Excel"
                                disabled={!latestResult.excel_path}
                              >
                                <Download className="w-4 h-4 mr-1" />
                                Excel
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDownload(latestResult.storage_uuid, 'pdf')}
                                title="Descargar PDF"
                                disabled={!latestResult.pdf_path}
                              >
                                <Download className="w-4 h-4 mr-1" />
                                PDF
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDownload(latestResult.storage_uuid, 'imagen')}
                                title="Descargar Imagen"
                                disabled={!latestResult.graph_image_path && !latestResult.image_path}
                              >
                                <Download className="w-4 h-4 mr-1" />
                                IMG
                              </Button>
                            </>
                          )}
                          
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleReprocess(file.id, file.perfil)}
                            title="Reprocesar"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </Button>
                          
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDelete(file.id)}
                            title="Eliminar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Paginación */}
            <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t">
              <div className="text-sm text-gray-700">
                Mostrando <span className="font-medium">{(page - 1) * perPage + 1}</span> a{' '}
                <span className="font-medium">
                  {Math.min(page * perPage, total)}
                </span>{' '}
                de <span className="font-medium">{total}</span> resultados
              </div>

              <div className="flex space-x-2">
                <Button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  variant="outline"
                  size="sm"
                >
                  Anterior
                </Button>
                
                <span className="px-4 py-2 text-sm">
                  Página {page} de {totalPages}
                </span>
                
                <Button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  variant="outline"
                  size="sm"
                >
                  Siguiente
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
