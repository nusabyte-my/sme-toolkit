/**
 * EnhancedBMCWizard Component
 * Displays enhanced BMC wizard with AI suggestions
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Sparkles,
  X,
  Loader2,
  LayoutGrid
} from 'lucide-react';
import { BusinessCanvasData } from '../../types';

interface WizardStep {
  id: string;
  title: string;
  description: string;
  fields: WizardField[];
}

interface WizardField {
  key: keyof BusinessCanvasData;
  label: string;
  placeholder: string;
  question: string;
}

interface EnhancedBMCWizardProps {
  prefillData?: Record<string, string>;
  sessionId?: string;
  onComplete: (canvas: BusinessCanvasData) => void;
  onBack: () => void;
}

import { authenticatedFetch } from '../../services/apiClient';

const WIZARD_STEPS: WizardStep[] = [
  {
    id: 'value',
    title: 'Value & Customers',
    description: 'Define what value you deliver and to whom',
    fields: [
      {
        key: 'valuePropositions',
        label: 'Value Propositions',
        placeholder: 'Enter each value proposition on a new line...',
        question: 'What unique value do you deliver to customers?'
      },
      {
        key: 'customerSegments',
        label: 'Customer Segments',
        placeholder: 'Enter each customer segment on a new line...',
        question: 'Who are your target customers?'
      }
    ]
  },
  {
    id: 'operations',
    title: 'Operations',
    description: 'How you create and deliver value',
    fields: [
      {
        key: 'keyActivities',
        label: 'Key Activities',
        placeholder: 'Enter each key activity on a new line...',
        question: 'What key activities does your business require?'
      },
      {
        key: 'keyResources',
        label: 'Key Resources',
        placeholder: 'Enter each key resource on a new line...',
        question: 'What resources do you need?'
      },
      {
        key: 'keyPartners',
        label: 'Key Partners',
        placeholder: 'Enter each key partner on a new line...',
        question: 'Who are your key partners and suppliers?'
      }
    ]
  },
  {
    id: 'customer',
    title: 'Customer Interface',
    description: 'How you reach and relate to customers',
    fields: [
      {
        key: 'channels',
        label: 'Channels',
        placeholder: 'Enter each channel on a new line...',
        question: 'Through which channels do you reach customers?'
      },
      {
        key: 'customerRelationships',
        label: 'Customer Relationships',
        placeholder: 'Enter each relationship type on a new line...',
        question: 'What type of relationship do customers expect?'
      }
    ]
  },
  {
    id: 'finance',
    title: 'Financial Model',
    description: 'Your revenue and cost structure',
    fields: [
      {
        key: 'revenueStreams',
        label: 'Revenue Streams',
        placeholder: 'Enter each revenue stream on a new line...',
        question: 'How will you make money?'
      },
      {
        key: 'costStructure',
        label: 'Cost Structure',
        placeholder: 'Enter each major cost on a new line...',
        question: 'What are your major costs?'
      }
    ]
  }
];

const EnhancedBMCWizard: React.FC<EnhancedBMCWizardProps> = ({
  prefillData = {},
  sessionId,
  onComplete,
  onBack
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [suggestions, setSuggestions] = useState<Record<string, string[]>>({});
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // Initialize form with prefill data
  useEffect(() => {
    if (prefillData && Object.keys(prefillData).length > 0) {
      setFormData(prefillData);
    }
  }, [prefillData]);

  // Fetch suggestions when step changes
  useEffect(() => {
    if (sessionId) {
      fetchSuggestions(WIZARD_STEPS[currentStep].id);
    }
  }, [currentStep, sessionId]);


  const fetchSuggestions = async (stepId: string) => {
    setIsLoadingSuggestions(true);
    try {
      const response = await authenticatedFetch('/api/v1/bmc/wizard/suggestions', 'POST', {
        session_id: sessionId,
        step_id: stepId,
        current_inputs: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || {});
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const handleFieldChange = (key: string, value: string) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const handleSuggestionAccept = (fieldKey: string, suggestion: string) => {
    const currentValue = formData[fieldKey] || '';
    const newValue = currentValue ? `${currentValue}\n${suggestion}` : suggestion;
    setFormData(prev => ({ ...prev, [fieldKey]: newValue }));

    // Remove accepted suggestion
    setSuggestions(prev => ({
      ...prev,
      [fieldKey]: (prev[fieldKey] || []).filter(s => s !== suggestion)
    }));
  };

  const handleNext = () => {
    if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    } else {
      onBack();
    }
  };

  const handleComplete = async () => {
    setIsGenerating(true);

    // Convert form data to canvas format
    const canvas: BusinessCanvasData = {
      keyPartners: (formData.keyPartners || '').split('\n').filter(Boolean),
      keyActivities: (formData.keyActivities || '').split('\n').filter(Boolean),
      keyResources: (formData.keyResources || '').split('\n').filter(Boolean),
      valuePropositions: (formData.valuePropositions || '').split('\n').filter(Boolean),
      customerRelationships: (formData.customerRelationships || '').split('\n').filter(Boolean),
      channels: (formData.channels || '').split('\n').filter(Boolean),
      customerSegments: (formData.customerSegments || '').split('\n').filter(Boolean),
      costStructure: (formData.costStructure || '').split('\n').filter(Boolean),
      revenueStreams: (formData.revenueStreams || '').split('\n').filter(Boolean)
    };

    setIsGenerating(false);
    onComplete(canvas);
  };

  const step = WIZARD_STEPS[currentStep];
  const isLastStep = currentStep === WIZARD_STEPS.length - 1;

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={handleBack}
          className="flex items-center text-[#64748b] hover:text-[#0f172a]"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          {currentStep === 0 ? 'Back' : 'Previous'}
        </button>

        {/* Progress */}
        <div className="flex items-center gap-2">
          {WIZARD_STEPS.map((s, index) => (
            <div
              key={s.id}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentStep
                  ? 'bg-[#1863d6]'
                  : index < currentStep
                  ? 'bg-[#10b981]'
                  : 'bg-[#e2e8f0]'
              }`}
            />
          ))}
        </div>

        <div className="text-sm text-[#64748b]">
          Step {currentStep + 1} of {WIZARD_STEPS.length}
        </div>
      </div>

      {/* Step Content */}
      <div className="backdrop-blur-sm bg-white/80 rounded-2xl shadow-sm border border-[#b6cbe1]/30 p-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-[#1863d6]/10 rounded-lg flex items-center justify-center">
            <LayoutGrid className="w-5 h-5 text-[#1863d6]" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[#0f172a]">{step.title}</h2>
            <p className="text-[#64748b] text-sm">{step.description}</p>
          </div>
        </div>

        {isLoadingSuggestions && (
          <div className="flex items-center gap-2 text-sm text-[#1863d6] mb-4">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading AI suggestions...
          </div>
        )}

        <div className="space-y-6 mt-6">
          {step.fields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-[#334155] mb-1">
                {field.label}
              </label>
              <p className="text-sm text-[#64748b] mb-2">{field.question}</p>

              {/* AI Suggestions */}
              {suggestions[field.key]?.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2">
                  {suggestions[field.key].map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionAccept(field.key, suggestion)}
                      className="group inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#1863d6]/10 hover:bg-[#1863d6]/20 border border-[#1863d6]/20 rounded-full text-sm text-[#1863d6] transition-colors"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      {suggestion}
                      <Check className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </button>
                  ))}
                </div>
              )}

              <textarea
                value={formData[field.key] || ''}
                onChange={(e) => handleFieldChange(field.key, e.target.value)}
                placeholder={field.placeholder}
                className="w-full px-4 py-3 border border-[#e2e8f0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1863d6] focus:border-transparent resize-none"
                rows={4}
              />
            </div>
          ))}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-8 pt-6 border-t border-[#e2e8f0]">
          <button
            onClick={handleBack}
            className="px-6 py-2.5 text-[#64748b] hover:text-[#0f172a]"
          >
            {currentStep === 0 ? 'Cancel' : 'Previous'}
          </button>

          {isLastStep ? (
            <button
              onClick={handleComplete}
              disabled={isGenerating}
              className="flex items-center px-6 py-2.5 bg-[#10b981] text-white rounded-lg hover:bg-[#059669] disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  Generate Canvas
                  <Check className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="flex items-center px-6 py-2.5 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg hover:shadow-md transition-all"
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          )}
        </div>
      </div>

      {/* Preview Mini Canvas */}
      <div className="mt-8 p-6 bg-[#f8fafc] rounded-xl">
        <h4 className="font-medium text-[#334155] mb-4">Canvas Preview</h4>
        <div className="grid grid-cols-5 gap-2">
          {Object.entries({
            keyPartners: 'Partners',
            keyActivities: 'Activities',
            valuePropositions: 'Value',
            customerRelationships: 'Relationships',
            customerSegments: 'Customers',
            keyResources: 'Resources',
            channels: 'Channels',
            costStructure: 'Costs',
            revenueStreams: 'Revenue'
          }).map(([key, label]) => {
            const items = (formData[key] || '').split('\n').filter(Boolean);
            const hasContent = items.length > 0;
            return (
              <div
                key={key}
                className={`p-2 rounded text-xs ${
                  hasContent ? 'bg-[#1863d6]/10 text-[#1863d6]' : 'bg-white text-[#94a3b8]'
                }`}
              >
                <div className="font-medium truncate">{label}</div>
                <div className="mt-0.5">{items.length} items</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default EnhancedBMCWizard;
