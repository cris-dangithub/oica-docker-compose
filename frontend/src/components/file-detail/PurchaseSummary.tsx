/**
 * Resumen de compra por diámetro, longitud y origen (US2: FR-027). Las barras de inventario
 * adicional se listan aparte y no cuentan como compra.
 */
import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { LineaCompra, NO_DISPONIBLE, kg, pct } from './types';

interface PurchaseSummaryProps {
   lineas?: LineaCompra[];
}

const metros = (value: number) => `${value.toLocaleString('es-CO', { maximumFractionDigits: 3 })} m`;

function Origen({ origen }: { origen: LineaCompra['origen'] }) {
   return origen === 'comercial'
      ? <Badge tone="info">Compra</Badge>
      : <Badge tone="neutral">Inventario adicional</Badge>;
}

export default function PurchaseSummary({ lineas }: PurchaseSummaryProps) {
   const compra = (lineas ?? []).filter(l => l.origen === 'comercial');
   const totalBarras = compra.reduce((sum, l) => sum + l.barras, 0);
   const totalMasa = compra.reduce((sum, l) => sum + l.masa_kg, 0);

   return (
      <Card className="p-5 sm:p-6" aria-labelledby="seccion-compra">
         <h2 id="seccion-compra" className="text-base font-semibold text-content">Resumen de compra</h2>
         {!lineas ? (
            <p className="mt-3 text-sm text-content-muted">
               Resumen de compra: {NO_DISPONIBLE} (versión procesada antes de este análisis).
            </p>
         ) : (
            <>
               <p className="mt-1 text-sm text-content-muted">
                  Compra: <span className="font-mono font-semibold text-content">{totalBarras}</span> barras ·{' '}
                  <span className="font-mono font-semibold text-content">{kg(totalMasa)}</span>. Las barras de inventario
                  adicional se toman del inventario y no se compran.
               </p>

               {/* Escritorio: tabla */}
               <div className="mt-4 hidden overflow-x-auto sm:block">
                  <table className="w-full text-left text-sm">
                     <caption className="sr-only">Barras por diámetro, longitud y origen</caption>
                     <thead className="border-b border-line bg-surface-subtle">
                        <tr className="text-xs font-semibold text-content-muted">
                           <th scope="col" className="px-3 py-2">Diámetro</th>
                           <th scope="col" className="px-3 py-2">Longitud</th>
                           <th scope="col" className="px-3 py-2">Origen</th>
                           <th scope="col" className="px-3 py-2 text-right">Barras</th>
                           <th scope="col" className="px-3 py-2 text-right">Masa</th>
                           <th scope="col" className="px-3 py-2 text-right">Aprovechamiento</th>
                        </tr>
                     </thead>
                     <tbody className="divide-y divide-line">
                        {lineas.map(l => (
                           <tr key={`${l.diametro}-${l.longitud_m}-${l.origen}`}>
                              <th scope="row" className="px-3 py-2 font-mono font-semibold text-content">{l.diametro}</th>
                              <td className="px-3 py-2 font-mono tabular-nums">{metros(l.longitud_m)}</td>
                              <td className="px-3 py-2"><Origen origen={l.origen} /></td>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{l.barras}</td>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{kg(l.masa_kg)}</td>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{pct(l.aprovechamiento_pct, 2)}</td>
                           </tr>
                        ))}
                     </tbody>
                  </table>
               </div>

               {/* Móvil: tarjetas */}
               <ul className="mt-4 space-y-3 sm:hidden" aria-label="Barras por diámetro, longitud y origen">
                  {lineas.map(l => (
                     <li key={`${l.diametro}-${l.longitud_m}-${l.origen}`} className="rounded-md border border-line p-3 text-sm">
                        <div className="flex items-center justify-between gap-3">
                           <span className="font-mono font-semibold text-content">{l.diametro} · {metros(l.longitud_m)}</span>
                           <Origen origen={l.origen} />
                        </div>
                        <p className="mt-2 font-mono text-xs tabular-nums text-content-muted">
                           {l.barras} barras · {kg(l.masa_kg)} · aprovechamiento {pct(l.aprovechamiento_pct, 2)}
                        </p>
                     </li>
                  ))}
               </ul>
            </>
         )}
      </Card>
   );
}
