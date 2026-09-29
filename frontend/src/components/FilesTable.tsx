'use client';
import { API_URL } from '@/lib/api';
/**
 * Componente de tabla de archivos procesados con filtros y acciones.
 *
 * Features:
 * - 4 filtros: búsqueda, estado, perfil, rango de fechas
 * - Descargas por archivo (Excel, PDF, Imagen, Inventario final)
 * - Eliminar y reprocesar con diálogos de confirmación
 * - Paginación
 * - Actualizaciones en tiempo real vía WebSocket para archivos en procesamiento
 * - Tabla en desktop y tarjetas en mobile/tablet
 */


import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Download, FileSpreadsheet, FolderOpen, Plus, RefreshCw, Search, SlidersHorizontal, Trash2 } from 'lucide-react';
import { Alert } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog } from '@/components/ui/dialog';
import { Field, Input, Select } from '@/components/ui/form-controls';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
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

type Tone = 'neutral' | 'info' | 'success' | 'warning' | 'error';

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

const STATUS_TONES: Record<string, Tone> = {
  pending: 'info',
  uploaded: 'neutral',
  validating: 'info',
  validated: 'neutral',
  processing: 'info',
  generating_artifacts: 'info',
  completed: 'success',
  error_validation: 'error',
  error_processing: 'error',
  error_generation: 'error',
};

const PERFILES = [
  { value: 'rapido', label: 'Rápido' },
  { value: 'balanceado', label: 'Balanceado' },
  { value: 'profundo', label: 'Profundo' },
];

const PERFIL_LABELS: Record<string, string> = Object.fromEntries(PERFILES.map(p => [p.value, p.label]));

const isInProgress = (status: string) =>
  status === 'processing' || status === 'validating' || status === 'generating_artifacts';

// El backend rechaza eliminar/reprocesar mientras hay una ejecución activa (409).
const isActive = (status: string) => status === 'pending' || isInProgress(status);

const responseError = async (response: Response, fallback: string) => {
  const data = await response.json().catch(() => null);
  return data?.details ? `${data.error ?? fallback}: ${data.details}` : (data?.error ?? fallback);
};

const formatDate = (value: string) =>
  new Date(value).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });

