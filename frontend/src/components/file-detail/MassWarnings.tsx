/**
 * Avisos de masa nominal NSR-10 (US5: FR-018). Solo aparece si hay avisos; no bloquean el plan.
 */
import React from 'react';
import { Alert } from '@/components/ui/alert';
import { AvisoMasa } from './types';

const ROTULO = 'masa nominal NSR-10 (Título C, Tabla C.3.5.3-2)';

interface MassWarningsProps {
   avisos?: AvisoMasa[];
}

export default function MassWarnings({ avisos }: MassWarningsProps) {
   if (!avisos || avisos.length === 0) return null;
   return (
      <Alert tone="warning" title="Avisos de masa nominal NSR-10">
         <p>
            La masa por metro de la cartilla no coincide (±1 %) con la {ROTULO}. El plan se generó igualmente;
            revisa la cartilla.
         </p>
         <ul className="mt-2 space-y-1 font-mono text-xs tabular-nums">
            {avisos.map(a => (
               <li key={a.diametro}>
                  {a.diametro}: cartilla {a.masa_cartilla_kg_m.toFixed(4)} kg/m
                  {a.estado === 'aviso' && a.masa_nominal_kg_m != null && a.diferencia_relativa_pct != null
                     ? ` · nominal ${a.masa_nominal_kg_m.toFixed(3)} kg/m · diferencia ${a.diferencia_relativa_pct > 0 ? '+' : ''}${a.diferencia_relativa_pct.toFixed(2)} %`
                     : ' · sin valor nominal: no se pudo contrastar'}
               </li>
            ))}
         </ul>
      </Alert>
   );
}
