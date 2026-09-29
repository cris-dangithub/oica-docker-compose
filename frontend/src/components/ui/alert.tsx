import * as React from 'react';
import { AlertCircle, CheckCircle2, Info, TriangleAlert } from 'lucide-react';
import { cn } from '@/lib/utils';

const styles = {
   info: 'border-status-info-border bg-status-info-bg text-status-info-text',
   success: 'border-status-success-border bg-status-success-bg text-status-success-text',
   warning: 'border-status-warning-border bg-status-warning-bg text-status-warning-text',
   error: 'border-status-error-border bg-status-error-bg text-status-error-text',
};

const icons = { info: Info, success: CheckCircle2, warning: TriangleAlert, error: AlertCircle };

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
   tone?: keyof typeof styles;
   title?: string;
}

function Alert({ tone = 'info', title, children, className, ...props }: AlertProps) {
   const Icon = icons[tone];
   return (
      <div
         role={tone === 'error' ? 'alert' : 'status'}
         className={cn('flex gap-3 rounded-md border p-4 text-sm', styles[tone], className)}
         {...props}
      >
         <Icon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
         <div className="min-w-0">
            {title && <p className="font-semibold">{title}</p>}
            <div className={cn(title && 'mt-1')}>{children}</div>
         </div>
      </div>
   );
}

export { Alert };