const kg = (value?: number) => (value != null ? `${value.toFixed(3)} kg` : '—');

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

  // Diálogos y avisos (sustituyen confirm/prompt/alert nativos)
  const [pendingDelete, setPendingDelete] = useState<UploadedFile | null>(null);
  const [pendingReprocess, setPendingReprocess] = useState<UploadedFile | null>(null);
  const [newPerfil, setNewPerfil] = useState('balanceado');
  const [busy, setBusy] = useState(false);
  const [dialogError, setDialogError] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ tone: 'success' | 'error'; text: string } | null>(null);

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

  const openDelete = (file: UploadedFile) => {
    setDialogError(null);
    setPendingDelete(file);
  };

  const openReprocess = (file: UploadedFile) => {
    setDialogError(null);
    setNewPerfil(file.perfil || 'balanceado');
    setPendingReprocess(file);
  };

  const handleDelete = async () => {
    if (!pendingDelete) return;
    setBusy(true);
    setDialogError(null);

    try {
      const response = await fetch(`${apiUrl}/file/${pendingDelete.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(await responseError(response, 'Error al eliminar archivo'));
      }

      setNotice({ tone: 'success', text: `Se eliminó «${pendingDelete.filename}» y todas sus versiones.` });
      setPendingDelete(null);
      // Recargar lista
      loadFiles();
    } catch (err) {
      setDialogError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setBusy(false);
    }
  };

  const handleReprocess = async () => {
    if (!pendingReprocess) return;
    setBusy(true);
    setDialogError(null);

    try {
      const response = await fetch(`${apiUrl}/reprocess/${pendingReprocess.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ perfil: newPerfil }),
      });

      if (!response.ok) {
        throw new Error(await responseError(response, 'Error al reprocesar archivo'));
      }

      const data = await response.json();
      setNotice({
        tone: 'success',
        text: `«${pendingReprocess.filename}» quedó en cola con perfil ${PERFIL_LABELS[newPerfil]}. Tarea: ${data.task_id}`,
      });
      setPendingReprocess(null);

      // Recargar después de 2 segundos
      setTimeout(() => loadFiles(), 2000);
    } catch (err) {
      setDialogError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setBusy(false);
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

  const activeFilters = [searchTerm, statusFilter, perfilFilter, dateFrom, dateTo].filter(Boolean).length;

  const renderStatus = (file: UploadedFile) => {
    const progress = fileProgress.get(file.id) || 0;
    return (
      <div className="space-y-2">
        <Badge tone={STATUS_TONES[file.status] || 'neutral'}>
          {STATUS_LABELS[file.status] || file.status}
        </Badge>
        {/* Barra de progreso en tiempo real para archivos en procesamiento */}
        {isInProgress(file.status) && (
          <Progress
            value={progress}
            label={`Progreso de ${file.filename}`}
            hideLabel
            className={cn('max-w-48 transition-opacity duration-fast', pulsing.has(file.id) ? 'opacity-60' : 'opacity-100')}
          />
        )}
      </div>
    );
  };

  const renderPerfil = (file: UploadedFile) => file.perfil ? (
    <Badge tone="info">{PERFIL_LABELS[file.perfil] || file.perfil}</Badge>
  ) : (
    <span className="text-sm italic text-content-muted">Sin procesar</span>
  );

  const renderMetrics = (result?: ProcessingResult) => {
    if (!result) return null;
    return (
      <div className="mt-1 space-y-1 text-xs text-content-muted">
        <p>
          <span className="font-mono">{result.motor?.startsWith('secuencial-') ? result.motor : 'Histórico'}</span>
          {' · '}v{result.version_number}
        </p>
        {result.motor === 'secuencial-2' && (
          <p className="font-mono tabular-nums">
            Corte {kg(result.perdida_corte_kg)} · Descartado {kg(result.descartado_kg)} · Reutilizable final {kg(result.sobrante_final_kg)}
          </p>
        )}
      </div>
    );
  };

  const renderWaste = (result?: ProcessingResult) => result?.desperdicio_porcentaje != null ? (
    <span className="font-mono text-sm font-semibold tabular-nums text-content">
      {result.desperdicio_porcentaje.toFixed(3)}%
      <span className="block text-xs font-normal text-content-muted">en masa</span>
    </span>
  ) : (
    <span className="text-sm text-content-muted">—</span>
  );

  const renderActions = (file: UploadedFile, align: 'start' | 'end') => {
    const latestResult = file.processing_results?.[0];
    return (
      <div className={cn('flex gap-2', align === 'end' ? 'items-center justify-end' : 'flex-wrap justify-start')}>
        {latestResult && (
          <div role="group" aria-label={`Descargas de ${file.filename}`} className={cn('flex gap-2', align === 'start' && 'flex-wrap')}>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleDownload(latestResult.storage_uuid, 'excel')}
              disabled={!latestResult.excel_path}
              aria-label={`Descargar Excel de ${file.filename}`}
            >
              <Download className="h-4 w-4" aria-hidden="true" />
              Excel
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleDownload(latestResult.storage_uuid, 'pdf')}
              disabled={!latestResult.pdf_path}
              aria-label={`Descargar PDF de ${file.filename}`}
            >
              <Download className="h-4 w-4" aria-hidden="true" />
              PDF
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleDownload(latestResult.storage_uuid, 'imagen')}
              disabled={!latestResult.graph_image_path && !latestResult.image_path}
              aria-label={`Descargar imagen de ${file.filename}`}
            >
              <Download className="h-4 w-4" aria-hidden="true" />
              Imagen
            </Button>
            {latestResult.inventory_path && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleDownload(latestResult.storage_uuid, 'inventario')}
                aria-label={`Descargar inventario final de ${file.filename}`}
              >
                <Download className="h-4 w-4" aria-hidden="true" />
                Inventario
              </Button>
            )}
          </div>
        )}
        <div className={cn('flex gap-1', align === 'end' && 'border-l border-line pl-2')}>
          <Button
            size="icon"
            variant="ghost"
            className="h-8 w-8"
            onClick={() => openReprocess(file)}
            disabled={isActive(file.status)}
            aria-label={`Reprocesar ${file.filename}`}
            title={isActive(file.status) ? 'Disponible al terminar la ejecución' : 'Reprocesar'}
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            className="h-8 w-8 hover:bg-status-error-bg hover:text-content-error"
            onClick={() => openDelete(file)}
            disabled={isActive(file.status)}
            aria-label={`Eliminar ${file.filename}`}
            title={isActive(file.status) ? 'Disponible al terminar la ejecución' : 'Eliminar'}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    );
  };

  const firstItem = total === 0 ? 0 : (page - 1) * perPage + 1;

  return (
    <>
    <div className="w-full space-y-6">
      {/* Filtros */}
      <Card className="p-5 sm:p-6">
        <div className="mb-5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-5 w-5 text-content-brand" aria-hidden="true" />
            <h2 className="text-base font-semibold text-content">Filtros</h2>
            {activeFilters > 0 && <Badge tone="info">{activeFilters} activos</Badge>}
          </div>
          <Button onClick={resetFilters} variant="ghost" size="sm" disabled={activeFilters === 0}>
            Limpiar filtros
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-5">
          <Field label="Buscar" htmlFor="filter-search" className="col-span-2 lg:col-span-1">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-content-muted" aria-hidden="true" />
              <Input
                id="filter-search"
                type="search"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(1);
                }}
                placeholder="Nombre o documento"
                className="pl-9"
              />
            </div>
          </Field>

          <Field label="Estado" htmlFor="filter-status">
            <Select
              id="filter-status"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos</option>
              <option value="uploaded">Cargado</option>
              <option value="validating">Validando</option>
              <option value="processing">Procesando</option>
              <option value="completed">Completado</option>
              <option value="error_validation">Error de validación</option>
              <option value="error_processing">Error de procesamiento</option>
            </Select>
          </Field>

          <Field label="Perfil" htmlFor="filter-perfil">
            <Select
              id="filter-perfil"
              value={perfilFilter}
              onChange={(e) => {
                setPerfilFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos</option>
              {PERFILES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </Select>
          </Field>

          <Field label="Desde" htmlFor="filter-from">
            <Input
              id="filter-from"
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value);
                setPage(1);
              }}
            />
          </Field>

          <Field label="Hasta" htmlFor="filter-to">
            <Input
              id="filter-to"
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value);
                setPage(1);
              }}
            />
          </Field>
        </div>
      </Card>

      {notice && (
        <Alert tone={notice.tone} className="items-start">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <p className="break-words">{notice.text}</p>
            <button type="button" className="text-xs font-semibold underline underline-offset-4" onClick={() => setNotice(null)}>
              Descartar
            </button>
          </div>
        </Alert>
      )}

      {/* Resultados */}
      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-4 sm:px-6">
          <h2 className="text-base font-semibold text-content">
            Proyectos <span className="font-mono text-sm font-normal text-content-muted">({total})</span>
          </h2>
          <Button variant="ghost" size="sm" onClick={loadFiles} disabled={loading}>
            <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} aria-hidden="true" />
            Actualizar
          </Button>
        </div>

        <div aria-live="polite" aria-busy={loading}>
        {loading && files.length === 0 ? (
          <div className="flex items-center justify-center gap-3 p-10 text-sm text-content-muted">
            <RefreshCw className="h-4 w-4 animate-spin" aria-hidden="true" />
            Cargando proyectos…
          </div>
        ) : error ? (
          <div className="p-5 sm:p-6">
            <Alert tone="error" title="No fue posible cargar los proyectos">
              <p>{error}</p>
              <Button size="sm" variant="outline" className="mt-3" onClick={loadFiles}>Reintentar</Button>
            </Alert>
          </div>
        ) : files.length === 0 ? (
          <div className="flex flex-col items-center px-6 py-12 text-center">
            <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-surface-interactive text-content-brand">
              <FolderOpen className="h-6 w-6" aria-hidden="true" />
            </span>
            <p className="font-semibold text-content">
              {activeFilters ? 'Ningún proyecto coincide con los filtros' : 'Aún no hay proyectos'}
            </p>
            <p className="mt-1 max-w-sm text-sm text-content-muted">
              {activeFilters
                ? 'Ajusta o limpia los filtros para ver más resultados.'
                : 'Sube una cartilla de trabajo para crear la primera optimización.'}
            </p>
            {activeFilters ? (
              <Button variant="outline" className="mt-5" onClick={resetFilters}>Limpiar filtros</Button>
            ) : (
              <Link href="/subir-cartilla" className={buttonVariants({ className: 'mt-5' })}>
                <Plus className="h-4 w-4" aria-hidden="true" />
                Nueva optimización
              </Link>
            )}
          </div>
        ) : (
          <>
            {/* Desktop: tabla */}
            <div className="hidden overflow-x-auto lg:block">
              <table className="w-full text-left">
                <caption className="sr-only">Proyectos procesados</caption>
                <thead className="border-b border-line bg-surface-subtle">
                  <tr className="text-xs font-semibold text-content-muted">
                    <th scope="col" className="px-6 py-3">Proyecto</th>
                    <th scope="col" className="px-4 py-3">Perfil</th>
                    <th scope="col" className="px-4 py-3">Estado</th>
                    <th scope="col" className="px-4 py-3">Desperdicio</th>
                    <th scope="col" className="px-6 py-3 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {files.map((file) => {
                    const latestResult = file.processing_results?.[0];
                    return (
                      <tr key={file.id} className="align-top transition-colors duration-fast hover:bg-surface-subtle">
                        <td className="min-w-64 px-6 py-4">
                          <div className="flex items-start gap-3">
                            <FileSpreadsheet className="mt-0.5 h-5 w-5 shrink-0 text-content-brand" aria-hidden="true" />
                            <div className="min-w-0">
                              <p className="break-all text-sm font-semibold text-content">{file.filename}</p>
                              <p className="font-mono text-xs text-content-muted">
                                Doc. {file.document_number || '—'} · {formatDate(file.created_at)}
                              </p>
                              {renderMetrics(latestResult)}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4">{renderPerfil(file)}</td>
                        <td className="px-4 py-4">{renderStatus(file)}</td>
                        <td className="px-4 py-4">{renderWaste(latestResult)}</td>
                        <td className="whitespace-nowrap px-6 py-4">{renderActions(file, 'end')}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile/tablet: tarjetas */}
            <ul className="divide-y divide-line lg:hidden" aria-label="Proyectos procesados">
              {files.map((file) => {
                const latestResult = file.processing_results?.[0];
                return (
                  <li key={file.id} className="space-y-4 p-5 sm:p-6">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="break-all text-sm font-semibold text-content">{file.filename}</p>
                        <p className="font-mono text-xs text-content-muted">
                          Doc. {file.document_number || '—'} · {formatDate(file.created_at)}
                        </p>
                      </div>
                      {renderPerfil(file)}
                    </div>
                    <div className="grid grid-cols-2 gap-3 rounded-md bg-surface-subtle p-3">
                      <div>
                        <p className="mb-1 text-xs font-semibold text-content-muted">Estado</p>
                        {renderStatus(file)}
                      </div>
                      <div>
                        <p className="mb-1 text-xs font-semibold text-content-muted">Desperdicio</p>
                        {renderWaste(latestResult)}
                      </div>
                    </div>
                    {renderMetrics(latestResult)}
                    {renderActions(file, 'start')}
                  </li>
                );
              })}
            </ul>

            {/* Paginación */}
            <nav
              aria-label="Paginación de proyectos"
              className="flex flex-col gap-3 border-t border-line bg-surface-subtle px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6"
            >
              <p className="text-sm text-content-muted">
                Mostrando <span className="font-mono font-semibold text-content">{firstItem}–{Math.min(page * perPage, total)}</span>{' '}
                de <span className="font-mono font-semibold text-content">{total}</span>
              </p>

              <div className="flex items-center gap-2">
                <Button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  variant="outline"
                  size="sm"
                >
                  Anterior
                </Button>
                <span className="px-2 font-mono text-sm text-content-muted" aria-current="page">
                  {page} / {totalPages}
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
            </nav>
          </>
        )}
        </div>
      </Card>
    </div>

      {/* Fuera del contenedor space-y: sus márgenes anularían el centrado del modal. */}
      <Dialog
        open={pendingDelete !== null}
        onClose={() => !busy && setPendingDelete(null)}
        title="Eliminar proyecto"
        description={pendingDelete && <>Se eliminarán <strong className="break-all text-content">{pendingDelete.filename}</strong> y todas sus versiones. Esta acción no se puede deshacer.</>}
        footer={<>
          <Button variant="outline" onClick={() => setPendingDelete(null)} disabled={busy}>Cancelar</Button>
          <Button variant="destructive" onClick={handleDelete} loading={busy}>
            <Trash2 className="h-4 w-4" aria-hidden="true" />
            Eliminar
          </Button>
        </>}
      >
        {dialogError && <Alert tone="error">{dialogError}</Alert>}
      </Dialog>

      <Dialog
        open={pendingReprocess !== null}
        onClose={() => !busy && setPendingReprocess(null)}
        title="Reprocesar proyecto"
        description={pendingReprocess && <>Se creará una nueva versión de <strong className="break-all text-content">{pendingReprocess.filename}</strong>. Perfil actual: {PERFIL_LABELS[pendingReprocess.perfil] || 'ninguno'}.</>}
        footer={<>
          <Button variant="outline" onClick={() => setPendingReprocess(null)} disabled={busy}>Cancelar</Button>
          <Button onClick={handleReprocess} loading={busy}>
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Reprocesar
          </Button>
        </>}
      >
        <div className="space-y-4">
          <Field label="Perfil de optimización" htmlFor="reprocess-perfil">
            <Select id="reprocess-perfil" value={newPerfil} onChange={e => setNewPerfil(e.target.value)} disabled={busy}>
              {PERFILES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </Select>
          </Field>
          {dialogError && <Alert tone="error">{dialogError}</Alert>}
        </div>
      </Dialog>
    </>
  );
}
