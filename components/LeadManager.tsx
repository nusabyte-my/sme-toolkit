import { useCallback, useEffect, useState } from "react";
import { Plus, RefreshCw, Users } from "lucide-react";
import { apiCall } from "../services/apiClient";
import { useOwner } from "../contexts/OwnerContext";
import { useUnsavedChanges } from "../hooks/useUnsavedChanges";
import WorkspaceLoading from './common/WorkspaceLoading';

interface CRMLead {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  lead_source: string;
  status: string;
  notes: string;
  next_follow_up_at: string | null;
}
interface CRMResult {
  items: CRMLead[];
  total: number;
  page: number;
  size: number;
  stages: Record<string, number>;
  overdue: number;
}
const blank = {
  name: "",
  email: "",
  phone: "",
  company: "",
  lead_source: "",
  status: "new",
  notes: "",
  next_follow_up_at: "",
};
const stages = ["new", "contacted", "qualified", "proposal", "won", "lost"];
export default function LeadManager() {
  const { overview } = useOwner();
  const [data, setData] = useState<CRMResult | null>(null),
    [search, setSearch] = useState(""),
    [stage, setStage] = useState(""),
    [page, setPage] = useState(1);
  const [form, setForm] = useState(blank),
    [editing, setEditing] = useState(""),
    [open, setOpen] = useState(false),
    [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  useUnsavedChanges(dirty || busy);
  const load = useCallback(async () => {
    const query = new URLSearchParams({
      search,
      status: stage,
      page: String(page),
    });
    const rows = await apiCall<CRMResult>(`/api/v1/workspace/leads?${query}`);
    setData(rows);
  }, [search, stage, page]);
  useEffect(() => {
    let active = true;
    if (overview?.context) {
      const query = new URLSearchParams({
        search,
        status: stage,
        page: String(page),
      });
      apiCall<CRMResult>(`/api/v1/workspace/leads?${query}`)
        .then((rows) => {
          if (active) {
            setData(rows);
            setError("");
          }
        })
        .catch((err) => {
          if (active) setError(err.message);
        });
    }
    return () => {
      active = false;
    };
  }, [overview?.context?.id, search, stage, page]);
  if (!overview?.context)
    return (
      <section className="owner-panel">
        <h2 className="text-2xl font-display font-bold">Lead manager</h2>
        <p className="my-4">
          Save business context to create your private customer pipeline.
        </p>
        <a className="owner-button" href="#/profiles">
          Set up business context
        </a>
      </section>
    );
  if (!data && !error) return <WorkspaceLoading label="leads" />;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h2 className="text-2xl font-display font-bold">Lead manager</h2>
          <p className="text-muted-foreground mt-2">
            A saved pipeline with follow-ups, contact details and ownership. No
            invented lead scores.
          </p>
        </div>
        <button
          className="owner-button"
          onClick={() => {
            if (dirty && !confirm("Discard unsaved lead changes?")) return;
            setForm(blank);
            setEditing("");
            setDirty(false);
            setOpen(true);
          }}
        >
          <Plus className="w-4 h-4" />
          Add lead
        </button>
      </div>
      {error && (
        <p className="owner-error" role="alert">
          {error}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      <section
        className="grid grid-cols-3 lg:grid-cols-6 gap-3"
        aria-label="Pipeline stages"
      >
        {stages.map((s) => (
          <button
            className="owner-panel text-left !p-4 hover:border-primary"
            key={s}
            onClick={() => {
              setStage(s);
              setPage(1);
            }}
          >
            <p className="capitalize text-xs text-muted-foreground">{s}</p>
            <p className="text-xl font-semibold mt-1">{data?.stages[s] || 0}</p>
          </button>
        ))}
      </section>
      <p className="text-sm text-muted-foreground">
        {data?.overdue || 0} open leads have an overdue follow-up.
      </p>
      {open && (
        <form
          className="owner-panel space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy(true);
            setError("");
            try {
              await apiCall(
                editing
                  ? `/api/v1/workspace/leads/${editing}`
                  : "/api/v1/workspace/leads",
                editing ? "PUT" : "POST",
                {
                  ...form,
                  next_follow_up_at: form.next_follow_up_at
                    ? new Date(form.next_follow_up_at).toISOString()
                    : null,
                },
              );
              setDirty(false);
              setOpen(false);
              await load();
              setMessage("Lead saved.");
            } catch (err) {
              setError(
                err instanceof Error ? err.message : "Lead could not be saved.",
              );
            } finally {
              setBusy(false);
            }
          }}
        >
          <h3 className="font-display text-lg font-semibold">
            {editing ? "Edit lead" : "New lead"}
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {(
              ["name", "email", "phone", "company", "lead_source"] as const
            ).map((key) => (
              <label className="owner-label capitalize" key={key}>
                {key.replaceAll("_", " ")}
                {key === "name" ? " (required)" : ""}
                <input
                  className="owner-input"
                  type={key === "email" ? "email" : "text"}
                  required={key === "name"}
                  maxLength={key === "email" ? 254 : 160}
                  value={form[key]}
                  onChange={(e) => {
                    setForm({ ...form, [key]: e.target.value });
                    setDirty(true);
                  }}
                />
              </label>
            ))}
            <label className="owner-label">
              Pipeline stage
              <select
                className="owner-input"
                value={form.status}
                onChange={(e) => {
                  setForm({ ...form, status: e.target.value });
                  setDirty(true);
                }}
              >
                {stages.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <label className="owner-label">
              Next follow-up (browser timezone)
              <input
                className="owner-input"
                type="datetime-local"
                value={form.next_follow_up_at}
                onChange={(e) => {
                  setForm({ ...form, next_follow_up_at: e.target.value });
                  setDirty(true);
                }}
              />
            </label>
            <label className="owner-label md:col-span-2">
              Notes
              <textarea
                className="owner-input"
                rows={4}
                maxLength={4000}
                value={form.notes}
                onChange={(e) => {
                  setForm({ ...form, notes: e.target.value });
                  setDirty(true);
                }}
              />
            </label>
          </div>
          <div className="flex gap-3">
            <button className="owner-button" disabled={busy}>
              Save lead
            </button>
            <button
              className="owner-button-secondary"
              type="button"
              onClick={() => {
                if (dirty && !confirm("Discard unsaved lead changes?")) return;
                setOpen(false);
                setDirty(false);
              }}
            >
              Cancel editing
            </button>
          </div>
        </form>
      )}
      <section className="owner-panel">
        <div className="flex flex-wrap items-end gap-3">
          <label className="owner-label flex-1">
            Search name, company or email
            <input
              className="owner-input"
              type="search"
              maxLength={160}
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </label>
          <label className="owner-label">
            Stage
            <select
              className="owner-input"
              value={stage}
              onChange={(e) => {
                setStage(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All stages</option>
              {stages.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <button
            className="owner-button-secondary"
            onClick={() => load().catch((err) => setError(err.message))}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
        <div className="mt-5 divide-y divide-border">
          {data?.items.map((lead) => (
            <article
              className="py-4 flex flex-wrap justify-between gap-4"
              key={lead.id}
            >
              <div className="min-w-0">
                <h3 className="font-semibold">
                  {lead.name}{" "}
                  <span className="text-xs text-muted-foreground font-normal">
                    {lead.company}
                  </span>
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {lead.email || lead.phone || "No contact details"} ·{" "}
                  {lead.status}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {lead.next_follow_up_at
                    ? `Follow up ${new Date(lead.next_follow_up_at).toLocaleString()}`
                    : "No follow-up planned"}
                </p>
                <p className="text-sm mt-2 whitespace-pre-wrap break-words">
                  {lead.notes}
                </p>
              </div>
              <div className="flex gap-2 items-start">
                <button
                  className="owner-button-secondary"
                  onClick={() => {
                    if (dirty && !confirm("Discard unsaved lead changes?"))
                      return;
                    const dt = lead.next_follow_up_at
                      ? new Date(lead.next_follow_up_at)
                      : null;
                    setEditing(lead.id);
                    setForm({
                      name: lead.name,
                      email: lead.email || "",
                      phone: lead.phone || "",
                      company: lead.company || "",
                      lead_source: lead.lead_source || "",
                      status: lead.status,
                      notes: lead.notes || "",
                      next_follow_up_at: dt
                        ? new Date(
                            dt.getTime() - dt.getTimezoneOffset() * 60000,
                          )
                            .toISOString()
                            .slice(0, 16)
                        : "",
                    });
                    setOpen(true);
                    setDirty(false);
                  }}
                >
                  Edit lead
                </button>
                {lead.email && !overview?.context?.is_demo && (
                  <a
                    className="owner-button-secondary"
                    href={`mailto:${encodeURIComponent(lead.email)}`}
                  >
                    Write email
                  </a>
                )}
              </div>
            </article>
          ))}
          {!data?.items.length && (
            <p className="py-8 text-muted-foreground text-sm flex gap-2">
              <Users className="w-5 h-5" />
              No leads match this view. Add a real prospect to begin.
            </p>
          )}
        </div>
        <div className="flex items-center justify-between gap-3 mt-4">
          <span className="text-sm text-muted-foreground">
            {data?.total || 0} leads · page {page}
          </span>
          <div className="flex gap-2">
            <button
              className="owner-button-secondary"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </button>
            <button
              className="owner-button-secondary"
              disabled={page * 30 >= (data?.total || 0)}
              onClick={() => setPage(page + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
