/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Kanban tool workspace */
import React from 'react';
import KPISOverview from './KPISOverview';
import EnhancedToolCard from './EnhancedToolCard';
import { AppView } from '../../types';
import { Layers, PenTool, TrendingUp, MoreHorizontal, Plus } from 'lucide-react';

interface ToolItem {
  id: AppView;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: 'royal' | 'midnight' | 'dark' | 'baby' | 'emerald' | 'amber' | 'pink' | 'cyan' | 'indigo' | 'purple' | 'slate';
  description: string;
}

interface KanbanDashboardProps {
  tools: ToolItem[];
  onNavigate: (view: AppView) => void;
}

const KanbanColumn: React.FC<{ 
  title: string; 
  icon: React.ReactNode; 
  iconColorClass: string;
  iconBgClass: string;
  count: number;
  tools: ToolItem[];
  onNavigate: (view: AppView) => void;
}> = ({ title, icon, iconColorClass, iconBgClass, count, tools, onNavigate }) => (
  <div className="flex flex-col h-full bg-muted/40 rounded-2xl p-3 border border-border/60">
    {/* Column Header */}
    <div className="flex items-center justify-between px-2 py-2 mb-2">
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-xl ${iconBgClass} ${iconColorClass} flex items-center justify-center shadow-xs border border-border/60`}>
          {icon}
        </div>
        <div>
          <h3 className="text-sm font-bold font-display text-foreground leading-none">{title}</h3>
          <span className="text-[10px] font-mono font-semibold text-muted-foreground uppercase tracking-wider">{count} Tools</span>
        </div>
      </div>
      <button 
        className="p-1.5 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label={`Options for ${title}`}
      >
        <MoreHorizontal className="w-4 h-4" />
      </button>
    </div>

    {/* Scrollable List */}
    <div className="space-y-3 flex-1 overflow-y-auto px-1">
      {tools.map(tool => {
        const IconComponent = tool.icon;
        return (
          <EnhancedToolCard
            key={tool.id}
            id={tool.id}
            title={tool.label}
            description={tool.description}
            icon={<IconComponent className="w-5 h-5" />}
            color={tool.color}
            usageStats={{
              totalUses: 28,
              thisMonth: 12,
              trend: 'up'
            }}
            onClick={() => onNavigate(tool.id)}
            className="shadow-xs border-border hover:shadow-brand hover:border-primary/40 transition-all duration-200"
          />
        );
      })}
      
      <button 
        className="w-full py-3 border-2 border-dashed border-border rounded-xl text-muted-foreground hover:border-primary/40 hover:text-primary hover:bg-primary/5 transition-all flex items-center justify-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring active:scale-[0.99]"
      >
        <Plus className="w-4 h-4" /> Add Tool
      </button>
    </div>
  </div>
);

const KanbanDashboard: React.FC<KanbanDashboardProps> = ({ tools, onNavigate }) => {
  const strategyTools = tools.filter(t => [AppView.BMC_HUB, AppView.STRATEGY].includes(t.id));
  const creationTools = tools.filter(t => [AppView.MARKETING_COPY, AppView.MARKETING_VISUAL, AppView.MARKETING_VIDEO].includes(t.id));
  const growthTools = tools.filter(t => [AppView.LEADS].includes(t.id));

  return (
    <div className="flex flex-col h-full space-y-6">
      <KPISOverview className="flex-shrink-0 shadow-sm border-border" />

      <div className="flex-1 min-h-0">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
          <KanbanColumn 
            title="Plan & Strategize" 
            icon={<Layers className="w-4 h-4" />} 
            iconBgClass="bg-primary/10"
            iconColorClass="text-primary"
            count={strategyTools.length}
            tools={strategyTools}
            onNavigate={onNavigate}
          />
          <KanbanColumn 
            title="Create & Execute" 
            icon={<PenTool className="w-4 h-4" />} 
            iconBgClass="bg-rainbow-pink/10"
            iconColorClass="text-rainbow-pink"
            count={creationTools.length}
            tools={creationTools}
            onNavigate={onNavigate}
          />
          <KanbanColumn 
            title="Analyze & Grow" 
            icon={<TrendingUp className="w-4 h-4" />} 
            iconBgClass="bg-rainbow-emerald/10"
            iconColorClass="text-rainbow-emerald"
            count={growthTools.length}
            tools={growthTools}
            onNavigate={onNavigate}
          />
        </div>
      </div>
    </div>
  );
};

export default KanbanDashboard;
