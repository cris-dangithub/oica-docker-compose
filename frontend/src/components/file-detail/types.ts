/**
 * Tipos del detalle de un proyecto (spec 001, data-model §2 y contracts/http-api.md).
 * Los campos del análisis son opcionales: las versiones históricas no los tienen.
 */

export type EstadoAdmisibilidad = 'dentro' | 'excede' | 'sin_evaluar';

export interface EvaluacionAdmisibilidad {
   estado: EstadoAdmisibilidad;
   desperdicio_pct: number;
   diferencia_pp: number | null;
   diametro?: string;
}

export interface Medida {
   kg: number;
   pct: number;
}

export interface Perdidas {
   irrecuperable: Medida;
   reutilizable: Medida;
   por_diametro: Record<string, { irrecuperable: Medida; reutilizable: Medida }>;
}

export interface LineaCompra {
   diametro: string;
   longitud_m: number;
   origen: 'comercial' | 'adicional';
   barras: number;
   masa_kg: number;
   aprovechamiento_pct: number;
}

export interface PatronResumen {
   patron_id: string;
   diametro: string;
   origen: string;
   longitud_m: number;
   repeticiones: number;
   aprovechamiento_pct: number;
}

export interface CotaDiametro {
   diametro: string;
   material_m: number | null;
   material_kg: number | null;
   desperdicio_pct: number | null;
   ajustada: boolean;
   simple: { material_m: number; desperdicio_pct: number; barras_minimas: number };
   brecha_pp: number | null;
   iteraciones?: number;
   columnas?: number;
   segundos?: number;
}

export interface CotaInferior {
   estado: 'calculada' | 'no_disponible';
   motivo: string | null;
   ajustada: boolean;
   proyecto?: {
      material_kg: number | null;
      desperdicio_pct: number | null;
      simple_desperdicio_pct: number;
      brecha_pp: number | null;
   };
   por_diametro?: CotaDiametro[];
}

export interface AvisoMasa {
   diametro: string;
   masa_cartilla_kg_m: number;
   masa_nominal_kg_m: number | null;
   diferencia_relativa_pct: number | null;
   estado: 'aviso' | 'no_contrastado';
}

export interface Analisis {
   version: string;
   umbral_desperdicio_pct: number | null;
   verificacion: { valido: boolean; comprobaciones: string[] };
   aprovechamiento_pct?: number;
   perdidas?: Perdidas;
   admisibilidad?: {
      proyecto: EvaluacionAdmisibilidad;
      por_diametro: EvaluacionAdmisibilidad[];
   };
   resumen_compra?: LineaCompra[];
   patrones?: { total: number; barras: number; max_repeticiones: number; top: PatronResumen[] };
   cota?: CotaInferior;
   avisos_masa?: AvisoMasa[];
}

export interface VersionDetalle {
   id: number;
   version_number: number;
   storage_uuid: string;
   status: string;
   result_status: string;
   error_message: string | null;
   perfil_usado: string | null;
   processing_time_seconds: number | null;
   motor?: string;
   desperdicio_porcentaje: number | null;
   perdida_corte_kg?: number | null;
   descartado_kg?: number | null;
   sobrante_final_kg?: number | null;
   valido: boolean | null;
   umbral_desperdicio_pct: number | null;
   admisibilidad_estado: EstadoAdmisibilidad | null;
   analisis?: Analisis | null;
   excel_path?: string | null;
   pdf_path?: string | null;
   graph_image_path?: string | null;
   image_path?: string | null;
   inventory_path?: string | null;
   created_at: string;
}

export interface ArchivoDetalle {
   id: number;
   filename: string;
   status: string;
   status_details: string | null;
   perfil: string | null;
   created_at: string;
   umbral_desperdicio_pct: number | null;
   processing_results?: VersionDetalle[];
}

/* Explorador de patrones (spec 002, contracts/api-patrones.md y contracts/ui.md «Tipos»). */

export interface PedidoPiezas {
   pedido: string;
   piezas: number;
}

export interface PiezaPatron {
   etapa: number;
   longitud_m: number;
   cantidad: number;
   pedidos: PedidoPiezas[];
}

export interface RangoBarras {
   desde: string;
   hasta: string;
   n: number;
}

export interface PatronExplorable {
   patron_id: string;
   diametro: string;
   origen: string;
   longitud_m: number;
   secuencia: string;
   repeticiones: number;
   aprovechamiento_pct: number;
   perdida_corte_m: number;
   descartado_m: number;
   saldo_m: number;
   etapas: number[];
   piezas: PiezaPatron[];
   barras: { total: number; rangos: RangoBarras[] };
}

export type VistaPatrones =
   | {
        disponible: true;
        storage_uuid: string;
        version_number: number;
        motor: string;
        escala_m: number;
        totales: { patrones: number; barras: number };
        diametros: string[];
        etapas: number[];
        origenes: string[];
        pedidos: PedidoPiezas[];
        patrones: PatronExplorable[];
     }
   | {
        disponible: false;
        storage_uuid: string;
        version_number: number;
        motor: string | null;
        motivo: string;
     };

export const NO_DISPONIBLE = 'no disponible';

/**
 * Cifra con coma decimal y punto de miles, con `digits` decimales fijos («152.039,571»), como el PDF
 * (spec 002, R-05). Es manual para que el servidor y el navegador produzcan el mismo texto.
 */
export function decimal(value: number, digits = 2): string {
   const [entero, decimales] = Math.abs(value).toFixed(digits).split('.');
   const miles = entero.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
   const signo = value < 0 && Number(`${entero}.${decimales ?? 0}`) !== 0 ? '-' : '';
   return `${signo}${miles}${decimales ? `,${decimales}` : ''}`;
}

/** Entero con punto de miles («14.301»). */
export const entero = (value: number) => decimal(value, 0);

/* Decimales por tipo de cifra (FR-033): porcentajes, pp y kg con 2; la cota y la brecha piden 3. */

export const pct = (value?: number | null, digits = 2) =>
   value != null ? `${decimal(value, digits)} %` : NO_DISPONIBLE;

export const pp = (value?: number | null, digits = 2) =>
   value != null ? `${value > 0 ? '+' : ''}${decimal(value, digits)} pp` : NO_DISPONIBLE;

export const kg = (value?: number | null) => (value != null ? `${decimal(value, 2)} kg` : NO_DISPONIBLE);

/**
 * Lee un decimal escrito por el usuario con coma o punto (FR-034): «0,5» y «0.5» valen lo mismo.
 * Devuelve `null` si el texto no es un número («0,5,1», «abc»).
 */
export function leerDecimal(texto: string): number | null {
   const limpio = texto.trim();
   return /^-?\d+([.,]\d+)?$/.test(limpio) ? Number(limpio.replace(',', '.')) : null;
}

/** Decimal escrito por el usuario, con punto, para la API (FR-035). */
export const decimalParaApi = (texto: string) => texto.trim().replace(',', '.');

export const ADMISIBILIDAD_LABELS: Record<EstadoAdmisibilidad, string> = {
   dentro: 'Dentro de lo admisible',
   excede: 'Excede',
   sin_evaluar: 'Sin evaluar',
};

export const ADMISIBILIDAD_TONES: Record<EstadoAdmisibilidad, 'success' | 'error' | 'neutral'> = {
   dentro: 'success',
   excede: 'error',
   sin_evaluar: 'neutral',
};

export const PERFIL_LABELS: Record<string, string> = {
   rapido: 'Rápido',
   balanceado: 'Balanceado',
   profundo: 'Profundo',
};
