/**
 * Detalle de un patrón (spec 002, FR-028): piezas en orden, pedidos que atiende y barras que lo
 * usan. Los rangos de barras se pintan por tramos de 100 para no cargar el navegador (SC-012).
 */
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { decimal, type PatronExplorable } from '../types';
import { claseEtapa } from './PatternRow';
import { metros, numero } from './filtros';

const TRAMO_RANGOS = 100;

interface PatternDetailProps {
   id: string;
   patron: PatronExplorable;
   pedido?: string;
   onClose: () => void;
}

export default function PatternDetail({ id, patron, pedido, onClose }: PatternDetailProps) {
   const [visibles, setVisibles] = useState(TRAMO_RANGOS);
   const rangos = patron.barras.rangos;
   const quedan = rangos.length - visibles;

   return (
      <div
         id={id}
         role="region"
         aria-label={`Detalle del patrón ${patron.patron_id}`}
         className="mt-2 rounded-md border border-line bg-surface-subtle p-4 text-sm"
      >
         <p className="font-mono text-xs text-content-muted">Secuencia por etapa</p>
         <p className="mt-1 break-words font-mono text-content">{patron.secuencia}</p>

         <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3 lg:grid-cols-6">
            {[
               ['Repeticiones', numero(patron.repeticiones, 0)],
               ['Aprovechamiento', `${decimal(patron.aprovechamiento_pct, 2)} %`],
               ['Barra', `${patron.diametro} · ${metros(patron.longitud_m)}`],
               ['Pérdida por corte', metros(patron.perdida_corte_m)],
               ['Descarte', metros(patron.descartado_m)],
               ['Saldo reutilizable', metros(patron.saldo_m)],
            ].map(([termino, valor]) => (
               <div key={termino}>
                  <dt className="text-xs text-content-muted">{termino}</dt>
                  <dd className="font-mono tabular-nums text-content">{valor}</dd>
               </div>
            ))}
         </dl>

         <h3 className="mt-5 text-sm font-semibold text-content">Piezas, en orden de corte</h3>
         <ol className="mt-2 space-y-2">
            {patron.piezas.map((pieza, i) => (
               <li key={i} className="rounded-md border border-line bg-surface-elevated p-3">
                  <p className="flex flex-wrap items-center gap-2">
                     <span className={cn('rounded-sm px-1.5 py-0.5 font-mono text-xs font-semibold', claseEtapa(pieza.etapa))}>
                        E{pieza.etapa}
                     </span>
                     <span className="font-mono tabular-nums text-content">
                        {numero(pieza.cantidad, 0)} × {metros(pieza.longitud_m)}
                     </span>
                     <span className="text-xs text-content-muted">por barra</span>
                  </p>
                  <p className="mt-1 text-xs text-content-muted">
                     Pedidos:{' '}
                     {pieza.pedidos.map((p, j) => (
                        <span key={p.pedido} className={cn('font-mono', p.pedido === pedido && 'font-semibold text-content-brand')}>
                           {j > 0 && ', '}
                           {p.pedido} ({numero(p.piezas, 0)} pzs)
                        </span>
                     ))}
                  </p>
               </li>
            ))}
         </ol>

         <h3 className="mt-5 text-sm font-semibold text-content">
            Barras que lo usan: <span className="font-mono tabular-nums">{numero(patron.barras.total, 0)}</span>
         </h3>
         <ul className="mt-2 flex flex-wrap gap-2" aria-label={`Rangos de barras del patrón ${patron.patron_id}`}>
            {rangos.slice(0, visibles).map(r => (
               <li key={r.desde} className="rounded-sm border border-line bg-surface-elevated px-2 py-1 font-mono text-xs tabular-nums">
                  {r.desde === r.hasta ? r.desde : `${r.desde} a ${r.hasta}`} ({numero(r.n, 0)})
               </li>
            ))}
         </ul>
         {quedan > 0 && (
            <Button size="sm" variant="outline" className="mt-3" onClick={() => setVisibles(v => v + TRAMO_RANGOS)}>
               Ver más (quedan {numero(quedan, 0)})
            </Button>
         )}
         <p className="mt-4 text-xs text-content-muted">
            La lista completa está en las hojas «Patrones» y «Barras» del Excel de esta versión.
         </p>
         <Button size="sm" variant="ghost" className="mt-2" onClick={onClose}>
            Cerrar detalle
         </Button>
      </div>
   );
}
