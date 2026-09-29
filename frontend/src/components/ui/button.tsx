import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
   'inline-flex shrink-0 items-center justify-center gap-2 rounded-md border text-sm font-semibold transition-colors duration-standard ease-standard focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-line-focus focus-visible:ring-offset-2 focus-visible:ring-offset-surface disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50',
   {
      variants: {
         variant: {
            default:
               'border-action-primary bg-action-primary text-action-primary-text shadow-raised hover:border-action-primary-hover hover:bg-action-primary-hover active:border-action-primary-active active:bg-action-primary-active',
            destructive:
               'border-action-danger bg-action-danger text-content-inverse shadow-raised hover:border-action-danger-hover hover:bg-action-danger-hover',
            outline:
               'border-line-strong bg-action-secondary text-content hover:border-line-focus hover:bg-action-secondary-hover hover:text-content-brand',
            secondary:
               'border-line bg-surface-subtle text-content hover:border-line-strong hover:bg-surface-interactive',
            ghost:
               'border-transparent bg-transparent text-content-muted hover:bg-surface-interactive hover:text-content-brand',
            link:
               'h-auto border-transparent bg-transparent p-0 text-content-brand underline-offset-4 hover:underline',
         },
         size: {
            default: 'h-10 px-4',
            sm: 'h-8 px-3 text-xs',
            lg: 'h-12 px-6 text-base',
            icon: 'h-10 w-10 px-0',
         },
      },
      defaultVariants: {
         variant: 'default',
         size: 'default',
      },
   }
);

export interface ButtonProps
   extends React.ButtonHTMLAttributes<HTMLButtonElement>,
      VariantProps<typeof buttonVariants> {
   asChild?: boolean;
   loading?: boolean;
   loader?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
   (
      {
         className,
         variant,
         size,
         asChild = false,
         loading = false,
         loader,
         children,
         disabled,
         ...props
      },
      ref
   ) => {
      const Comp = asChild ? Slot : 'button';
      return (
         <Comp
            className={cn(buttonVariants({ variant, size, className }))}
            ref={ref}
            disabled={disabled || loading}
            {...props}
         >
            {loading ? (
               <span className="flex items-center justify-center gap-2">
                  {loader || <DefaultLoader />}
                  <span className="sr-only">Procesando</span>
               </span>
            ) : (
               children
            )}
         </Comp>
      );
   }
);
Button.displayName = 'Button';

const DefaultLoader: React.FC = () => (
   <svg
      className="h-5 w-5 animate-spin text-current"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
   >
      <circle
         className="opacity-25"
         cx="12"
         cy="12"
         r="10"
         stroke="currentColor"
         strokeWidth="4"
      ></circle>
      <path
         className="opacity-75"
         fill="currentColor"
         d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
   </svg>
);

export { Button, buttonVariants };
