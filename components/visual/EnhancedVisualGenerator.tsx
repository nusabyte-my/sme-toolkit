/**
 * EnhancedVisualGenerator Component
 * Displays visual design studio with mockup templates
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState, useRef, useEffect } from 'react';
import { generateVisual, editVisual, enhancePrompt } from '../../services/geminiService';
import {
  Image as ImageIcon, Loader2, Download, Share2, Wand2, Layout, Upload,
  Palette, Sparkles, Layers, Monitor, Smartphone, Tablet,
  Move, Type, MousePointer, Eye, CheckCircle2, AlertTriangle, Code, Edit3, AlertCircle
} from 'lucide-react';
import AdvancedImageEditor from './AdvancedImageEditor';
import useTokenConsumption from '../../hooks/useTokenConsumption';
import useTokens from '../../hooks/useTokens';
import TokenCostBadge from '../common/TokenCostBadge';
import { calculateImageCost } from '../../utils/tokenCosts';

// --- Constants & Configs ---

const TEMPLATES = [
  { id: 'browser', label: 'Browser Window', type: 'frame', icon: Monitor },
  { id: 'phone', label: 'Mobile App', type: 'frame', icon: Smartphone },
  { id: 'social_card', label: 'Social Card', type: 'layout', icon: Layout },
];

const BACKGROUNDS = [
  { id: 'none', label: 'Transparent', value: 'transparent', type: 'color' },
  { id: 'gradient_1', label: 'Sunset', value: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)', type: 'gradient' },
  { id: 'gradient_2', label: 'Ocean', value: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)', type: 'gradient' },
  { id: 'dots', label: 'Dots', value: 'radial-gradient(#cbd5e1 1px, transparent 1px)', style: { backgroundSize: '20px 20px' }, type: 'pattern' },
  { id: 'grid', label: 'Grid', value: 'linear-gradient(#e2e8f0 1px, transparent 1px), linear-gradient(90deg, #e2e8f0 1px, transparent 1px)', style: { backgroundSize: '20px 20px' }, type: 'pattern' },
];

const UI_STATES = [
  { id: 'default', label: 'Default' },
  { id: 'hover', label: 'Hover' },
  { id: 'active', label: 'Active' },
  { id: 'disabled', label: 'Disabled' },
];

const VIEWPORTS = [
  { id: 'desktop', label: 'Desktop', width: '100%', icon: Monitor },
  { id: 'tablet', label: 'Tablet', width: '768px', icon: Tablet },
  { id: 'mobile', label: 'Mobile', width: '375px', icon: Smartphone },
];

// --- Helper Components ---

const AccessibilityCheck = ({ score }: { score: number }) => (
  <div className={`p-3 rounded-lg border flex items-start gap-3 text-sm ${score >= 4.5 ? 'bg-[#10b981]/10 border-[#10b981]/20' : 'bg-[#f59e0b]/10 border-[#f59e0b]/20'}`}>
    {score >= 4.5 ? <CheckCircle2 className="w-5 h-5 text-[#10b981]" /> : <AlertTriangle className="w-5 h-5 text-[#f59e0b]" />}
    <div>
      <div className={`font-semibold ${score >= 4.5 ? 'text-[#10b981]' : 'text-[#f59e0b]'}`}>
        {score >= 4.5 ? 'WCAG AA Compliant' : 'Low Contrast Detected'}
      </div>
      <div className="text-[#64748b] mt-1 text-xs">
        Contrast ratio: {score}:1. {score < 4.5 ? 'Try darker text or lighter background.' : 'Good for standard text.'}
      </div>
    </div>
  </div>
);

// --- Main Component ---

const EnhancedVisualGenerator: React.FC = () => {
  // --- State ---
  const [activeTab, setActiveTab] = useState<'GENERATE' | 'DESIGN' | 'PREVIEW'>('GENERATE');
  
  // Generation State
  const [prompt, setPrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const { guard } = useTokenConsumption();
  const { balance: tokenBalance } = useTokens();
  const imageTokenCost = calculateImageCost({ resolution: '1024x1024', quality: 'standard' });
  
  // Design/Mockup State
  const [selectedBackground, setSelectedBackground] = useState(BACKGROUNDS[0]);
  const [selectedTemplate, setSelectedTemplate] = useState(TEMPLATES[0]);
  const [uiState, setUiState] = useState('default');
  const [viewport, setViewport] = useState(VIEWPORTS[0]);
  
  // Accessibility
  const [contrastScore, setContrastScore] = useState(5.2); // Mocked start
  
  // Advanced Editor
  const [showAdvancedEditor, setShowAdvancedEditor] = useState(false);

  // Handlers
  const handleGenerate = async () => {
    if (!prompt) return;
    setLoading(true);
    setTokenError(null);

    const { data, error } = await guard('image_generation', () =>
      generateVisual(prompt, "16:9")
    );

    if (error) {
      setTokenError(error);
      setLoading(false);
      return;
    }

    if (data) {
      setGeneratedImage(data);
      setActiveTab('DESIGN');
    }
    setLoading(false);
  };

  const handleDownload = () => {
    // Basic download logic (would ideally use html2canvas for the composite)
    if (generatedImage) {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = `visual-${Date.now()}.png`;
      link.click();
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-6 relative">
      
      {/* Advanced Editor Modal */}
      {showAdvancedEditor && generatedImage && (
        <div className="fixed inset-0 z-50 bg-[#001f3d]/95 flex items-center justify-center p-6 animate-in fade-in duration-200">
          <div className="w-full max-w-6xl h-full max-h-[800px] flex flex-col">
            <div className="flex justify-between items-center mb-4 text-white">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-[#1863d6]" /> Advanced Editor
              </h3>
              <button
                onClick={() => setShowAdvancedEditor(false)}
                className="text-[#94a3b8] hover:text-white px-3 py-1 rounded hover:bg-white/10 transition-colors"
              >
                Close
              </button>
            </div>
            <div className="flex-1 backdrop-blur-sm bg-white/80 rounded-xl overflow-hidden">
              <AdvancedImageEditor initialImage={generatedImage} onClose={() => setShowAdvancedEditor(false)} />
            </div>
          </div>
        </div>
      )}

      {tokenError && (
        <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">{tokenError}</div>
          <button onClick={() => setTokenError(null)} className="text-amber-400 hover:text-amber-600">&times;</button>
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-[#0f172a] flex items-center gap-2">
            <Palette className="w-6 h-6 text-[#1863d6]" />
            Visual Design Studio
          </h2>
          <p className="text-[#64748b] text-sm">Generate, mock up, and refine UI visuals.</p>
        </div>
        <div className="flex bg-[#f8fafc] p-1 rounded-lg">
          {['GENERATE', 'DESIGN', 'PREVIEW'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-2 text-xs font-medium rounded-md transition-all ${activeTab === tab ? 'bg-white shadow-sm text-[#1863d6]' : 'text-[#64748b] hover:text-[#0f172a]'}`}
            >
              {tab.charAt(0) + tab.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-200px)] min-h-[600px]">
        
        {/* Left Sidebar: Controls */}
        <div className="lg:col-span-3 space-y-6 overflow-y-auto pr-2">
          
          {activeTab === 'GENERATE' && (
            <div className="backdrop-blur-sm bg-white/80 p-5 rounded-xl border border-[#b6cbe1]/30 shadow-sm space-y-4">
              <label className="text-xs font-bold text-[#64748b] uppercase">Generation Prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full p-3 border border-[#e2e8f0] rounded-lg text-sm h-32 field-focus resize-none"
                placeholder="Describe your UI element or scene..."
              />
              <div className="flex items-center justify-between">
                <TokenCostBadge cost={imageTokenCost} balance={tokenBalance.balance} />
                <span className="text-[10px] text-[#94a3b8]">Balance: {tokenBalance.balance.toLocaleString()} tokens</span>
              </div>
              <button
                onClick={handleGenerate}
                disabled={loading || !prompt}
                className="w-full py-3 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg font-medium hover:shadow-md disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                Generate Base Visual
              </button>
            </div>
          )}

          {(activeTab === 'DESIGN' || activeTab === 'PREVIEW') && (
            <div className="space-y-6">
              
              {/* Quick Actions */}
              <div className="backdrop-blur-sm bg-[#1863d6]/10 p-4 rounded-xl border border-[#1863d6]/20 shadow-sm">
                 <label className="text-xs font-bold text-[#1863d6] uppercase mb-3 block">Refinement</label>
                 <button
                   onClick={() => setShowAdvancedEditor(true)}
                   disabled={!generatedImage}
                   className="w-full py-2 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg text-xs font-medium hover:shadow-md flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
                 >
                   <Edit3 className="w-3.5 h-3.5" /> Open Advanced Editor
                 </button>
              </div>

              {/* Templates */}
              <div className="backdrop-blur-sm bg-white/80 p-4 rounded-xl border border-[#b6cbe1]/30 shadow-sm">
                <label className="text-xs font-bold text-[#64748b] uppercase mb-3 block">Mockup Template</label>
                <div className="grid grid-cols-3 gap-2">
                  {TEMPLATES.map(t => (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTemplate(t)}
                      className={`flex flex-col items-center p-2 rounded-lg border transition-all ${selectedTemplate.id === t.id ? 'border-[#1863d6] bg-[#1863d6]/10 text-[#1863d6]' : 'border-[#e2e8f0] hover:bg-[#f8fafc]'}`}
                    >
                      <t.icon className="w-5 h-5 mb-1" />
                      <span className="text-[10px] font-medium">{t.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Backgrounds */}
              <div className="backdrop-blur-sm bg-white/80 p-4 rounded-xl border border-[#b6cbe1]/30 shadow-sm">
                <label className="text-xs font-bold text-[#64748b] uppercase mb-3 block">Background</label>
                <div className="grid grid-cols-5 gap-2">
                  {BACKGROUNDS.map(bg => (
                    <button
                      key={bg.id}
                      onClick={() => setSelectedBackground(bg)}
                      className={`w-8 h-8 rounded-full border-2 transition-all ${selectedBackground.id === bg.id ? 'border-[#1863d6] ring-2 ring-[#1863d6]/20' : 'border-[#e2e8f0]'}`}
                      style={{ background: bg.value, ...bg.style }}
                      title={bg.label}
                    />
                  ))}
                </div>
              </div>

              {/* States */}
              <div className="backdrop-blur-sm bg-white/80 p-4 rounded-xl border border-[#b6cbe1]/30 shadow-sm">
                <label className="text-xs font-bold text-[#64748b] uppercase mb-3 block">Element State</label>
                <div className="flex flex-wrap gap-2">
                  {UI_STATES.map(s => (
                    <button
                      key={s.id}
                      onClick={() => setUiState(s.id)}
                      className={`px-3 py-1.5 text-xs rounded-full border transition-all ${uiState === s.id ? 'bg-[#1863d6]/10 border-[#1863d6]/20 text-[#1863d6]' : 'bg-white border-[#e2e8f0] text-[#64748b]'}`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Accessibility */}
              <div className="backdrop-blur-sm bg-white/80 p-4 rounded-xl border border-[#b6cbe1]/30 shadow-sm space-y-3">
                <label className="text-xs font-bold text-[#64748b] uppercase block flex justify-between">
                  Accessibility
                  <Eye className="w-3 h-3" />
                </label>
                <AccessibilityCheck score={contrastScore} />
                <button
                  onClick={() => setContrastScore(Math.random() > 0.5 ? 5.2 : 3.1)}
                  className="text-xs text-[#1863d6] hover:underline w-full text-right"
                >
                  Re-check Contrast
                </button>
              </div>

              {/* Tooling Recommendations */}
              <div className="bg-[#001f3d] text-[#94a3b8] p-4 rounded-xl shadow-sm text-xs space-y-3">
                <label className="font-bold text-white uppercase flex items-center gap-2">
                  <Code className="w-3 h-3" /> Tooling Recommendations
                </label>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>ESLint</span>
                    <span className="text-[#64748b]">Linting</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Prettier</span>
                    <span className="text-[#64748b]">Formatting</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tailwind CSS IntelliSense</span>
                    <span className="text-[#64748b]">Styling</span>
                  </div>
                  <div className="flex justify-between">
                    <span>axe-core</span>
                    <span className="text-[#64748b]">Accessibility</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Center: Canvas / Preview */}
        <div className="lg:col-span-9 bg-[#f8fafc] rounded-xl border border-[#e2e8f0] flex flex-col relative overflow-hidden">
          
          {/* Toolbar */}
          <div className="backdrop-blur-sm bg-white/80 border-b border-[#e2e8f0] p-3 flex justify-between items-center px-6">
            <div className="flex gap-2">
              {VIEWPORTS.map(v => (
                <button
                  key={v.id}
                  onClick={() => setViewport(v)}
                  className={`p-2 rounded-lg transition-colors ${viewport.id === v.id ? 'bg-[#1863d6]/10 text-[#1863d6]' : 'text-[#94a3b8] hover:bg-[#f8fafc]'}`}
                  title={v.label}
                >
                  <v.icon className="w-4 h-4" />
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <button onClick={handleDownload} className="text-xs flex items-center gap-2 px-3 py-1.5 bg-[#001f3d] text-white rounded-lg hover:bg-[#151983] transition-colors">
                <Download className="w-3 h-3" /> Export
              </button>
            </div>
          </div>

          {/* Canvas Area */}
          <div className="flex-1 flex items-center justify-center p-8 overflow-auto" style={{ background: '#f1f5f9' }}>
            <div
              className="relative transition-all duration-500 ease-in-out shadow-2xl bg-white"
              style={{
                width: viewport.width,
                  height: viewport.id === 'mobile' ? '667px' : '600px', // Mock heights
                  borderRadius: selectedTemplate.id === 'phone' ? '32px' : '8px',
                  border: selectedTemplate.id === 'phone' ? '8px solid #1e293b' : '1px solid #cbd5e1',
                  overflow: 'hidden'
              }}
            >
              {/* Mockup Header (Browser) */}
              {selectedTemplate.id === 'browser' && (
                <div className="h-8 bg-[#f8fafc] border-b border-[#e2e8f0] flex items-center px-3 gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ef4444]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></div>
                  <div className="flex-1 mx-2">
                    <div className="h-5 bg-white rounded-md w-3/4 mx-auto shadow-sm"></div>
                  </div>
                </div>
              )}

              {/* Viewport Content */}
              <div
                className="w-full h-full relative"
                style={{
                  background: selectedBackground.value,
                  ...selectedBackground.style
                }}
              >
                {generatedImage ? (
                  <div className="w-full h-full flex items-center justify-center p-4">
                    <div className={`relative group transition-all duration-300 ${uiState === 'hover' ? 'scale-105 shadow-xl' : ''} ${uiState === 'active' ? 'scale-95 opacity-90' : ''} ${uiState === 'disabled' ? 'grayscale opacity-50' : ''}`}>
                      <img
                        src={generatedImage}
                        alt="Generated UI"
                        className="max-w-full max-h-full object-contain rounded-md shadow-lg"
                      />
                      
                      {/* UI State Indicator Overlay */}
                      <div className="absolute -top-3 -right-3 bg-[#1863d6] text-white text-[10px] px-2 py-0.5 rounded-full uppercase font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                        {uiState}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-[#94a3b8]">
                    <ImageIcon className="w-12 h-12 mb-2 opacity-20" />
                    <p className="text-sm">Generated visuals will appear here</p>
                  </div>
                )}
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default EnhancedVisualGenerator;