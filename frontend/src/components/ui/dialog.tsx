'use client';

import * as React from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DialogProps {
   open: boolean;
   onClose: () => void;
   title: string;
   description?: React.ReactNode;
   children?: React.ReactNode;
   footer?: React.ReactNode;
   className?: string;
}

/**
 * Diálogo modal sobre <dialog> nativo: el navegador gestiona foco, Escape y
 * la capa inerte del resto de la página.
 */
function Dialog({ open, onClose, title, description, children, footer, className }: DialogProps) {
   const ref = React.useRef<HTMLDialogElement>(null);
   const titleId = React.useId();
   const descriptionId = React.useId();

   React.useEffect(() => {
      const dialog = ref.current;
      if (!dialog) return;
      if (open && !dialog.open) dialog.showModal();
      if (!open && dialog.open) dialog.close();
   }, [open]);

   return (
      <dialog
         ref={ref}
         aria-labelledby={titleId}
         aria-describedby={description ? descriptionId : undefined}
         onClose={onClose}
         onCancel={event => { event.preventDefault(); onClose(); }}
         onClick={event => { if (event.target === ref.current) onClose(); }}
         className={cn(
            'fixed inset-0 m-auto h-fit max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-md overflow-y-auto rounded-lg border border-line bg-surface-elevated p-0 text-content shadow-overlay backdrop:bg-surface-inverse/40',
            className
         )}
      >
         {open && (
            <div className="p-5 sm:p-6">
               <div className="flex items-start justify-between gap-4">
                  <h2 id={titleId} className="text-lg font-semibold text-content">{title}</h2>
                  <button
                     type="button"
                     onClick={onClose}
                     aria-label="Cerrar"
                     className="-mr-2 -mt-2 inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md text-content-muted hover:bg-surface-interactive hover:text-content focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus"
                  >
                     <X className="h-5 w-5" aria-hidden="true" />
                  </button>
               </div>
               {description && (
                  <div id={descriptionId} className="mt-2 text-sm leading-6 text-content-muted">{description}</div>
               )}
               {children && <div className="mt-5">{children}</div>}
               {footer && (
                  <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">{footer}</div>
               )}
            </div>
         )}
      </dialog>
   );
}

export { Dialog };
