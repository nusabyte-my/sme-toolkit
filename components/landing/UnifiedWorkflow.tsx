import { ArrowRight } from 'lucide-react';
import { AppView } from '../../types';

export default function UnifiedWorkflow({ onDemo, demoBusy }: { onDemo: (view?: AppView) => void; demoBusy: boolean }) {
  const stages = [
    {name:'Start with a sample quote',detail:'Open the fictional customer’s quote and inspect its line items. No setup or customer data needed.'},
    {name:'Try the next step',detail:'Issue the quote, record its acceptance and create an invoice. Your changes stay in the sample business.'},
    {name:'See where the money goes',detail:'Record a sample payment. Watch the invoice balance and linked bookkeeping update.'},
  ];
  return <section id="unified-workflow" className="py-12 sm:py-16 bg-muted/40 scroll-mt-24" aria-labelledby="workflow-heading"><div className="showcase-container grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-8 lg:gap-16">
    <div><h2 id="workflow-heading" className="showcase-heading">How does it work?</h2><p className="text-muted-foreground leading-relaxed mt-4 max-w-md">Follow one quote from agreement to payment. Try the working flow before bringing in your business.</p><button className="commercial-cta mt-6" disabled={demoBusy} aria-busy={demoBusy} onClick={()=>onDemo(AppView.BILLING)}>{demoBusy?'Opening demo…':'Try the invoice flow'}<ArrowRight className="w-4 h-4" aria-hidden="true"/></button><p className="text-xs text-muted-foreground mt-3">No customer is charged. No message is sent.</p></div>
    <ol className="divide-y divide-border">{stages.map((stage,index)=><li key={stage.name} className="py-5 first:pt-0 flex gap-4"><span className="text-primary font-display text-xl tabular-nums" aria-hidden="true">{index+1}</span><div className="min-w-0"><h3 className="font-display text-lg font-semibold">{stage.name}</h3><p className="text-sm text-muted-foreground leading-relaxed mt-2">{stage.detail}</p></div></li>)}</ol>
  </div></section>;
}
