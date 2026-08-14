import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/common/EmptyState";
import { useAppStore } from "@/store/appStore";

/** 404 with a clear way back. */
export function NotFoundPage() {
  const hi = useAppStore((s) => s.language) === "hi";

  return (
    <div className="flex min-h-[55vh] items-center justify-center">
      <EmptyState
        icon={Compass}
        title={hi ? "यह पेज उपलब्ध नहीं है" : "This page isn't here"}
        description={
          hi
            ? "आप जिस पेज को खोज रहे हैं, वह हट गया हो सकता है या कभी मौजूद नहीं था। आइए वापस चलें।"
            : "The page you're looking for may have moved or never existed. Let's get you back on track."
        }
        action={
          <Button asChild>
            <Link to="/">{hi ? "सहायक पर वापस जाएँ" : "Back to the assistant"}</Link>
          </Button>
        }
      />
    </div>
  );
}
