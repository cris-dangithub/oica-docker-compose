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

export const NO_DISPONIBLE = 'no disponible';

export const pct = (value?: number | null, digits = 3) =>
   value != null ? `${value.toFixed(digits)} %` : NO_DISPONIBLE;

export const pp = (value?: number | null, digits = 3) =>
   value != null ? `${value > 0 ? '+' : ''}${value.toFixed(digits)} pp` : NO_DISPONIBLE;

export const kg = (value?: number | null) => (value != null ? `${value.toFixed(3)} kg` : NO_DISPONIBLE);

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
