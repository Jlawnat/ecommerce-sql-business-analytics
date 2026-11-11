import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const buttonVariants = cva(
  "button inline-flex min-h-11 items-center justify-center gap-2 whitespace-nowrap rounded-md px-3 text-sm font-medium transition-colors focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-60",
  {
    variants: {
      variant: {
        primary: "bg-[var(--ink)] text-white hover:bg-[var(--ink-strong)]",
        secondary: "border border-[var(--control)] bg-[var(--sheet)] text-[var(--ink)] hover:bg-[var(--surface-muted)]",
        ghost: "text-[var(--ink-muted)] hover:bg-[var(--active)] hover:text-[var(--ink)]",
      },
    },
    defaultVariants: { variant: "secondary" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, ...props }: ButtonProps) {
  return <button className={cn(buttonVariants({ variant }), className)} {...props} />;
}
