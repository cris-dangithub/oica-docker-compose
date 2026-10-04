/**
 * Comparación de versiones de un archivo (US1: FR-028). Los datos que faltan en versiones
 * históricas se muestran como «no disponible».
 */
import React from 'react';
import { Download } from 'lucide-react';
import { Alert } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { buttonVariants } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { API_URL } from '@/lib/api';
import { cn } from '@/lib/utils';
import {
   ADMISIBILIDAD_LABELS,
   ADMISIBILIDAD_TONES,
   NO_DISPONIBLE,
   PERFIL_LABELS,
   VersionDetalle,
   decimal,
   pct,
} from './types';

interface VersionsTableProps {
   versions: VersionDetalle[];
   selected?: number;
   onSelect: (version: number) => void;
}

const seconds = (value: number | null) => (value != null ? `${decimal(value, 1)} s` : NO_DISPONIBLE);

const umbral = (value: number | null) => (value != null ? pct(value, 2) : 'sin umbral');

function Admisibilidad({ version }: { version: VersionDetalle }) {
   if (!version.admisibilidad_estado) return <span className="text-content-muted">{NO_DISPONIBLE}</span>;
   return (
      <Badge tone={ADMISIBILIDAD_TONES[version.admisibilidad_estado]}>
         {ADMISIBILIDAD_LABELS[version.admisibilidad_estado]}
      </Badge>
   );
}

function Verificacion({ version }: { version: VersionDetalle }) {
   if (version.valido == null) return <span className="text-content-muted">{NO_DISPONIBLE}</span>;
   return version.valido ? <Badge tone="success">Verificado</Badge> : <Badge tone="error">No verificado</Badge>;
}

function Descargas({ version }: { version: VersionDetalle }) {
   const items: { type: string; label: string; available: boolean }[] = [
      { type: 'excel', label: 'Excel', available: Boolean(version.excel_path) },
      { type: 'pdf', label: 'PDF', available: Boolean(version.pdf_path) },
      { type: 'imagen', label: 'Imagen', available: Boolean(version.graph_image_path || version.image_path) },
      { type: 'inventario', label: 'Inventario', available: Boolean(version.inventory_path) },
   ];
   return (
      <div role="group" aria-label={`Descargas de la versión ${version.version_number}`} className="flex flex-wrap gap-2">
         {items.filter(item => item.available).map(item => (
            <a
               key={item.type}
               href={`${API_URL}/descargar-${item.type}/${version.storage_uuid}`}
               target="_blank"
               rel="noopener noreferrer"
               className={buttonVariants({ size: 'sm', variant: 'outline' })}
               aria-label={`Descargar ${item.label} de la versión ${version.version_number}`}
            >
               <Download className="h-4 w-4" aria-hidden="true" />
               {item.label}
            </a>
         ))}
      </div>
   );
}

