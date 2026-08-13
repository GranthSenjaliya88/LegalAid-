import { Toaster as SonnerToaster } from "sonner";

/**
 * App-wide toast surface. Styled to match the LegalAId palette
 * (ivory surface, teal text, hairline border) rather than sonner defaults.
 */
export function Toaster() {
  return (
    <SonnerToaster
      position="bottom-center"
      gap={10}
      toastOptions={{
        classNames: {
          toast:
            "!rounded-xl !border !border-hairline !bg-surface !text-ink !shadow-lift !font-sans !text-small",
          title: "!font-medium",
          description: "!text-muted",
          actionButton: "!bg-teal !text-ivory-soft !rounded-md",
          cancelButton: "!bg-ivory !text-muted !rounded-md",
          error: "!border-danger/30",
          success: "!border-success/30",
        },
      }}
    />
  );
}
