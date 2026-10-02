'use client';
/**
 * Detalle de un proyecto (spec 001, contracts/ui.md): verificación, admisibilidad, compra,
 * calidad del plan, avisos y comparación de versiones. Los datos vienen de GET /file/<id>.
 */
import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import { Alert } from '@/components/ui/alert';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Field, Select } from '@/components/ui/form-controls';
import { API_URL } from '@/lib/api';
import AdmissibilitySection from './AdmissibilitySection';
import MassWarnings from './MassWarnings';
import PurchaseSummary from './PurchaseSummary';
import QualitySection from './QualitySection';
import { ArchivoDetalle, PERFIL_LABELS, pct } from './types';
import VerificationBanner from './VerificationBanner';
import VersionsTable from './VersionsTable';

interface FileDetailProps {
   id: string;
}

const formatDate = (value: string) =>
   new Date(value).toLocaleString('es-CO', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

export default function FileDetail({ id }: FileDetailProps) {
   const [file, setFile] = useState<ArchivoDetalle | null>(null);
   const [loading, setLoading] = useState(true);
   const [error, setError] = useState<string | null>(null);
   const [notFound, setNotFound] = useState(false);
   const [selected, setSelected] = useState<number | null>(null);

   const load = useCallback(async () => {
      setLoading(true);
      setError(null);
      try {
         const response = await fetch(`${API_URL}/file/${encodeURIComponent(id)}`);
         if (response.status === 404) {
            setNotFound(true);
            return;
         }
         if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
         const data: ArchivoDetalle = await response.json();
         setFile(data);
         // Las versiones llegan de la más reciente a la más antigua.
         setSelected(current => current ?? data.processing_results?.[0]?.version_number ?? null);
      } catch (err) {
         setError(err instanceof Error ? err.message : 'Error al cargar el proyecto');
      } finally {
         setLoading(false);
      }
   }, [id]);

   useEffect(() => {
      load();
   }, [load]);

   const versions = file?.processing_results ?? [];
   const version = versions.find(v => v.version_number === selected) ?? versions[0];

   return (
      <div className="mx-auto w-full max-w-wide px-4 py-10 sm:px-6 sm:py-12 lg:px-8">
         <Link href="/archivos" className={buttonVariants({ variant: 'ghost', size: 'sm', className: 'mb-6' })}>
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Volver a proyectos
         </Link>

         <div aria-live="polite" aria-busy={loading}>
            {loading && !file ? (
               <div className="flex items-center gap-3 text-sm text-content-muted">
                  <RefreshCw className="h-4 w-4 animate-spin" aria-hidden="true" />
                  Cargando proyecto…
               </div>
            ) : notFound ? (
               <Alert tone="warning" title="Proyecto no encontrado">
                  <p>El proyecto no existe o fue eliminado.</p>
               </Alert>
            ) : error ? (
               <Alert tone="error" title="No fue posible cargar el proyecto">
                  <p>{error}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={load}>Reintentar</Button>
               </Alert>
            ) : file ? (
               <div className="space-y-6">
                  <header className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                     <div className="min-w-0">
                        <p className="mb-2 font-mono text-xs font-semibold uppercase tracking-widest text-content-brand">
                           Detalle del proyecto
                        </p>
                        <h1 className="break-all text-2xl font-semibold tracking-tight text-content sm:text-3xl">
                           {file.filename}
                        </h1>
                        <p className="mt-2 font-mono text-xs text-content-muted">
                           Cargado {formatDate(file.created_at)} · Desperdicio admisible vigente:{' '}
                           {file.umbral_desperdicio_pct != null ? pct(file.umbral_desperdicio_pct, 2) : 'sin umbral'}
                        </p>
                     </div>
                     {versions.length > 0 && (
                        <Field label="Versión" htmlFor="detalle-version" className="sm:w-64">
                           <Select
                              id="detalle-version"
                              value={version?.version_number ?? ''}
                              onChange={e => setSelected(Number(e.target.value))}
                           >
                              {versions.map(v => (
                                 <option key={v.version_number} value={v.version_number}>
                                    v{v.version_number} · {PERFIL_LABELS[v.perfil_usado ?? ''] ?? v.perfil_usado ?? 'sin perfil'}
                                 </option>
                              ))}
                           </Select>
                        </Field>
                     )}
                  </header>

                  {!version ? (
                     <Card className="p-5 sm:p-6">
                        <p className="text-sm text-content-muted">
                           Este proyecto aún no tiene versiones procesadas.
                           {file.status_details && <> Estado: {file.status_details}</>}
                        </p>
                     </Card>
                  ) : (
                     <div className="space-y-6">
                        {/* Secciones de la spec 001 (contracts/ui.md), en orden. */}
                        <VerificationBanner
                           version={version}
                           fileStatus={file.status}
                           statusDetails={file.status_details}
                        />
                        <AdmissibilitySection version={version} />
                        <PurchaseSummary lineas={version.analisis?.resumen_compra} />
                        <QualitySection cota={version.analisis?.cota} desperdicioPlan={version.desperdicio_porcentaje} />
                        <MassWarnings avisos={version.analisis?.avisos_masa} />
                        <VersionsTable
                           versions={versions}
                           selected={version.version_number}
                           onSelect={setSelected}
                        />
                     </div>
                  )}
               </div>
            ) : null}
         </div>
      </div>
   );
}
