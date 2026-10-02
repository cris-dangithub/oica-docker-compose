/**
 * Verificación independiente visible (US2: FR-029). Una ejecución que no supera la
 * verificación no crea versión: su motivo queda en el estado del archivo.
 */
import React from 'react';
import { Alert } from '@/components/ui/alert';
import { NO_DISPONIBLE, VersionDetalle } from './types';

interface VerificationBannerProps {
   version: VersionDetalle;
   fileStatus: string;
   statusDetails: string | null;
}

export default function VerificationBanner({ version, fileStatus, statusDetails }: VerificationBannerProps) {
   const failed = fileStatus.startsWith('error_') && fileStatus !== 'error_generation';
   return (
      <div className="space-y-3">
         {failed && (
            <Alert tone="error" title="La última ejecución no produjo un plan válido">
               <p>{statusDetails || 'Motivo no registrado.'}</p>
               <p className="mt-1 text-xs">
                  Las versiones mostradas abajo son anteriores y conservan su propia verificación.
               </p>
            </Alert>
         )}
         {version.valido == null ? (
            <Alert tone="info" title="Verificación no disponible">
               Esta versión se procesó con el motor histórico; su verificación independiente está {NO_DISPONIBLE}.
            </Alert>
         ) : version.valido ? (
            <Alert tone="success" title="Plan verificado">
               La versión v{version.version_number} pasó la verificación independiente de demanda, diámetro, capacidad,
               etapas e inventario. Puede usarse como base de compra.
            </Alert>
         ) : (
            <Alert tone="error" title="Plan no verificado">
               La versión v{version.version_number} no pasó la verificación independiente y no debe usarse como base de
               compra.
            </Alert>
         )}
      </div>
   );
}
