import * as React from 'react';
import { cn } from '@/lib/utils';

const controlClasses =
   'h-10 w-full rounded-md border border-line-strong bg-surface-elevated px-3 text-sm text-content shadow-raised transition-colors duration-standard placeholder:text-content-subtle hover:border-line-focus focus-visible:border-line-focus focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus/20 disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:text-content-subtle';

const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
   ({ className, ...props }, ref) => (
      <input ref={ref} className={cn(controlClasses, className)} {...props} />
   )
);
Input.displayName = 'Input';

const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
   ({ className, ...props }, ref) => (
      <select ref={ref} className={cn(controlClasses, 'pr-9', className)} {...props} />
   )
);
Select.displayName = 'Select';

const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
   ({ className, ...props }, ref) => (
      <textarea
         ref={ref}
         className={cn(controlClasses, 'min-h-28 resize-y py-3', className)}
         {...props}
      />
   )
);
Textarea.displayName = 'Textarea';

interface FieldProps {
   label: React.ReactNode;
   htmlFor: string;
   description?: React.ReactNode;
   error?: React.ReactNode;
   className?: string;
   children: React.ReactNode;
}

function Field({ label, htmlFor, description, error, className, children }: FieldProps) {
   return (
      <div className={cn('space-y-2 text-left', className)}>
         <label htmlFor={htmlFor} className="block text-sm font-semibold text-content">
            {label}
         </label>
         {children}
         {description && !error && (
            <p id={`${htmlFor}-description`} className="text-xs leading-5 text-content-muted">
               {description}
            </p>
         )}
         {error && (
            <p id={`${htmlFor}-error`} className="text-xs font-medium leading-5 text-content-error">
               {error}
            </p>
         )}
      </div>
   );
}

interface CheckboxFieldProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
   label: React.ReactNode;
   description?: React.ReactNode;
}

function CheckboxField({ label, description, className, id, ...props }: CheckboxFieldProps) {
   const generatedId = React.useId();
   const inputId = id ?? generatedId;
   return (
      <div className={cn('flex items-start gap-3', className)}>
         <input
            id={inputId}
            type="checkbox"
            className="mt-0.5 h-5 w-5 shrink-0 rounded-sm border-line-strong accent-action-primary focus-visible:ring-2 focus-visible:ring-line-focus disabled:cursor-not-allowed disabled:opacity-50"
            {...props}
         />
         <div className="min-w-0">
            <label htmlFor={inputId} className="block cursor-pointer text-sm font-medium text-content">
               {label}
            </label>
            {description && <p className="mt-1 text-xs leading-5 text-content-muted">{description}</p>}
         </div>
      </div>
   );
}

export { CheckboxField, Field, Input, Select, Textarea, controlClasses };
