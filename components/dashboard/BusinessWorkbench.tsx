import { useEffect, useRef, useState } from "react";
import { Download, Plus, Save, Sparkles } from "lucide-react";
import { apiCall } from "../../services/apiClient";
import { useOwner } from "../../contexts/OwnerContext";
import { useUnsavedChanges } from "../../hooks/useUnsavedChanges";
import type { AgentRun } from "../../types/owner";
import OwnerActions from "./OwnerActions";
import WorkspaceLoading from '../common/WorkspaceLoading';
import { StrategyModeToggle, useStrategyMode } from '../../contexts/StrategyModeContext';
import { strategyGuidance } from './strategyGuidance';

export type WorkbenchKind =
  | "canvas"
  | "strategy"
  | "ideation"
  | "seo"
  | "research"
  | "quickwins";
interface WorkDocument {
  id: string;
  kind: string;
  title: string;
  fields: Record<string, string>;
  updated_at: string;
}
const definitions = {
  canvas: {
    title: "Business canvas",
    description:
      "Nine connected decisions about how your business creates, delivers and captures value.",
    fields: [
      ["partners", "Key partners"],
      ["activities", "Key activities"],
      ["resources", "Key resources"],
      ["value", "Value proposition"],
      ["relationships", "Customer relationships"],
      ["channels", "Channels"],
      ["customers", "Customer segments"],
      ["costs", "Cost structure"],
      ["revenue", "Revenue streams"],
    ],
  },
  strategy: {
    title: "Strategy advisor",
    description:
      "Compare options against a stated goal. Record evidence, constraints and a measurable next action.",
    fields: [
      ["goal", "Business goal"],
      ["baseline", "Current baseline"],
      ["target", "Measurable target"],
      ["deadline", "Decision / review date"],
      ["constraints", "Constraints"],
      ["options", "Options and tradeoffs"],
      ["decision", "Chosen direction"],
      ["evidence", "Evidence and sources"],
      ["next_action", "Next action"],
    ],
  },
  ideation: {
    title: "Ideation lab",
    description:
      "Turn a real customer problem into a testable idea. Assumptions are not evidence.",
    fields: [
      ["problem", "Customer problem"],
      ["audience", "Target audience"],
      ["idea", "Proposed idea"],
      ["benefit", "Customer benefit"],
      ["assumptions", "Riskiest assumptions"],
      ["experiment", "Smallest useful experiment"],
      ["metric", "Success metric and threshold"],
      ["decision", "Decision / learning"],
    ],
  },
  seo: {
    title: "SEO studio",
    description:
      "Write metadata and generate valid structured data from your facts. No invented search score or rich-result guarantee.",
    fields: [
      ["page_title", "Page title"],
      ["description", "Meta description"],
      ["url", "Canonical page URL"],
      ["business_name", "Business name"],
      ["business_type", "Business category"],
      ["keywords", "Target search phrases"],
      ["content_outline", "Page outline and search intent"],
    ],
  },
  research: {
    title: "Market research",
    description:
      "An evidence notebook, not a fabricated market-size estimate. Capture source links, publication dates and what remains uncertain.",
    fields: [
      ["question", "Research question"],
      ["segment", "Market / customer segment"],
      ["source_url", "Source URL"],
      ["source_title", "Source title / publisher"],
      ["published_date", "Publication date"],
      ["evidence", "Observed evidence"],
      ["assumptions", "Unverified assumptions"],
      ["conclusion", "Decision implication"],
    ],
  },
};
export default function BusinessWorkbench({ kind }: { kind: WorkbenchKind }) {
  const { overview, refresh } = useOwner();
  const { mode } = useStrategyMode();
  const guided = mode === 'guided';
  const [step, setStep] = useState(0);
  const stepHeading = useRef<HTMLHeadingElement>(null);
  const formRef = useRef<HTMLFormElement>(null);
  const guide = kind === 'quickwins' ? null : strategyGuidance[kind];
  const reviewing = !!guide && step === guide.steps.length;
  const questions = guide?.steps.flatMap(section => section.questions) || [];
  const [quickStep, setQuickStep] = useState(0);
  const [suggestion, setSuggestion] = useState<{ title: string; notes: string; sequence: number } | null>(null);
  const [documents, setDocuments] = useState<WorkDocument[]>([]),
    [id, setId] = useState(""),
    [title, setTitle] = useState(""),
    [fields, setFields] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(""),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [dirty, setDirty] = useState(false),
    [generated, setGenerated] = useState("");
  const [documentsLoading, setDocumentsLoading] = useState(kind !== 'quickwins');
  useUnsavedChanges(dirty || !!busy);
  useEffect(() => {
    let active = true;
    setId("");
    setTitle("");
    setFields({});
    setDirty(false);
    setGenerated("");
    setStep(0); setQuickStep(0); setSuggestion(null);
    setDocumentsLoading(kind !== 'quickwins' && !!overview?.context);
    if (overview?.context && kind !== "quickwins")
      apiCall<WorkDocument[]>(`/api/v1/workspace/documents?kind=${kind}`)
        .then((rows) => {
          if (active) { setDocuments(rows); setDocumentsLoading(false); }
        })
        .catch((err) => {
          if (active) { setError(err.message); setDocumentsLoading(false); }
        });
    return () => {
      active = false;
    };
  }, [kind, overview?.context?.id]);
  const context = overview?.context;
  const goToStep = (next: number) => {
    if (next > step && !formRef.current?.reportValidity()) return;
    if (next > step) {
      const invalid = guide?.steps[step]?.questions.find(question => ['url','source_url'].includes(question.key) && fields[question.key] && !safeUrl(fields[question.key]));
      if (invalid) { setError('Use a full http:// or https:// address without a username or password, or leave it blank.'); formRef.current?.querySelector<HTMLInputElement>(`[name="${invalid.key}"]`)?.focus(); return; }
    }
    setError('');
    setStep(next);
    requestAnimationFrame(() => stepHeading.current?.focus());
  };
  if (!context)
    return (
      <section className="owner-panel">
        <h2 className="font-display text-2xl font-bold">Business workspace</h2>
        <p className="my-4">
          Save your business context before building plans.
        </p>
        <a className="owner-button" href="#/profiles">
          Set up business context
        </a>
      </section>
    );
  if (documentsLoading && !error) return <WorkspaceLoading label="saved documents" />;
  if (kind === "quickwins")
    return (
      <div className="space-y-6">
        <div className="flex flex-wrap justify-between gap-4"><div><h2 className="font-display text-2xl font-bold">{guided ? 'Pick one useful next action' : 'Quick wins'}</h2><p className="text-muted-foreground mt-2">{guided ? 'Choose a priority, give it an owner and track what happens next.' : 'Priorities from your recorded business state. Assign and track the work below.'}</p></div><StrategyModeToggle disabled={!!busy}/></div>
        {guided && <section className="owner-panel space-y-3"><p role="status" className="text-sm font-medium">Step {quickStep+1} of 3 · {['Choose a priority','Review and assign','Track the work'][quickStep]}</p><nav aria-label="Action steps" className="flex flex-wrap gap-2">{['Choose a priority','Review and assign','Track the work'].map((label,index)=><button type="button" key={label} className={index===quickStep?'owner-button':'owner-button-secondary'} aria-current={index===quickStep?'step':undefined} onClick={()=>setQuickStep(index)}>{index+1}. {label}</button>)}</nav><p className="text-sm text-muted-foreground">{quickStep===0?'Choose a recorded issue below, or write your own action. Nothing is created yet.':quickStep===1?'Name the work, choose a responsible person and an optional due date. Review before saving.':'Change an action to In progress when work starts, and Done when it is finished. Status changes do not send messages or execute work.'}</p>{quickStep===0&&<button className="owner-button-secondary" onClick={()=>setQuickStep(1)}>Write my own action</button>}</section>}
        {!guided && <section className="owner-panel"><h3 className="font-display text-lg font-semibold">Stop repeating the same checks</h3><p className="text-sm text-muted-foreground mt-2">Preview a recurring check, enable its schedule, then review the internal actions it creates.</p><div className="flex flex-wrap gap-3 mt-4"><a className="owner-button" href="#/automations">Configure automations</a><a className="owner-button-secondary" href="#/agent-forge">Explore advisor skills</a></div></section>}
        <section className={`owner-panel ${guided && quickStep!==0?'hidden':''}`}>
          <h3 className="font-semibold">Evidence-based priorities</h3>
          <div className="divide-y divide-border mt-3">
            {overview.attention.map((item) => (
              <div
                key={item.id}
                className="py-4 flex flex-wrap justify-between gap-3"
              >
                <div className="flex-1">
                  <h4 className="font-medium">{item.title}</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    {item.detail}
                  </p>
                </div>
                <button
                  className="owner-button-secondary"
                  disabled={!!busy}
                  onClick={async () => {
                    if (guided) { setSuggestion({title:item.title,notes:item.detail,sequence:Date.now()}); setQuickStep(1); return; }
                    setBusy(item.id);
                    try {
                      await apiCall("/api/v1/workspace/tasks", "POST", {
                        title: item.title,
                        notes: item.detail,
                      });
                      await refresh();
                      setMessage("Priority added to the owner action board.");
                    } catch (err) {
                      setError(
                        err instanceof Error ? err.message : "Save failed.",
                      );
                    } finally {
                      setBusy("");
                    }
                  }}
                >
                  {guided ? 'Choose this priority' : 'Assign action'}
                </button>
              </div>
            ))}
            {!overview.attention.length && (
              <p className="py-4 text-muted-foreground text-sm">
                No missing-data or review alerts. Add your next business
                experiment to the action board.
              </p>
            )}
          </div>
        </section>
        {message && <p role="status">{message}</p>}
        {error && (
          <p role="alert" className="owner-error">
            {error}
          </p>
        )}
        <OwnerActions guided={guided} stage={quickStep} suggestion={suggestion} onCreated={()=>setQuickStep(2)} refreshSignal={message}/>
      </div>
    );
  const definition = definitions[kind];
  const safeUrl = (value: string) => {
    try {
      const url = new URL(value);
      return ["https:", "http:"].includes(url.protocol) &&
        !url.username &&
        !url.password
        ? url.href
        : "";
    } catch {
      return "";
    }
  };
  const schema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: fields.business_name || context.company_name,
    ...(safeUrl(fields.url || "") ? { url: safeUrl(fields.url) } : {}),
    ...(fields.description ? { description: fields.description } : {}),
  };
  const save = async () => {
    if (busy) return;
    setBusy("save");
    if (!title.trim()) { setError('Give this plan a name before saving.'); setBusy(''); return; }
    for (const key of ['url', 'source_url']) {
      if (fields[key] && !safeUrl(fields[key])) { setError('Use a full http:// or https:// address without a username or password.'); setBusy(''); return; }
    }
    setError("");
    try {
      const row = await apiCall<WorkDocument>(
        id
          ? `/api/v1/workspace/documents/${id}`
          : "/api/v1/workspace/documents",
        id ? "PUT" : "POST",
        { kind, title, fields },
      );
      setId(row.id);
      setDirty(false);
      setDocuments(
        await apiCall<WorkDocument[]>(
          `/api/v1/workspace/documents?kind=${kind}`,
        ),
      );
      setMessage("Document saved to this business.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Document save failed.");
    } finally {
      setBusy("");
    }
  };
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">
            {guided ? guide?.title : definition.title}
          </h2>
          <p className="text-muted-foreground mt-2 max-w-prose">
            {guided ? guide?.description : definition.description}
          </p>
        </div>
        <StrategyModeToggle disabled={!!busy}/>
        <button
          className="owner-button-secondary"
          disabled={!!busy}
          onClick={() => {
            if (dirty && !confirm("Discard unsaved document changes?")) return;
            setId("");
            setTitle("");
            setFields({});
            setDirty(false);
            setGenerated("");
            setStep(0); setMessage(''); setError('');
          }}
        >
          <Plus className="w-4 h-4" />
          {guided ? 'Start a new plan' : 'New document'}
        </button>
      </div>
      {error && (
        <p className="owner-error" role="alert">
          {error}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      <div className="grid grid-cols-1 xl:grid-cols-[230px_minmax(0,1fr)] gap-6 items-start">
        <aside className="owner-panel !p-4">
          <details open={guided ? undefined : true}>
          <summary className="font-semibold cursor-pointer min-h-11 py-2">{guided ? 'Open a saved plan' : 'Saved documents'}</summary>
          <p className="text-xs text-muted-foreground mt-1">
            Latest 100 · {context.company_name}
          </p>
          <div className="divide-y divide-border mt-3">
            {documents.map((doc) => (
              <button
                key={doc.id}
                className="block py-3 text-left w-full hover:text-primary text-sm"
                onClick={() => {
                  if (dirty && !confirm("Discard unsaved document changes?"))
                    return;
                  setId(doc.id);
                  setTitle(doc.title);
                  setFields(doc.fields);
                  setDirty(false);
                  setGenerated("");
                  setStep(0); setMessage(''); setError('');
                }}
              >
                <span className="block font-medium break-words">
                  {doc.title}
                </span>
                <span className="text-xs text-muted-foreground">
                  {new Date(doc.updated_at).toLocaleDateString()}
                </span>
              </button>
            ))}
            {!documents.length && (
              <p className="py-4 text-sm text-muted-foreground">
                No saved documents yet.
              </p>
            )}
          </div>
          </details>
        </aside>
        <div className="space-y-5 min-w-0">
          <form
            className="owner-panel space-y-5"
            ref={formRef}
            onSubmit={(event) => {
              event.preventDefault();
              if (guided && guide && !reviewing) goToStep(step + 1);
              else void save();
            }}
          >
            {guided && guide && <div className="space-y-3">
              <p className="text-xs text-muted-foreground" role="status">Step {step + 1} of {guide.steps.length + 1} · {reviewing ? 'Review and save' : guide.steps[step].title}</p>
              <nav aria-label="Plan steps" className="flex flex-wrap gap-2">{[...guide.steps.map(section=>section.title),'Review and save'].map((label,index)=><button key={label} type="button" className={`min-h-11 px-3 py-2 rounded-lg text-sm text-left ${index===step?'bg-primary/10 text-primary font-semibold':'hover:bg-muted'}`} aria-current={index===step?'step':undefined} disabled={!!busy} onClick={()=>goToStep(index)}>{index+1}. {label}</button>)}</nav>
              <h3 ref={stepHeading} tabIndex={-1} className="font-display text-xl font-semibold">{reviewing ? 'Check your plan before saving' : guide.steps[step].title}</h3>
              <p className="text-sm text-muted-foreground">{reviewing ? 'Blank answers stay blank. Saving records your plan; it does not validate the idea or carry out any action.' : guide.steps[step].description}</p>
              <p className="text-xs text-muted-foreground">{reviewing ? `${questions.filter(question=>fields[question.key]?.trim()).length} of ${questions.length} answers added.` : 'Examples are suggestions, not facts about your business. Answers are optional; return to them when you know more.'}</p>
            </div>}
            {(!guided || step === 0) && <label className="owner-label">
              {guided ? 'Give this plan a name' : 'Document title'}
              <input
                className="owner-input"
                value={title}
                maxLength={180}
                required
                placeholder={guided ? guide?.titleExample : undefined}
                onChange={(event) => {
                  setTitle(event.target.value);
                  setDirty(true);
                }}
              />
            </label>}
            <div
              className={`grid gap-4 ${guided ? 'grid-cols-1' : kind === "canvas" ? "lg:grid-cols-3" : "md:grid-cols-2"}`}
            >
              {(guided ? reviewing ? [] : guide!.steps[step].questions.map(question=>[question.key,question.question]) : definition.fields).map(([key, label]) => (
                <label className="owner-label" key={key}>
                  {label}
                  {key === "url" || key === "source_url" ? (
                    <input
                      className="owner-input"
                      name={key}
                      aria-describedby={guided ? `help-${kind}-${key}` : undefined}
                      type="url"
                      aria-invalid={!!fields[key] && !safeUrl(fields[key])}
                      value={fields[key] || ""}
                      maxLength={1000}
                      onChange={(event) => {
                        setFields({ ...fields, [key]: event.target.value });
                        setDirty(true);
                      }}
                    />
                  ) : key === "published_date" || key === "deadline" ? (
                    <input
                      className="owner-input"
                      name={key}
                      aria-describedby={guided ? `help-${kind}-${key}` : undefined}
                      type="date"
                      max="9999-12-31"
                      value={fields[key] || ""}
                      onChange={(event) => {
                        setFields({ ...fields, [key]: event.target.value });
                        setDirty(true);
                      }}
                    />
                  ) : (
                    <textarea
                      className="owner-input min-h-28"
                      name={key}
                      aria-describedby={guided ? `help-${kind}-${key}` : undefined}
                      rows={kind === "canvas" ? 5 : 4}
                      maxLength={12000}
                      value={fields[key] || ""}
                      onChange={(event) => {
                        setFields({ ...fields, [key]: event.target.value });
                        setDirty(true);
                      }}
                    />
                  )}
                  {guided && <span id={`help-${kind}-${key}`} className="block text-sm text-muted-foreground leading-relaxed">{questions.find(question=>question.key===key)?.help}{questions.find(question=>question.key===key)?.example && <span className="block mt-2 text-xs">Example: {questions.find(question=>question.key===key)?.example}</span>}</span>}
                </label>
              ))}
            </div>
            {guided && reviewing && <div className="space-y-4"><div className="flex justify-between gap-3"><h4 className="font-semibold break-words">{title || 'Untitled plan'}</h4><button type="button" className="text-primary underline min-h-11 shrink-0" onClick={()=>goToStep(0)}>Edit name</button></div><dl className="divide-y divide-border">{questions.map(question=><div key={question.key} className="py-3"><dt className="font-medium text-sm">{question.question}</dt><dd className="whitespace-pre-wrap break-words text-sm text-muted-foreground mt-1">{fields[question.key]?.trim() || 'Not added yet'}</dd></div>)}</dl><p className="text-xs text-muted-foreground">You can save an incomplete plan and reopen it later.</p></div>}
            <div className="flex flex-wrap gap-3">
              {guided && <button type="button" className="owner-button-secondary" disabled={step===0||!!busy} onClick={()=>goToStep(step-1)}>Back</button>}
              <button
                className="owner-button"
                disabled={!!busy || ((!guided || reviewing || step===0) && !title.trim())}
              >
                {(!guided || reviewing) && <Save className="w-4 h-4" />}
                {busy === 'save' ? 'Saving…' : guided && !reviewing ? 'Continue' : guided ? 'Save plan' : 'Save document'}
              </button>
              <button
                type="button"
                className={guided && !reviewing ? 'hidden' : 'owner-button-secondary'}
                onClick={() => {
                  const contents =
                    kind === "seo"
                      ? JSON.stringify(schema, null, 2)
                      : `# ${title}\n\n` +
                        definition.fields
                          .map(
                            ([key, label]) =>
                              `## ${label}\n${fields[key] || ""}`,
                          )
                          .join("\n\n");
                  const url = URL.createObjectURL(
                    new Blob([contents], {
                      type:
                        kind === "seo"
                          ? "application/ld+json"
                          : "text/markdown",
                    }),
                  );
                  const link = document.createElement("a");
                  link.href = url;
                  link.download = `${kind}-document.${kind === "seo" ? "json" : "md"}`;
                  link.click();
                  URL.revokeObjectURL(url);
                }}
              >
                <Download className="w-4 h-4" />
                Export {kind === "seo" ? "JSON-LD" : "document"}
              </button>
              <button
                type="button"
                className="owner-button-secondary"
                onClick={() => {
                  const next =
                    kind === "canvas"
                      ? {
                          value: context.products_services,
                          customers: context.target_market,
                        }
                      : kind === "strategy"
                        ? {
                            goal: context.goals,
                            constraints: context.constraints,
                            evidence: context.proof_points,
                          }
                        : kind === "ideation"
                          ? { audience: context.target_market }
                          : kind === "seo"
                            ? {
                                business_name: context.company_name,
                                url: context.website,
                              }
                            : { segment: context.target_market };
                  setFields({ ...next, ...fields });
                  setDirty(true);
                }}
              >
                Use business context
              </button>
            </div>
          </form>
          {kind === "seo" && (!guided || reviewing) && (
            <section className="owner-panel">
              <h3 className="font-semibold">
                Metadata checks and search preview
              </h3>
              <ul className="text-sm text-muted-foreground mt-3 space-y-2">
                <li>
                  Title: {(fields.page_title || "").length} characters ·
                  descriptive titles around 50–60 characters are usually
                  readable; not a ranking score.
                </li>
                <li>
                  Description: {(fields.description || "").length} characters ·
                  search engines may rewrite descriptions.
                </li>
                <li>
                  Canonical URL:{" "}
                  {safeUrl(fields.url || "")
                    ? "valid HTTP(S) URL"
                    : "add a valid canonical URL"}
                </li>
              </ul>
              <div className="mt-5 border-t border-border pt-4">
                <p className="text-sm">
                  {fields.url || "Canonical URL not set"}
                </p>
                <h4 className="text-primary text-xl font-medium mt-1">
                  {fields.page_title || "Your page title"}
                </h4>
                <p className="mt-2 text-sm">
                  {fields.description ||
                    "Write a useful description for search visitors."}
                </p>
              </div>
              <details className="mt-4">
                <summary className="cursor-pointer text-sm">
                  Organization JSON-LD
                </summary>
                <pre className="overflow-x-auto text-xs mt-3">
                  {JSON.stringify(schema, null, 2)}
                </pre>
              </details>
            </section>
          )}
          {kind === "research" && (!guided || reviewing) && (
            <section className="owner-panel">
              <h3 className="font-semibold">Evidence quality</h3>
              <p className="text-sm text-muted-foreground mt-2">
                {fields.source_url && safeUrl(fields.source_url)
                  ? "Source link recorded. Verify the claim against the original publication."
                  : "No valid source URL recorded. Treat conclusions as assumptions."}{" "}
                {fields.published_date
                  ? `Publication: ${fields.published_date}.`
                  : "Publication date missing."}
              </p>
              {safeUrl(fields.source_url || "") && (
                <a
                  href={safeUrl(fields.source_url)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="owner-button-secondary mt-3"
                >
                  Open source in new tab
                </a>
              )}
            </section>
          )}
          {(kind === "strategy" || kind === "ideation") && (!guided || reviewing) && (
            <section className="owner-panel space-y-3">
              <h3 className="font-semibold">AI challenge pass</h3>
              <p className="text-sm text-muted-foreground">
                Sends this document and saved business context to your
                configured provider. Responses are suggestions, not verified
                research.
              </p>
              <button
                className="owner-button-secondary"
                disabled={!!busy || !overview.capabilities.ai_available}
                onClick={async () => {
                  setBusy("ai");
                  setError("");
                  try {
                    const result = await apiCall<AgentRun>(
                      "/api/v1/owner/runs",
                      "POST",
                      {
                        kind,
                        objective:
                          `Critique this ${kind} document; propose concrete next experiments and identify unsupported assumptions.\n${JSON.stringify(fields)}`.slice(
                            0,
                            16000,
                          ),
                      },
                    );
                    await refresh();
                    if (result.status === "failed")
                      throw new Error(result.error || "Generation failed");
                    setGenerated(result.output);
                  } catch (err) {
                    setError(
                      err instanceof Error ? err.message : "AI request failed.",
                    );
                  } finally {
                    setBusy("");
                  }
                }}
              >
                <Sparkles className="w-4 h-4" />
                Challenge this {kind === "ideation" ? "idea" : "strategy"}
              </button>
              {generated && (
                <>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">
                    {generated}
                  </p>
                  <button
                    className="owner-button-secondary"
                    onClick={() => {
                      setFields({
                        ...fields,
                        [kind === "strategy" ? "options" : "assumptions"]:
                          generated,
                      });
                      setDirty(true);
                    }}
                  >
                    Use response in document
                  </button>
                </>
              )}
            </section>
          )}
          {(kind === "strategy" || kind === "ideation") && <div className={guided && !reviewing ? 'hidden' : ''}><OwnerActions /></div>}
        </div>
      </div>
    </div>
  );
}
