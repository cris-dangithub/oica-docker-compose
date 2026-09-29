import * as React from 'react';
import { cn } from '@/lib/utils';

function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
   return (
      <div
         className={cn('rounded-lg border border-line bg-surface-elevated shadow-raised', className)}
         {...props}
      />
   );
}

export { Card };
