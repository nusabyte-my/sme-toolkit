/**
 * BusinessModelCanvas Component
 * Displays business model canvas with AI-powered generation
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState } from 'react';
import { generateBusinessCanvas, enhancePrompt } from '../services/geminiService';
import { BusinessCanvasData } from '../types';
import { Loader2, Sparkles, AlertCircle, Edit2, Save, X, Plus, ArrowRight, ArrowLeft, CheckCircle2, Wand2 } from 'lucide-react';

const SECTIONS = [
  { key: 'keyPartners', title: 'Key Partners', question: 'Who are your key partners and suppliers?' },
  { key: 'keyActivities', title: 'Key Activities', question: 'What key activities does your business require?' },
  { key: 'keyResources', title: 'Key Resources', question: 'What key resources do you need (assets, intellectual property, etc.)?' },
  { key: 'valuePropositions', title: 'Value Propositions', question: 'What value do you deliver to the customer? What problem do you solve?' },
  { key: 'customerRelationships', title: 'Customer Relationships', question: 'What type of relationship does each customer segment expect?' },
  { key: 'channels', title: 'Channels', question: 'Through which channels do your customers want to be reached?' },
  { key: 'customerSegments', title: 'Customer Segments', question: 'Who are your most important customers?' },
  { key: 'costStructure', title: 'Cost Structure', question: 'What are the most important costs in your business model?' },
  { key: 'revenueStreams', title: 'Revenue Streams', question: 'How will you make money? What are your pricing models?' },
] as const;

type CanvasKey = typeof SECTIONS[number]['key'];

const CanvasBlock: React.FC<{ 
  title: string; 
  description?: string;
  items: string[]; 
  className?: string;
  onUpdate: (newItems: string[]) => void;
}> = ({ title, description, items, className, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState('');

  const handleStartEdit = () => {
    setEditValue(items.join('\n'));
    setIsEditing(true);
  };

  const handleSave = () => {
    const newItems = editValue.split('\n').filter(line => line.trim() !== '');
    onUpdate(newItems);
    setIsEditing(false);
  };

  return (
    <div className={`backdrop-blur-sm bg-white/80 p-4 border border-[#b6cbe1]/30 rounded-lg shadow-sm flex flex-col h-full min-h-[160px] relative transition-all hover:shadow-md ${className}`}>
      <div className="flex items-center justify-between mb-3 border-b border-[#e2e8f0] pb-2">
        <h3 className="text-[#334155] font-semibold text-sm uppercase tracking-wide">{title}</h3>
        {!isEditing && (
          <button
            onClick={handleStartEdit}
            className="p-1 hover:bg-[#f8fafc] rounded text-[#94a3b8] hover:text-[#1863d6] transition-colors"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {isEditing ? (
        <div className="flex-1 flex flex-col gap-2">
          <textarea
            className="flex-1 w-full p-2 text-sm border border-[#1863d6]/30 rounded-md field-focus resize-none bg-[#1863d6]/5"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            placeholder="Enter items (one per line)..."
            autoFocus
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setIsEditing(false)}
              className="px-2 py-1 text-xs text-[#64748b] hover:bg-[#f8fafc] rounded"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-2 py-1 text-xs bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded hover:shadow-md transition-all duration-200 flex items-center gap-1"
            >
              <Save className="w-3 h-3" /> Save
            </button>
          </div>
        </div>
      ) : (
        <ul className="space-y-2 flex-1 overflow-y-auto max-h-[300px]">
          {items && items.length > 0 ? (
            items.map((item, idx) => (
              <li key={idx} className="text-sm text-[#64748b] flex items-start gap-2 group">
                <span className="w-1.5 h-1.5 rounded-full bg-[#1863d6]/20 mt-1.5 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))
          ) : (
            <li className="text-sm text-[#94a3b8] italic">No data yet...</li>
          )}
        </ul>
      )}
    </div>
  );
};

const BusinessModelCanvas: React.FC = () => {
  const [mode, setMode] = useState<'INITIAL' | 'WIZARD' | 'RESULT'>('INITIAL');
  const [description, setDescription] = useState('');
  const [wizardData, setWizardData] = useState<Record<string, string>>({});
  const [canvas, setCanvas] = useState<BusinessCanvasData | null>(null);
  const [loading, setLoading] = useState(false);
  const [enhancing, setEnhancing] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async (useWizardData: boolean = false) => {
    if (!description.trim()) return;
    setLoading(true);
    setError('');
    try {
      const inputs = useWizardData ? wizardData : undefined;
      const data = await generateBusinessCanvas(description, inputs);
      setCanvas(data);
      setMode('RESULT');
    } catch (err) {
      setError('Failed to generate canvas. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEnhance = async () => {
    if (!description.trim()) return;
    setEnhancing(true);
    try {
      const enhanced = await enhancePrompt(description);
      setDescription(enhanced);
    } catch (e) {
      console.error(e);
    } finally {
      setEnhancing(false);
    }
  };

  const updateWizardField = (key: string, value: string) => {
    setWizardData(prev => ({ ...prev, [key]: value }));
  };

  const updateCanvasBlock = (key: keyof BusinessCanvasData, newItems: string[]) => {
    if (canvas) {
      setCanvas({ ...canvas, [key]: newItems });
    }
  };

  if (mode === 'RESULT' && canvas) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6 animate-in fade-in duration-500">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
             <button
               onClick={() => setMode('INITIAL')}
               className="text-xs text-[#64748b] hover:text-[#1863d6] mb-1 flex items-center gap-1"
             >
               <ArrowLeft className="w-3 h-3" /> Start Over
             </button>
             <h2 className="text-2xl font-bold text-[#0f172a]">Your Business Model</h2>
             <p className="text-[#64748b] text-sm">Review and edit your canvas below.</p>
          </div>
          <button
            onClick={() => handleGenerate(Object.keys(wizardData).length > 0)}
            disabled={loading}
            className="text-sm bg-[#1863d6]/10 border border-[#1863d6]/30 text-[#1863d6] px-4 py-2 rounded-lg hover:bg-[#1863d6]/20 flex items-center gap-2 transition-colors"
          >
            {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
            Regenerate
          </button>
        </div>

        <div className="bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9] p-4 rounded-xl">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-1 flex flex-col gap-4">
              <CanvasBlock 
                title="Key Partners" 
                description={SECTIONS.find(s => s.key === 'keyPartners')?.question}
                items={canvas.keyPartners} 
                onUpdate={(items) => updateCanvasBlock('keyPartners', items)} 
                className="flex-1" 
              />
            </div>
            <div className="md:col-span-1 flex flex-col gap-4">
              <CanvasBlock 
                title="Key Activities" 
                items={canvas.keyActivities} 
                onUpdate={(items) => updateCanvasBlock('keyActivities', items)} 
                className="h-1/2" 
              />
              <CanvasBlock 
                title="Key Resources" 
                items={canvas.keyResources} 
                onUpdate={(items) => updateCanvasBlock('keyResources', items)} 
                className="h-1/2" 
              />
            </div>
            <div className="md:col-span-1 flex flex-col gap-4">
              <CanvasBlock
                title="Value Propositions"
                items={canvas.valuePropositions}
                onUpdate={(items) => updateCanvasBlock('valuePropositions', items)}
                className="h-full bg-[#1863d6]/10 border-[#1863d6]/30"
              />
            </div>
            <div className="md:col-span-1 flex flex-col gap-4">
              <CanvasBlock 
                title="Customer Relationships" 
                items={canvas.customerRelationships} 
                onUpdate={(items) => updateCanvasBlock('customerRelationships', items)} 
                className="h-1/2" 
              />
              <CanvasBlock 
                title="Channels" 
                items={canvas.channels} 
                onUpdate={(items) => updateCanvasBlock('channels', items)} 
                className="h-1/2" 
              />
            </div>
            <div className="md:col-span-1 flex flex-col gap-4">
              <CanvasBlock 
                title="Customer Segments" 
                items={canvas.customerSegments} 
                onUpdate={(items) => updateCanvasBlock('customerSegments', items)} 
                className="flex-1" 
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
             <CanvasBlock 
               title="Cost Structure" 
               items={canvas.costStructure} 
               onUpdate={(items) => updateCanvasBlock('costStructure', items)} 
             />
             <CanvasBlock 
               title="Revenue Streams" 
               items={canvas.revenueStreams} 
               onUpdate={(items) => updateCanvasBlock('revenueStreams', items)} 
             />
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'WIZARD') {
    return (
      <div className="max-w-4xl mx-auto p-4 md:p-6 animate-in slide-in-from-right-4 duration-300">
        <button
          onClick={() => setMode('INITIAL')}
          className="mb-6 flex items-center gap-2 text-[#64748b] hover:text-[#0f172a] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Idea
        </button>

        <div className="mb-8">
           <h2 className="text-2xl font-bold text-[#0f172a] mb-2">Refine Your Business Model</h2>
           <p className="text-[#64748b]">Provide details for specific sections to get a more accurate result. All fields are optional.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
           {SECTIONS.map((section) => (
             <div key={section.key} className="backdrop-blur-sm bg-white/80 p-4 rounded-xl border border-[#b6cbe1]/30 shadow-sm focus-within:ring-2 focus-within:ring-[#1863d6]/20 transition-all">
                 <label className="block font-semibold text-[#0f172a] mb-1">{section.title}</label>
                 <p className="text-xs text-[#64748b] mb-3">{section.question}</p>
                 <textarea
                   className="w-full text-sm p-3 bg-[#f8fafc] border border-[#e2e8f0] rounded-lg outline-none focus:bg-white transition-colors resize-none h-24"
                   placeholder={`Enter details for ${section.title}...`}
                   value={wizardData[section.title] || ''}
                   onChange={(e) => updateWizardField(section.title, e.target.value)}
                 />
             </div>
           ))}
        </div>

        <div className="sticky bottom-4 backdrop-blur-md bg-white/95 p-4 rounded-xl border border-[#b6cbe1]/30 shadow-lg flex justify-between items-center z-10">
           <div className="text-sm text-[#64748b]">
             {Object.keys(wizardData).filter(k => wizardData[k].trim()).length} sections customized
           </div>
           <button
             onClick={() => handleGenerate(true)}
             disabled={loading}
             className="bg-gradient-to-r from-[#1863d6] to-[#151983] hover:shadow-md text-white px-8 py-3 rounded-lg font-medium flex items-center gap-2 shadow-md transition-all hover:scale-105"
           >
             {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
             Generate Personalized Canvas
           </button>
        </div>
      </div>
    );
  }

  // Initial Mode
  return (
    <div className="max-w-3xl mx-auto p-4 md:p-6 flex flex-col items-center justify-center min-h-[60vh] space-y-8 animate-in fade-in duration-500">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-[#1863d6] to-[#151983] text-white mb-4 shadow-lg shadow-[#1863d6]/30">
           <Sparkles className="w-8 h-8" />
        </div>
        <h2 className="text-3xl font-bold text-[#0f172a]">Business Model Generator</h2>
        <p className="text-lg text-[#64748b] max-w-xl mx-auto">
          Turn your business idea into a structured 9-block canvas instantly. Start with a simple description or customize every detail.
        </p>
      </div>

      <div className="w-full backdrop-blur-sm bg-white/80 p-2 rounded-2xl shadow-lg border border-[#b6cbe1]/30 relative">
        <div className="relative">
          <textarea
            className="w-full p-4 pb-12 text-lg rounded-xl outline-none resize-none h-32 placeholder:text-[#94a3b8]"
            placeholder="Describe your business idea (e.g., A subscription service for organic coffee beans delivered to offices...)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button
            onClick={handleEnhance}
            disabled={enhancing || !description.trim()}
            className="absolute right-3 bottom-3 text-xs bg-[#1863d6]/10 text-[#1863d6] hover:bg-[#1863d6]/20 px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5 font-medium disabled:opacity-50"
            title="Enhance your description with AI"
          >
            {enhancing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
            Enhance
          </button>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 p-2 bg-[#f8fafc] rounded-xl border border-[#e2e8f0]">
          <button
            onClick={() => setMode('WIZARD')}
            disabled={!description.trim()}
            className="flex-1 px-4 py-3 rounded-lg text-[#334155] font-medium hover:bg-white hover:shadow-sm border border-transparent hover:border-[#e2e8f0] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Edit2 className="w-4 h-4" /> Refine Details First
          </button>
          <button
            onClick={() => handleGenerate(false)}
            disabled={loading || !description.trim()}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-[#1863d6] to-[#151983] hover:shadow-md text-white rounded-lg font-medium shadow-md transition-all hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50 disabled:shadow-none"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Quick Generate
          </button>
        </div>
      </div>
      
      {error && (
        <div className="flex items-center gap-2 text-[#ef4444] bg-[#ef4444]/10 px-4 py-2 rounded-lg border border-[#ef4444]/20">
            <AlertCircle className="w-4 h-4" />
            {error}
        </div>
      )}

      <div className="grid grid-cols-3 gap-8 text-center w-full max-w-2xl pt-8 border-t border-[#e2e8f0]/60">
         <div className="space-y-1">
            <div className="font-bold text-2xl text-[#0f172a]">9</div>
            <div className="text-xs font-semibold text-[#64748b] uppercase tracking-wider">Building Blocks</div>
         </div>
         <div className="space-y-1">
            <div className="font-bold text-2xl text-[#0f172a]">100%</div>
            <div className="text-xs font-semibold text-[#64748b] uppercase tracking-wider">Customizable</div>
         </div>
         <div className="space-y-1">
            <div className="font-bold text-2xl text-[#0f172a]">AI</div>
            <div className="text-xs font-semibold text-[#64748b] uppercase tracking-wider">Powered</div>
         </div>
      </div>
    </div>
  );
};

export default BusinessModelCanvas;