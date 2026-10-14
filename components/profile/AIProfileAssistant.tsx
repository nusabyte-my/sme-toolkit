import React, { useState, useEffect } from 'react';
import {
  Sparkles, ArrowRight, RefreshCw, CheckCircle,
  AlertCircle, Info, X, Zap, Brain, Target,
  Lightbulb, TrendingUp, Share2
} from 'lucide-react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { ProfileSetupState } from '../../contexts/ProfileContext';

export interface SetupPrompt {
  id: string;
  type: 'critical' | 'enhancement' | 'social' | 'verification';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  value_prop: string;
  action_label: string;
  fields?: string[];
  suggested_value?: string;
  confidence_score?: number;
}

export interface PlatformRecommendation {
  platform: string;
  platform_name: string;
  icon: string;
  priority: 'high' | 'medium' | 'low';
  reason: string;
  value_prop: string;
  expected_benefits: string[];
  connection_status?: 'not_connected' | 'connecting' | 'connected' | 'error';
}

interface AIProfileAssistantProps {
  profileState: ProfileSetupState;
  setupPrompts: SetupPrompt[];
  platformRecommendations: PlatformRecommendation[];
  loading: boolean;
  onEnrichProfile: () => Promise<void>;
  onAcceptSuggestion: (suggestionId: string) => Promise<void>;
  onDismissPrompt: (promptId: string) => void;
  onConnectPlatform: (platform: string) => Promise<void>;
}

