/**
 * Fila del explorador (spec 002, R-17): un botón por patrón con su barra dibujada a escala común.
 * El dibujo es decorativo (`aria-hidden`); su información está en el nombre accesible y en el detalle.
 */
import React from 'react';
import { cn } from '@/lib/utils';
import { decimal, type PatronExplorable } from '../types';
import { metros, numero, tonoEtapa } from './filtros';

// Clases completas para que Tailwind las conserve; texto con contraste AA sobre cada etapa.
const TONOS: Record<number, string> = {
   1: 'bg-data-stage-1 text-content-inverse',
   2: 'bg-data-stage-2 text-content-inverse',
   3: 'bg-data-stage-3 text-content-inverse',
   4: 'bg-data-stage-4 text-content-inverse',
   5: 'bg-data-stage-5 text-content',
   6: 'bg-data-stage-6 text-content',
};

export const claseEtapa = (etapa: number) => TONOS[tonoEtapa(etapa)];

// Ancho aproximado de un carácter mono de 11 px, más el margen interior de la pieza.
const cabeRotulo = (anchoPx: number, texto: string) => anchoPx >= texto.length * 6.8 + 6;

interface PatternRowProps {
   patron: PatronExplorable;
   escala: number;
   anchoPx: number;
   abierto: boolean;
   detalleId: string;
   pedido?: string;
   aporte?: number;
   onToggle: () => void;
}

const PatternRow = React.forwardRef<HTMLButtonElement, PatternRowProps>(function PatternRow(
   { patron, escala, anchoPx, abierto, detalleId, pedido, aporte, onToggle },
   ref,
) {
   const etiqueta =
      `${patron.patron_id}, barra ${patron.diametro} de ${metros(patron.longitud_m)}, ` +
      `${numero(patron.repeticiones, 0)} repeticiones, aprovechamiento ${decimal(patron.aprovechamiento_pct, 2)} %` +
      (pedido && aporte != null ? `, aporta ${numero(aporte, 0)} piezas del pedido ${pedido}` : '');
   const anchoBarra = escala > 0 ? patron.longitud_m / escala : 0;
   const piezas = patron.piezas.flatMap((pieza, i) =>
      Array.from({ length: pieza.cantidad }, (_, j) => ({ ...pieza, clave: `${i}-${j}` })),
   );

   return (
      <button
         ref={ref}
         type="button"
         aria-expanded={abierto}
         aria-controls={detalleId}
         aria-label={etiqueta}
         onClick={onToggle}
         className={cn(
            'block w-full rounded-md border bg-surface-elevated p-3 text-left transition-colors duration-standard ease-standard',
            'hover:border-line-focus hover:bg-surface-interactive active:bg-surface-subtle',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus',
            abierto ? 'border-line-focus' : 'border-line',
         )}
      >
         <span className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
            <span className="font-mono text-sm font-semibold text-content">{patron.patron_id}</span>
            <span className="font-mono text-xs tabular-nums text-content-muted">
               {patron.diametro} · {metros(patron.longitud_m)} · ×{numero(patron.repeticiones, 0)} ·{' '}
               {decimal(patron.aprovechamiento_pct, 2)} %
               {pedido && aporte != null && (
                  <span className="text-content-brand"> · {numero(aporte, 0)} pzs del pedido {pedido}</span>
               )}
            </span>
         </span>
         <span className="mt-2 block" aria-hidden="true">
            <span
               className="flex h-7 overflow-hidden rounded-sm border border-line-strong"
               style={{ width: `${anchoBarra * 100}%` }}
            >
               {piezas.map(pieza => {
                  const fraccion = pieza.longitud_m / patron.longitud_m;
                  const texto = numero(pieza.longitud_m, 3);
                  return (
                     <span
                        key={pieza.clave}
                        title={`E${pieza.etapa} · ${metros(pieza.longitud_m)}`}
                        className={cn(
                           'flex shrink-0 items-center justify-center border-r border-surface-elevated font-mono text-[11px] font-semibold',
                           claseEtapa(pieza.etapa),
                        )}
                        style={{ width: `${fraccion * 100}%` }}
                     >
                        {cabeRotulo(fraccion * anchoBarra * anchoPx, texto) ? texto : null}
                     </span>
                  );
               })}
               {patron.descartado_m > 0 && (
                  <span
                     title={`Descarte · ${metros(patron.descartado_m)}`}
                     className="shrink-0 bg-status-error-text"
                     style={{ width: `${(patron.descartado_m / patron.longitud_m) * 100}%` }}
                  />
               )}
               {patron.saldo_m > 0 && (
                  <span
                     title={`Saldo reutilizable · ${metros(patron.saldo_m)}`}
                     className="shrink-0 bg-data-remaining"
                     style={{ width: `${(patron.saldo_m / patron.longitud_m) * 100}%` }}
                  />
               )}
            </span>
         </span>
      </button>
   );
});

export default PatternRow;
