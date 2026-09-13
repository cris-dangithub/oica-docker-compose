'use client';

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
   return <div className="text-sm text-gray-700 my-3" aria-live="polite">
      {timing?.elapsed_seconds !== undefined && <p>Tiempo de procesamiento: {Math.round(timing.elapsed_seconds)} s</p>}
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
   const update = (index: number, patch: Partial<StockRow>) => onCatalog(catalog.map((r, i) => i === index ? { ...r, ...patch } : r));
   return <fieldset disabled={disabled} className="my-5 text-left text-gray-800 space-y-4">
      <details className="border rounded p-3">
         <summary className="cursor-pointer font-semibold">Catálogo comercial: longitudes y disponibilidad</summary>
         <p className="text-sm my-2">Vacío en cantidad significa disponibilidad ilimitada. Los cambios se guardan con este proyecto.</p>
         <table className="w-full text-sm"><thead><tr><th>Diámetro</th><th>Longitud (m)</th><th>Cantidad</th><th>Acción</th></tr></thead>
            <tbody>{catalog.map((row, i) => <tr key={i}>
               <td><input aria-label={`Diámetro ${i + 1}`} className="border w-20 p-1" value={row.diametro}
                  onChange={e => update(i, { diametro: e.target.value })} /></td>
               <td><input aria-label={`Longitud ${i + 1}`} className="border w-24 p-1" type="number" min="0" step="any"
                  value={row.longitud_m} onChange={e => update(i, { longitud_m: Number(e.target.value) })} /></td>
               <td><input aria-label={`Cantidad ${i + 1}`} className="border w-24 p-1" type="number" min="1" step="1"
                  placeholder="Ilimitada" value={row.cantidad ?? ''}
                  onChange={e => update(i, { cantidad: e.target.value === '' ? null : Number(e.target.value) })} /></td>
               <td><button type="button" onClick={() => onCatalog(catalog.filter((_, j) => j !== i))}>Quitar</button></td>
            </tr>)}</tbody></table>
         <button type="button" className="underline mt-3" onClick={() => onCatalog([...catalog, { diametro: '#3', longitud_m: 6, cantidad: null }])}>Agregar longitud</button>
      </details>
      <label className="block font-semibold">Inventario adicional (opcional)
         <input className="block mt-2 text-sm" type="file" accept=".xlsx,.csv"
            onChange={e => onInventory(e.target.files?.[0] ?? null)} />
      </label>
      <p className="text-sm">Columnas: diametro, longitud_m, cantidad. Puede importar el inventario final de otro proyecto después de verificar las existencias físicas.</p>
      <label className="block"><input type="checkbox" checked={visuals} onChange={e => onVisuals(e.target.checked)} /> Generar PDF y gráfica de muestra, además del Excel completo</label>
      <p className="text-sm">Los grupos se procesan en orden y comparten sus sobrantes disponibles según las condiciones de corte.</p>
   </fieldset>;
}