const AIProfileAssistant: React.FC<AIProfileAssistantProps> = ({
  profileState,
  setupPrompts,
  platformRecommendations,
  loading,
  onEnrichProfile,
  onAcceptSuggestion,
  onDismissPrompt,
  onConnectPlatform
}) => {
  const [dismissedPrompts, setDismissedPrompts] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<'prompts' | 'platforms'>('prompts');

  const visiblePrompts = setupPrompts.filter(p => !dismissedPrompts.has(p.id));
  const criticalPrompts = visiblePrompts.filter(p => p.type === 'critical');
  const enhancementPrompts = visiblePrompts.filter(p => p.type === 'enhancement' || p.type === 'verification');
  const socialPrompts = visiblePrompts.filter(p => p.type === 'social');

  const handleDismissPrompt = (promptId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDismissedPrompts(prev => new Set([...prev, promptId]));
    onDismissPrompt(promptId);
  };

  const handlePlatformConnect = (platform: string) => {
    onConnectPlatform(platform);
  };

  const getPromptIcon = (type: SetupPrompt['type']) => {
    switch (type) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'enhancement':
        return <Lightbulb className="w-5 h-5 text-amber-500" />;
      case 'social':
        return <Share2 className="w-5 h-5 text-blue-500" />;
      case 'verification':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <Info className="w-5 h-5 text-slate-400" />;
    }
  };

  const getPromptStyle = (type: SetupPrompt['type']) => {
    switch (type) {
      case 'critical':
        return 'border-red-200 bg-red-50/50 hover:bg-red-50';
      case 'enhancement':
        return 'border-amber-200 bg-amber-50/50 hover:bg-amber-50';
      case 'social':
        return 'border-blue-200 bg-blue-50/50 hover:bg-blue-50';
      case 'verification':
        return 'border-green-200 bg-green-50/50 hover:bg-green-50';
      default:
        return 'border-slate-200 bg-slate-50/50 hover:bg-slate-50';
    }
  };

  const getStateMessage = () => {
    switch (profileState) {
      case ProfileSetupState.NOT_STARTED:
        return {
          icon: <Sparkles className="w-6 h-6" />,
          title: "Welcome to SME Toolkit!",
          message: "Let's set up your profile to unlock AI-powered insights"
        };
      case ProfileSetupState.AI_INITIALIZING:
        return {
          icon: <Brain className="w-6 h-6 animate-pulse" />,
          title: "Analyzing your profile...",
          message: "Our AI is preparing personalized recommendations"
        };
      case ProfileSetupState.AWAITING_BUSINESS_INFO:
        return {
          icon: <Target className="w-6 h-6" />,
          title: "Tell us about your business",
          message: "Complete your business profile to get started"
        };
      case ProfileSetupState.AWAITING_SOCIAL_SYNC:
        return {
          icon: <Share2 className="w-6 h-6" />,
          title: "Connect your social media",
          message: "Sync accounts to unlock audience insights"
        };
      case ProfileSetupState.ENRICHING_DATA:
        return {
          icon: <Zap className="w-6 h-6 animate-pulse" />,
          title: "Enriching your profile...",
          message: "AI is generating personalized suggestions"
        };
      case ProfileSetupState.READY_FOR_AI:
        return {
          icon: <TrendingUp className="w-6 h-6" />,
          title: "Your profile is ready!",
          message: "AI features are now available"
        };
      case ProfileSetupState.COMPLETED:
        return {
          icon: <CheckCircle className="w-6 h-6" />,
          title: "Profile fully optimized!",
          message: "You're getting the most out of SME Toolkit"
        };
      default:
        return {
          icon: <Info className="w-6 h-6" />,
          title: "Setup in progress",
          message: "Continue to unlock all features"
        };
    }
  };

  const stateInfo = getStateMessage();

  if (loading || profileState === ProfileSetupState.AI_INITIALIZING) {
    return (
      <Card className="bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Brain className="w-16 h-16 mx-auto text-indigo-500 animate-pulse mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Analyzing your profile...
            </h3>
            <p className="text-sm text-slate-600">
              Our AI is preparing personalized recommendations
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200 overflow-hidden">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600">
                {stateInfo.icon}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  {stateInfo.title}
                </h3>
                <p className="text-sm text-slate-600">
                  {stateInfo.message}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {(visiblePrompts.length > 0 || platformRecommendations.length > 0) && (
        <Card>
          <div className="p-6 border-b border-slate-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-500" />
                <h3 className="text-lg font-semibold text-slate-900">
                  AI Recommendations
                </h3>
                <Badge variant="indigo" className="ml-2">
                  {visiblePrompts.length + platformRecommendations.length}
                </Badge>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={activeTab === 'prompts' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('prompts')}
                  className={activeTab === 'prompts' ? 'bg-indigo-600 text-white' : ''}
                >
                  Setup Steps
                </Button>
                <Button
                  variant={activeTab === 'platforms' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('platforms')}
                  className={activeTab === 'platforms' ? 'bg-indigo-600 text-white' : ''}
                >
                  Platforms
                </Button>
              </div>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'prompts' && (
              <div className="space-y-4">
                {criticalPrompts.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold text-red-600 uppercase tracking-wider">
                      Required for AI Features
                    </p>
                    {criticalPrompts.map((prompt) => (
                      <div
                        key={prompt.id}
                        className={`p-4 rounded-xl border-2 ${getPromptStyle(prompt.type)} transition-all duration-200`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {getPromptIcon(prompt.type)}
                            <div className="flex-1">
                              <h4 className="font-semibold text-slate-900 mb-1">
                                {prompt.title}
                              </h4>
                              <p className="text-sm text-slate-600 mb-2">
                                {prompt.description}
                              </p>
                              {prompt.suggested_value && (
                                <div className="flex items-center gap-2 text-xs text-slate-500 bg-white/50 rounded px-2 py-1">
                                  <Sparkles className="w-3 h-3" />
                                  <span>AI suggestion: <strong>{prompt.suggested_value}</strong></span>
                                  {prompt.confidence_score && (
                                    <span className="text-indigo-600">
                                      ({Math.round(prompt.confidence_score * 100)}% confidence)
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                          <button
                            onClick={(e) => handleDismissPrompt(prompt.id, e)}
                            className="p-1 hover:bg-white/50 rounded transition-colors"
                          >
                            <X className="w-4 h-4 text-slate-400" />
                          </button>
                        </div>
                        <div className="mt-3 flex items-center justify-between">
                          <p className="text-xs text-slate-500">
                            <Lightbulb className="w-3 h-3 inline mr-1" />
                            {prompt.value_prop}
                          </p>
                          <Button
                            size="sm"
                            onClick={() => onEnrichProfile()}
                            className="bg-indigo-600 hover:bg-indigo-700"
                          >
                            {prompt.action_label}
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {enhancementPrompts.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold text-amber-600 uppercase tracking-wider">
                      Improve AI Quality
                    </p>
                    {enhancementPrompts.map((prompt) => (
                      <div
                        key={prompt.id}
                        className={`p-4 rounded-xl border-2 ${getPromptStyle(prompt.type)} transition-all duration-200`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {getPromptIcon(prompt.type)}
                            <div className="flex-1">
                              <h4 className="font-semibold text-slate-900 mb-1">
                                {prompt.title}
                              </h4>
                              <p className="text-sm text-slate-600 mb-2">
                                {prompt.description}
                              </p>
                              {prompt.suggested_value && (
                                <div className="flex items-center gap-2 text-xs text-slate-500 bg-white/50 rounded px-2 py-1">
                                  <Sparkles className="w-3 h-3" />
                                  <span>AI suggestion: <strong>{prompt.suggested_value}</strong></span>
                                </div>
                              )}
                            </div>
                          </div>
                          <button
                            onClick={(e) => handleDismissPrompt(prompt.id, e)}
                            className="p-1 hover:bg-white/50 rounded transition-colors"
                          >
                            <X className="w-4 h-4 text-slate-400" />
                          </button>
                        </div>
                        <div className="mt-3 flex items-center justify-between">
                          <p className="text-xs text-slate-500">
                            <Lightbulb className="w-3 h-3 inline mr-1" />
                            {prompt.value_prop}
                          </p>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => prompt.suggested_value ? onAcceptSuggestion(prompt.id) : onEnrichProfile()}
                          >
                            {prompt.action_label}
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {socialPrompts.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
                      Social Media
                    </p>
                    {socialPrompts.map((prompt) => (
                      <div
                        key={prompt.id}
                        className={`p-4 rounded-xl border-2 ${getPromptStyle(prompt.type)} transition-all duration-200`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {getPromptIcon(prompt.type)}
                            <div className="flex-1">
                              <h4 className="font-semibold text-slate-900 mb-1">
                                {prompt.title}
                              </h4>
                              <p className="text-sm text-slate-600 mb-2">
                                {prompt.description}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={(e) => handleDismissPrompt(prompt.id, e)}
                            className="p-1 hover:bg-white/50 rounded transition-colors"
                          >
                            <X className="w-4 h-4 text-slate-400" />
                          </button>
                        </div>
                        <div className="mt-3 flex items-center justify-between">
                          <p className="text-xs text-slate-500">
                            <Lightbulb className="w-3 h-3 inline mr-1" />
                            {prompt.value_prop}
                          </p>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => onEnrichProfile()}
                            className="border-blue-300 text-blue-600 hover:bg-blue-50"
                          >
                            {prompt.action_label}
                            <ArrowRight className="w-4 h-4 ml-2" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {visiblePrompts.length === 0 && (
                  <div className="text-center py-8">
                    <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-3" />
                    <p className="text-sm text-slate-600">
                      All prompts completed! Your profile is well-optimized.
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'platforms' && (
              <div className="space-y-4">
                {platformRecommendations.map((recommendation) => (
                  <div
                    key={recommendation.platform}
                    className="p-4 rounded-xl border-2 border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-all duration-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center text-2xl shadow-sm">
                          {recommendation.icon}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-semibold text-slate-900">
                              {recommendation.platform_name}
                            </h4>
                            <Badge variant={
                              recommendation.priority === 'high' ? 'error' :
                              recommendation.priority === 'medium' ? 'warning' : 'success'
                            }>
                              {recommendation.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-600 mb-2">
                            {recommendation.reason}
                          </p>
                          <div className="flex flex-wrap gap-1 mb-2">
                            {recommendation.expected_benefits.map((benefit, idx) => (
                              <span
                                key={idx}
                                className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded"
                              >
                                {benefit}
                              </span>
                            ))}
                          </div>
                          <p className="text-xs text-slate-500">
                            <Lightbulb className="w-3 h-3 inline mr-1" />
                            {recommendation.value_prop}
                          </p>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handlePlatformConnect(recommendation.platform)}
                        disabled={recommendation.connection_status === 'connecting' || recommendation.connection_status === 'connected'}
                        className={
                          recommendation.connection_status === 'connected'
                            ? 'bg-green-600 hover:bg-green-700'
                            : 'bg-indigo-600 hover:bg-indigo-700'
                        }
                      >
                        {recommendation.connection_status === 'connecting' ? (
                          <>
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            Connecting...
                          </>
                        ) : recommendation.connection_status === 'connected' ? (
                          <>
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Connected
                          </>
                        ) : (
                          <>
                            <Share2 className="w-4 h-4 mr-2" />
                            Connect
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                ))}

                {platformRecommendations.length === 0 && (
                  <div className="text-center py-8">
                    <Share2 className="w-12 h-12 mx-auto text-slate-400 mb-3" />
                    <p className="text-sm text-slate-600">
                      No platform recommendations at this time.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default AIProfileAssistant;
