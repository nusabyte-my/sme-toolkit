import React, { useEffect, useState } from 'react';
import { Bot, Play, Check, X, RefreshCw, FileText } from "lucide-react";
import { useOwner } from "../../contexts/OwnerContext";
import { apiCall } from "../../services/apiClient";
import type { AgentKind, AgentRun, AdvisorSkill } from '../../types/owner';
import WorkspaceLoading from '../common/WorkspaceLoading';

export const AdvisorWorkspace: React.FC = () => {
  const { overview, loading, error: loadError, refresh } = useOwner();
  const [kind, setKind] = useState<AgentKind>("business_review");
  const [objective, setObjective] = useState(
    "Review my recorded business performance and recommend the next priorities.",
  );
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const [status, setStatus] = useState("");
  const [filter, setFilter] = useState("all");
  const [roles,setRoles] = useState<AdvisorSkill[]>([]);
  const [skillError,setSkillError] = useState('');
  const [roleSearch,setRoleSearch] = useState('');
  useEffect(()=>{
    let active=true;
    apiCall<AdvisorSkill[]>('/api/v1/owner/advisors').then(items=>{if(active)setRoles(items);}).catch(err=>{if(active)setSkillError(err instanceof Error?err.message:'Advisor catalog could not be loaded.');});
    return()=>{active=false;};
  },[]);
  const selectedSkill=roles.find(role=>role.kind===kind);
  const runs = overview?.agents || [];
  const active = runs.find((run) => run.id === selected) || runs[0];
  const run = async () => {
    setBusy("run");
    setError("");
    setStatus("");
    try {
      const result = await apiCall<AgentRun>("/api/v1/owner/runs", "POST", {
        kind,
        objective,
      });
      setSelected(result.id);
      await refresh();
      if (result.status === "failed")
        setError(result.error || "Generation failed.");
      else
        setStatus(
          "Findings saved for your review. No external action was taken.",
        );
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Agent run failed. Try again.",
      );
    } finally {
      setBusy("");
    }
  };
  if (!roles.length && !skillError) return <WorkspaceLoading label="advisor catalog" />;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold">
            JEBAT agent workspace
          </h2>
          <p className="mt-2 text-muted-foreground max-w-prose">
            Give the work a clear objective. Inspect the evidence and saved
            business context, then approve or dismiss the findings.
          </p>
        </div>
        <button
          className="owner-button-secondary"
          onClick={() => void refresh()}
          disabled={loading || !!busy}
        >
          <RefreshCw className="w-4 h-4" />
          Refresh runs
        </button>
        <a className="owner-button-secondary" href="#/automations">Open automations</a>
      </div>
      {loadError && (
        <p role="alert" className="owner-error">
          {loadError}
        </p>
      )}
      {skillError&&<p className="owner-error" role="alert">{skillError}<button className="ml-3 underline" onClick={()=>apiCall<AdvisorSkill[]>('/api/v1/owner/advisors').then(items=>{setRoles(items);setSkillError('');}).catch(err=>setSkillError(err.message))}>Retry advisor catalog</button></p>}
      {!overview?.context ? (
        <section className="owner-panel">
          <p>
            {loading
              ? "Loading business context…"
              : "Save business context before running an agent."}
          </p>
          <a
            href="#/profiles"
            className="inline-block mt-4 text-primary underline"
          >
            Set up business context
          </a>
        </section>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-[minmax(240px,1fr)_minmax(0,2fr)] gap-6">
            <section className="owner-panel">
              <h3 className="font-display font-semibold">Choose the work</h3>
              <label className="owner-label mt-3">Find an advisor<input className="owner-input" type="search" value={roleSearch} onChange={e=>setRoleSearch(e.target.value)} placeholder="Finance, leads, campaigns…"/></label>
              <fieldset className="mt-4 space-y-3 max-h-[620px] overflow-y-auto pr-1" disabled={!!busy}>
                <legend className="sr-only">Agent role</legend>
                {roles.filter(role=>(role.title+' '+role.group+' '+role.description).toLowerCase().includes(roleSearch.toLowerCase())).map((role) => (
                  <label
                    key={role.kind}
                    className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer ${kind === role.kind ? "border-primary bg-primary/5" : "border-border hover:bg-muted"}`}
                  >
                    <input
                      className="mt-1 accent-primary"
                      type="radio"
                      name="agent-kind"
                      value={role.kind}
                      checked={kind === role.kind}
                      onChange={() => {setKind(role.kind);setObjective(role.default_objective);}}
                    />
                    <span>
                      <span className="block font-medium text-sm">
                        {role.title}
                      </span>
                      <span className="block mt-1 text-xs text-muted-foreground">
                        {role.description}
                      </span>
                      <span className="block mt-1 text-xs text-muted-foreground">{role.group} · {role.mode==='rules'?'Evidence rules · no AI charge':'AI-assisted'} · v{role.version}</span>
                    </span>
                  </label>
                ))}
              </fieldset>
              <p className="mt-5 text-xs text-muted-foreground">{roles.length} advisors. Evidence-rule advisors run without provider keys. AI advisors use the selected skill and saved business evidence; failures never become sample answers.</p>
            </section>
            <form
              className="owner-panel flex flex-col"
              onSubmit={(event) => {
                event.preventDefault();
                void run();
              }}
            >
              <p className="text-sm font-medium flex gap-2 items-center">
                <BuildingContext name={overview.context.company_name} />
              </p>
              {selectedSkill&&<details className="mt-4 border border-border rounded-lg p-3"><summary className="cursor-pointer text-sm font-semibold">Advisor skill: {selectedSkill.title} · v{selectedSkill.version}</summary><p className="mt-3 text-sm text-muted-foreground">Inputs: {selectedSkill.inputs.join(', ')}</p><pre className="mt-3 whitespace-pre-wrap break-words text-xs leading-relaxed max-h-80 overflow-y-auto">{selectedSkill.skill_markdown}</pre><button type="button" className="owner-button-secondary mt-3" onClick={()=>{const url=URL.createObjectURL(new Blob([selectedSkill.skill_markdown],{type:'text/markdown'}));const link=document.createElement('a');link.href=url;link.download=`${selectedSkill.name}-SKILL.md`;link.click();URL.revokeObjectURL(url);}}>Download advisor skill</button></details>}
              <label className="owner-label mt-5">
                What should this agent work on?
                <textarea
                  className="owner-input"
                  rows={5}
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  required
                  minLength={3}
                  maxLength={2000}
                  disabled={!!busy}
                />
              </label>
              <div className="mt-5 flex flex-wrap gap-3 items-center">
                <button
                  className="owner-button"
                  disabled={
                    !!busy || !selectedSkill || objective.trim().length < 3 ||
                    (selectedSkill.mode==='llm' && !overview.capabilities.ai_available)
                  }
                >
                  <Play className="w-4 h-4" />
                  {busy === "run"
                    ? "Running analysis…"
                    : selectedSkill?.mode==='llm'
                      ? "Generate AI response"
                      : "Run evidence brief"}
                </button>
                <span className="text-xs text-muted-foreground">
                  {selectedSkill?.mode==='llm'
                    ? overview.capabilities.ai_available
                      ? `Provider: ${overview.capabilities.ai_provider} · may incur usage charges`
                      : overview.context?.is_demo ? 'AI generation is disabled in the demo. Choose an evidence-rule advisor or edit the sample drafts.' : 'Configure an AI provider to generate. Manual marketing drafts remain available.'
                    : 'Source: saved business evidence · no external actions or paid AI requests'}
                </span>
              </div>
            </form>
          </div>
          {error && (
            <p className="owner-error" role="alert">
              {error}
            </p>
          )}
          {status && (
            <p role="status" className="text-sm">
              {status}
            </p>
          )}
          <div className="grid grid-cols-1 lg:grid-cols-[minmax(240px,1fr)_minmax(0,2fr)] gap-6">
            <section className="owner-panel">
              <h3 className="font-display font-semibold">Run history</h3>
              <p className="text-xs text-muted-foreground mt-1">
                Latest 100 saved runs
              </p>
              <label className="owner-label mt-3">
                Run status
                <select
                  className="owner-input"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  {[
                    "all",
                    "needs_review",
                    "approved",
                    "dismissed",
                    "failed",
                  ].map((value) => (
                    <option value={value} key={value}>
                      {value.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </label>
              <div className="mt-3 divide-y divide-border">
                {runs
                  .filter((item) => filter === "all" || item.status === filter)
                  .map((item) => (
                    <button
                      key={item.id}
                      className={`w-full py-4 text-left ${active?.id === item.id ? "text-primary" : "hover:text-primary"}`}
                      onClick={() => setSelected(item.id)}
                    >
                      <span className="block font-medium text-sm">
                        {roles.find((role) => role.kind === item.kind)?.title ||
                          item.kind}
                      </span>
                      <span className="block text-xs mt-1 text-muted-foreground truncate">
                        {item.objective}
                      </span>
                      <span className="block text-xs mt-2 capitalize">
                        {item.status.replaceAll("_", " ")} ·{" "}
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                    </button>
                  ))}
                {!runs.length && (
                  <p className="py-5 text-sm text-muted-foreground">
                    No saved runs. Your first brief will appear here.
                  </p>
                )}
              </div>
            </section>
            <section className="owner-panel min-w-0">
              <h3 className="font-display font-semibold">
                {active ? "Findings and review" : "Your evidence appears here"}
              </h3>
              {active ? (
                <>
                  <div className="flex flex-wrap gap-2 text-xs text-muted-foreground mt-3">
                    <span>
                      {active.provider === "rules"
                        ? 'Deterministic evidence analysis'
                        : `AI: ${active.provider}`}
                    </span>
                    <span>·</span>
                    <span>{new Date(active.created_at).toLocaleString()}</span>
                    <span>· {active.status.replaceAll("_", " ")}</span>
                  </div>
                  {active.skill&&<p className="text-xs text-muted-foreground mt-2">Executed skill: {active.skill.name} v{active.skill.version}</p>}
                  {active.evidence&&<details className="mt-3 text-sm"><summary className="cursor-pointer">Evidence snapshot · {active.evidence.issue_count} review flags</summary><p className="text-xs text-muted-foreground mt-2">As of {new Date(active.evidence.as_of).toLocaleString()}. The saved snapshot does not change when source records are edited.</p><ul className="mt-3 space-y-2">{active.evidence.observations.map((text,index)=><li key={index}>{text}</li>)}</ul><ul className="mt-3 space-y-2 text-muted-foreground">{active.evidence.limits.map((text,index)=><li key={index}>{text}</li>)}</ul></details>}
                  {active.error ? (
                    <p className="owner-error mt-4" role="alert">
                      {active.error}
                    </p>
                  ) : (
                    <div className="mt-5 whitespace-pre-wrap break-words text-sm leading-relaxed">
                      {active.output}
                    </div>
                  )}
                  <details className="mt-5 text-sm">
                    <summary className="cursor-pointer font-medium">
                      Business context used for this run
                    </summary>
                    <dl className="mt-3 space-y-2 text-muted-foreground">
                      <div>
                        <dt className="font-medium text-foreground">
                          Business
                        </dt>
                        <dd>{active.context_snapshot.company_name}</dd>
                      </div>
                      <div>
                        <dt className="font-medium text-foreground">
                          Products and services
                        </dt>
                        <dd className="whitespace-pre-wrap">
                          {active.context_snapshot.products_services ||
                            "Not supplied"}
                        </dd>
                      </div>
                      <div>
                        <dt className="font-medium text-foreground">Goals</dt>
                        <dd className="whitespace-pre-wrap">
                          {active.context_snapshot.goals || "Not supplied"}
                        </dd>
                      </div>
                    </dl>
                  </details>
                  <div className="flex flex-wrap gap-3 mt-6">
                    {active.status === "needs_review" &&
                      (["approved", "dismissed"] as const).map((next) => (
                        <button
                          key={next}
                          className={
                            next === "approved"
                              ? "owner-button"
                              : "owner-button-secondary"
                          }
                          disabled={!!busy}
                          onClick={async () => {
                            setBusy(active.id);
                            setError("");
                            try {
                              await apiCall(
                                `/api/v1/owner/runs/${active.id}`,
                                "PATCH",
                                { status: next },
                              );
                              await refresh();
                              setStatus(
                                `Findings ${next}. No external action was taken.`,
                              );
                            } catch (err) {
                              setError(
                                err instanceof Error
                                  ? err.message
                                  : "Review failed.",
                              );
                            } finally {
                              setBusy("");
                            }
                          }}
                        >
                          {next === "approved" ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <X className="w-4 h-4" />
                          )}
                          {next === "approved"
                            ? "Approve findings"
                            : "Dismiss findings"}
                        </button>
                      ))}
                    <button
                      className="owner-button-secondary"
                      disabled={!active.output}
                      onClick={() => {
                        const url = URL.createObjectURL(
                          new Blob([active.output], {
                            type: "text/plain;charset=utf-8",
                          }),
                        );
                        const link = document.createElement("a");
                        link.href = url;
                        link.download = `business-brief-${active.id}.txt`;
                        link.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      <FileText className="w-4 h-4" />
                      Download brief
                    </button>
                    <button
                      className="owner-button-secondary"
                      disabled={!!busy || !active.output}
                      onClick={async () => {
                        setBusy(active.id);
                        setError("");
                        try {
                          await apiCall("/api/v1/workspace/tasks", "POST", {
                            title: active.objective.slice(0, 180),
                            notes:
                              `From agent run ${active.id}:\n${active.output}`.slice(
                                0,
                                4000,
                              ),
                          });
                          await refresh();
                          setStatus("Finding added to the owner action board.");
                        } catch (err) {
                          setError(
                            err instanceof Error
                              ? err.message
                              : "Could not create action.",
                          );
                        } finally {
                          setBusy("");
                        }
                      }}
                    >
                      Create owner action
                    </button>
                  </div>
                  <p className="text-xs text-muted-foreground mt-3">
                    Approval is an internal review decision, not permission to
                    send messages, publish ads or move money.
                  </p>
                </>
              ) : (
                <p className="text-sm text-muted-foreground mt-3">
                  Run a brief to inspect its output, provenance and approval
                  state.
                </p>
              )}
            </section>
          </div>
        </>
      )}
    </div>
  );
};
function BuildingContext({ name }: { name: string }) {
  return (
    <>
      <Bot className="w-5 h-5 text-primary" />
      Context: {name}
    </>
  );
}
export default AdvisorWorkspace;
