/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Activity timeline & event audit */
import React, { useState } from 'react';
import Card from '../../ui/Card';
import Badge from '../../ui/Badge';
import Button from '../../ui/Button';
import { useProfile } from '../../../contexts/ProfileContext';
import { 
  User, 
  Building2, 
  Share2, 
  RefreshCw, 
  Lightbulb, 
  Eye, 
  BarChart3, 
  Settings, 
  Key, 
  LogOut, 
  FileText, 
  Target, 
  Download, 
  Upload, 
  Pin,
  Laptop
} from 'lucide-react';

interface ActivityTimelineProps {
  limit?: number;
}

const renderActivityIcon = (activityType: string) => {
  switch (activityType) {
    case 'profile_update': return <User className="w-4 h-4" />;
    case 'business_update': return <Building2 className="w-4 h-4" />;
    case 'social_media_connect': return <Share2 className="w-4 h-4" />;
    case 'social_media_sync': return <RefreshCw className="w-4 h-4" />;
    case 'insight_generated': return <Lightbulb className="w-4 h-4" />;
    case 'insight_viewed': return <Eye className="w-4 h-4" />;
    case 'analytics_viewed': return <BarChart3 className="w-4 h-4" />;
    case 'settings_changed': return <Settings className="w-4 h-4" />;
    case 'login': return <Key className="w-4 h-4" />;
    case 'logout': return <LogOut className="w-4 h-4" />;
    case 'page_view': return <FileText className="w-4 h-4" />;
    case 'feature_used': return <Target className="w-4 h-4" />;
    case 'export_data': return <Download className="w-4 h-4" />;
    case 'import_data': return <Upload className="w-4 h-4" />;
    default: return <Pin className="w-4 h-4" />;
  }
};

const getActivityColor = (activityType: string) => {
  const colors: Record<string, string> = {
    profile_update: 'bg-primary/10 text-primary',
    business_update: 'bg-rainbow-emerald/10 text-rainbow-emerald',
    social_media_connect: 'bg-rainbow-pink/10 text-rainbow-pink',
    social_media_sync: 'bg-rainbow-amber/10 text-rainbow-amber',
    insight_generated: 'bg-primary/15 text-primary',
    insight_viewed: 'bg-rainbow-cyan/10 text-rainbow-cyan',
    analytics_viewed: 'bg-rainbow-blue/10 text-rainbow-blue',
    settings_changed: 'bg-muted text-muted-foreground',
    login: 'bg-rainbow-emerald/10 text-rainbow-emerald',
    logout: 'bg-destructive/10 text-destructive',
    page_view: 'bg-muted text-muted-foreground',
    feature_used: 'bg-primary/10 text-primary',
    export_data: 'bg-rainbow-emerald/10 text-rainbow-emerald',
    import_data: 'bg-rainbow-amber/10 text-rainbow-amber',
  };
  return colors[activityType] || 'bg-muted text-muted-foreground';
};

