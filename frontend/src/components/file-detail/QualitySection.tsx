/**
 * Calidad del plan frente al mejor resultado posible (US4: FR-012 a FR-014). La cota solo mide:
 * el plan lo produce el algoritmo genético y no se afirma optimalidad.
 */
import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { CotaInferior, NO_DISPONIBLE, pct, pp } from './types';

interface QualitySectionProps {
   cota?: CotaInferior;
   desperdicioPlan: number | null;
}

export default function QualitySection({ cota, desperdicioPlan }: QualitySectionProps) {
   const calculada = cota?.estado === 'calculada';
   return (
      <Card className="p-5 sm:p-6" aria-labelledby="seccion-calidad">
         <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 id="seccion-calidad" className="text-base font-semibold text-content">Calidad del plan</h2>
            {cota && (calculada
               ? <Badge tone={cota.ajustada ? 'success' : 'warning'}>{cota.ajustada ? 'Cota ajustada' : 'Cota no ajustada'}</Badge>
               : <Badge tone="neutral">Cota por patrones no disponible</Badge>)}
         </div>
         {!cota ? (
            <p className="mt-3 text-sm text-content-muted">
               Cota inferior: {NO_DISPONIBLE} (versión procesada antes de este análisis).
            </p>
         ) : (
            <>
               <dl className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  {[
                     { label: 'Desperdicio del plan', value: pct(desperdicioPlan) },
                     { label: 'Cota por patrones', value: calculada ? pct(cota.proyecto?.desperdicio_pct) : NO_DISPONIBLE },
                     { label: 'Cota simple', value: pct(cota.proyecto?.simple_desperdicio_pct) },
                     { label: 'Brecha del plan', value: calculada ? pp(cota.proyecto?.brecha_pp) : NO_DISPONIBLE },
                  ].map(item => (
                     <div key={item.label} className="rounded-md border border-line bg-surface-interactive p-4">
                        <dt className="text-xs font-semibold text-content-muted">{item.label}</dt>
                        <dd className="mt-1 font-mono text-lg font-semibold tabular-nums text-content">{item.value}</dd>
                     </div>
                  ))}
               </dl>
               {!calculada && cota.motivo && (
                  <p className="mt-3 text-xs text-content-muted">Motivo: {cota.motivo}</p>
               )}
               {calculada && cota.por_diametro && (
                  <ul className="mt-4 grid gap-2 text-xs sm:grid-cols-2 lg:grid-cols-3" aria-label="Cota por diámetro">
                     {cota.por_diametro.map(d => (
                        <li key={d.diametro} className="rounded-md border border-line p-3 font-mono tabular-nums">
                           <span className="font-semibold text-content">{d.diametro}</span>
                           <span className="text-content-muted">
                              {' · '}cota {pct(d.desperdicio_pct)} · brecha {pp(d.brecha_pp)}
                              {!d.ajustada && ' · no ajustada'}
                           </span>
                        </li>
                     ))}
                  </ul>
               )}
               <p className="mt-4 text-xs text-content-muted">
                  La cota inferior es el desperdicio por debajo del cual ningún plan puede bajar (enfoque de patrones de
                  corte de Gilmore–Gomory, relajación lineal con las etapas relajadas). Mide la calidad del plan; no lo
                  construye ni demuestra que sea óptimo. Una cota «no ajustada» sigue siendo válida, pero puede ser más
                  holgada.
               </p>
            </>
         )}
      </Card>
   );
}
