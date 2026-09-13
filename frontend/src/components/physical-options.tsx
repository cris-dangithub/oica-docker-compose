'use client';

export interface PhysicalParameters {
   perdida_activa: boolean;
   proceso: 'disco' | 'cizalla';
   perdida_mm: string;
   minimo_activo: boolean;
   modo_minimo: 'automatico' | 'manual';
   minimo_m: string;
   descarte: 'inmediato' | 'fin_etapa';
}

export interface ParameterMetadata {
   defaults: PhysicalParameters;
   referencias: Record<string, { valor_mm?: string; nota: string; url?: string }>;
}

export function PhysicalOptions({ value, metadata, onChange, disabled }: {
   value: PhysicalParameters; metadata: ParameterMetadata;
   onChange: (value: PhysicalParameters) => void; disabled: boolean;
}) {
   const update = (patch: Partial<PhysicalParameters>) => onChange({ ...value, ...patch });
   const reference = metadata.referencias[value.proceso];
   return <fieldset disabled={disabled} className="border rounded p-4 my-4 text-left text-gray-800 space-y-3">
      <legend className="font-semibold">Condiciones de corte y reutilización</legend>
      <label className="block"><input type="checkbox" checked={value.perdida_activa}
         onChange={e => update({ perdida_activa: e.target.checked })} /> Activar pérdida por corte de acero</label>
      {value.perdida_activa && <div className="space-y-2">
         <label className="block">Proceso <select className="border p-1" value={value.proceso}
            onChange={e => { const proceso = e.target.value as PhysicalParameters['proceso'];
               update({ proceso, perdida_mm: metadata.referencias[proceso].valor_mm ?? '0' }); }}>
            <option value="disco">Disco</option><option value="cizalla">Cizalla</option>
         </select></label>
         <label className="block">Pérdida por separación (mm) <input className="border p-1 w-24" type="number"
            min="0" step="any" value={value.perdida_mm} onChange={e => update({ perdida_mm: e.target.value })} /></label>
         <p className="text-sm">{Number(value.perdida_mm) === Number(reference.valor_mm) ? 'Valor de referencia.' : 'Valor personalizado.'} {reference.nota}
            {reference.url && <> <a className="underline" href={reference.url} target="_blank" rel="noreferrer">Ficha del fabricante</a>.</>}</p>
         <p className="text-sm">Una pieza que ocupa exactamente el saldo no requiere separación. En los demás casos se reserva la pérdida completa.</p>
      </div>}
      <label className="block"><input type="checkbox" checked={value.minimo_activo}
         onChange={e => update({ minimo_activo: e.target.checked })} /> Activar longitud mínima para reutilizar</label>
      {value.minimo_activo && <div className="space-y-2">
         <label className="block">Criterio <select className="border p-1" value={value.modo_minimo}
            onChange={e => update({ modo_minimo: e.target.value as PhysicalParameters['modo_minimo'] })}>
            <option value="automatico">Automático por diámetro</option><option value="manual">Mínimo personalizado</option>
         </select></label>
         {value.modo_minimo === 'manual' ? <label className="block">Mínimo común (m) <input className="border p-1 w-24"
            type="number" min="0" step="any" value={value.minimo_m} onChange={e => update({ minimo_m: e.target.value })} /></label>
            : <p className="text-sm">Menor longitud demandada por diámetro en toda la cartilla; se mantiene fija entre etapas.
               <a className="underline ml-1" href={metadata.referencias.automatico.url} target="_blank" rel="noreferrer">Referencia de investigación</a>.
               Usa «Estimar tiempo» para consultar los mínimos de tu archivo.</p>}
         <label className="block">Aplicar descarte <select className="border p-1" value={value.descarte}
            onChange={e => update({ descarte: e.target.value as PhysicalParameters['descarte'] })}>
            <option value="inmediato">Después de cada corte</option><option value="fin_etapa">Al terminar cada etapa</option>
         </select></label>
         <p className="text-sm">Los saldos iguales al mínimo se conservan. El inventario inicial inferior al mínimo se excluye y se informa aparte.</p>
      </div>}
      <p className="text-sm">Son supuestos editables del modelo, no mínimos legales ni una validación estructural. Se evalúa el desperdicio de todo el proyecto conocido.</p>
   </fieldset>;
}
