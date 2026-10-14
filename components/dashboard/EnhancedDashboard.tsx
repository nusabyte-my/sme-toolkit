/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Enhanced dashboard & profile integration */
import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { useProfile } from '../../contexts/ProfileContext';
import { 
  Bell, 
  Settings, 
  User, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  LogOut, 
  RefreshCw, 
  Share2, 
  Sparkles 
} from 'lucide-react';
import { cn } from '../../utils/cn';
import UserProfileCard from './profiles/UserProfileCard';
import BusinessProfilePanel from './profiles/BusinessProfilePanel';
import SocialMediaSection from './profiles/SocialMediaSection';
import ProfileInsights from './profiles/ProfileInsights';
import ActivityTimeline from './profiles/ActivityTimeline';
import ProfileEditor from './profiles/ProfileEditor';
import SocialMediaEditor from './profiles/SocialMediaEditor';
import AIProfileAssistant from '../profile/AIProfileAssistant';
import SmartEmptyState from '../profile/SmartEmptyState';

const EnhancedStatCard: React.FC<{
  title: string;
  value: string;
  trend: 'up' | 'down' | 'stable';
  trendValue?: string;
  icon: React.ReactNode;
  gradient: string;
  tooltip: string;
}> = ({ title, value, trend, trendValue, icon, gradient, tooltip }) => {
  return (
    <div className={`bg-gradient-to-br ${gradient} rounded-2xl p-6 text-white shadow-brand hover:shadow-brand-lg transition-all duration-300 hover:-translate-y-1 group relative overflow-hidden`}>
      {/* Tooltip */}
      <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out pointer-events-none z-10">
        <div className="bg-slate-950/95 text-white text-xs rounded-xl px-3 py-2 max-w-[200px] shadow-xl backdrop-blur-md border border-white/10">
          {tooltip}
        </div>
      </div>
      
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium opacity-90 mb-2 flex items-center gap-2 transition-colors group-hover:opacity-100 font-mono uppercase tracking-wider text-xs">
            {title}
          </p>
          <div className="flex items-baseline gap-2">
            <h3 className="text-3xl font-bold font-display tracking-tight">{value}</h3>
            {trendValue && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-white/20 backdrop-blur-sm flex items-center gap-0.5">
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '•'} {trendValue}
              </span>
            )}
          </div>
        </div>
        <div className="w-12 h-12 rounded-xl bg-white/15 backdrop-blur-sm flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
          {icon}
        </div>
      </div>

      {/* Progress Bar */}
      {value.includes('%') && (
        <div className="mt-5 h-1.5 bg-white/20 rounded-full overflow-hidden">
          <div 
            className="h-full bg-white rounded-full transition-all duration-500 ease-out" 
            style={{ width: `${Math.min(parseInt(value) || 0, 100)}%` }} 
          />
        </div>
      )}
    </div>
  );
};

