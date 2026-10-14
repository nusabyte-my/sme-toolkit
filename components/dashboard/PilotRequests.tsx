import { useEffect, useState } from 'react';
import { Inbox, RefreshCw } from 'lucide-react';
import { apiCall } from '../../services/apiClient';

type Enquiry = { id: string; name: string; company: string; email: string; workflow: string; goal: string; status: 'new' | 'contacted' | 'closed'; created_at: string; contact_consent_at: string };
type Page = { items: Enquiry[]; has_more: boolean };
const labels: Record<string, string> = { sales: 'Sales & follow-ups', billing: 'Quotations & invoices', marketing: 'Marketing & creative', agents: 'Agents & recurring checks', enterprise: 'Enterprise scope' };

export default function PilotRequests() {
  const [data, setData] = useState<Page | null>(null);
  const [state, setState] = useState('new');
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  useEffect(() => {
    let active = true;
    setLoading(true); setError('');
    apiCall<Page>(`/api/v1/pilot-requests?state=${state}&offset=${offset}&limit=25`).then(result => {
      if (active) setData(result);
    }).catch(e => { if (active) setError(e.message); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [state, offset, revision]);
  const change = async (row: Enquiry, next: Enquiry['status'] | 'delete') => {
    if (busy || (next === 'delete' && !window.confirm(`Permanently delete the pilot enquiry from ${row.company}? Contact details and the request will be removed.`))) return;
    setBusy(row.id); setError(''); setMessage('');
    try {
      await apiCall(`/api/v1/pilot-requests/${row.id}`, next === 'delete' ? 'DELETE' : 'PATCH', next === 'delete' ? undefined : { status: next });
      setMessage(next === 'delete' ? 'Enquiry deleted.' : 'Enquiry status saved. No email was sent.');
      setRevision(value => value + 1);
    } catch (e) { setError(e instanceof Error ? e.message : 'The enquiry could not be updated. Refresh before trying again.'); }
    finally { setBusy(''); }
  };
  return <section className="owner-panel space-y-5" aria-labelledby="pilot-inbox-heading">
    <div className="flex flex-wrap items-start justify-between gap-4"><div><h2 id="pilot-inbox-heading" className="font-display text-2xl font-semibold flex items-center gap-2"><Inbox className="w-6 h-6 text-primary" aria-hidden="true"/>Pilot enquiries</h2><p className="text-sm text-muted-foreground mt-2">Real landing-page submissions. Administrator access only; contact follow-up is manual.</p></div><button className="owner-button-secondary" disabled={loading || !!busy} onClick={() => setRevision(value => value + 1)}><RefreshCw className="w-4 h-4" aria-hidden="true"/>Refresh enquiries</button></div>
    <label className="owner-label max-w-xs">Show enquiries<select className="owner-input" value={state} disabled={!!busy} onChange={event => { setState(event.target.value); setOffset(0); setMessage(''); }}><option value="new">New</option><option value="contacted">Contacted</option><option value="closed">Closed</option><option value="all">All enquiries</option></select></label>
    {error && <p role="alert" className="owner-error">{error}</p>}
    {(loading || message) && <p role="status" className="text-sm">{loading ? 'Loading pilot enquiries…' : message}</p>}
    {!loading && !error && data?.items.length === 0 && <p className="text-sm text-muted-foreground py-6">No enquiries in this view. New requests appear here after the landing form confirms receipt.</p>}
    {!loading && !error && <div className="divide-y divide-border">{data?.items.map(row => <article key={row.id} className="py-5 space-y-3 min-w-0">
      <div className="flex flex-wrap justify-between items-start gap-3"><div className="min-w-0"><h3 className="font-semibold break-words">{row.company}</h3><p className="text-sm text-muted-foreground mt-1 break-words">{row.name} · {labels[row.workflow]} · {new Date(row.created_at).toLocaleString()}</p></div><span className="text-xs font-semibold capitalize">{row.status}</span></div>
      <a className="inline-flex items-center min-h-11 text-primary underline break-all text-sm" href={`mailto:${encodeURIComponent(row.email)}?subject=${encodeURIComponent('Your SME OS pilot enquiry')}`}>{row.email}</a>
      <p className="text-sm whitespace-pre-wrap break-words">{row.goal}</p>
      <p className="text-xs text-muted-foreground break-all">Reference: {row.id} · Contact consent recorded {new Date(row.contact_consent_at).toLocaleString()}</p>
      <div className="flex flex-wrap gap-2">{row.status !== 'contacted' && <button className="owner-button-secondary" disabled={!!busy} onClick={() => void change(row, 'contacted')}>Mark contacted</button>}{row.status !== 'closed' && <button className="owner-button-secondary" disabled={!!busy} onClick={() => void change(row, 'closed')}>Close enquiry</button>}{row.status !== 'new' && <button className="owner-button-secondary" disabled={!!busy} onClick={() => void change(row, 'new')}>Reopen enquiry</button>}<button className="owner-button-secondary" disabled={!!busy} onClick={() => void change(row, 'delete')}>Delete enquiry</button></div>
    </article>)}</div>}
    <div className="flex items-center gap-3"><button className="owner-button-secondary" disabled={!offset || loading || !!busy} onClick={() => setOffset(value => Math.max(0, value - 25))}>Previous</button><span className="text-sm">Page {offset / 25 + 1}</span><button className="owner-button-secondary" disabled={!data?.has_more || loading || !!busy || !!error} onClick={() => setOffset(value => value + 25)}>Next</button></div>
  </section>;
}