const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ limit = 10 }) => {
  const { activityLogs, activityLogsLoading, activityLogsError, fetchActivityLogs, activityLogsTotal } = useProfile();
  const [filter, setFilter] = useState<string>('all');
  const [displayLimit, setDisplayLimit] = useState(limit);

  React.useEffect(() => {
    if (activityLogs.length === 0 && !activityLogsLoading && !activityLogsError) {
      fetchActivityLogs(displayLimit);
    }
  }, [activityLogs.length, activityLogsLoading, activityLogsError, fetchActivityLogs, displayLimit]);

  const filteredLogs = filter === 'all'
    ? activityLogs
    : activityLogs.filter(log => log.activity_type === filter || log.activity_category === filter);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const handleLoadMore = () => {
    setDisplayLimit(prev => prev + 10);
    fetchActivityLogs(displayLimit + 10);
  };

  if (activityLogsLoading && activityLogs.length === 0) {
    return (
      <Card className="bg-card border-border rounded-2xl p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-muted rounded w-1/3 mb-4" />
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-start space-x-3 mb-4">
              <div className="w-8 h-8 rounded-full bg-muted flex-shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-3 bg-muted rounded w-1/2" />
                <div className="h-2 bg-muted rounded w-full" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card className="backdrop-blur-sm bg-card border border-border rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold font-display text-foreground">Activity Timeline</h3>
          <p className="text-sm text-muted-foreground font-mono">
            {filteredLogs.length} of {activityLogsTotal} events
          </p>
        </div>
        <Button size="sm" variant="outline" onClick={() => fetchActivityLogs(displayLimit)} className="border-border hover:bg-primary/10 hover:border-primary/40 hover:text-primary rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-ring">
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh
        </Button>
      </div>

      {/* Filters — only when there is something to filter */}
      {!activityLogsError && activityLogs.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-6">
          {['all', 'profile_update', 'business_update', 'social_media_sync', 'insight_generated'].map((f) => (
            <Button
              key={f}
              size="sm"
              variant={filter === f ? 'primary' : 'outline'}
              onClick={() => setFilter(f)}
              className="rounded-lg text-xs font-mono capitalize focus-visible:ring-2 focus-visible:ring-ring"
            >
              {f === 'all' ? 'All' : f.replace(/_/g, ' ')}
            </Button>
          ))}
        </div>
      )}

      {activityLogsError && (
        <div role="alert" className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 mb-4">
          <p className="text-destructive text-sm font-semibold">We couldn't load your activity history right now.</p>
          <p className="text-muted-foreground text-xs mt-0.5">Check your connection, then try again — nothing was lost.</p>
          <Button size="sm" variant="outline" onClick={() => void fetchActivityLogs(displayLimit)} className="mt-2 rounded-lg">
            Try again
          </Button>
        </div>
      )}

      {!activityLogsError && (filteredLogs.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground mb-4 text-sm">
            {filter === 'all' ? 'No activity recorded yet' : `No ${filter.replace(/_/g, ' ')} activities found`}
          </p>
          <Button size="sm" variant="outline" onClick={() => setFilter('all')} className="rounded-xl">
            Show All Activities
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredLogs.map((log) => {
            const icon = renderActivityIcon(log.activity_type);
            const colorClass = getActivityColor(log.activity_type);

            return (
              <div key={log.id} className="flex items-start space-x-3 p-2 rounded-xl hover:bg-muted/30 transition-colors">
                {/* Icon */}
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                  {icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground truncate">
                        {log.action || log.activity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                      {log.feature_name && (
                        <Badge variant="info" size="sm" className="mt-1 font-mono text-[10px]">
                          {log.feature_name}
                        </Badge>
                      )}
                    </div>
                    <span className="text-[11px] font-mono text-muted-foreground flex-shrink-0">
                      {formatTimestamp(log.created_at)}
                    </span>
                  </div>

                  {/* Additional Details */}
                  {(log.page_url || log.device_type || log.browser) && (
                    <div className="mt-1.5 space-y-0.5 text-xs text-muted-foreground">
                      {log.page_url && (
                        <p className="truncate flex items-center gap-1 font-mono text-[11px]">
                          <FileText className="w-3 h-3 flex-shrink-0 text-muted-foreground" />
                          <span>{log.page_url}</span>
                        </p>
                      )}
                      {(log.device_type || log.browser) && (
                        <p className="flex items-center gap-1 text-[11px]">
                          <Laptop className="w-3 h-3 flex-shrink-0 text-muted-foreground" />
                          <span>{log.device_type || ''} {log.browser ? `• ${log.browser}` : ''}</span>
                        </p>
                      )}
                    </div>
                  )}

                  {/* Error Details */}
                  {log.error_details && (
                    <div className="mt-2 bg-destructive/10 border border-destructive/20 rounded-lg p-2 text-destructive text-xs font-mono">
                      {log.error_details}
                    </div>
                  )}

                  {/* Metadata */}
                  {log.metadata && Object.keys(log.metadata).length > 0 && (
                    <details className="mt-2">
                      <summary className="text-xs text-primary font-mono cursor-pointer hover:underline">
                        View Details
                      </summary>
                      <div className="mt-1.5 bg-muted/40 rounded-lg p-2 border border-border">
                        <pre className="text-[10px] text-muted-foreground overflow-x-auto font-mono">
                          {JSON.stringify(log.metadata, null, 2)}
                        </pre>
                      </div>
                    </details>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ))}

      {/* Load More */}
      {filteredLogs.length < activityLogsTotal && (
        <div className="mt-6 text-center">
          <Button size="sm" variant="outline" onClick={handleLoadMore} loading={activityLogsLoading} className="rounded-xl">
            Load More Activities
          </Button>
        </div>
      )}
    </Card>
  );
};

export default ActivityTimeline;
