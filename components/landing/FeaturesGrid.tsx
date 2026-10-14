import { useState } from 'react';
import { ArrowRight, Check } from 'lucide-react';
import { AppView } from '../../types';
import { workspaceNavigation } from '../dashboard/navigation';
import { workspaceGuide } from '../dashboard/workspaceContent';

export default function FeaturesGrid({ onDemo, demoBusy }: { onDemo: (view?: AppView) => void; demoBusy: boolean }) {
  const [group, setGroup] = useState('Business');
  const [selected, setSelected] = useState(AppView.DASHBOARD);
  const guide = workspaceGuide[selected]!;
  const active = workspaceNavigation.find(item => item.view === selected)!;
  const items = workspaceNavigation.filter(item => item.group === group);
  return <section id="features" className="py-6 scroll-mt-24" aria-labelledby="features-heading">
    <div>
      <h2 id="features-heading" className="font-display text-2xl font-semibold mb-5">Find your workspace</h2>
      <div className="flex flex-wrap gap-2 mb-6" role="group" aria-label="Business areas">{[...new Set(workspaceNavigation.map(item=>item.group))].map(name=><button key={name} className={group===name?'owner-button':'owner-button-secondary'} aria-pressed={group===name} onClick={()=>{setGroup(name);setSelected(workspaceNavigation.find(item=>item.group===name)!.view);}}>{name}</button>)}</div>
      <div className="grid grid-cols-1 md:grid-cols-[minmax(210px,1fr)_minmax(0,2fr)] border border-border rounded-2xl overflow-hidden">
        <nav aria-label={`${group} workspaces`} className="bg-muted/40 p-3 md:border-r border-b md:border-b-0 border-border">{items.map(item=><button key={item.view} onClick={()=>setSelected(item.view)} aria-pressed={selected===item.view} className={`w-full text-left px-4 py-3.5 text-sm rounded-lg flex justify-between items-center gap-3 ${selected===item.view?'bg-primary/10 text-primary font-semibold':'hover:bg-muted text-muted-foreground'}`}>{item.label}<ArrowRight className="w-4 h-4 shrink-0" aria-hidden="true"/></button>)}</nav>
        <article className="p-5 sm:p-8 lg:p-10" aria-live="polite" aria-atomic="true">
          <p className="text-sm font-semibold text-primary mb-3">{active.label}</p><h3 className="font-display text-2xl sm:text-3xl font-semibold leading-tight">{guide.headline}</h3><p className="text-sm sm:text-base text-muted-foreground leading-relaxed mt-4 max-w-prose">{guide.summary}</p>
          <ul className="space-y-3 mt-6">{guide.capabilities.map(text=><li key={text} className="flex items-start gap-2 text-sm"><Check className="w-4 h-4 shrink-0 text-primary mt-0.5" aria-hidden="true"/>{text}</li>)}</ul>
          <div className="border-t border-border mt-7 pt-5"><h4 className="font-semibold text-sm">Inside the demo</h4><p className="text-sm leading-relaxed mt-2">{guide.tryIt}</p><p className="text-xs text-muted-foreground mt-3">{guide.boundary}</p></div>
          <button className="commercial-ghost mt-6" disabled={demoBusy} aria-busy={demoBusy} onClick={()=>onDemo(selected)}>{demoBusy?'Opening demo…':'Explore this solution'}<ArrowRight className="w-4 h-4" aria-hidden="true"/></button>
        </article>
      </div>
    </div>
  </section>;
}
