import { useRef, useState } from 'react';
import { ArrowDown, ArrowRight, Expand, LoaderCircle, X } from 'lucide-react';
import { AppView } from '../../types';

export interface DemoLaunchProps {
  onDemo: (view?: AppView) => void;
  demoBusy: boolean;
}

const previews = [
  { key: 'overview', label: 'Your day', title: 'Know what needs you next.', description: 'See recorded sales, orders to review and customer follow-ups in one working view.', action: 'Try the overview', view: AppView.DASHBOARD, alt: 'Meranti demo: recorded sales, pending orders and owner actions.' },
  { key: 'billing', label: 'Invoices', title: 'Quote. Invoice. Keep track.', description: 'Turn an accepted quote into an invoice, then record payments against its balance.', action: 'Try quotations', view: AppView.BILLING, alt: 'Meranti demo: a customer quotation with itemized prices and totals.' },
  { key: 'agents', label: 'Agents', title: 'Give the checks to an agent.', description: 'Describe the job, choose its tools and approve proposed changes. You keep control.', action: 'Try agent chat', view: AppView.AGENT_FORGE, alt: 'Meranti demo: guided creation of an invoice-review agent.' },
];

export default function HeroSection({ onDemo, demoBusy }: DemoLaunchProps) {
  const [selected, setSelected] = useState(0);
  const previewHeading = useRef<HTMLHeadingElement>(null);
  const enlarged = useRef<HTMLDialogElement>(null);
  const preview = previews[selected];
  const showPreview = () => {
    previewHeading.current?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    previewHeading.current?.focus({ preventScroll: true });
  };

  return <section className="commercial-hero" aria-labelledby="hero-heading">
    <div className="showcase-container">
      <div className="commercial-hero-intro">
        <h1 id="hero-heading" tabIndex={-1} className="commercial-hero-heading">Run the business.<span>Not the busywork.</span></h1>
        <div className="commercial-hero-copy">
          <p className="text-base sm:text-lg text-muted-foreground leading-relaxed">Keep customer follow-ups, invoices and daily tasks in one workspace for SME owners. See what needs attention, then take the next step.</p>
          <div className="commercial-hero-actions">
            <button className="commercial-cta" disabled={demoBusy} aria-busy={demoBusy} aria-describedby="hero-demo-note" onClick={()=>onDemo()}>{demoBusy&&<LoaderCircle className="w-4 h-4 motion-safe:animate-spin" aria-hidden="true"/>}{demoBusy?'Opening demo…':'Explore demo'}<ArrowRight className="w-4 h-4" aria-hidden="true"/></button>
            <button className="commercial-hero-link" onClick={showPreview}>See what you can do<ArrowDown className="w-4 h-4" aria-hidden="true"/></button>
          </div>
          <p id="hero-demo-note" className="text-xs text-muted-foreground leading-relaxed mt-3">No signup or card. Sample data only.</p>
        </div>
      </div>

      <div id="product-preview" className="commercial-product-proof scroll-mt-24">
        <div className="commercial-preview-header">
          <div><h2 ref={previewHeading} id="hero-preview-heading" tabIndex={-1} className="font-display text-lg font-semibold scroll-mt-28">What would you like to get done?</h2><p className="text-xs text-muted-foreground mt-1">Pick a view. See the real product. Try it yourself.</p></div>
          <fieldset className="commercial-preview-options">
            <legend className="sr-only">Choose a product preview</legend>
            {previews.map((item,index)=><label key={item.key} className="commercial-preview-option"><input className="absolute inset-0 z-10 m-0 h-full w-full cursor-pointer opacity-0" type="radio" name="hero-preview" value={item.key} checked={selected===index} onChange={()=>setSelected(index)} aria-controls="hero-product-preview"/><span>{item.label}</span></label>)}
          </fieldset>
        </div>
        <figure id="hero-product-preview" className="commercial-preview-layout" aria-labelledby="hero-preview-title">
          <figcaption className="commercial-preview-caption">
            <div aria-live="polite" aria-atomic="true"><h3 id="hero-preview-title" className="font-display text-2xl sm:text-3xl font-semibold leading-tight">{preview.title}</h3><p className="text-sm leading-relaxed mt-4">{preview.description}</p></div>
            <button className="commercial-cta self-start mt-auto" disabled={demoBusy} aria-busy={demoBusy} onClick={()=>onDemo(preview.view)}>{demoBusy?'Opening demo…':preview.action}<ArrowRight className="w-4 h-4" aria-hidden="true"/></button>
          </figcaption>
          <div className="commercial-preview-stage">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-4"><span className="text-xs font-medium text-muted-foreground">Meranti Supply Co. · sample workspace</span><button className="commercial-hero-link" aria-haspopup="dialog" onClick={()=>enlarged.current?.showModal()}><Expand className="w-4 h-4" aria-hidden="true"/>View full screen</button></div>
            <picture className="commercial-preview-image">
              <source media="(max-width: 639px)" srcSet={`/hero-${preview.key}-mobile.webp`}/>
              <img src={`/hero-${preview.key}.webp`} width="1700" height="1063" alt={preview.alt} fetchPriority={selected===0?'high':'auto'}/>
            </picture>
            <p className="text-xs text-muted-foreground leading-relaxed mt-4">Real product · fictional sample data.</p>
          </div>
        </figure>
        <dialog ref={enlarged} className="commercial-preview-dialog" aria-labelledby="hero-enlarged-title" onClick={event=>{if(event.target===event.currentTarget)enlarged.current?.close();}}>
          <div className="flex items-center justify-between gap-4 p-4 border-b border-border"><div><h2 id="hero-enlarged-title" className="font-semibold">{preview.label} · product capture</h2><p className="text-xs text-muted-foreground mt-1">Fictional Meranti business data. Open the demo to use these controls.</p></div><button className="owner-button-secondary shrink-0" autoFocus onClick={()=>enlarged.current?.close()} aria-label="Close full-screen preview"><X className="w-5 h-5" aria-hidden="true"/></button></div>
          <div className="commercial-preview-dialog-image"><img src={`/hero-${preview.key}.webp`} width="1700" height="1063" alt={preview.alt} loading="lazy"/></div>
        </dialog>
      </div>
    </div>
  </section>;
}
