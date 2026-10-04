/**
 * Lógica pura del explorador de patrones (spec 002, FR-027 y FR-031; data-model §8.2).
 * Sin React: filtra, ordena y mide la cobertura sobre la respuesta de /patrones/<uuid>.
 */
import { decimal, type PatronExplorable } from '../types';

export interface Filtro {
   diametro: string;
   etapa: string;
   origen: string;
   pedido: string;
}

export const FILTRO_VACIO: Filtro = { diametro: '', etapa: '', origen: '', pedido: '' };

export type Criterio = 'excel' | 'repeticiones' | 'aprovechamiento' | 'saldo';

export const CRITERIOS: { value: Criterio; label: string }[] = [
   { value: 'excel', label: 'Como el Excel' },
   { value: 'repeticiones', label: 'Repeticiones' },
   { value: 'aprovechamiento', label: 'Aprovechamiento' },
   { value: 'saldo', label: 'Saldo' },
];

export const ORIGEN_LABELS: Record<string, string> = {
   comercial: 'Compra',
   adicional: 'Inventario adicional',
};

/** Piezas que el patrón aporta al pedido, con sus repeticiones incluidas. */
export function aportePedido(patron: PatronExplorable, pedido: string): number {
   return patron.piezas.reduce(
      (total, pieza) => total + pieza.pedidos.reduce((s, p) => s + (p.pedido === pedido ? p.piezas : 0), 0),
      0,
   );
}

/** Los filtros activos se combinan con Y (FR-027). */
export function filtrar(patrones: PatronExplorable[], filtro: Filtro): PatronExplorable[] {
   const etapa = filtro.etapa ? Number(filtro.etapa) : null;
   return patrones.filter(
      (p) =>
         (!filtro.diametro || p.diametro === filtro.diametro) &&
         (etapa === null || p.etapas.includes(etapa)) &&
         (!filtro.origen || p.origen === filtro.origen) &&
         (!filtro.pedido || aportePedido(p, filtro.pedido) > 0),
   );
}

/** De mayor a menor; los empates conservan el orden del Excel, que es el de llegada (FR-031). */
export function ordenar(patrones: PatronExplorable[], criterio: Criterio): PatronExplorable[] {
   if (criterio === 'excel') return patrones;
   const valor = (p: PatronExplorable) =>
      criterio === 'repeticiones' ? p.repeticiones : criterio === 'aprovechamiento' ? p.aprovechamiento_pct : p.saldo_m;
   return patrones
      .map((p, indice) => ({ p, indice }))
      .sort((a, b) => valor(b.p) - valor(a.p) || a.indice - b.indice)
      .map(({ p }) => p);
}

export interface Cobertura {
   n: number;
   m: number;
   b: number;
   t: number;
   pct: number;
}

/** Patrones y barras mostrados frente al total; `b ≤ t` y, sin filtros, `b = t`. */
export function cobertura(filtrados: PatronExplorable[], totales: { patrones: number; barras: number }): Cobertura {
   const b = filtrados.reduce((s, p) => s + p.repeticiones, 0);
   return { n: filtrados.length, m: totales.patrones, b, t: totales.barras, pct: totales.barras ? (100 * b) / totales.barras : 0 };
}

/**
 * Cifra con punto de miles y coma decimal, sin ceros finales, como en el PDF (R-05).
 * Es manual para que el servidor y el navegador produzcan el mismo texto.
 */
export function numero(valor: number, digits = 2): string {
   const texto = decimal(valor, digits);
   // Solo se quitan ceros después de la coma: «4,200» → «4,2»; «13.000» queda igual.
   return texto.includes(',') ? texto.replace(/0+$/, '').replace(/,$/, '') : texto;
}

/** Longitud legible: «4,2 m». */
export function metros(valor: number): string {
   return `${numero(valor, 3)} m`;
}

/** Índice (1–6) del token de color de una etapa; se repite en ciclo desde la etapa 7. */
export function tonoEtapa(etapa: number): number {
   return ((((etapa - 1) % 6) + 6) % 6) + 1;
}
