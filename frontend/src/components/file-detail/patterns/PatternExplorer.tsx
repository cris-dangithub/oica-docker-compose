'use client';
/**
 * Explorador de patrones de corte (spec 002, US2; contracts/ui.md §5 y api-patrones.md).
 * Pide los patrones de la versión solo cuando la sección entra en pantalla; filtra, ordena y mide la
 * cobertura en el navegador, sin más peticiones (R-11, R-18).
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { Alert } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Field, Input, Select } from '@/components/ui/form-controls';
import { API_URL } from '@/lib/api';
import { cn } from '@/lib/utils';
import type { VistaPatrones } from '../types';
import PatternDetail from './PatternDetail';
import PatternRow, { claseEtapa } from './PatternRow';
import {
   CRITERIOS,
   type Criterio,
   FILTRO_VACIO,
   type Filtro,
   ORIGEN_LABELS,
   aportePedido,
   cobertura,
   filtrar,
   numero,
   ordenar,
} from './filtros';

const TRAMO_PATRONES = 50;

type Estado =
   | { fase: 'inactiva' | 'cargando' }
   | { fase: 'lista'; vista: Extract<VistaPatrones, { disponible: true }> }
   | { fase: 'no_disponible'; motivo: string }
   | { fase: 'error'; mensaje: string };

interface PatternExplorerProps {
   storageUuid: string;
}

export default function PatternExplorer({ storageUuid }: PatternExplorerProps) {
   const seccion = useRef<HTMLElement>(null);
   const lista = useRef<HTMLUListElement>(null);
   const filas = useRef(new Map<string, HTMLButtonElement>());
   const [estado, setEstado] = useState<Estado>({ fase: 'inactiva' });
   const [visible, setVisible] = useState(false);
   const [filtro, setFiltro] = useState<Filtro>(FILTRO_VACIO);
   const [pedidoTexto, setPedidoTexto] = useState('');
   const [criterio, setCriterio] = useState<Criterio>('excel');
   const [mostrados, setMostrados] = useState(TRAMO_PATRONES);
   const [abierto, setAbierto] = useState<string | null>(null);
   const [anchoPx, setAnchoPx] = useState(0);

   // Cambiar de versión reinicia la sección.
   useEffect(() => {
      setEstado({ fase: 'inactiva' });
      setFiltro(FILTRO_VACIO);
      setPedidoTexto('');
      setCriterio('excel');
      setMostrados(TRAMO_PATRONES);
      setAbierto(null);
   }, [storageUuid]);

   // Carga diferida: solo cuando la sección se acerca a la pantalla.
   useEffect(() => {
      const nodo = seccion.current;
      if (!nodo || typeof IntersectionObserver === 'undefined') {
         setVisible(true);
         return;
      }
      const observer = new IntersectionObserver(entries => {
         if (entries.some(e => e.isIntersecting)) {
            setVisible(true);
            observer.disconnect();
         }
      }, { rootMargin: '200px' });
      observer.observe(nodo);
      return () => observer.disconnect();
   }, []);

   const cargar = useCallback(async () => {
      setEstado({ fase: 'cargando' });
      try {
         const response = await fetch(`${API_URL}/patrones/${encodeURIComponent(storageUuid)}`);
         const data = await response.json().catch(() => null);
         if (!response.ok) throw new Error(data?.error ?? `Error ${response.status}: ${response.statusText}`);
         const vista = data as VistaPatrones;
         setEstado(vista.disponible ? { fase: 'lista', vista } : { fase: 'no_disponible', motivo: vista.motivo });
      } catch (err) {
         setEstado({ fase: 'error', mensaje: err instanceof Error ? err.message : 'Error al cargar los patrones' });
      }
   }, [storageUuid]);

   useEffect(() => {
      if (visible && estado.fase === 'inactiva') cargar();
   }, [visible, estado.fase, cargar]);

   const vista = estado.fase === 'lista' ? estado.vista : null;
   const pedidosValidos = useMemo(() => new Set(vista?.pedidos.map(p => p.pedido) ?? []), [vista]);
   const filtrados = useMemo(() => (vista ? filtrar(vista.patrones, filtro) : []), [vista, filtro]);
   const ordenados = useMemo(() => ordenar(filtrados, criterio), [filtrados, criterio]);
   const cob = vista ? cobertura(filtrados, vista.totales) : null;
   const hayLista = ordenados.length > 0;

   // Ancho real de la lista, para decidir qué medidas caben dentro de cada pieza (26 px de bordes y
   // márgenes de la fila). Se vuelve a medir cuando la lista reaparece tras un filtro vacío.
   useEffect(() => {
      const nodo = lista.current;
      if (!nodo || typeof ResizeObserver === 'undefined') return;
      const observer = new ResizeObserver(([entrada]) => setAnchoPx(entrada.contentRect.width - 26));
      observer.observe(nodo);
      return () => observer.disconnect();
   }, [hayLista]);

   const cambiarFiltro = (cambio: Partial<Filtro>) => {
      setFiltro(f => ({ ...f, ...cambio }));
      setMostrados(TRAMO_PATRONES);
      setAbierto(null);
   };
   const cambiarPedido = (texto: string) => {
      setPedidoTexto(texto);
      const valor = texto.trim();
      // Solo se aplica un pedido que existe en la versión; se elige uno a la vez.
      const pedido = pedidosValidos.has(valor) ? valor : '';
      if (pedido !== filtro.pedido) cambiarFiltro({ pedido });
   };
   const quitarFiltros = () => {
      setPedidoTexto('');
      cambiarFiltro(FILTRO_VACIO);
   };
   const cerrar = (id: string) => {
      setAbierto(null);
      filas.current.get(id)?.focus();
   };

   const hayFiltros = Object.values(filtro).some(Boolean) || pedidoTexto !== '';
   const pedidoPendiente = pedidoTexto.trim() !== '' && !filtro.pedido;

   return (
      <Card className="p-5 sm:p-6" aria-labelledby="seccion-patrones">
         <section ref={seccion} aria-busy={estado.fase === 'cargando' || estado.fase === 'inactiva'}>
            <h2 id="seccion-patrones" className="text-base font-semibold text-content">Patrones de corte</h2>

            {(estado.fase === 'inactiva' || estado.fase === 'cargando') && (
               <div className="mt-3 flex items-center gap-3 text-sm text-content-muted">
                  <RefreshCw className="h-4 w-4 animate-spin" aria-hidden="true" />
                  Cargando patrones…
               </div>
            )}

            {estado.fase === 'no_disponible' && (
               <p className="mt-3 text-sm text-content-muted">
                  Patrones: no disponible para esta versión. {estado.motivo}.
               </p>
            )}

            {estado.fase === 'error' && (
               <Alert tone="error" title="No fue posible cargar los patrones" className="mt-3">
                  <p>{estado.mensaje}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={cargar}>Reintentar</Button>
               </Alert>
            )}

            {vista && cob && (
               <>
                  <p className="mt-1 text-sm text-content-muted">
                     <span className="font-mono font-semibold text-content">{numero(vista.totales.patrones, 0)}</span> patrones para{' '}
                     <span className="font-mono font-semibold text-content">{numero(vista.totales.barras, 0)}</span> barras. Cada
                     patrón es una forma de cortar que se repite.
                  </p>

                  <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                     <Field label="Diámetro" htmlFor="patrones-diametro">
                        <Select id="patrones-diametro" value={filtro.diametro} onChange={e => cambiarFiltro({ diametro: e.target.value })}>
                           <option value="">Todos</option>
                           {vista.diametros.map(d => <option key={d} value={d}>{d}</option>)}
                        </Select>
                     </Field>
                     <Field label="Etapa" htmlFor="patrones-etapa">
                        <Select id="patrones-etapa" value={filtro.etapa} onChange={e => cambiarFiltro({ etapa: e.target.value })}>
                           <option value="">Todas</option>
                           {vista.etapas.map(e => <option key={e} value={e}>E{e}</option>)}
                        </Select>
                     </Field>
                     <Field label="Origen" htmlFor="patrones-origen">
                        <Select id="patrones-origen" value={filtro.origen} onChange={e => cambiarFiltro({ origen: e.target.value })}>
                           <option value="">Todos</option>
                           {vista.origenes.map(o => <option key={o} value={o}>{ORIGEN_LABELS[o] ?? o}</option>)}
                        </Select>
                     </Field>
                     <Field
                        label="Pedido (N° Orden)"
                        htmlFor="patrones-pedido"
                        description={pedidoPendiente ? 'Elige un pedido de la lista.' : undefined}
                     >
                        <Input
                           id="patrones-pedido"
                           list="patrones-pedidos"
                           inputMode="search"
                           autoComplete="off"
                           value={pedidoTexto}
                           aria-describedby={pedidoPendiente ? 'patrones-pedido-description' : undefined}
                           onChange={e => cambiarPedido(e.target.value)}
                        />
                        <datalist id="patrones-pedidos">
                           {vista.pedidos.map(p => <option key={p.pedido} value={p.pedido} />)}
                        </datalist>
                     </Field>
                     <Field label="Orden" htmlFor="patrones-orden">
                        <Select id="patrones-orden" value={criterio} onChange={e => setCriterio(e.target.value as Criterio)}>
                           {CRITERIOS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                        </Select>
                     </Field>
                  </div>

                  <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                     <p aria-live="polite" className="font-mono text-xs tabular-nums text-content-muted">
                        Se muestran {numero(cob.n, 0)} de {numero(cob.m, 0)} patrones, que cubren {numero(cob.b, 0)} de{' '}
                        {numero(cob.t, 0)} barras ({numero(cob.pct, 1)} %)
                     </p>
                     {hayFiltros && <Button size="sm" variant="outline" onClick={quitarFiltros}>Quitar filtros</Button>}
                  </div>

                  <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-content-muted" aria-label="Leyenda del dibujo">
                     {vista.etapas.map(e => (
                        <li key={e} className="flex items-center gap-1.5">
                           <span className={cn('inline-block h-3 w-4 rounded-sm', claseEtapa(e))} aria-hidden="true" />
                           Etapa E{e}
                        </li>
                     ))}
                     <li className="flex items-center gap-1.5">
                        <span className="inline-block h-3 w-1 border-x border-line-strong bg-surface-elevated" aria-hidden="true" />
                        Pérdida por corte (separación)
                     </li>
                     <li className="flex items-center gap-1.5">
                        <span className="inline-block h-3 w-4 rounded-sm bg-status-error-text" aria-hidden="true" />
                        Descarte
                     </li>
                     <li className="flex items-center gap-1.5">
                        <span className="inline-block h-3 w-4 rounded-sm bg-data-remaining" aria-hidden="true" />
                        Saldo reutilizable
                     </li>
                  </ul>
                  {vista.etapas.length > 6 && (
                     <p className="mt-1 text-xs text-content-muted">Los colores se repiten desde la etapa E7; la etapa se nombra en el detalle.</p>
                  )}

                  {!hayLista ? (
                     <div className="mt-4 rounded-md border border-line p-4 text-sm text-content-muted">
                        Ningún patrón cumple los filtros.{' '}
                        <Button size="sm" variant="link" onClick={quitarFiltros}>Quitar filtros</Button>
                     </div>
                  ) : (
                     <ul ref={lista} className="mt-4 space-y-2" aria-label="Patrones de corte de la versión">
                        {ordenados.slice(0, mostrados).map(p => {
                           const detalleId = `detalle-${p.patron_id}`;
                           const aporte = filtro.pedido ? aportePedido(p, filtro.pedido) : undefined;
                           return (
                              <li key={p.patron_id}>
                                 <PatternRow
                                    ref={nodo => {
                                       if (nodo) filas.current.set(p.patron_id, nodo);
                                       else filas.current.delete(p.patron_id);
                                    }}
                                    patron={p}
                                    escala={vista.escala_m}
                                    anchoPx={anchoPx}
                                    abierto={abierto === p.patron_id}
                                    detalleId={detalleId}
                                    pedido={filtro.pedido || undefined}
                                    aporte={aporte}
                                    onToggle={() => setAbierto(a => (a === p.patron_id ? null : p.patron_id))}
                                 />
                                 {abierto === p.patron_id && (
                                    <PatternDetail
                                       id={detalleId}
                                       patron={p}
                                       pedido={filtro.pedido || undefined}
                                       onClose={() => cerrar(p.patron_id)}
                                    />
                                 )}
                              </li>
                           );
                        })}
                     </ul>
                  )}
                  {ordenados.length > mostrados && (
                     <Button size="sm" variant="outline" className="mt-3" onClick={() => setMostrados(m => m + TRAMO_PATRONES)}>
                        Mostrar más patrones (quedan {numero(ordenados.length - mostrados, 0)})
                     </Button>
                  )}
                  <p className="mt-4 text-xs text-content-muted">
                     Los mismos patrones, con sus identificadores, están en la hoja «Patrones» del Excel. La imagen de nesting
                     se descarga desde la tabla de versiones.
                  </p>
               </>
            )}
         </section>
      </Card>
   );
}
