/**
 * ConversationalChat Component
 * Displays conversational chat for BMC discovery
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  ArrowLeft,
  Sparkles,
  Check,
  Loader2,
  MessageSquare,
  ArrowRight
} from 'lucide-react';
import { ChatMessage, ChatSession } from '../../types';

interface ConversationalChatProps {
  onComplete: (session: ChatSession, wizardPrefill: Record<string, string>) => void;
  onBack: () => void;
}

import { authenticatedFetch } from '../../services/apiClient';

const ConversationalChat: React.FC<ConversationalChatProps> = ({ onComplete, onBack }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [extractedContext, setExtractedContext] = useState<Record<string, unknown>>({});
  const [readyForWizard, setReadyForWizard] = useState(false);
  const [wizardPrefill, setWizardPrefill] = useState<Record<string, string>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize session
  useEffect(() => {
    initializeSession();
  }, []);


  const initializeSession = async () => {
    try {
      const response = await authenticatedFetch('/api/v1/bmc/session', 'POST', {});

      if (!response.ok) {
        throw new Error('Failed to create session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setMessages([{
        role: 'assistant',
        content: data.greeting,
        timestamp: new Date().toISOString()
      }]);
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to initialize session:', error);
      // Fallback greeting
      setMessages([{
        role: 'assistant',
        content: "Hello! I'm here to help you build your Business Model Canvas. Tell me about your business idea - what problem are you solving and for whom?",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsInitializing(false);
    }
  };

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setSuggestions([]);

    try {
      const response = await authenticatedFetch('/api/v1/bmc/message', 'POST', {
        session_id: sessionId,
        message,
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSuggestions(data.suggestions || []);
      setExtractedContext(data.extracted_context || {});
      setReadyForWizard(data.ready_for_wizard || false);

      if (data.wizard_prefill) {
        setWizardPrefill(data.wizard_prefill);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I apologize, but I'm having trouble processing that. Could you try again?",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  const handleProceedToWizard = () => {
    const session: ChatSession = {
      id: sessionId || '',
      messages: messages,
      extracted_context: extractedContext,
      phase: 'confirmation',
      ready_for_wizard: true,
      wizard_prefill: wizardPrefill
    };
    onComplete(session, wizardPrefill);
  };

  // Progress indicator
  const getProgress = () => {
    const bmcBlocks = [
      'keyPartners', 'keyActivities', 'keyResources', 'valuePropositions',
      'customerRelationships', 'channels', 'customerSegments', 'costStructure', 'revenueStreams'
    ];
    const filled = bmcBlocks.filter(block => {
      const data = extractedContext[block] as { items?: string[] } | undefined;
      return data?.items && data.items.length > 0;
    }).length;
    return (filled / 9) * 100;
  };

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-[#1863d6] mx-auto mb-4" />
          <p className="text-[#64748b]">Starting your BMC journey...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-[#e2e8f0] bg-white">
        <button
          onClick={onBack}
          className="flex items-center text-[#64748b] hover:text-[#0f172a]"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-[#1863d6]" />
            <span className="font-medium text-[#0f172a]">BMC Discovery</span>
          </div>

          {/* Progress */}
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-[#e2e8f0] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#1863d6] transition-all duration-500"
                style={{ width: `${getProgress()}%` }}
              />
            </div>
            <span className="text-sm text-[#64748b]">{Math.round(getProgress())}%</span>
          </div>
        </div>

        {readyForWizard && (
          <button
            onClick={handleProceedToWizard}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg hover:shadow-md transition-all"
          >
            Continue to Canvas
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#f8fafc]">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-[#1863d6] to-[#151983] text-white'
                  : 'backdrop-blur-sm bg-white/80 shadow-sm border border-[#b6cbe1]/30'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className="w-4 h-4 text-[#1863d6]" />
                  <span className="text-xs font-medium text-[#1863d6]">BMC Advisor</span>
                </div>
              )}
              <p className={`text-sm ${message.role === 'user' ? 'text-white' : 'text-[#334155]'}`}>
                {message.content}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="backdrop-blur-sm bg-white/80 rounded-2xl px-4 py-3 shadow-sm border border-[#b6cbe1]/30">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-[#1863d6]" />
                <span className="text-sm text-[#64748b]">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && !isLoading && (
        <div className="px-4 py-2 bg-white border-t border-[#e2e8f0]">
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-xs text-[#94a3b8] whitespace-nowrap">Suggestions:</span>
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="flex items-center gap-1 px-3 py-1.5 bg-[#1863d6]/10 hover:bg-[#1863d6]/20 text-[#1863d6] text-sm rounded-full whitespace-nowrap transition-colors"
              >
                <Sparkles className="w-3 h-3" />
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-[#e2e8f0]">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Tell me about your business..."
              className="w-full px-4 py-3 pr-12 border border-[#e2e8f0] rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-[#1863d6] focus:border-transparent"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="p-3 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-xl hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {readyForWizard && (
          <div className="mt-3 p-3 bg-[#10b981]/10 border border-[#10b981]/20 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-[#10b981]" />
              <span className="text-sm text-[#10b981]">
                Great progress! You have enough context to build your canvas.
              </span>
            </div>
            <button
              onClick={handleProceedToWizard}
              className="px-4 py-1.5 bg-[#10b981] text-white text-sm rounded-lg hover:bg-[#059669]"
            >
              Continue
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default ConversationalChat;
