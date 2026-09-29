'use client';

import { ChevronDown, FileUp, Plus, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { CheckboxField, Input } from '@/components/ui/form-controls';

export interface StockRow {
   diametro: string;
   longitud_m: number;
   cantidad: number | null;
}

export const initialCatalog: StockRow[] = [3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 18].flatMap(
   d => [6, 9, 12].map(length => ({ diametro: `#${d}`, longitud_m: length, cantidad: null }))
);

export interface Timing {
   elapsed_seconds?: number;
   estimated_total_seconds?: [number, number] | null;
   remaining_seconds?: [number, number] | null;
   calibration?: string;
   parametros_corte?: { minimos_por_diametro_m: Record<string, string> };
}

export function TimingInfo({ timing }: { timing: Timing | null }) {
   const range = (v: [number, number]) => `${Math.round(v[0])}–${Math.round(v[1])} s`;
   return <div className="my-4 rounded-md border border-line bg-surface-subtle p-4 text-sm leading-6 text-content-muted" aria-live="polite">
      {timing?.elapsed_seconds !== undefined && <p className="font-medium text-content">Tiempo de procesamiento: {Math.round(timing.elapsed_seconds)} s</p>}
      {timing?.estimated_total_seconds
         ? <p>Duración estimada: {range(timing.estimated_total_seconds)}. Rango basado en ejecuciones anteriores.</p>
         : <p>Estimación: calibrando. Aún no hay suficientes ejecuciones comparables.</p>}
      {timing?.remaining_seconds && <p>Tiempo restante estimado: {range(timing.remaining_seconds)}</p>}
      {timing?.calibration === 'fuera_del_rango_observado' && <p>La ejecución superó el rango observado; continúa procesando.</p>}
      <p>La espera en cola no forma parte de la estimación.</p>
      {timing?.parametros_corte && <p>Mínimos reutilizables: {Object.entries(timing.parametros_corte.minimos_por_diametro_m)
         .map(([diameter, length]) => `${diameter}: ${length} m`).join('; ') || 'desactivados'}.</p>}
   </div>;
}

export function CuttingOptions({ catalog, onCatalog, onInventory, visuals, onVisuals, disabled }: {
   catalog: StockRow[]; onCatalog: (rows: StockRow[]) => void;
   onInventory: (file: File | null) => void; visuals: boolean; onVisuals: (value: boolean) => void;
   disabled: boolean;
}) {
   const [inventoryName, setInventoryName] = useState<string | null>(null);
   const update = (index: number, patch: Partial<StockRow>) => onCatalog(catalog.map((r, i) => i === index ? { ...r, ...patch } : r));
   return <fieldset disabled={disabled} className="space-y-6 text-left">
      <Card className="overflow-hidden">
         <details className="group">
            <summary className="flex min-h-16 cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 sm:px-6">
               <span>
                  <span className="block font-semibold text-content">Catálogo comercial</span>
                  <span className="mt-1 block text-xs text-content-muted">Longitudes y disponibilidad por diámetro</span>
               </span>
               <span className="flex items-center gap-3">
                  <span className="font-mono text-xs font-semibold text-content-brand">{catalog.length} filas</span>
                  <ChevronDown className="h-5 w-5 text-content-muted transition-transform duration-standard group-open:rotate-180" aria-hidden="true" />
               </span>
            </summary>
            <div className="border-t border-line px-5 py-5 sm:px-6">
               <p className="mb-4 text-sm leading-6 text-content-muted">
                  Una cantidad vacía indica disponibilidad ilimitada. Los cambios se guardan con este proyecto.
               </p>
               <div className="grid grid-cols-[0.8fr_0.8fr_1.4fr_2.5rem] sm:grid-cols-[1fr_1fr_1.25fr_2.5rem] gap-2 px-2 pb-2 text-xs font-semibold text-content-muted sm:gap-3" aria-hidden="true">
                  <span>Diámetro</span>
                  <span>Longitud (m)</span>
                  <span>Cantidad</span>
                  <span className="sr-only">Acción</span>
               </div>
               <ul aria-label="Catálogo de barras comerciales" className="space-y-2">
                  {catalog.map((row, i) => (
                     <li
                        key={`${row.diametro}-${row.longitud_m}-${i}`}
                        className="grid grid-cols-[0.8fr_0.8fr_1.4fr_2.5rem] sm:grid-cols-[1fr_1fr_1.25fr_2.5rem] items-center gap-2 rounded-md border border-line bg-surface-subtle p-2 sm:gap-3"
                     >
                        <Input
                           aria-label={`Diámetro, fila ${i + 1}`}
                           className="px-2 sm:px-3"
                           value={row.diametro}
                           onChange={event => update(i, { diametro: event.target.value })}
                        />
                        <Input
                           aria-label={`Longitud en metros, fila ${i + 1}`}
                           className="px-2 font-mono tabular-nums sm:px-3"
                           type="number"
                           min="0"
                           step="any"
                           value={row.longitud_m}
                           onChange={event => update(i, { longitud_m: Number(event.target.value) })}
                        />
                        <Input
                           aria-label={`Cantidad, fila ${i + 1}`}
                           className="px-2 font-mono tabular-nums sm:px-3"
                           type="number"
                           min="1"
                           step="1"
                           placeholder="Ilimitada"
                           value={row.cantidad ?? ''}
                           onChange={event => update(i, { cantidad: event.target.value === '' ? null : Number(event.target.value) })}
                        />
                        <Button
                           type="button"
                           variant="ghost"
                           size="icon"
                           aria-label={`Quitar fila ${i + 1}`}
                           onClick={() => onCatalog(catalog.filter((_, index) => index !== i))}
                        >
                           <Trash2 className="h-4 w-4" aria-hidden="true" />
                        </Button>
                     </li>
                  ))}
               </ul>
               <Button
                  type="button"
                  variant="outline"
                  className="mt-4"
                  onClick={() => onCatalog([...catalog, { diametro: '#3', longitud_m: 6, cantidad: null }])}
               >
                  <Plus className="h-4 w-4" aria-hidden="true" />
                  Agregar longitud
               </Button>
            </div>
         </details>
      </Card>

      <Card className="p-5 sm:p-6">
         <div className="flex items-start gap-4">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-surface-interactive text-content-brand">
               <FileUp className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
               <p id="inventory-title" className="text-sm font-semibold text-content">
                  Inventario adicional <span className="font-normal text-content-muted">(opcional)</span>
               </p>
               <p className="mt-1 text-xs leading-5 text-content-muted">
                  XLSX o CSV con columnas diametro, longitud_m y cantidad. Verifica antes las existencias físicas.
               </p>
               <div className="mt-3 flex flex-wrap items-center gap-3">
                  <input
                     id="inventory-file"
                     aria-labelledby="inventory-title"
                     className="peer sr-only"
                     type="file"
                     accept=".xlsx,.csv"
                     onChange={event => {
                        const file = event.target.files?.[0] ?? null;
                        setInventoryName(file?.name ?? null);
                        onInventory(file);
                     }}
                  />
                  <label
                     htmlFor="inventory-file"
                     className={buttonVariants({ variant: 'outline', size: 'sm', className: 'cursor-pointer peer-focus-visible:ring-2 peer-focus-visible:ring-line-focus peer-focus-visible:ring-offset-2 peer-disabled:cursor-not-allowed peer-disabled:opacity-50' })}
                  >
                     Seleccionar inventario
                  </label>
                  <span className="min-w-0 break-all text-xs text-content-muted" aria-live="polite">
                     {inventoryName ?? 'Ningún archivo seleccionado'}
                  </span>
               </div>
            </div>
         </div>
      </Card>

      <Card className="p-5 sm:p-6">
         <CheckboxField
            checked={visuals}
            onChange={event => onVisuals(event.target.checked)}
            label="Generar visualizaciones complementarias"
            description="Incluye PDF y gráfica de muestra, además del Excel completo."
         />
         <p className="mt-4 border-t border-line pt-4 text-xs leading-5 text-content-muted">
            Los grupos se procesan en orden y comparten sus sobrantes según las condiciones de corte.
         </p>
      </Card>
   </fieldset>;
}
