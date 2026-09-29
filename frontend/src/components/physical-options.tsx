'use client';

import { ExternalLink, Gauge, Recycle } from 'lucide-react';
import { Alert } from '@/components/ui/alert';
import { Card } from '@/components/ui/card';
import { CheckboxField, Field, Input, Select } from '@/components/ui/form-controls';

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
   return <Card className="overflow-hidden">
      <fieldset disabled={disabled}>
         <legend className="sr-only">Condiciones de corte y reutilización</legend>
         <div className="border-b border-line px-5 py-5 sm:px-6">
            <p className="font-semibold text-content">Condiciones físicas</p>
            <p className="mt-1 text-xs leading-5 text-content-muted">
               Configura la pérdida por separación y qué saldos pueden reutilizarse.
            </p>
         </div>

         <div className="space-y-6 p-5 sm:p-6">
            <section aria-labelledby="cut-loss-title" className="space-y-4">
               <div className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-surface-interactive text-content-brand">
                     <Gauge className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <CheckboxField
                     id="cut-loss-enabled"
                     checked={value.perdida_activa}
                     onChange={event => update({ perdida_activa: event.target.checked })}
                     label={<span id="cut-loss-title">Pérdida por corte</span>}
                     description="Reserva material por cada separación cuando el proceso lo requiere."
                  />
               </div>

               {value.perdida_activa && <div className="grid gap-4 rounded-md border border-line bg-surface-subtle p-4 sm:grid-cols-2">
                  <Field label="Proceso" htmlFor="cut-process">
                     <Select
                        id="cut-process"
                        value={value.proceso}
                        onChange={event => {
                           const proceso = event.target.value as PhysicalParameters['proceso'];
                           update({ proceso, perdida_mm: metadata.referencias[proceso].valor_mm ?? '0' });
                        }}
                     >
                        <option value="disco">Disco</option>
                        <option value="cizalla">Cizalla</option>
                     </Select>
                  </Field>
                  <Field label="Pérdida por separación (mm)" htmlFor="cut-loss-mm">
                     <Input
                        id="cut-loss-mm"
                        type="number"
                        min="0"
                        step="any"
                        value={value.perdida_mm}
                        onChange={event => update({ perdida_mm: event.target.value })}
                     />
                  </Field>
                  <div className="sm:col-span-2 text-xs leading-5 text-content-muted">
                     <p>
                        {Number(value.perdida_mm) === Number(reference.valor_mm) ? 'Valor de referencia. ' : 'Valor personalizado. '}
                        {reference.nota}
                        {reference.url && <>{' '}<a className="inline-flex items-center gap-1 font-medium text-content-brand underline underline-offset-4" href={reference.url} target="_blank" rel="noreferrer">Ficha del fabricante <ExternalLink className="h-3 w-3" aria-hidden="true" /></a>.</>}
                     </p>
                     <p className="mt-2">Una pieza que ocupa exactamente el saldo no requiere separación; en los demás casos se reserva la pérdida completa.</p>
                  </div>
               </div>}
            </section>

            <div className="border-t border-line" />

            <section aria-labelledby="reuse-title" className="space-y-4">
               <div className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-status-success-bg text-status-success-text">
                     <Recycle className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <CheckboxField
                     id="minimum-enabled"
                     checked={value.minimo_activo}
                     onChange={event => update({ minimo_activo: event.target.checked })}
                     label={<span id="reuse-title">Longitud mínima reutilizable</span>}
                     description="Define cuándo un saldo sigue siendo inventario útil."
                  />
               </div>

               {value.minimo_activo && <div className="grid gap-4 rounded-md border border-line bg-surface-subtle p-4 sm:grid-cols-2">
                  <Field label="Criterio" htmlFor="minimum-mode">
                     <Select
                        id="minimum-mode"
                        value={value.modo_minimo}
                        onChange={event => update({ modo_minimo: event.target.value as PhysicalParameters['modo_minimo'] })}
                     >
                        <option value="automatico">Automático por diámetro</option>
                        <option value="manual">Mínimo personalizado</option>
                     </Select>
                  </Field>
                  {value.modo_minimo === 'manual' && <Field label="Mínimo común (m)" htmlFor="minimum-length">
                     <Input
                        id="minimum-length"
                        type="number"
                        min="0"
                        step="any"
                        value={value.minimo_m}
                        onChange={event => update({ minimo_m: event.target.value })}
                     />
                  </Field>}
                  <Field label="Aplicar descarte" htmlFor="discard-mode" className={value.modo_minimo === 'automatico' ? 'sm:col-span-1' : 'sm:col-span-2'}>
                     <Select
                        id="discard-mode"
                        value={value.descarte}
                        onChange={event => update({ descarte: event.target.value as PhysicalParameters['descarte'] })}
                     >
                        <option value="inmediato">Después de cada corte</option>
                        <option value="fin_etapa">Al terminar cada etapa</option>
                     </Select>
                  </Field>
                  <div className="sm:col-span-2 text-xs leading-5 text-content-muted">
                     {value.modo_minimo === 'automatico' && <p>
                        Se usa la menor longitud demandada por diámetro en toda la cartilla y permanece fija entre etapas.{' '}
                        <a className="inline-flex items-center gap-1 font-medium text-content-brand underline underline-offset-4" href={metadata.referencias.automatico.url} target="_blank" rel="noreferrer">Referencia de investigación <ExternalLink className="h-3 w-3" aria-hidden="true" /></a>.
                     </p>}
                     <p className="mt-2">Los saldos iguales al mínimo se conservan. El inventario inicial inferior se excluye y se informa aparte.</p>
                  </div>
               </div>}
            </section>

            <Alert tone="info" title="Supuestos editables del modelo">
               No representan mínimos legales ni una validación estructural. OICA evalúa el desperdicio del proyecto conocido.
            </Alert>
         </div>
      </fieldset>
   </Card>;
}
