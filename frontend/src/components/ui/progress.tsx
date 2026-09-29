import { cn } from '@/lib/utils';

interface ProgressProps {
   value: number;
   label: string;
   detail?: string;
   /** Oculta visualmente la etiqueta (sigue disponible para lectores de pantalla). */
   hideLabel?: boolean;
   className?: string;
}

function Progress({ value, label, detail, hideLabel = false, className }: ProgressProps) {
   const normalizedValue = Math.max(0, Math.min(100, value));
   return (
      <div className={cn('space-y-2', className)}>
         <div className="flex items-center justify-between gap-4 text-sm">
            <span className={cn('font-medium text-content', hideLabel && 'sr-only')}>{label}</span>
            <span className="font-mono font-semibold tabular-nums text-content-brand">
               {normalizedValue}%
            </span>
         </div>
         <div
            className="h-2 overflow-hidden rounded-full bg-surface-subtle"
            role="progressbar"
            aria-label={label}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={normalizedValue}
         >
            <div
               className="h-full rounded-full bg-data-primary transition-[width] duration-slow ease-standard"
               style={{ width: `${normalizedValue}%` }}
            />
         </div>
         {detail && <p className="text-xs leading-5 text-content-muted">{detail}</p>}
      </div>
   );
}

export { Progress };
