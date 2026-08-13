import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/common/EmptyState";

/** 404 — a calm dead-end with a clear way back. */
export function NotFoundPage() {
  return (
    <div className="flex min-h-[55vh] items-center justify-center">
      <EmptyState
        icon={Compass}
        title="This page isn't here"
        description="The page you're looking for may have moved or never existed. Let's get you back on track."
        action={
          <Button asChild>
            <Link to="/">Back to the assistant</Link>
          </Button>
        }
      />
    </div>
  );
}
