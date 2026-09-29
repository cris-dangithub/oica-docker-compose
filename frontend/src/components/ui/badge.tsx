import * as React from 'react';
import { cn } from '@/lib/utils';

const tones = {
   neutral: 'border-line bg-surface-subtle text-content-muted',
   info: 'border-status-info-border bg-status-info-bg text-status-info-text',
   success: 'border-status-success-border bg-status-success-bg text-status-success-text',
   warning: 'border-status-warning-border bg-status-warning-bg text-status-warning-text',
   error: 'border-status-error-border bg-status-error-bg text-status-error-text',
};

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
   tone?: keyof typeof tones;
}

function Badge({ tone = 'neutral', className, ...props }: BadgeProps) {
   return (
      <span
         className={cn(
            'inline-flex min-h-6 items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold',
            tones[tone],
            className
         )}
         {...props}
      />
   );
}

export { Badge };
