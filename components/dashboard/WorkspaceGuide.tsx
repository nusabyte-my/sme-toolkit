import { ArrowRight, Compass, LogOut, CircleHelp } from 'lucide-react';
import { AppView } from '../../types';
import { useOwner } from '../../contexts/OwnerContext';
import { exitDemoSession } from '../../services/apiClient';
import { workspaceNavigation } from './navigation';
import { demoJourney, workspaceGuide } from './workspaceContent';
import { useStrategyMode } from '../../contexts/StrategyModeContext';
import { strategyMenu } from './strategyGuidance';

export default function WorkspaceGuide({view,onNavigate}:{view:AppView;onNavigate:(view:AppView)=>void}) {
  const { mode } = useStrategyMode();
  const {overview}=useOwner();const guide=workspaceGuide[view];const navigation=workspaceNavigation.find(item=>item.view===view);
  if(!guide||!navigation)return null;
  const demo=overview?.context?.is_demo;const step=demoJourney.findIndex(item=>item.view===view);const next=demoJourney[(step+1)%demoJourney.length];
  return <div className="mb-5 space-y-3">
    {demo&&<aside aria-label="Demo enterprise" className="flex flex-wrap items-center justify-between gap-2 text-xs border-b border-border pb-3"><p><strong>Meranti Supply Co. · Demo</strong><span className="text-muted-foreground ml-2">Fictional records · no paid AI or external actions</span></p><button className="inline-flex gap-2 items-center min-h-9 px-2 text-primary font-medium" onClick={exitDemoSession}><LogOut className="w-4 h-4"/>Exit demo</button></aside>}
    <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs text-muted-foreground">{navigation.group}</p><h1 id="workspace-title" className="font-display text-lg font-semibold">{mode === 'guided' ? strategyMenu.find(step=>step.view===view)?.label || navigation.label : navigation.label}</h1></div><details className="max-w-xl group" key={view}><summary className="cursor-pointer text-sm text-primary min-h-11 py-3 flex gap-2 items-center"><CircleHelp className="w-4 h-4"/>What can I do here?</summary><div className="owner-panel mt-2 text-sm space-y-3"><p>{guide.summary}</p><ul className="list-disc pl-5 space-y-1">{guide.capabilities.map(item=><li key={item}>{item}</li>)}</ul><p>{guide.tryIt}</p><p className="text-xs text-muted-foreground">{guide.boundary}</p></div></details></div>
    {demo&&<details className="text-xs border-b border-border pb-2"><summary className="cursor-pointer min-h-9 py-2 text-muted-foreground"><Compass className="w-3.5 h-3.5 inline mr-2"/>Guided demo{step>=0?` · step ${step+1} of ${demoJourney.length}`:''}</summary><nav aria-label="Demo walkthrough" className="flex flex-wrap gap-2 items-center py-2">{demoJourney.map((item,index)=><button key={item.view} className={`min-h-9 px-2 rounded ${item.view===view?'bg-primary/10 text-primary font-semibold':'hover:bg-muted'}`} aria-current={item.view===view?'step':undefined} onClick={()=>onNavigate(item.view)}>{index+1}. {item.label}</button>)}<button className="owner-button-secondary" onClick={()=>onNavigate(next.view)}>Next step<ArrowRight className="w-4 h-4"/></button></nav></details>}
  </div>;
}
