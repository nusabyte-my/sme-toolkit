import { useEffect, useRef, useState } from 'react';
import { Layers, Menu, X, ArrowRight, LoaderCircle, RotateCcw } from 'lucide-react';
import { AppView, SubscriptionTier } from '../types';
import { startDemoSession } from '../services/apiClient';
import { workspaceNavigation } from './dashboard/navigation';
import HeroSection from './landing/HeroSection';
import UnifiedWorkflow from './landing/UnifiedWorkflow';
import FeaturesGrid from './landing/FeaturesGrid';
import PricingSection from './landing/PricingSection';
import FAQSection from './landing/FAQSection';

interface LandingPageProps {
  onGetStarted: (tier: SubscriptionTier) => void;
  onNavigateLegal?: (view: AppView) => void;
}
const sections = [['product-preview','See the product'],['faq','Questions'],['pricing','Plan a pilot']];

export default function LandingPage({ onGetStarted, onNavigateLegal }: LandingPageProps) {
  const [menu, setMenu] = useState(false);
  const [demoBusy, setDemoBusy] = useState(false);
  const [demoError, setDemoError] = useState('');
  const [retryView, setRetryView] = useState(AppView.DASHBOARD);
  const menuButton = useRef<HTMLButtonElement>(null);
  const header = useRef<HTMLElement>(null);
  useEffect(()=>{
    if(!menu)return;
    const close=(event:KeyboardEvent)=>{if(event.key==='Escape'){setMenu(false);menuButton.current?.focus();}};
    const outside=(event:PointerEvent)=>{if(!header.current?.contains(event.target as Node))setMenu(false);};
    window.addEventListener('keydown',close);window.addEventListener('pointerdown',outside);
    return()=>{window.removeEventListener('keydown',close);window.removeEventListener('pointerdown',outside);};
  },[menu]);
  const onDemo = async (view = AppView.DASHBOARD) => {
    if (demoBusy) return;
    setDemoBusy(true);setDemoError('');setMenu(false);setRetryView(view);
    try {
      await startDemoSession();
      window.location.hash = '#/' + workspaceNavigation.find(item => item.view === view)!.slug;
    } catch (error) {
      setDemoError(error instanceof Error ? error.message : 'The demo could not be opened. Check your connection, then try again.');
    } finally { setDemoBusy(false); }
  };
  const scrollTo = (id: string) => {
    setMenu(false);
    const section=document.getElementById(id);
    section?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
    const heading=section?.querySelector('h2');heading?.setAttribute('tabindex','-1');heading?.focus({preventScroll:true});
  };
  return <div className="commercial-page min-h-screen text-foreground">
    <a href="#main-content" onClick={event=>{event.preventDefault();document.getElementById('main-content')?.focus();}} className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[60] focus:bg-card focus:p-3">Skip to main content</a>
    <header ref={header} className="commercial-header fixed top-0 inset-x-0 z-50">
      <nav aria-label="Main navigation" className="showcase-container h-20 flex items-center justify-between gap-3">
        <button onClick={()=>window.scrollTo({top:0,behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'})} className="flex items-center gap-3 min-h-11 shrink-0" aria-label="SME OS product overview"><span className="w-10 h-10 rounded-xl bg-gradient-primary text-white grid place-items-center"><Layers className="w-5 h-5" aria-hidden="true"/></span><span className="font-display text-xl font-bold">SME OS</span></button>
        <div className="hidden lg:flex items-center gap-5 text-sm">{sections.map(([id,label])=><button key={id} className="min-h-11 text-muted-foreground hover:text-primary" onClick={()=>scrollTo(id)}>{label}</button>)}</div>
        <div className="hidden lg:flex items-center gap-3"><button className="commercial-ghost" disabled={demoBusy} onClick={()=>onGetStarted(SubscriptionTier.FREE)}>Sign in</button><button className="commercial-cta" disabled={demoBusy} aria-busy={demoBusy} onClick={()=>void onDemo()}>{demoBusy?'Opening demo…':'Explore demo'}<ArrowRight className="w-4 h-4" aria-hidden="true"/></button></div>
        <button ref={menuButton} className="lg:hidden p-3 rounded-lg hover:bg-muted" aria-label={menu?'Close menu':'Open menu'} aria-expanded={menu} aria-controls="landing-mobile-menu" onClick={()=>setMenu(!menu)}>{menu?<X className="w-5 h-5" aria-hidden="true"/>:<Menu className="w-5 h-5" aria-hidden="true"/>}</button>
      </nav>
      {menu&&<nav id="landing-mobile-menu" aria-label="Mobile navigation" className="lg:hidden p-4 border-t border-border bg-card grid gap-2 max-h-[calc(100dvh-5rem)] overflow-y-auto">{sections.map(([id,label])=><button key={id} className="text-left min-h-11 px-3 hover:bg-muted rounded-lg" onClick={()=>scrollTo(id)}>{label}</button>)}<button className="commercial-cta" disabled={demoBusy} onClick={()=>void onDemo()}>{demoBusy?'Opening demo…':'Explore demo'}</button><button className="commercial-ghost" disabled={demoBusy} onClick={()=>{setMenu(false);onGetStarted(SubscriptionTier.FREE);}}>Sign in</button></nav>}
    </header>
    {(demoBusy||demoError)&&<div className="commercial-feedback" role={demoError?'alert':'status'} aria-live="polite"><div className="flex items-start gap-3">{demoBusy&&<LoaderCircle className="w-5 h-5 text-primary motion-safe:animate-spin shrink-0" aria-hidden="true"/>}<p className="text-sm leading-relaxed flex-1">{demoBusy?'Opening your sample business. Your own records stay separate.':demoError}</p>{demoError&&<button onClick={()=>setDemoError('')} className="p-2 hover:bg-muted rounded-lg" aria-label="Dismiss demo error"><X className="w-4 h-4" aria-hidden="true"/></button>}</div>{demoError&&<div className="flex flex-wrap gap-2 mt-3"><button className="commercial-ghost" onClick={()=>void onDemo(retryView)}><RotateCcw className="w-4 h-4" aria-hidden="true"/>Try demo again</button><button className="commercial-ghost" onClick={()=>{setDemoError('');scrollTo('product-preview');}}>See product examples</button></div>}</div>}
    <main id="main-content" tabIndex={-1}>
      <HeroSection onDemo={onDemo} demoBusy={demoBusy}/>
      <UnifiedWorkflow onDemo={onDemo} demoBusy={demoBusy}/>
      <div className="showcase-container pb-12"><details className="border-y border-border"><summary className="min-h-12 py-4 text-sm font-semibold cursor-pointer">Looking for a specific tool? Browse all workspaces</summary><FeaturesGrid onDemo={onDemo} demoBusy={demoBusy}/></details></div>
      <FAQSection/>
      <PricingSection />
    </main>
    <footer className="commercial-dark py-8"><div className="showcase-container flex flex-wrap justify-between items-center gap-4 text-sm"><p>© {new Date().getFullYear()} SME OS</p><div className="flex gap-6"><button className="min-h-11 underline underline-offset-4" onClick={()=>onNavigateLegal?.(AppView.PRIVACY)}>Privacy</button><button className="min-h-11 underline underline-offset-4" onClick={()=>onNavigateLegal?.(AppView.TERMS)}>Terms</button></div></div></footer>
  </div>;
}