export default function VersionsTable({ versions, selected, onSelect }: VersionsTableProps) {
   const umbrales = new Set(versions.map(v => v.umbral_desperdicio_pct ?? null));

   return (
      <Card className="overflow-hidden" aria-labelledby="seccion-versiones">
         <div className="border-b border-line px-5 py-4 sm:px-6">
            <h2 id="seccion-versiones" className="text-base font-semibold text-content">
               Versiones <span className="font-mono text-sm font-normal text-content-muted">({versions.length})</span>
            </h2>
            <p className="mt-1 text-xs text-content-muted">
               Compara perfil, tiempo de procesamiento, desperdicio y admisibilidad de cada versión.
            </p>
         </div>
         {umbrales.size > 1 && (
            <div className="px-5 pt-4 sm:px-6">
               <Alert tone="warning" title="Umbrales distintos">
                  Las versiones se evaluaron con umbrales distintos; compara cada estado con su propio umbral.
               </Alert>
            </div>
         )}

         {/* Escritorio: tabla */}
         <div className="hidden overflow-x-auto lg:block">
            <table className="w-full text-left text-sm">
               <caption className="sr-only">Comparación de versiones</caption>
               <thead className="border-b border-line bg-surface-subtle">
                  <tr className="text-xs font-semibold text-content-muted">
                     <th scope="col" className="px-6 py-3">Versión</th>
                     <th scope="col" className="px-3 py-3">Perfil</th>
                     <th scope="col" className="px-3 py-3">Tiempo</th>
                     <th scope="col" className="px-3 py-3">Desperdicio</th>
                     <th scope="col" className="px-3 py-3">Umbral</th>
                     <th scope="col" className="px-3 py-3">Admisibilidad</th>
                     <th scope="col" className="px-3 py-3">Verificación</th>
                     <th scope="col" className="px-6 py-3">Descargas</th>
                  </tr>
               </thead>
               <tbody className="divide-y divide-line">
                  {versions.map(v => (
                     <tr key={v.version_number} className={cn('align-top', v.version_number === selected && 'bg-surface-interactive')}>
                        <th scope="row" className="px-6 py-3">
                           <button
                              type="button"
                              className="font-mono font-semibold text-content-brand underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus"
                              onClick={() => onSelect(v.version_number)}
                              aria-current={v.version_number === selected ? 'true' : undefined}
                              aria-label={`Ver la versión ${v.version_number}`}
                           >
                              v{v.version_number}
                           </button>
                        </th>
                        <td className="px-3 py-3">{PERFIL_LABELS[v.perfil_usado ?? ''] ?? v.perfil_usado ?? NO_DISPONIBLE}</td>
                        <td className="px-3 py-3 font-mono tabular-nums">{seconds(v.processing_time_seconds)}</td>
                        <td className="px-3 py-3 font-mono tabular-nums">{pct(v.desperdicio_porcentaje)}</td>
                        <td className="px-3 py-3 font-mono tabular-nums">{umbral(v.umbral_desperdicio_pct)}</td>
                        <td className="px-3 py-3"><Admisibilidad version={v} /></td>
                        <td className="px-3 py-3"><Verificacion version={v} /></td>
                        <td className="px-6 py-3"><Descargas version={v} /></td>
                     </tr>
                  ))}
               </tbody>
            </table>
         </div>

         {/* Móvil y tableta: tarjetas */}
         <ul className="divide-y divide-line lg:hidden" aria-label="Comparación de versiones">
            {versions.map(v => (
               <li key={v.version_number} className={cn('space-y-3 p-5 sm:p-6', v.version_number === selected && 'bg-surface-interactive')}>
                  <div className="flex items-center justify-between gap-3">
                     <button
                        type="button"
                        className="font-mono text-sm font-semibold text-content-brand underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus"
                        onClick={() => onSelect(v.version_number)}
                        aria-current={v.version_number === selected ? 'true' : undefined}
                        aria-label={`Ver la versión ${v.version_number}`}
                     >
                        v{v.version_number} · {PERFIL_LABELS[v.perfil_usado ?? ''] ?? v.perfil_usado ?? NO_DISPONIBLE}
                     </button>
                     <Verificacion version={v} />
                  </div>
                  <dl className="grid grid-cols-2 gap-3 rounded-md bg-surface-subtle p-3 text-xs">
                     <div><dt className="font-semibold text-content-muted">Tiempo</dt><dd className="font-mono">{seconds(v.processing_time_seconds)}</dd></div>
                     <div><dt className="font-semibold text-content-muted">Desperdicio</dt><dd className="font-mono">{pct(v.desperdicio_porcentaje)}</dd></div>
                     <div><dt className="font-semibold text-content-muted">Umbral</dt><dd className="font-mono">{umbral(v.umbral_desperdicio_pct)}</dd></div>
                     <div><dt className="font-semibold text-content-muted">Admisibilidad</dt><dd><Admisibilidad version={v} /></dd></div>
                  </dl>
                  <Descargas version={v} />
               </li>
            ))}
         </ul>
      </Card>
   );
}
