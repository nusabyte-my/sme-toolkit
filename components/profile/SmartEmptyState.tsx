import React, { useState } from 'react';
import {
  Sparkles, ArrowRight, RefreshCw, CheckCircle,
  AlertCircle, Lightbulb, Share2, Zap, TrendingUp,
  Brain, Target, Settings, X
} from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';

export interface SmartEmptyStateConfig {
  type: 'user_profile' | 'business_profile' | 'social_media';
  state: 'not_started' | 'loading' | 'error' | 'awaiting_data' | 'ready';
  message?: string;
  suggestions?: string[];
  primaryAction?: {
    label: string;
    onClick: () => void;
    loading?: boolean;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  aiMessage?: string;
  aiConfidence?: number;
  showRefresh?: boolean;
  onRefresh?: () => void;
}

const SmartEmptyState: React.FC<SmartEmptyStateConfig> = ({
  type,
  state,
  message,
  suggestions = [],
  primaryAction,
  secondaryAction,
  aiMessage,
  aiConfidence,
  showRefresh = true,
  onRefresh
}) => {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) {
    return (
      <Card className="h-full">
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Settings className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground mb-3">
              This section has been dismissed
            </p>
            <Button size="sm" variant="outline" onClick={() => setDismissed(false)}>
              Restore
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  const getConfig = () => {
    switch (type) {
      case 'user_profile':
        return {
          icon: <Target className="w-9 h-9" />,
          gradient: 'from-primary/5 to-accent/10',
          borderColor: 'border-primary/25',
          iconColor: 'text-primary',
          defaultTitle: 'User Profile Not Set Up',
          defaultMessage: 'Complete your user profile to personalize your experience',
          defaultSuggestions: [
            'Add your name and contact information',
            'Set your preferences and goals',
            'Upload a profile picture'
          ]
        };
      case 'business_profile':
        return {
          icon: <TrendingUp className="w-9 h-9" />,
          gradient: 'from-rainbow-emerald/5 to-rainbow-cyan/10',
          borderColor: 'border-rainbow-emerald/25',
          iconColor: 'text-rainbow-emerald',
          defaultTitle: 'Business Profile Not Set Up',
          defaultMessage: 'Tell us about your business to unlock AI-powered insights',
          defaultSuggestions: [
            'Add your company name and industry',
            'Specify your business type and stage',
            'Connect your social media accounts'
          ]
        };
      case 'social_media':
        return {
          icon: <Share2 className="w-9 h-9" />,
          gradient: 'from-rainbow-pink/5 to-primary/10',
          borderColor: 'border-rainbow-pink/25',
          iconColor: 'text-rainbow-pink',
          defaultTitle: 'No Social Media Connected',
          defaultMessage: 'Connect your social media accounts to track performance and audience',
          defaultSuggestions: [
            'Connect LinkedIn for B2B insights',
            'Add Instagram for visual content analysis',
            'Sync Twitter for real-time engagement'
          ]
        };
      default:
        return {
          icon: <Sparkles className="w-9 h-9" />,
          gradient: 'from-muted to-background',
          borderColor: 'border-border',
          iconColor: 'text-muted-foreground',
          defaultTitle: 'Not Configured',
          defaultMessage: 'This section requires setup',
          defaultSuggestions: []
        };
    }
  };

  const config = getConfig();

  const renderContent = () => {
    switch (state) {
      case 'loading':
        return (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <Brain className="w-10 h-10 text-primary animate-pulse mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Analyzing your profile...
            </h3>
            <p className="text-sm text-muted-foreground text-center">
              Our AI is preparing personalized recommendations
            </p>
          </div>
        );

      case 'error':
        return (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <AlertCircle className="w-10 h-10 text-destructive mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Unable to load data
            </h3>
            <p className="text-sm text-muted-foreground text-center mb-4">
              {message || 'An error occurred while loading your profile'}
            </p>
            {onRefresh && (
              <Button
                size="sm"
                variant="outline"
                onClick={onRefresh}
                className="border-destructive/40 text-destructive hover:bg-destructive/10"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            )}
          </div>
        );

      case 'awaiting_data':
        return (
          <div className="p-6 space-y-6">
            <div className="text-center">
              <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${config.gradient} flex items-center justify-center mb-4 ${config.borderColor} border-2`}>
                {config.icon}
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">
                {config.defaultTitle}
              </h3>
              <p className="text-sm text-muted-foreground">
                {message || config.defaultMessage}
              </p>
            </div>

            {aiMessage && (
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                        AI Suggestion
                      </span>
                      {aiConfidence && (
                        <Badge variant="info" className="text-xs">
                          {Math.round(aiConfidence * 100)}% confidence
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {aiMessage}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {suggestions.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  <Lightbulb className="w-4 h-4" />
                  Recommended Steps
                </div>
                <div className="space-y-2">
                  {suggestions.map((suggestion, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                    >
                      <div className={`w-6 h-6 rounded-full ${config.iconColor} bg-background border border-border flex items-center justify-center flex-shrink-0`}>
                        <span className="text-sm font-bold">{idx + 1}</span>
                      </div>
                      <p className="text-sm text-foreground/80 flex-1">
                        {suggestion}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center gap-3 pt-2">
              {primaryAction && (
                <Button
                  onClick={primaryAction.onClick}
                  disabled={primaryAction.loading}
                  className="flex-1"
                >
                  {primaryAction.loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      {primaryAction.label}
                    </>
                  )}
                </Button>
              )}
              {secondaryAction && (
                <Button
                  variant="outline"
                  onClick={secondaryAction.onClick}
                  className="flex-1"
                >
                  {secondaryAction.label}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        );

      case 'ready':
        return (
          <div className="space-y-4">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-rainbow-emerald/5 to-rainbow-cyan/10 flex items-center justify-center mb-4 border-2 border-rainbow-emerald/25">
                <CheckCircle className="w-8 h-8 text-rainbow-emerald" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">
                Ready to Go!
              </h3>
              <p className="text-sm text-muted-foreground">
                {message || 'Your profile is configured and ready to use'}
              </p>
            </div>

            {primaryAction && (
              <Button
                onClick={primaryAction.onClick}
                className="w-full bg-gradient-cta text-white font-semibold shadow-brand hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {primaryAction.label}
              </Button>
            )}
          </div>
        );

      case 'not_started':
      default:
        return (
          <div className="p-6 space-y-6">
            <div className="text-center">
              <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${config.gradient} flex items-center justify-center mb-4 ${config.borderColor} border-2`}>
                {config.icon}
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">
                {config.defaultTitle}
              </h3>
              <p className="text-sm text-muted-foreground">
                {message || config.defaultMessage}
              </p>
            </div>

            {suggestions.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  <Lightbulb className="w-4 h-4" />
                  Get Started
                </div>
                <div className="space-y-2">
                  {suggestions.slice(0, 3).map((suggestion, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg"
                    >
                      <div className={`w-6 h-6 rounded-full ${config.iconColor} bg-background border border-border flex items-center justify-center flex-shrink-0`}>
                        <span className="text-sm font-bold">{idx + 1}</span>
                      </div>
                      <p className="text-sm text-foreground/80 flex-1">
                        {suggestion}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex items-center gap-3 pt-2">
              {primaryAction && (
                <Button
                  onClick={primaryAction.onClick}
                  disabled={primaryAction.loading}
                  className="flex-1"
                >
                  {primaryAction.loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      {primaryAction.label}
                    </>
                  )}
                </Button>
              )}
              {secondaryAction && (
                <Button
                  variant="outline"
                  onClick={secondaryAction.onClick}
                  className="flex-1"
                >
                  {secondaryAction.label}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </div>
        );
    }
  };

  return (
    <Card padding="none" className={`h-full bg-gradient-to-br ${config.gradient} ${config.borderColor} border-2 relative overflow-hidden`}>
      <button
        onClick={() => setDismissed(true)}
        className="absolute top-3 right-3 p-1.5 hover:bg-white/50 dark:hover:bg-white/10 rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        title="Dismiss"
      >
        <X className="w-4 h-4 text-muted-foreground" />
      </button>
      {renderContent()}
    </Card>
  );
};

export default SmartEmptyState;
