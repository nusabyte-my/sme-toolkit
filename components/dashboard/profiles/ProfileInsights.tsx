/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Profile insights & AI recommendations */
import React, { useState } from 'react';
import Card from '../../ui/Card';
import Badge from '../../ui/Badge';
import Button from '../../ui/Button';
import { useProfile } from '../../../contexts/ProfileContext';
import { Lightbulb, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-react';

interface ProfileInsightsProps {
  onGenerate?: () => void;
}

type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info' | 'indigo';

const ProfileInsights: React.FC<ProfileInsightsProps> = ({ onGenerate }) => {
  const { insights, insightsLoading, insightsError, fetchInsights, generateNewInsights, provideInsightFeedback } = useProfile();
  const [filter, setFilter] = useState<'all' | 'growth' | 'engagement' | 'optimization'>('all');
  const [expandedInsight, setExpandedInsight] = useState<string | null>(null);

  React.useEffect(() => {
    if (insights.length === 0 && !insightsLoading && !insightsError) {
      fetchInsights();
    }
  }, [insights.length, insightsLoading, insightsError, fetchInsights]);

  const filteredInsights = insights.filter(insight => {
    if (filter === 'all') return true;
    return insight.insight_type?.toLowerCase() === filter || insight.insight_category?.toLowerCase() === filter;
  });

  const handleFeedback = async (insightId: string, feedback: 'helpful' | 'not_helpful') => {
    try {
      await provideInsightFeedback(insightId, feedback);
    } catch {
      // Feedback submission handled gracefully
    }
  };

  const getPriorityVariant = (priority?: string): BadgeVariant => {
    switch (priority?.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getConfidenceVariant = (confidence?: number): BadgeVariant => {
    if (!confidence) return 'default';
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'info';
    return 'warning';
  };

  if (insightsLoading && insights.length === 0) {
    return (
      <Card className="bg-card border-border rounded-2xl p-6 shadow-sm">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-muted rounded w-1/3 mb-4" />
          <div className="h-24 bg-muted rounded-xl w-full" />
          <div className="h-24 bg-muted rounded-xl w-full" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="backdrop-blur-sm bg-card border border-border rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold font-display text-foreground">AI Insights</h3>
          <p className="text-sm text-muted-foreground font-mono">
            {filteredInsights.length} insight{filteredInsights.length !== 1 ? 's' : ''} available
          </p>
        </div>
        <Button size="sm" onClick={onGenerate || generateNewInsights} loading={insightsLoading} className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-brand focus-visible:ring-2 focus-visible:ring-ring">
          <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Generate New
        </Button>
      </div>

      {/* Filters — only when there is something to filter */}
      {!insightsError && insights.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-6">
          {(['all', 'growth', 'engagement', 'optimization'] as const).map((f) => (
            <Button
              key={f}
              size="sm"
              variant={filter === f ? 'primary' : 'outline'}
              onClick={() => setFilter(f)}
              className="rounded-lg text-xs font-mono capitalize focus-visible:ring-2 focus-visible:ring-ring"
            >
              {f}
            </Button>
          ))}
        </div>
      )}

      {insightsError && (
        <div role="alert" className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 mb-4">
          <p className="text-destructive text-sm font-semibold">We couldn't load your AI insights right now.</p>
          <p className="text-muted-foreground text-xs mt-0.5">Check your connection, then try again — your data is safe.</p>
          <Button size="sm" variant="outline" onClick={() => void fetchInsights()} className="mt-2 rounded-lg">
            Try again
          </Button>
        </div>
      )}

      {!insightsError && (filteredInsights.length === 0 ? (
        <div className="text-center py-12">
          <Lightbulb className="w-12 h-12 text-primary mx-auto mb-4" />
          <p className="text-muted-foreground mb-4 text-sm font-medium">
            {filter === 'all' ? 'No insights available yet' : `No ${filter} insights available`}
          </p>
          <Button size="sm" onClick={onGenerate || generateNewInsights} className="rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground">
            Generate Insights
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredInsights.map((insight) => {
            const isExpanded = expandedInsight === insight.id;
            const priorityVariant = getPriorityVariant(insight.priority);
            const confidenceVariant = getConfidenceVariant(insight.confidence_score);

            return (
              <div
                key={insight.id}
                className="bg-muted/30 rounded-xl p-4 border border-border hover:border-primary/40 hover:shadow-xs transition-all"
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge variant={priorityVariant} size="sm">
                        {insight.priority || 'Normal'}
                      </Badge>
                      {insight.insight_type && (
                        <Badge variant="info" size="sm">
                          {insight.insight_type}
                        </Badge>
                      )}
                      {insight.confidence_score && (
                        <Badge variant={confidenceVariant} size="sm">
                          {insight.confidence_score.toFixed(0)}% confidence
                        </Badge>
                      )}
                    </div>
                    <h4 className="font-semibold text-foreground text-sm">{insight.title}</h4>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setExpandedInsight(isExpanded ? null : insight.id)}
                    className="text-xs text-muted-foreground hover:text-foreground flex-shrink-0"
                  >
                    {isExpanded ? 'Less' : 'Details'}
                  </Button>
                </div>

                {/* Description */}
                <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                  {insight.description}
                </p>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="space-y-3 pt-3 border-t border-border/70">
                    {/* Recommendations from insight_data */}
                    {Array.isArray(insight.insight_data?.recommendations) && (insight.insight_data.recommendations as unknown[]).length > 0 && (
                      <div>
                        <p className="text-xs font-mono font-semibold uppercase text-foreground mb-1.5">Recommendations</p>
                        <ul className="list-disc list-inside space-y-1">
                          {(insight.insight_data.recommendations as string[]).map((rec, index) => (
                            <li key={index} className="text-xs text-muted-foreground">
                              <span className="text-foreground">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action Items */}
                    {insight.action_items && insight.action_items.length > 0 && (
                      <div>
                        <p className="text-xs font-mono font-semibold uppercase text-foreground mb-1.5">Action Items</p>
                        <div className="space-y-1">
                          {insight.action_items.map((item, index) => (
                            <div key={index} className="flex items-center space-x-2 text-xs text-foreground">
                              <span className="w-1.5 h-1.5 bg-primary rounded-full" />
                              <span>{item}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    {(insight.estimated_effort || insight.estimated_timeframe) && (
                      <div className="flex items-center space-x-4 text-xs font-mono text-muted-foreground">
                        {insight.estimated_effort && (
                          <span>Effort: <strong className="text-foreground">{insight.estimated_effort}</strong></span>
                        )}
                        {insight.estimated_timeframe && (
                          <span>Timeframe: <strong className="text-foreground">{insight.estimated_timeframe}</strong></span>
                        )}
                      </div>
                    )}

                    {/* User Notes */}
                    {insight.user_notes && (
                      <div className="bg-primary/10 rounded-xl p-3 border border-primary/20">
                        <p className="text-xs font-mono font-medium text-primary mb-1">Your Notes</p>
                        <p className="text-xs text-foreground">{insight.user_notes}</p>
                      </div>
                    )}

                    {/* Generated At */}
                    <p className="text-[11px] text-muted-foreground font-mono">
                      Generated: {new Date(insight.generated_at).toLocaleString()}
                    </p>
                  </div>
                )}

                {/* Feedback Actions */}
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/70">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">Was this helpful?</span>
                    <Button
                      size="sm"
                      variant={insight.user_feedback === 'helpful' ? 'primary' : 'outline'}
                      onClick={() => handleFeedback(insight.id, 'helpful')}
                      className="text-xs rounded-lg px-2.5 py-1 hover:border-rainbow-emerald hover:text-rainbow-emerald"
                    >
                      <ThumbsUp className="w-3.5 h-3.5 mr-1 inline" /> Yes
                    </Button>
                    <Button
                      size="sm"
                      variant={insight.user_feedback === 'not_helpful' ? 'primary' : 'outline'}
                      onClick={() => handleFeedback(insight.id, 'not_helpful')}
                      className="text-xs rounded-lg px-2.5 py-1 hover:border-destructive hover:text-destructive"
                    >
                      <ThumbsDown className="w-3.5 h-3.5 mr-1 inline" /> No
                    </Button>
                  </div>
                  {insight.is_actionable && (
                    <Badge variant="success" size="sm">
                      Actionable
                    </Badge>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ))}
    </Card>
  );
};

export default ProfileInsights;
