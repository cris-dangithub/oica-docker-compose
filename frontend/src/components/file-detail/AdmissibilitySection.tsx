/**
 * Desperdicio y admisibilidad de una versión (US1: FR-003, FR-004, FR-006).
 */
import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
   ADMISIBILIDAD_LABELS,
   ADMISIBILIDAD_TONES,
   NO_DISPONIBLE,
   VersionDetalle,
   kg,
   pct,
   pp,
} from './types';

interface AdmissibilitySectionProps {
   version: VersionDetalle;
}

function Stat({ label, value, detail }: { label: string; value: React.ReactNode; detail?: React.ReactNode }) {
   return (
      <div className="rounded-md border border-line bg-surface-interactive p-4">
         <p className="text-xs font-semibold text-content-muted">{label}</p>
         <div className="mt-1 font-mono text-lg font-semibold tabular-nums text-content">{value}</div>
         {detail && <p className="mt-1 text-xs text-content-muted">{detail}</p>}
      </div>
   );
}

export default function AdmissibilitySection({ version }: AdmissibilitySectionProps) {
   const analisis = version.analisis;
   const admisibilidad = analisis?.admisibilidad;
   const perdidas = analisis?.perdidas;

   return (
      <Card className="p-5 sm:p-6" aria-labelledby="seccion-admisibilidad">
         <h2 id="seccion-admisibilidad" className="text-base font-semibold text-content">
            Desperdicio y admisibilidad
         </h2>
         {!admisibilidad || !perdidas ? (
            <p className="mt-3 text-sm text-content-muted">
               Desperdicio en masa: <span className="font-mono">{pct(version.desperdicio_porcentaje)}</span>. Evaluación de
               admisibilidad: {NO_DISPONIBLE} (versión procesada antes de este análisis).
            </p>
         ) : (
            <>
               <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <Stat
                     label="Desperdicio en masa"
                     value={pct(admisibilidad.proyecto.desperdicio_pct)}
                     detail={analisis.aprovechamiento_pct != null ? `Aprovechamiento: ${pct(analisis.aprovechamiento_pct)}` : undefined}
                  />
                  <Stat
                     label="Estado del proyecto"
                     value={
                        <Badge tone={ADMISIBILIDAD_TONES[admisibilidad.proyecto.estado]}>
                           {ADMISIBILIDAD_LABELS[admisibilidad.proyecto.estado]}
                        </Badge>
                     }
                     detail={
                        analisis.umbral_desperdicio_pct != null
                           ? `Umbral ${pct(analisis.umbral_desperdicio_pct, 2)} · diferencia ${pp(admisibilidad.proyecto.diferencia_pp)}`
                           : 'Sin umbral definido para esta versión'
                     }
                  />
                  <Stat
                     label="Pérdida irrecuperable"
                     value={kg(perdidas.irrecuperable.kg)}
                     detail={`${pct(perdidas.irrecuperable.pct)} · corte y descartes`}
                  />
                  <Stat
                     label="Saldo reutilizable final"
                     value={kg(perdidas.reutilizable.kg)}
                     detail={`${pct(perdidas.reutilizable.pct)} · queda en el inventario final`}
                  />
               </div>

               {/* Escritorio: tabla por diámetro */}
               <div className="mt-5 hidden overflow-x-auto sm:block">
                  <table className="w-full text-left text-sm">
                     <caption className="sr-only">Admisibilidad por diámetro</caption>
                     <thead className="border-b border-line bg-surface-subtle">
                        <tr className="text-xs font-semibold text-content-muted">
                           <th scope="col" className="px-3 py-2">Diámetro</th>
                           <th scope="col" className="px-3 py-2">Desperdicio</th>
                           <th scope="col" className="px-3 py-2">Estado</th>
                           <th scope="col" className="px-3 py-2">Diferencia</th>
                           <th scope="col" className="px-3 py-2">Irrecuperable</th>
                           <th scope="col" className="px-3 py-2">Reutilizable</th>
                        </tr>
                     </thead>
                     <tbody className="divide-y divide-line">
                        {admisibilidad.por_diametro.map(e => {
                           const p = perdidas.por_diametro[e.diametro ?? ''];
                           return (
                              <tr key={e.diametro}>
                                 <th scope="row" className="px-3 py-2 font-mono font-semibold text-content">{e.diametro}</th>
                                 <td className="px-3 py-2 font-mono tabular-nums">{pct(e.desperdicio_pct)}</td>
                                 <td className="px-3 py-2">
                                    <Badge tone={ADMISIBILIDAD_TONES[e.estado]}>{ADMISIBILIDAD_LABELS[e.estado]}</Badge>
                                 </td>
                                 <td className="px-3 py-2 font-mono tabular-nums">{e.diferencia_pp != null ? pp(e.diferencia_pp) : '—'}</td>
                                 <td className="px-3 py-2 font-mono tabular-nums">{p ? `${kg(p.irrecuperable.kg)} · ${pct(p.irrecuperable.pct)}` : NO_DISPONIBLE}</td>
                                 <td className="px-3 py-2 font-mono tabular-nums">{p ? `${kg(p.reutilizable.kg)} · ${pct(p.reutilizable.pct)}` : NO_DISPONIBLE}</td>
                              </tr>
                           );
                        })}
                     </tbody>
                  </table>
               </div>

               {/* Móvil: una tarjeta por diámetro */}
               <ul className="mt-5 space-y-3 sm:hidden" aria-label="Admisibilidad por diámetro">
                  {admisibilidad.por_diametro.map(e => {
                     const p = perdidas.por_diametro[e.diametro ?? ''];
                     return (
                        <li key={e.diametro} className="rounded-md border border-line p-3 text-sm">
                           <div className="flex items-center justify-between gap-3">
                              <span className="font-mono font-semibold text-content">{e.diametro}</span>
                              <Badge tone={ADMISIBILIDAD_TONES[e.estado]}>{ADMISIBILIDAD_LABELS[e.estado]}</Badge>
                           </div>
                           <p className="mt-2 font-mono text-xs tabular-nums text-content-muted">
                              Desperdicio {pct(e.desperdicio_pct)}
                              {e.diferencia_pp != null && <> · {pp(e.diferencia_pp)}</>}
                           </p>
                           {p && (
                              <p className="mt-1 font-mono text-xs tabular-nums text-content-muted">
                                 Irrecuperable {kg(p.irrecuperable.kg)} · Reutilizable {kg(p.reutilizable.kg)}
                              </p>
                           )}
                        </li>
                     );
                  })}
               </ul>

               <p className="mt-4 text-xs text-content-muted">
                  El umbral lo define el usuario; no se identificó un máximo normativo. El desperdicio incluye el saldo
                  reutilizable final (INF-012); la pérdida irrecuperable se informa aparte.
               </p>
            </>
         )}
      </Card>
   );
}
