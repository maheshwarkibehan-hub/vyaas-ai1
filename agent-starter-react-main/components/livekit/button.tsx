import * as React from 'react';
import { type VariantProps, cva } from 'class-variance-authority';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  [
    'text-sm font-semibold tracking-wide whitespace-nowrap',
    'inline-flex items-center justify-center gap-2 shrink-0 rounded-xl cursor-pointer outline-none transition-all duration-300',
    'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
    'disabled:pointer-events-none disabled:opacity-50',
    'aria-invalid:ring-destructive/20 aria-invalid:border-destructive dark:aria-invalid:ring-destructive/40 ',
    "[&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 [&_svg]:shrink-0",
    'effect-3d-hover',
  ],
  {
    variants: {
      variant: {
        default: 'effect-glass text-white hover:effect-neon-glow border border-slate-600 hover:border-cyan-500/50',
        destructive: [
          'bg-red-500/20 text-red-400 border border-red-500/30',
          'hover:bg-red-500/30 hover:border-red-400/50 hover:effect-neon-glow',
          'focus-visible:ring-red-500/20',
        ],
        outline: [
          'border border-cyan-500/30 bg-transparent text-cyan-400',
          'hover:bg-cyan-500/10 hover:border-cyan-400/50 hover:effect-neon-glow',
          'focus-visible:ring-cyan-500/20',
        ],
        primary: 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:from-cyan-400 hover:to-blue-500 hover:scale-105 hover:shadow-lg hover:shadow-cyan-500/25',
        secondary: 'effect-glass text-slate-300 hover:effect-neon-glow border border-slate-600 hover:border-cyan-500/50',
        ghost: 'text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10',
        link: 'text-cyan-400 underline-offset-4 hover:underline hover:text-cyan-300',
      },
      size: {
        default: 'h-10 px-6 py-2 has-[>svg]:px-4',
        sm: 'h-8 gap-1.5 px-4 has-[>svg]:px-3',
        lg: 'h-12 px-8 py-3 text-lg has-[>svg]:px-6',
        icon: 'size-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<'button'> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : 'button';

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
