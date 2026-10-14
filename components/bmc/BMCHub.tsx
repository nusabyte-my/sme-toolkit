/**
 * BMCHub Component
 * Displays hub for business model canvas with multiple modes
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState } from 'react';
import {
  MessageSquare,
  Wand2,
  ArrowRight,
  Sparkles,
  LayoutGrid,
  TrendingUp
} from 'lucide-react';
import ConversationalChat from './ConversationalChat';
import EnhancedBMCWizard from './EnhancedBMCWizard';
import { BusinessCanvasData, ChatSession, GrowthScore } from '../../types';

interface BMCHubProps {
  onCanvasGenerated: (canvas: BusinessCanvasData) => void;
  onAnalysisComplete?: (growthScore: GrowthScore) => void;
}

type BMCMode = 'select' | 'chat' | 'wizard' | 'result';

const BMCHub: React.FC<BMCHubProps> = ({ onCanvasGenerated, onAnalysisComplete }) => {
  const [mode, setMode] = useState<BMCMode>('select');
  const [session, setSession] = useState<ChatSession | null>(null);
  const [wizardPrefill, setWizardPrefill] = useState<Record<string, string>>({});
  const [generatedCanvas, setGeneratedCanvas] = useState<BusinessCanvasData | null>(null);

  const handleStartChat = () => {
    setMode('chat');
  };

  const handleQuickWizard = () => {
    setWizardPrefill({});
    setMode('wizard');
  };

  const handleChatComplete = (chatSession: ChatSession, prefill: Record<string, string>) => {
    setSession(chatSession);
    setWizardPrefill(prefill);
    setMode('wizard');
  };

  const handleWizardComplete = (canvas: BusinessCanvasData) => {
    setGeneratedCanvas(canvas);
    onCanvasGenerated(canvas);
    setMode('result');
  };

  const handleStartOver = () => {
    setMode('select');
    setSession(null);
    setWizardPrefill({});
    setGeneratedCanvas(null);
  };

  if (mode === 'chat') {
    return (
      <ConversationalChat
        onComplete={handleChatComplete}
        onBack={() => setMode('select')}
      />
    );
  }

  if (mode === 'wizard') {
    return (
      <EnhancedBMCWizard
        prefillData={wizardPrefill}
        sessionId={session?.id}
        onComplete={handleWizardComplete}
        onBack={() => session ? setMode('chat') : setMode('select')}
      />
    );
  }

  // Selection mode
  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-[#1863d6] to-[#151983] rounded-2xl mb-4 shadow-lg shadow-[#1863d6]/30">
          <LayoutGrid className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-[#0f172a] mb-2">
          Business Model Canvas
        </h1>
        <p className="text-[#64748b] max-w-xl mx-auto">
          Build your business model with AI-powered guidance. Choose how you'd like to get started.
        </p>
      </div>

      {/* Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Conversational Option */}
        <button
          onClick={handleStartChat}
          className="group relative p-8 bg-white rounded-2xl border-2 border-[#e2e8f0] hover:border-[#1863d6] hover:shadow-lg transition-all duration-200 text-left"
        >
          <div className="absolute top-4 right-4">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#1863d6]/10 text-[#1863d6]">
              Recommended
            </span>
          </div>

          <div className="w-14 h-14 bg-[#1863d6]/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-[#1863d6]/20 transition-colors">
            <MessageSquare className="w-7 h-7 text-[#1863d6]" />
          </div>

          <h3 className="text-xl font-semibold text-[#0f172a] mb-2">
            Start with a Conversation
          </h3>

          <p className="text-[#64748b] mb-4">
            Chat with our AI consultant to discover and articulate your business model.
            Perfect if you're still refining your ideas.
          </p>

          <div className="flex items-center text-[#1863d6] font-medium group-hover:translate-x-1 transition-transform">
            Start Chatting
            <ArrowRight className="w-4 h-4 ml-2" />
          </div>

          <div className="mt-4 pt-4 border-t border-[#e2e8f0]">
            <div className="flex items-center gap-4 text-sm text-[#94a3b8]">
              <span className="flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                AI-guided discovery
              </span>
              <span className="flex items-center gap-1">
                <TrendingUp className="w-4 h-4" />
                Personalized suggestions
              </span>
            </div>
          </div>
        </button>

        {/* Quick Wizard Option */}
        <button
          onClick={handleQuickWizard}
          className="group p-8 bg-white rounded-2xl border-2 border-[#e2e8f0] hover:border-[#151983] hover:shadow-lg transition-all duration-200 text-left"
        >
          <div className="w-14 h-14 bg-[#151983]/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-[#151983]/20 transition-colors">
            <Wand2 className="w-7 h-7 text-[#151983]" />
          </div>

          <h3 className="text-xl font-semibold text-[#0f172a] mb-2">
            Quick Canvas Builder
          </h3>

          <p className="text-[#64748b] mb-4">
            Jump straight into a guided wizard to build your canvas step by step.
            Best if you already know your business model.
          </p>

          <div className="flex items-center text-[#151983] font-medium group-hover:translate-x-1 transition-transform">
            Start Building
            <ArrowRight className="w-4 h-4 ml-2" />
          </div>

          <div className="mt-4 pt-4 border-t border-[#e2e8f0]">
            <div className="flex items-center gap-4 text-sm text-[#94a3b8]">
              <span className="flex items-center gap-1">
                <LayoutGrid className="w-4 h-4" />
                Step-by-step wizard
              </span>
              <span className="flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                AI suggestions
              </span>
            </div>
          </div>
        </button>
      </div>

      {/* Info Section */}
      <div className="mt-12 p-6 bg-gradient-to-r from-[#f8fafc] to-[#f1f5f9] rounded-xl">
        <h4 className="font-semibold text-[#0f172a] mb-3">
          What is a Business Model Canvas?
        </h4>
        <p className="text-[#64748b] text-sm mb-4">
          The Business Model Canvas is a strategic management template for developing new or documenting
          existing business models. It covers 9 key building blocks:
        </p>
        <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
          {[
            'Key Partners',
            'Key Activities',
            'Key Resources',
            'Value Propositions',
            'Customer Relationships',
            'Channels',
            'Customer Segments',
            'Cost Structure',
            'Revenue Streams'
          ].map((block) => (
            <span
              key={block}
              className="px-2 py-1 bg-white rounded text-xs text-[#64748b] text-center shadow-sm"
            >
              {block}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BMCHub;
