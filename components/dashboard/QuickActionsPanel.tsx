/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Quick actions panel & AI recommendations */
import React from 'react';
import { Zap, FileText, Users, Image as ImageIcon, Video, BarChart3, Plus, Clock } from 'lucide-react';
import { Card, Button, Badge } from '../ui';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: 'indigo' | 'emerald' | 'amber' | 'purple' | 'pink' | 'cyan';
  iconBgClass: string;
  iconTextClass: string;
  onClick: () => void;
  badge?: string;
}

interface QuickActionsPanelProps {
  className?: string;
}

const QuickActionsPanel: React.FC<QuickActionsPanelProps> = ({ className = '' }) => {
  const quickActions: QuickAction[] = [
    {
      id: 'generate-copy',
      title: 'Generate Marketing Copy',
      description: 'Create compelling content for your campaigns',
      icon: <FileText className="w-5 h-5" />,
      color: 'emerald',
      iconBgClass: 'bg-rainbow-emerald/10',
      iconTextClass: 'text-rainbow-emerald',
      badge: 'AI Powered',
      onClick: () => console.log('Navigate to Copywriter')
    },
    {
      id: 'create-visual',
      title: 'Create Visual Content',
      description: 'Generate images and graphics for marketing',
      icon: <ImageIcon className="w-5 h-5" />,
      color: 'purple',
      iconBgClass: 'bg-rainbow-violet/10',
      iconTextClass: 'text-rainbow-violet',
      badge: 'AI Powered',
      onClick: () => console.log('Navigate to Visual Studio')
    },
    {
      id: 'analyze-leads',
      title: 'Analyze Lead Pipeline',
      description: 'Get AI insights on your sales opportunities',
      icon: <Users className="w-5 h-5" />,
      color: 'cyan',
      iconBgClass: 'bg-rainbow-cyan/10',
      iconTextClass: 'text-rainbow-cyan',
      badge: 'AI Powered',
      onClick: () => console.log('Navigate to Lead CRM')
    },
    {
      id: 'business-canvas',
      title: 'Business Model Canvas',
      description: 'Map out your business model visually',
      icon: <BarChart3 className="w-5 h-5" />,
      color: 'indigo',
      iconBgClass: 'bg-primary/10',
      iconTextClass: 'text-primary',
      onClick: () => console.log('Navigate to Business Canvas')
    },
    {
      id: 'quick-video',
      title: 'Quick Video Creation',
      description: 'Create short videos for social media',
      icon: <Video className="w-5 h-5" />,
      color: 'pink',
      iconBgClass: 'bg-rainbow-pink/10',
      iconTextClass: 'text-rainbow-pink',
      badge: 'Popular',
      onClick: () => console.log('Navigate to Video Studio')
    },
    {
      id: 'schedule-content',
      title: 'Schedule Content',
      description: 'Plan and automate your content calendar',
      icon: <Clock className="w-5 h-5" />,
      color: 'amber',
      iconBgClass: 'bg-rainbow-amber/10',
      iconTextClass: 'text-rainbow-amber',
      onClick: () => console.log('Open content scheduler')
    }
  ];

  const recentSuggestions = [
    'Complete your business model canvas to unlock strategic growth insights',
    'Your lead conversion rate improved by 15% this week',
    'Generate holiday marketing content to boost seasonal sales',
    'Schedule a weekly video to increase social engagement by 25%'
  ];

  return (
    <Card className={`bg-card border-border shadow-sm rounded-2xl p-6 ${className}`}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center shadow-brand text-white">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold font-display text-foreground">Quick Actions</h3>
              <p className="text-sm text-muted-foreground">AI-powered shortcuts to boost your business velocity</p>
            </div>
          </div>
          
          <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring">
            Customize
          </Button>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={action.onClick}
              className="group p-4 text-left backdrop-blur-sm bg-card/90 border border-border rounded-xl hover:border-primary/40 hover:-translate-y-0.5 hover:shadow-brand transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 active:scale-[0.98]"
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${action.iconBgClass} ${action.iconTextClass} group-hover:scale-105 transition-transform flex-shrink-0`}>
                  {action.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-foreground group-hover:text-primary transition-colors text-sm">
                    {action.title}
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2 leading-relaxed">
                    {action.description}
                  </p>
                  {action.badge && (
                    <div className="mt-2">
                      <Badge variant="default" size="sm" color={action.color}>
                        {action.badge}
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* AI Suggestions */}
        <div className="mt-8 p-5 bg-primary/5 rounded-2xl border border-primary/20">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center shadow-brand text-white">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold font-display text-foreground">AI Suggestions</h3>
              <p className="text-xs text-muted-foreground">Personalized recommendations based on your SME activity</p>
            </div>
          </div>
          
          <div className="space-y-2.5">
            {recentSuggestions.map((suggestion, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-card/80 border border-border/60 rounded-xl shadow-xs">
                <div className="w-2 h-2 bg-primary rounded-full mt-1.5 flex-shrink-0" />
                <p className="text-sm text-foreground flex-1 leading-snug">{suggestion}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Add Button */}
        <div className="mt-6 text-center">
          <Button variant="primary" size="lg" className="w-full md:w-auto bg-primary hover:bg-primary/90 text-primary-foreground shadow-brand rounded-xl px-6 py-2.5 font-semibold focus-visible:ring-2 focus-visible:ring-ring active:scale-95">
            <Plus className="w-4 h-4 mr-2" />
            Create New Project
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default QuickActionsPanel;
