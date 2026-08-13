import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-[background-color,color,box-shadow,border-color] duration-200 ease-calm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2 focus-visible:ring-offset-ivory disabled:pointer-events-none disabled:cursor-not-allowed [&_svg]:size-[1.15em] [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        primary:
          "bg-teal text-white shadow-soft hover:bg-teal-dark active:bg-teal-900 disabled:bg-hairline disabled:text-muted disabled:shadow-none",
        gold: "bg-gold text-teal-dark shadow-gold hover:bg-gold-deep hover:text-white disabled:bg-hairline disabled:text-muted disabled:shadow-none",
        secondary: "bg-teal/[0.06] text-teal hover:bg-teal/10 disabled:opacity-40",
        outline:
          "border border-hairline bg-surface text-ink hover:border-teal/40 hover:bg-teal/[0.04] disabled:opacity-40",
        ghost: "text-ink hover:bg-teal/[0.06] disabled:opacity-40",
        subtle: "bg-ivory text-muted hover:text-ink hover:bg-teal/[0.05] disabled:opacity-40",
        danger:
          "bg-danger text-white shadow-soft hover:brightness-[0.96] disabled:bg-hairline disabled:text-muted disabled:shadow-none",
        link: "text-teal underline-offset-4 hover:underline disabled:opacity-40",
      },
      size: {
        sm: "h-9 px-3.5 text-small",
        md: "h-11 px-5 text-small",
        lg: "h-12 px-6 text-body",
        icon: "h-11 w-11",
        "icon-sm": "h-9 w-9",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, type, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        type={asChild ? undefined : (type ?? "button")}
        className={cn(buttonVariants({ variant, size }), className)}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { buttonVariants };
