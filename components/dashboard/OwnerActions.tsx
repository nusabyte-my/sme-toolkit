import { useEffect, useState } from "react";
import { CheckCheck, Plus, RefreshCw } from "lucide-react";
import { apiCall } from "../../services/apiClient";
import { useOwner } from "../../contexts/OwnerContext";
import { useUnsavedChanges } from '../../hooks/useUnsavedChanges';

export interface OwnerAction {
  id: string;
  title: string;
  notes: string;
  owner: string;
  due_date: string | null;
  status: "open" | "in_progress" | "done";
  created_at: string;
  updated_at: string;
}
export default function OwnerActions({ guided=false, stage=1, suggestion, onCreated, refreshSignal }: { guided?: boolean; stage?: number; suggestion?: {title:string;notes:string;sequence:number}|null; onCreated?:()=>void; refreshSignal?:string }) {
  const { overview, refresh } = useOwner();
  const [items, setItems] = useState<OwnerAction[]>([]),
    [title, setTitle] = useState(""),
    [owner, setOwner] = useState(""),
    [due, setDue] = useState("");
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [showDone, setShowDone] = useState(false);
  const [notes,setNotes] = useState(''), [reviewing,setReviewing] = useState(false), [message,setMessage] = useState('');
  useUnsavedChanges(!!title||!!owner||!!due||!!busy);
  useEffect(()=>{
    if (!suggestion) return;
    if ((title||owner||due)&&!confirm('Replace the unsaved action with this priority?')) return;
    setTitle(suggestion.title);setNotes(suggestion.notes);setReviewing(false);setMessage('');
  },[suggestion]);
  const load = async () => {
    setError("");
    try {
      setItems(await apiCall<OwnerAction[]>("/api/v1/workspace/tasks"));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Actions could not be loaded.",
      );
    }
  };
  useEffect(() => {
    let active = true;
    if (overview?.context)
      apiCall<OwnerAction[]>("/api/v1/workspace/tasks")
        .then((rows) => {
          if (active) setItems(rows);
        })
        .catch((err) => {
          if (active) setError(err.message);
        });
    return () => {
      active = false;
    };
  }, [overview?.context?.id, refreshSignal]);
  if (!overview?.context) return null;
  return (
    <section className={`owner-panel space-y-4 ${guided && stage===0?'hidden':''}`}>
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h3 className="font-display text-lg font-semibold">
            {guided ? stage===1?'Who will do what, and by when?':'Your action list' : 'Owner action board'}
          </h3>
          <p className="text-xs text-muted-foreground mt-1">
            Saved assignments and deadlines. Actions do not execute external
            changes.
          </p>
        </div>
        <button
          className="owner-button-secondary"
          onClick={() => void load()}
          disabled={busy}
        >
          <RefreshCw className="w-4 h-4" />
          Refresh actions
        </button>
      </div>
      {error && (
        <p className="owner-error" role="alert">
          {error}
        </p>
      )}
      {message&&<p role="status" className="text-sm">{message}</p>}
      <form
        className={guided && stage!==1 ? 'hidden' : 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)_160px_auto] gap-3 items-end'}
        onSubmit={async (e) => {
          e.preventDefault();
          if (busy) return;
          if (guided && !reviewing) { setReviewing(true); return; }
          setBusy(true);
          setError("");
          try {
            await apiCall("/api/v1/workspace/tasks", "POST", {
              title,
              notes,
              owner,
              due_date: due || null,
            });
            setTitle('');setOwner('');setDue('');setNotes('');setReviewing(false);setMessage('Action saved. It has not sent a message or executed any work.');onCreated?.();
            await load();
            await refresh();
          } catch (err) {
            setError(
              err instanceof Error ? err.message : "Action could not be saved.",
            );
          } finally {
            setBusy(false);
          }
        }}
      >
        <label className={`owner-label ${guided&&reviewing?'hidden':''}`}>
          Next action
          <input
            className="owner-input"
            required
            maxLength={180}
            value={title}
            onChange={(e) => { setTitle(e.target.value);setReviewing(false); }}
          />
        </label>
        <label className={`owner-label ${guided&&reviewing?'hidden':''}`}>
          Responsible person
          <input
            className="owner-input"
            maxLength={120}
            value={owner}
            onChange={(e) => { setOwner(e.target.value);setReviewing(false); }}
          />
        </label>
        <label className={`owner-label ${guided&&reviewing?'hidden':''}`}>
          Due date
          <input
            className="owner-input"
            type="date"
            value={due}
            onChange={(e) => { setDue(e.target.value);setReviewing(false); }}
          />
        </label>
        {guided&&reviewing&&<div className="sm:col-span-2 lg:col-span-4 space-y-3"><h4 className="font-semibold">Review your action</h4><dl className="text-sm space-y-2"><div><dt className="font-medium">Action</dt><dd className="break-words">{title}</dd></div><div><dt className="font-medium">Responsible person</dt><dd>{owner||'Unassigned'}</dd></div><div><dt className="font-medium">Due date</dt><dd>{due||'No deadline'}</dd></div>{notes&&<div><dt className="font-medium">Why this matters</dt><dd className="break-words">{notes}</dd></div>}</dl><button type="button" className="owner-button-secondary" onClick={()=>setReviewing(false)}>Edit action</button></div>}
        <button className="owner-button" disabled={busy || !title.trim()}>
          <Plus className="w-4 h-4" />
          {guided ? reviewing?'Save action':'Review action' : 'Add action'}
        </button>
      </form>
      <label className={`flex gap-2 items-center text-sm ${guided&&stage!==2?'hidden':''}`}>
        <input
          type="checkbox"
          checked={showDone}
          onChange={(e) => setShowDone(e.target.checked)}
        />
        Show completed actions
      </label>
      <div className={`divide-y divide-border ${guided&&stage!==2?'hidden':''}`}>
        {items
          .filter((item) => showDone || item.status !== "done")
          .map((item) => (
            <article
              className="py-4 flex flex-wrap justify-between gap-3"
              key={item.id}
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium break-words">{item.title}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {item.owner || "Unassigned"} ·{" "}
                  {item.due_date ? `Due ${item.due_date}` : "No deadline"}
                  {item.due_date &&
                  item.due_date < new Date().toLocaleDateString("en-CA") &&
                  item.status !== "done"
                    ? " · Overdue"
                    : ""}
                </p>
              </div>
              <select
                className="owner-input !w-auto"
                aria-label={`Action status: ${item.title}`}
                value={item.status}
                disabled={busy}
                onChange={async (e) => {
                  setBusy(true);
                  try {
                    await apiCall(`/api/v1/workspace/tasks/${item.id}`, "PUT", {
                      title: item.title,
                      notes: item.notes,
                      owner: item.owner,
                      due_date: item.due_date,
                      status: e.target.value,
                    });
                    await load();
                    await refresh();
                  } catch (err) {
                    setError(
                      err instanceof Error
                        ? err.message
                        : "Status update failed.",
                    );
                  } finally {
                    setBusy(false);
                  }
                }}
              >
                <option value="open">Open</option>
                <option value="in_progress">In progress</option>
                <option value="done">Done</option>
              </select>
            </article>
          ))}
        {!items.some((item) => showDone || item.status !== "done") && (
          <p className="text-sm text-muted-foreground py-5 flex gap-2">
            <CheckCheck className="w-5 h-5" />
            No actions in this view. Add a concrete next step above.
          </p>
        )}
      </div>
    </section>
  );
}
