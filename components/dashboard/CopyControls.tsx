import { useMemo, useState } from "react";
import { Copy, Plus, Sparkles } from "lucide-react";
import type { AdDraftInput, AdProfileInput } from "../../types/ads";

export default function CopyControls({
  draft,
  profile,
  disabled,
  onChange,
  onGenerate,
}: {
  draft: AdDraftInput;
  profile: AdProfileInput;
  disabled: boolean;
  onChange: (patch: Partial<AdDraftInput>) => void;
  onGenerate: (instruction: string) => Promise<void>;
}) {
  const [task, setTask] = useState(
    "Write a benefit-led ad with a clear next step.",
  );
  const checks = useMemo(() => {
    const words = draft.body.trim().split(/\s+/).filter(Boolean);
    const sentences = draft.body.split(/[.!?]+/).filter((s) => s.trim());
    const issues: string[] = [];
    if (!draft.headline.trim()) issues.push("Add a specific headline.");
    if (!draft.cta.trim()) issues.push("Add one clear call to action.");
    if (profile.channel === "Google" && draft.headline.length > 30)
      issues.push("Google search headline exceeds 30 characters.");
    if (profile.channel === "Google" && draft.body.length > 90)
      issues.push(
        "Google search description exceeds 90 characters; split into separate descriptions.",
      );
    if (
      /\b(guaranteed|best|#1|100%|miracle)\b/i.test(
        draft.body + " " + draft.headline,
      )
    )
      issues.push(
        "Review absolute or comparative claims; retain only substantiated language.",
      );
    if (/\d+\s*%/.test(draft.body))
      issues.push("Verify every percentage against supplied evidence.");
    for (const phrase of profile.prohibited_claims
      .split(/[\n,;]+/)
      .map((s) => s.trim())
      .filter((s) => s.length > 2 && s.length < 80)) {
      if (
        (draft.body + " " + draft.headline)
          .toLowerCase()
          .includes(phrase.toLowerCase())
      )
        issues.push(`Potential prohibited phrase: ${phrase}`);
    }
    if (sentences.some((s) => s.trim().split(/\s+/).length > 30))
      issues.push(
        "Some sentences exceed 30 words. Consider shorter sentences.",
      );
    return { words: words.length, sentences: sentences.length, issues };
  }, [draft.body, draft.headline, draft.cta, profile]);
  return (
    <fieldset
      disabled={disabled}
      className="space-y-4 border-t border-border pt-4"
    >
      <legend className="font-display font-semibold pt-4">
        Copywriting workbench
      </legend>
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="owner-label">
          Message framework
          <select
            className="owner-input"
            value={draft.copy_framework || "Direct"}
            onChange={(e) =>
              onChange({
                copy_framework: e.target
                  .value as AdDraftInput["copy_framework"],
              })
            }
          >
            {["Direct", "AIDA", "PAS", "BAB"].map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
        <label className="owner-label">
          Rewrite objective
          <select
            className="owner-input"
            value={task}
            onChange={(e) => setTask(e.target.value)}
          >
            {[
              "Write a benefit-led ad with a clear next step.",
              "Shorten the draft without losing factual meaning.",
              "Generate three distinct hooks for the same offer.",
              "Rewrite for the named audience and brand voice.",
              "Audit unsupported claims and explain needed evidence.",
            ].map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
      </div>
      <button
        type="button"
        className="owner-button-secondary"
        onClick={() =>
          void onGenerate(
            `Framework: ${draft.copy_framework || "Direct"}. ${task} Preserve verified facts. Return concise usable copy.\nHeadline: ${draft.headline}\nBody: ${draft.body}\nCTA: ${draft.cta}`,
          )
        }
      >
        <Sparkles className="w-4 h-4" />
        Run copy assistant
      </button>
      <p className="text-xs text-muted-foreground">
        Real provider request; may incur charges. Quality checks below are local
        rules, not a predicted conversion score.
      </p>
      <section className="border-t border-border pt-4">
        <h4 className="font-semibold text-sm">Preflight checks</h4>
        <p className="text-xs text-muted-foreground mt-2">
          {checks.words} words · {checks.sentences} sentences ·{" "}
          {draft.body.length} characters
        </p>
        <ul className="text-sm mt-3 space-y-2">
          {checks.issues.map((issue) => (
            <li key={issue}>{issue}</li>
          ))}
          {!checks.issues.length && (
            <li>
              No local rule violations found. Human fact/compliance review still
              required.
            </li>
          )}
        </ul>
      </section>
      <section className="border-t border-border pt-4 space-y-3">
        <div className="flex flex-wrap justify-between gap-3">
          <h4 className="font-semibold text-sm">
            Saved variants · {(draft.copy_variants || []).length}/8
          </h4>
          <button
            type="button"
            className="owner-button-secondary"
            disabled={
              !draft.body.trim() || (draft.copy_variants || []).length >= 8
            }
            onClick={() =>
              onChange({
                copy_variants: [...(draft.copy_variants || []), draft.body],
              })
            }
          >
            <Plus className="w-4 h-4" />
            Keep this variant
          </button>
        </div>
        {draft.copy_variants?.map((variant, index) => (
          <div
            className="border border-border rounded-lg p-3 space-y-3"
            key={index}
          >
            <p className="text-xs text-muted-foreground">Variant {index + 1}</p>
            <p className="text-sm whitespace-pre-wrap break-words">{variant}</p>
            <div className="flex gap-2">
              <button
                type="button"
                className="owner-button-secondary"
                onClick={() => onChange({ body: variant })}
              >
                <Copy className="w-4 h-4" />
                Use variant
              </button>
              <button
                type="button"
                className="owner-button-secondary"
                onClick={() =>
                  onChange({
                    copy_variants: draft.copy_variants?.filter(
                      (_, i) => i !== index,
                    ),
                  })
                }
              >
                Remove
              </button>
            </div>
          </div>
        ))}
        <p className="text-xs text-muted-foreground">
          Save the creative to persist variants. Measure variants in Ad
          optimization; no winner is inferred from wording alone.
        </p>
      </section>
    </fieldset>
  );
}
