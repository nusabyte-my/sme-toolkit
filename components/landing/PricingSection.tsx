import { useRef, useState } from 'react';
import { ArrowRight, Download, LoaderCircle } from 'lucide-react';
import { submitPilotEnquiry } from '../../services/apiClient';
import { useUnsavedChanges } from '../../hooks/useUnsavedChanges';

const pilotItems = [
  'Choose one business workflow and a named owner.',
  'Agree the starting data, its source and who may access it.',
  'Define the outcome to measure and the review date.',
  'List integrations and paid AI providers separately.',
  'Agree export, retention, backup and support requirements.',
];

export default function PricingSection() {
  const [downloaded, setDownloaded] = useState(false);
  const submission = useRef({ id: '', signature: '' });
  const [form, setForm] = useState({ name: '', company: '', email: '', workflow: 'billing', goal: '', consent: false, website_url: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [receipt, setReceipt] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  useUnsavedChanges(!receipt && (busy || !!form.name || !!form.company || !!form.email || !!form.goal));
  const sendEnquiry = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true); setError('');
    const payload = { ...form, name: form.name.trim(), company: form.company.trim(), email: form.email.trim(), goal: form.goal.trim() };
    const signature = JSON.stringify(payload);
    if (submission.current.signature !== signature) submission.current = { id: crypto.randomUUID(), signature };
    try {
      const result = await submitPilotEnquiry<{ reference: string; status: string }>({ ...payload, submission_id: submission.current.id });
      setReceipt(result.reference);
    } catch (e) { setError(e instanceof TypeError ? 'Connection interrupted. Your details remain here. Retry with the same details; a received request will not be duplicated.' : e instanceof Error ? e.message : 'The request could not be saved. Your details remain here.'); }
    finally { setBusy(false); }
  };
  const download = () => {
    const text = ['SME OS — pilot planning brief','', 'Downloading this brief does not send an enquiry or activate a paid plan.','', ...pilotItems.map((item,i)=>`${i+1}. ${item}`),'', 'Use the landing-page enquiry form when you are ready to discuss your workflow. Pricing, hosting, support, integrations and provider costs are agreed separately.'].join('\n');
    const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download='sme-os-evaluation-brief.txt';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setDownloaded(true);
  };
  return <section id="pricing" className="py-12 sm:py-16 bg-muted/40 scroll-mt-24" aria-labelledby="pricing-heading"><div className="showcase-container max-w-4xl">
    <h2 id="pricing-heading" tabIndex={-1} className="showcase-heading scroll-mt-28">Could this fit your business?</h2>
    <p className="text-muted-foreground leading-relaxed mt-4 max-w-2xl">Tell us one task you want to improve. We’ll use your enquiry to scope a pilot—not sign you up for a plan.</p>
    <details className="mt-6 border-y border-border group">
      <summary className="min-h-12 py-4 font-semibold text-primary cursor-pointer">Request a pilot</summary>
      <section id="pilot-enquiry" className="pb-6 pt-2" aria-label="Pilot enquiry form">
        <p className="text-sm text-muted-foreground mb-5">Saved for administrator review. No automatic booking, payment or marketing subscription.</p>
        {receipt ? <div role="status" className="space-y-4"><h4 className="font-semibold text-lg">Your pilot enquiry was received.</h4><p className="text-sm text-muted-foreground">Saved for administrator review. No meeting, subscription or payment was created.</p><p className="text-sm break-all"><strong>Reference:</strong> {receipt}</p></div> : <form className="space-y-4 min-w-0" onSubmit={event=>void sendEnquiry(event)} aria-busy={busy}>
          <p className="text-xs text-muted-foreground">All visible fields are required.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{([['name','Your name','name',100,2],['company','Business name','organization',160,2],['email','Work email','email',254,5]] as const).map(([key,label,autoComplete,max,min])=><label key={key} className={`owner-label ${key==='email'?'sm:col-span-2':''}`}>{label}<input className="owner-input !text-base" name={key} type={key==='email'?'email':'text'} autoComplete={autoComplete} required minLength={min} maxLength={max} value={form[key]} disabled={busy} aria-invalid={!!fieldErrors[key]} aria-describedby={`pilot-${key}-error`} onChange={event=>{setForm({...form,[key]:event.target.value});setFieldErrors({...fieldErrors,[key]:''});}} onBlur={event=>setFieldErrors({...fieldErrors,[key]:event.target.validationMessage})}/><span id={`pilot-${key}-error`} className="block min-h-4 text-xs text-destructive">{fieldErrors[key]}</span></label>)}</div>
          <label className="owner-label">Workflow to improve<select className="owner-input !text-base" name="workflow" value={form.workflow} disabled={busy} onChange={event=>setForm({...form,workflow:event.target.value})}><option value="sales">Sales & customer follow-ups</option><option value="billing">Quotations & invoices</option><option value="marketing">Marketing & creative</option><option value="agents">Agents & recurring checks</option><option value="enterprise">Enterprise scope</option></select></label>
          <label className="owner-label">What is getting in the way?<textarea className="owner-input !text-base" name="goal" rows={4} minLength={15} maxLength={1500} required disabled={busy} value={form.goal} aria-describedby="pilot-goal-help pilot-goal-error" aria-invalid={!!fieldErrors.goal} onChange={event=>{setForm({...form,goal:event.target.value});setFieldErrors({...fieldErrors,goal:''});}} onBlur={event=>setFieldErrors({...fieldErrors,goal:event.target.validationMessage})}/><span id="pilot-goal-help" className="block text-xs text-muted-foreground">Describe the current task and the result you need. 15–1,500 characters; no passwords or sensitive customer records.</span><span id="pilot-goal-error" className="block min-h-4 text-xs text-destructive">{fieldErrors.goal}</span></label>
          <label hidden aria-hidden="true">Leave this field blank<input name="website_url" tabIndex={-1} autoComplete="off" value={form.website_url} onChange={event=>setForm({...form,website_url:event.target.value})}/></label>
          <label className="flex items-start gap-3 min-h-11 text-sm leading-relaxed"><input className="mt-1 h-5 w-5 shrink-0 accent-primary" type="checkbox" name="consent" required checked={form.consent} disabled={busy} onChange={event=>setForm({...form,consent:event.target.checked})}/><span>I agree to be contacted about this enquiry. Read the <a href="#/privacy" target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-4">Privacy Policy<span className="sr-only"> (opens in a new tab)</span></a>.</span></label>
          {error&&<p className="owner-error" role="alert">{error}</p>}
          <button className="commercial-cta w-full sm:w-auto min-w-52" disabled={busy||!form.consent||!form.name.trim()||!form.company.trim()||!form.email.trim()||!form.goal.trim()}>{busy?<><LoaderCircle className="w-4 h-4 motion-safe:animate-spin" aria-hidden="true"/>Saving your enquiry…</>:<>Send pilot enquiry<ArrowRight className="w-4 h-4" aria-hidden="true"/></>}</button>
        </form>}
      </section>
    </details>
    <details className="mt-3 border-b border-border"><summary className="cursor-pointer text-sm min-h-11 py-3">Prefer to prepare first? Get the planning brief</summary><div className="pb-5"><ol className="list-decimal pl-5 space-y-2 text-sm text-muted-foreground">{pilotItems.map(item=><li key={item}>{item}</li>)}</ol><button className="commercial-ghost mt-4" onClick={download}><Download className="w-4 h-4" aria-hidden="true"/>Download brief</button>{downloaded&&<p role="status" className="text-sm mt-3">Brief downloaded. No enquiry was sent.</p>}</div></details>
    <p className="text-xs text-muted-foreground leading-relaxed mt-5">Pricing, hosting and support are agreed for your scope. <a href="#/terms" className="text-primary underline underline-offset-4">Terms</a> · <a href="#/privacy" className="text-primary underline underline-offset-4">Privacy</a></p>
  </div></section>;
}
