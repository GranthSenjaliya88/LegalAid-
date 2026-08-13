import { useEffect } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { Save, RotateCcw } from "lucide-react";
import type { DocumentData, UpdateDocumentRequest } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PrivacyNote } from "@/components/common/PrivacyNote";

interface DocumentEditorProps {
  document: DocumentData;
  onSave: (body: UpdateDocumentRequest) => void;
  saving?: boolean;
}

interface FormValues {
  title: string;
  sections: { id: string; title: string; content: string }[];
}

/**
 * Editable form for a generated document (Part 17). Every field is under the
 * user's control; nothing is sent until they choose to save.
 */
export function DocumentEditor({ document, onSave, saving = false }: DocumentEditorProps) {
  const { register, control, handleSubmit, reset, formState } = useForm<FormValues>({
    defaultValues: { title: document.title, sections: document.sections },
  });
  const { fields } = useFieldArray({ control, name: "sections" });

  // Re-sync the form whenever a freshly saved/loaded document arrives.
  useEffect(() => {
    reset({ title: document.title, sections: document.sections });
  }, [document, reset]);

  const submit = handleSubmit((values) => {
    onSave({
      title: values.title.trim() || document.title,
      sections: values.sections.map((s) => ({
        id: s.id,
        title: s.title,
        content: s.content,
      })),
    });
  });

  return (
    <form onSubmit={submit} className="space-y-5">
      <div className="space-y-1.5">
        <Label htmlFor="doc-title">Document title</Label>
        <Input id="doc-title" {...register("title")} />
      </div>

      <div className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.id} className="space-y-2 rounded-xl border border-hairline bg-surface p-4">
            <div className="space-y-1.5">
              <Label htmlFor={`section-title-${index}`} className="text-tiny uppercase tracking-wide text-muted">
                Section heading
              </Label>
              <Input
                id={`section-title-${index}`}
                {...register(`sections.${index}.title` as const)}
                className="font-medium"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor={`section-content-${index}`} className="sr-only">
                Section content
              </Label>
              <Textarea
                id={`section-content-${index}`}
                {...register(`sections.${index}.content` as const)}
                className="min-h-[9rem]"
              />
            </div>
          </div>
        ))}
      </div>

      <PrivacyNote />

      <div className="flex flex-wrap items-center gap-3">
        <Button type="submit" disabled={saving || !formState.isDirty}>
          <Save className="size-4" />
          {saving ? "Saving…" : "Save changes"}
        </Button>
        <Button
          type="button"
          variant="ghost"
          onClick={() => reset({ title: document.title, sections: document.sections })}
          disabled={saving || !formState.isDirty}
        >
          <RotateCcw className="size-4" />
          Reset
        </Button>
      </div>
    </form>
  );
}
