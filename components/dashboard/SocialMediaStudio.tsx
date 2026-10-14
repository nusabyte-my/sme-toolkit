import { useState } from "react";
import { CalendarDays, Copy, Megaphone, Plus, Sparkles } from "lucide-react";
import { useOwner } from "../../contexts/OwnerContext";
import { apiCall } from "../../services/apiClient";
import type { AgentRun, Campaign } from "../../types/owner";
import { useUnsavedChanges } from "../../hooks/useUnsavedChanges";

const blank = {
  title: "",
  platform: "instagram",
  caption: "",
  scheduled_at: "",
};
export function SocialMediaStudio() {
  const { overview, loading, refresh, error: loadError } = useOwner();
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState<string | null>(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [filter, setFilter] = useState("active");
  const [topic, setTopic] = useState("");
  const [search, setSearch] = useState("");
  const [calendarDay, setCalendarDay] = useState("");
  useUnsavedChanges(!!(form.title || form.caption || busy));
  const changeStatus = async (
    campaign: Campaign,
    status: Campaign["status"],
  ) => {
    setBusy(campaign.id);
    setError("");
    try {
      await apiCall(`/api/v1/owner/campaigns/${campaign.id}`, "PATCH", {
        status,
      });
      await refresh();
      setMessage(`Campaign ${status}. Nothing was published.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed.");
    } finally {
      setBusy("");
    }
  };
  if (!overview?.context)
    return (
      <section className="owner-panel">
        <h2 className="text-2xl font-display font-bold">Marketing planner</h2>
        <p className="my-4" role="status">
          {loadError ||
            (loading
              ? "Loading business context…"
              : "Save business context before planning campaigns.")}
        </p>
        <a className="text-primary underline" href="#/profiles">
          Open business context
        </a>
        {loadError && (
          <button
            className="owner-button-secondary ml-3"
            onClick={() => void refresh()}
          >
            Retry loading
          </button>
        )}
      </section>
    );
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h2 className="text-2xl font-display font-bold">Marketing planner</h2>
          <p className="text-muted-foreground mt-2">
            Draft, review and plan content for {overview.context.company_name}.
            Publishing is not connected.
          </p>
        </div>
        <a href="#/ads" className="owner-button">
          <Megaphone className="w-4 h-4" />
          Open Ads Studio
        </a>
      </div>
      {error && (
        <p className="owner-error" role="alert">
          {error}
        </p>
      )}
      {loadError && (
        <p className="owner-error" role="alert">
          {loadError}
        </p>
      )}
      {message && (
        <p role="status" className="text-sm">
          {message}
        </p>
      )}
      <div className="grid xl:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] gap-6">
        <form
          className="owner-panel space-y-4"
          onSubmit={async (event) => {
            event.preventDefault();
            setBusy("save");
            setError("");
            setMessage("");
            try {
              const body = {
                ...form,
                scheduled_at: form.scheduled_at
                  ? new Date(form.scheduled_at).toISOString()
                  : null,
              };
              await apiCall(
                editing
                  ? `/api/v1/owner/campaigns/${editing}`
                  : "/api/v1/owner/campaigns",
                editing ? "PATCH" : "POST",
                body,
              );
              await refresh();
              setEditing(null);
              setForm(blank);
              setMessage(
                "Draft saved. No external post was scheduled or published.",
              );
            } catch (err) {
              setError(
                err instanceof Error
                  ? err.message
                  : "Save failed. Your draft remains in the editor.",
              );
            } finally {
              setBusy("");
            }
          }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-semibold">
              {editing ? "Edit campaign" : "Create a campaign"}
            </h3>
            {editing && (
              <button
                type="button"
                className="text-sm text-primary underline"
                onClick={() => {
                  setEditing(null);
                  setForm(blank);
                }}
              >
                Cancel editing
              </button>
            )}
          </div>
          <label className="owner-label">
            Campaign title
            <input
              className="owner-input"
              value={form.title}
              required
              maxLength={160}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </label>
          <div className="grid sm:grid-cols-2 gap-4">
            <label className="owner-label">
              Channel
              <select
                className="owner-input"
                value={form.platform}
                onChange={(e) => setForm({ ...form, platform: e.target.value })}
              >
                {[
                  "instagram",
                  "facebook",
                  "tiktok",
                  "linkedin",
                  "email",
                  "whatsapp",
                  "other",
                ].map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
            <label className="owner-label">
              Planned time (optional)
              <input
                className="owner-input"
                type="datetime-local"
                value={form.scheduled_at}
                onChange={(e) =>
                  setForm({ ...form, scheduled_at: e.target.value })
                }
              />
              <span className="text-xs text-muted-foreground">
                Your browser timezone:{" "}
                {Intl.DateTimeFormat().resolvedOptions().timeZone}. Planning
                only.
              </span>
            </label>
          </div>
          <label className="owner-label">
            Caption / content
            <textarea
              className="owner-input"
              rows={9}
              value={form.caption}
              required
              maxLength={10000}
              onChange={(e) => setForm({ ...form, caption: e.target.value })}
            />
            <span className="text-xs text-muted-foreground">
              {form.caption.length}/10,000 characters. Review claims and links
              before using.
            </span>
          </label>
          <div className="flex flex-wrap gap-3">
            <button className="owner-button" disabled={!!busy}>
              {busy === "save" ? "Saving…" : "Save campaign draft"}
            </button>
            <button
              type="button"
              className="owner-button-secondary"
              disabled={!form.caption}
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(form.caption);
                  setMessage("Caption copied.");
                } catch {
                  setError(
                    "Clipboard unavailable. Select the caption and copy it manually.",
                  );
                }
              }}
            >
              <Copy className="w-4 h-4" />
              Copy caption
            </button>
          </div>
          <details className="pt-4 border-t border-border">
            <summary className="text-sm font-semibold cursor-pointer">
              Draft with your AI provider
            </summary>
            <label className="owner-label mt-4">
              Brief / offer
              <input
                className="owner-input"
                value={topic}
                maxLength={1500}
                onChange={(e) => setTopic(e.target.value)}
              />
            </label>
            <p className="text-xs text-muted-foreground mt-2">
              Your saved business context is included. Generation may incur
              provider charges. Generated copy replaces the caption only after
              success.
            </p>
            <button
              type="button"
              className="owner-button-secondary mt-3"
              disabled={
                !!busy || !topic.trim() || !overview.capabilities.ai_available
              }
              onClick={async () => {
                setBusy("generate");
                setError("");
                try {
                  const result = await apiCall<AgentRun>(
                    "/api/v1/owner/runs",
                    "POST",
                    {
                      kind: "marketing",
                      objective: `Write ${form.platform} content for: ${topic}`,
                    },
                  );
                  await refresh();
                  if (result.status === "failed")
                    throw new Error(result.error || "Generation failed.");
                  setForm((prev) => ({
                    ...prev,
                    caption: result.output,
                    title: prev.title || topic.slice(0, 160),
                  }));
                  setMessage(
                    "AI draft loaded into the editor. Review and save it.",
                  );
                } catch (err) {
                  setError(
                    err instanceof Error ? err.message : "Generation failed.",
                  );
                } finally {
                  setBusy("");
                }
              }}
            >
              <Sparkles className="w-4 h-4" />
              {busy === "generate" ? "Generating…" : "Generate caption"}
            </button>
            {!overview.capabilities.ai_available && (
              <p className="mt-2 text-sm text-muted-foreground">
                AI is not configured. Manual drafts work without an API key.
              </p>
            )}
          </details>
        </form>
        <section className="owner-panel">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h3 className="font-display text-lg font-semibold flex items-center gap-2">
              <CalendarDays className="w-5 h-5 text-primary" />
              Campaign library
            </h3>
            <label className="text-sm">
              Show
              <select
                className="owner-input mt-1"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="active">Drafts and approved</option>
                <option value="archived">Archived</option>
                <option value="all">All campaigns</option>
              </select>
            </label>
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            Latest 100 campaigns. Approved means reviewed, not published.
          </p>
          <div className="grid sm:grid-cols-2 gap-3 mt-4">
            <label className="owner-label">
              Search campaigns
              <input
                className="owner-input"
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </label>
            <label className="owner-label">
              Planned date
              <input
                className="owner-input"
                type="date"
                value={calendarDay}
                onChange={(e) => setCalendarDay(e.target.value)}
              />
            </label>
          </div>
          <div className="divide-y divide-border mt-4">
            {overview.campaigns
              .filter(
                (c) =>
                  filter === "all" ||
                  (filter === "archived"
                    ? c.status === "archived"
                    : c.status !== "archived"),
              )
              .filter(
                (c) =>
                  (c.title + " " + c.caption)
                    .toLowerCase()
                    .includes(search.toLowerCase()) &&
                  (!calendarDay ||
                    (c.scheduled_at &&
                      new Date(c.scheduled_at).toLocaleDateString("en-CA") ===
                        calendarDay)),
              )
              .sort((a, b) =>
                (a.scheduled_at || "9999").localeCompare(
                  b.scheduled_at || "9999",
                ),
              )
              .map((c) => (
                <article className="py-5" key={c.id}>
                  <div className="flex justify-between gap-3">
                    <h4 className="font-semibold break-words">{c.title}</h4>
                    <span className="text-xs capitalize shrink-0">
                      {c.status}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {c.platform} ·{" "}
                    {c.scheduled_at
                      ? `Planned ${new Date(c.scheduled_at).toLocaleString()}`
                      : "No planned time"}
                  </p>
                  <p className="text-sm whitespace-pre-wrap break-words mt-3 line-clamp-4">
                    {c.caption}
                  </p>
                  <div className="flex flex-wrap gap-2 mt-4">
                    {c.status !== "archived" && (
                      <button
                        className="owner-button-secondary"
                        disabled={!!busy}
                        onClick={() => {
                          setEditing(c.id);
                          const date = c.scheduled_at
                            ? new Date(c.scheduled_at)
                            : null;
                          setForm({
                            title: c.title,
                            platform: c.platform,
                            caption: c.caption,
                            scheduled_at: date
                              ? new Date(
                                  date.getTime() -
                                    date.getTimezoneOffset() * 60000,
                                )
                                  .toISOString()
                                  .slice(0, 16)
                              : "",
                          });
                          setMessage(
                            "Campaign loaded into the editor. Saving edits resets approval.",
                          );
                        }}
                      >
                        Edit draft
                      </button>
                    )}
                    {c.status === "draft" && (
                      <button
                        className="owner-button-secondary"
                        disabled={!!busy}
                        onClick={() => void changeStatus(c, "approved")}
                      >
                        Approve
                      </button>
                    )}
                    <button
                      className="owner-button-secondary"
                      disabled={!!busy}
                      onClick={() =>
                        void changeStatus(
                          c,
                          c.status === "archived" ? "draft" : "archived",
                        )
                      }
                    >
                      {c.status === "archived" ? "Restore draft" : "Archive"}
                    </button>
                    <button
                      className="owner-button-secondary"
                      onClick={() => {
                        const url = URL.createObjectURL(
                          new Blob(
                            [
                              `${c.title}\nChannel: ${c.platform}\n\n${c.caption}`,
                            ],
                            { type: "text/plain" },
                          ),
                        );
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `campaign-${c.id}.txt`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      Export text
                    </button>
                  </div>
                </article>
              ))}
            {!overview.campaigns.length && (
              <div className="py-10 text-sm text-muted-foreground">
                <Plus className="w-6 h-6 mb-3" />
                No campaigns yet. Save your first draft to start the library.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