const EnhancedDashboard: React.FC = () => {
  const { 
    userProfile, 
    businessProfile, 
    refreshAll, 
    userProfileLoading, 
    businessProfileLoading,
    fetchProfileAnalysis,
    profileState,
    setupPrompts,
    platformRecommendations,
    enrichProfile,
    acceptAISuggestion,
    dismissPrompt,
    connectPlatform,
    assistantLoading
  } = useProfile();
  const [showProfileEditor, setShowProfileEditor] = useState(false);
  const [showBusinessEditor, setShowBusinessEditor] = useState(false);
  const [showSocialEditor, setShowSocialEditor] = useState(false);
  const [editingSocialProfile, setEditingSocialProfile] = useState<Record<string, unknown> | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Load initial data and AI profile analysis
  useEffect(() => {
    refreshAll();
    fetchProfileAnalysis();
  }, [refreshAll, fetchProfileAnalysis]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.relative') && !target.closest('.group')) {
        setShowNotifications(false);
        setShowUserMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshAll();
    } finally {
      setRefreshing(false);
    }
  };

  const getGrowthStatus = () => {
    const completionScore = businessProfile?.profile_completeness_score || 0;
    if (completionScore >= 80) return { status: 'Excellent', icon: <TrendingUp className="w-4 h-4 text-rainbow-emerald" />, color: 'bg-rainbow-emerald' };
    if (completionScore >= 50) return { status: 'Good', icon: <TrendingUp className="w-4 h-4 text-rainbow-cyan" />, color: 'bg-rainbow-cyan' };
    if (completionScore >= 30) return { status: 'Needs Attention', icon: <AlertTriangle className="w-4 h-4 text-rainbow-amber" />, color: 'bg-rainbow-amber' };
    return { status: 'Critical', icon: <AlertTriangle className="w-4 h-4 text-destructive" />, color: 'bg-destructive' };
  };

  const growthStatus = getGrowthStatus();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const userName = userProfile?.full_name || userProfile?.first_name || 'Business Owner';

  return (
    <div className="space-y-6">
      {/* Header with User Menu and Notifications */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold font-display text-foreground tracking-tight">
              {getGreeting()}, {userName}!
            </h1>
            {/* User Avatar */}
            <div className="relative group">
              <button
                type="button"
                className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-brand hover:scale-105 transition-all cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
                onClick={() => setShowUserMenu(!showUserMenu)}
                aria-label="Toggle user options menu"
              >
                {userName.charAt(0).toUpperCase()}
              </button>
              {/* User Menu Dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-52 bg-popover rounded-xl shadow-xl border border-border z-50 animate-scale-in">
                  <div className="p-4 border-b border-border">
                    <p className="font-bold text-foreground truncate">{userName}</p>
                    <p className="text-xs text-muted-foreground truncate">{userProfile?.email}</p>
                  </div>
                  <div className="py-2">
                    <button 
                      className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" 
                      onClick={() => setShowProfileEditor(true)}
                    >
                      <User className="w-4 h-4 text-primary" /> Profile
                    </button>
                    <button className="w-full text-left px-4 py-2 text-sm text-foreground hover:bg-muted flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                      <Settings className="w-4 h-4 text-muted-foreground" /> Settings
                    </button>
                  </div>
                  <div className="p-2 border-t border-border">
                    <button className="w-full text-left px-4 py-2 text-sm text-destructive hover:bg-destructive/10 rounded-lg flex items-center gap-2 font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                      <LogOut className="w-4 h-4" /> Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          <p className="text-muted-foreground mt-1 text-sm">
            Here is your SME growth overview and verified business diagnostics.
          </p>
          {/* Quick Stats Badges */}
          <div className="flex items-center gap-3 mt-4 flex-wrap">
            {userProfile?.profile_completion_percentage && (
              <Badge variant={userProfile.profile_completion_percentage >= 80 ? 'success' : userProfile.profile_completion_percentage >= 50 ? 'warning' : 'error'} className="flex items-center gap-1 font-mono text-xs">
                <User className="w-3 h-3" /> Profile: {userProfile.profile_completion_percentage}%
              </Badge>
            )}
            {businessProfile?.profile_completeness_score && (
              <Badge variant={businessProfile.profile_completeness_score >= 80 ? 'success' : businessProfile.profile_completeness_score >= 50 ? 'warning' : 'error'} className="flex items-center gap-1.5 font-mono text-xs">
                <span className={cn("w-2 h-2 rounded-full", growthStatus.color)}></span>
                Business: {businessProfile.profile_completeness_score.toFixed(0)}% • {growthStatus.status}
              </Badge>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Notifications */}
          <div className="relative">
            <button 
              className="w-10 h-10 bg-muted hover:bg-muted/80 rounded-xl flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors relative focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              onClick={() => setShowNotifications(!showNotifications)}
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full flex items-center justify-center">3</span>
            </button>
            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-72 bg-popover rounded-xl shadow-xl border border-border z-50 animate-scale-in overflow-hidden">
                <div className="p-4 border-b border-border">
                  <h4 className="font-bold text-foreground text-sm">Notifications</h4>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {[1, 2, 3].map((item) => (
                    <div key={item} className="p-3 border-b border-border/50 hover:bg-muted/50 cursor-pointer">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0 text-primary">
                          <CheckCircle className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-foreground">New AI insights available</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Your growth analysis has been refreshed with recommendations</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-2 border-t border-border">
                  <button className="w-full text-center px-4 py-2 text-xs text-primary hover:underline font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded">
                    View All Notifications
                  </button>
                </div>
              </div>
            )}
          </div>
          
          <Button
            size="sm"
            variant="outline"
            onClick={handleRefresh}
            loading={refreshing}
            className="border-primary/30 text-primary hover:bg-primary/10 hover:text-primary flex items-center gap-2 rounded-xl focus-visible:ring-2 focus-visible:ring-ring"
          >
            <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Quick Stats with Rainbow Rotation */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <EnhancedStatCard 
          title="Profile Completion"
          value={`${userProfile?.profile_completion_percentage || 0}%`}
          trend="up"
          trendValue="5%"
          icon={<User className="w-5 h-5 text-white" />}
          gradient="from-primary to-primary-700"
          tooltip="Complete your profile to unlock verified business analytics"
        />

        <EnhancedStatCard 
          title="Business Score"
          value={`${businessProfile?.profile_completeness_score?.toFixed(0) || 0}%`}
          trend={growthStatus.status === 'Excellent' ? 'up' : growthStatus.status === 'Good' ? 'stable' : 'down'}
          trendValue={growthStatus.status === 'Excellent' ? '10%' : growthStatus.status === 'Good' ? '5%' : '-3%'}
          icon={growthStatus.icon}
          gradient="from-rainbow-cyan to-cyan-700"
          tooltip={growthStatus.status === 'Excellent' ? 'Excellent! Your business is well-positioned for growth.' : 
                   growthStatus.status === 'Good' ? 'Good progress! Consider completing more sections for better insights.' : 
                   'Needs attention! Complete your business profile for better AI recommendations.'}
        />

        <EnhancedStatCard 
          title="Social Profiles"
          value={`${userProfile?.number_of_businesses || 0}`}
          trend="up"
          trendValue="2"
          icon={<Share2 className="w-5 h-5 text-white" />}
          gradient="from-rainbow-pink to-pink-700"
          tooltip="Connect more social profiles for multi-platform analytics"
        />

        <EnhancedStatCard 
          title="Active Insights"
          value={userProfile?.owns_business ? 'Yes' : 'No'}
          trend="stable"
          icon={<Sparkles className="w-5 h-5 text-white" />}
          gradient="from-rainbow-emerald to-emerald-700"
          tooltip={userProfile?.owns_business ? 'AI insights are actively analyzing your business data' : 'Set up your business profile to enable AI insights'}
        />
      </div>

      {/* AI Profile Assistant */}
      {(setupPrompts.length > 0 || platformRecommendations.length > 0) && (
        <AIProfileAssistant
          profileState={profileState}
          setupPrompts={setupPrompts}
          platformRecommendations={platformRecommendations}
          loading={assistantLoading}
          onEnrichProfile={enrichProfile}
          onAcceptSuggestion={acceptAISuggestion}
          onDismissPrompt={dismissPrompt}
          onConnectPlatform={connectPlatform}
        />
      )}

      {/* Smart Empty States */}
      {userProfileLoading && businessProfileLoading && setupPrompts.length === 0 && (
        <SmartEmptyState
          type="user_profile"
          state="loading"
          primaryAction={{
            label: "AI is analyzing your profile...",
            onClick: () => {},
            loading: true
          }}
        />
      )}

      {!userProfile && !userProfileLoading && setupPrompts.length === 0 && (
        <SmartEmptyState
          type="user_profile"
          state="not_started"
          message="Let's set up your profile to unlock AI-powered insights"
          primaryAction={{
            label: "Start AI Profile Setup",
            onClick: () => fetchProfileAnalysis()
          }}
        />
      )}

      {!businessProfile && !businessProfileLoading && setupPrompts.length === 0 && (
        <SmartEmptyState
          type="business_profile"
          state="not_started"
          message="Tell us about your business to enable AI analysis"
          primaryAction={{
            label: "Add Business Information",
            onClick: () => setShowBusinessEditor(true)
          }}
        />
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="group">
          <UserProfileCard onEdit={() => setShowProfileEditor(true)} />
        </div>

        <div className="group">
          <BusinessProfilePanel onEdit={() => setShowBusinessEditor(true)} />
        </div>
      </div>

      {/* Social Media Section */}
      <div className="group">
        <SocialMediaSection 
          onAdd={() => { setEditingSocialProfile(null); setShowSocialEditor(true); }} 
          onEdit={(profile) => { setEditingSocialProfile(profile as unknown as Record<string, unknown>); setShowSocialEditor(true); }} 
        />
      </div>

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="group">
          <ProfileInsights />
        </div>

        <div className="group">
          <ActivityTimeline limit={10} />
        </div>
      </div>

      {/* Editors */}
      {showProfileEditor && (
        <ProfileEditor
          isOpen={showProfileEditor}
          onClose={() => setShowProfileEditor(false)}
          profileType="user"
        />
      )}

      {showBusinessEditor && (
        <ProfileEditor
          isOpen={showBusinessEditor}
          onClose={() => setShowBusinessEditor(false)}
          profileType="business"
        />
      )}

      {showSocialEditor && (
        <SocialMediaEditor
          isOpen={showSocialEditor}
          onClose={() => setShowSocialEditor(false)}
          editingProfile={editingSocialProfile}
        />
      )}
    </div>
  );
};

export default EnhancedDashboard;
