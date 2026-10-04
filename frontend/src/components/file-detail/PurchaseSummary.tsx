/**
 * Resumen de compra por diámetro, longitud y origen (spec 001, FR-027). Las barras de inventario
 * adicional se listan aparte y no cuentan como compra. Spec 002 (FR-016): totales por diámetro,
 * total comprado y, aparte, total tomado del inventario; coinciden con la hoja «Resumen» del Excel.
 */
import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { metros } from './patterns/filtros';
import { LineaCompra, NO_DISPONIBLE, entero, kg, pct } from './types';

interface PurchaseSummaryProps {
   lineas?: LineaCompra[];
}


function Origen({ origen }: { origen: LineaCompra['origen'] }) {
   return origen === 'comercial'
      ? <Badge tone="info">Compra</Badge>
      : <Badge tone="neutral">Inventario adicional</Badge>;
}

interface Total {
   etiqueta: string;
   barras: number;
   masa_kg: number;
}

const sumar = (etiqueta: string, lineas: LineaCompra[]): Total => ({
   etiqueta,
   barras: lineas.reduce((sum, l) => sum + l.barras, 0),
   masa_kg: lineas.reduce((sum, l) => sum + l.masa_kg, 0),
});

export default function PurchaseSummary({ lineas }: PurchaseSummaryProps) {
   const compra = (lineas ?? []).filter(l => l.origen === 'comercial');
   const inventario = (lineas ?? []).filter(l => l.origen === 'adicional');
   const diametros = Array.from(new Set(compra.map(l => l.diametro)));
   const totales: Total[] = [
      ...diametros.map(d => sumar(`Total ${d}`, compra.filter(l => l.diametro === d))),
      sumar('Total comprado', compra),
      ...(inventario.length ? [sumar('Total tomado del inventario', inventario)] : []),
   ];
   const { barras: totalBarras, masa_kg: totalMasa } = sumar('', compra);

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
                  Compra: <span className="font-mono font-semibold text-content">{entero(totalBarras)}</span> barras ·{' '}
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
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{entero(l.barras)}</td>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{kg(l.masa_kg)}</td>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{pct(l.aprovechamiento_pct, 2)}</td>
                           </tr>
                        ))}
                     </tbody>
                     <tfoot className="border-t-2 border-line-strong bg-surface-subtle">
                        {totales.map(t => (
                           <tr key={t.etiqueta} className="font-semibold">
                              <th scope="row" colSpan={3} className="px-3 py-2 text-content">{t.etiqueta}</th>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{entero(t.barras)}</td>
                              <td className="px-3 py-2 text-right font-mono tabular-nums">{kg(t.masa_kg)}</td>
                              <td className="px-3 py-2" />
                           </tr>
                        ))}
                     </tfoot>
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
                           {entero(l.barras)} barras · {kg(l.masa_kg)} · aprovechamiento {pct(l.aprovechamiento_pct, 2)}
                        </p>
                     </li>
                  ))}
                  <li className="rounded-md border border-line-strong bg-surface-subtle p-3 text-sm">
                     <p className="font-semibold text-content">Totales</p>
                     <dl className="mt-2 space-y-1 font-mono text-xs tabular-nums">
                        {totales.map(t => (
                           <div key={t.etiqueta} className="flex flex-wrap justify-between gap-x-3">
                              <dt className="text-content-muted">{t.etiqueta}</dt>
                              <dd className="text-content">{entero(t.barras)} barras · {kg(t.masa_kg)}</dd>
                           </div>
                        ))}
                     </dl>
                  </li>
               </ul>
            </>
         )}
      </Card>
   );
}
