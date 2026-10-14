import React, { useState, useEffect, useCallback } from 'react';
import {
  LayoutGrid,
  Sparkles,
  ArrowRight,
  Check,
  X,
  Save,
  Download,
  History,
  TrendingUp,
  Lightbulb,
  AlertCircle,
  RefreshCw,
  FileText,
  Image,
  Share2,
  Lock,
  Unlock,
  Eye,
  Edit3,
  Trash2,
  Copy,
  Plus,
  ChevronDown,
  ChevronRight,
  Star,
  Zap,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { BusinessCanvasData, BusinessProfile } from '../../types';
import type { UserProfile } from '../../types/profiles';
import { useProfile } from '../../contexts/ProfileContext';

interface BMCVersion {
  id: string;
  timestamp: number;
  canvas: BusinessCanvasData;
  notes?: string;
  isDraft?: boolean;
}

interface BMCSuggestion {
  block: keyof BusinessCanvasData;
  suggestion: string;
  confidence: number;
  source: 'profile' | 'ai' | 'template';
}

interface BMCQualityScore {
  overall: number;
  completeness: number;
  depth: number;
  coherence: number;
  recommendations: string[];
}

interface ImprovedBMCWorkflowProps {
  initialCanvas?: BusinessCanvasData;
  onCanvasChange?: (canvas: BusinessCanvasData) => void;
  onSave?: (canvas: BusinessCanvasData, notes?: string) => void;
}

type BMCMode = 'overview' | 'edit' | 'compare' | 'export' | 'suggestions';

const BLOCK_TITLES: Record<keyof BusinessCanvasData, string> = {
  keyPartners: 'Key Partners',
  keyActivities: 'Key Activities',
  keyResources: 'Key Resources',
  valuePropositions: 'Value Propositions',
  customerRelationships: 'Customer Relationships',
  channels: 'Channels',
  customerSegments: 'Customer Segments',
  costStructure: 'Cost Structure',
  revenueStreams: 'Revenue Streams'
};

const ImprovedBMCWorkflow: React.FC<ImprovedBMCWorkflowProps> = ({
  initialCanvas,
  onCanvasChange,
  onSave
}) => {
  const { userProfile, businessProfile } = useProfile();

  const [canvas, setCanvas] = useState<BusinessCanvasData>(initialCanvas || {
    keyPartners: [],
    keyActivities: [],
    keyResources: [],
    valuePropositions: [],
    customerRelationships: [],
    channels: [],
    customerSegments: [],
    costStructure: [],
    revenueStreams: []
  });

  const [mode, setMode] = useState<BMCMode>('overview');
  const [versions, setVersions] = useState<BMCVersion[]>([]);
  const [currentVersionId, setCurrentVersionId] = useState<string | null>(null);
  const [selectedVersions, setSelectedVersions] = useState<[string | null, string | null]>([null, null]);
  const [suggestions, setSuggestions] = useState<BMCSuggestion[]>([]);
  const [qualityScore, setQualityScore] = useState<BMCQualityScore | null>(null);
  const [loading, setLoading] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [editingBlock, setEditingBlock] = useState<keyof BusinessCanvasData | null>(null);
  const [editValue, setEditValue] = useState('');
  const [versionNotes, setVersionNotes] = useState('');

  const generateProfileBasedSuggestions = useCallback((): BMCSuggestion[] => {
    const newSuggestions: BMCSuggestion[] = [];

    if (businessProfile) {
      if (businessProfile.industry) {
        newSuggestions.push({
          block: 'customerSegments',
          suggestion: `Target customers in ${businessProfile.industry} industry`,
          confidence: 0.8,
          source: 'profile'
        });
      }

      if (businessProfile.business_description?.length) {
        businessProfile.business_description.split(/[.,\n]/).map(s => s.trim()).filter(Boolean).slice(0, 3).forEach(productName => {
          newSuggestions.push({
            block: 'valuePropositions',
            suggestion: productName,
            confidence: 0.9,
            source: 'profile'
          });
        });
      }

      if (businessProfile.business_type) {
        const typeSuggestions: Record<string, { block: keyof BusinessCanvasData; suggestion: string }[]> = {
          'retail': [
            { block: 'channels', suggestion: 'Physical stores' },
            { block: 'channels', suggestion: 'E-commerce platform' },
            { block: 'customerRelationships', suggestion: 'In-store assistance' }
          ],
          'service': [
            { block: 'customerRelationships', suggestion: 'Consultative support' },
            { block: 'keyActivities', suggestion: 'Service delivery' }
          ],
          'technology': [
            { block: 'keyResources', suggestion: 'Technical infrastructure' },
            { block: 'keyActivities', suggestion: 'R&D' },
            { block: 'channels', suggestion: 'Digital platforms' }
          ],
          'manufacturing': [
            { block: 'keyActivities', suggestion: 'Production operations' },
            { block: 'keyResources', suggestion: 'Manufacturing facilities' },
            { block: 'costStructure', suggestion: 'Raw materials' }
          ]
        };

        const typeSugs = typeSuggestions[businessProfile.business_type] || [];
        typeSugs.forEach(sug => {
          newSuggestions.push({
            block: sug.block,
            suggestion: sug.suggestion,
            confidence: 0.75,
            source: 'profile'
          });
        });
      }
    }

    if (userProfile) {
      if (userProfile.skills?.length) {
        userProfile.skills.slice(0, 3).forEach(skill => {
          newSuggestions.push({
            block: 'keyResources',
            suggestion: `Team expertise: ${skill}`,
            confidence: 0.7,
            source: 'profile'
          });
        });
      }
    }

    return newSuggestions;
  }, [businessProfile, userProfile]);

  const calculateQualityScore = useCallback((): BMCQualityScore => {
    const blocks = Object.keys(canvas) as (keyof BusinessCanvasData)[];

    const completeness = (blocks.filter(block => 
      canvas[block] && canvas[block].length > 0
    ).length / blocks.length) * 100;

    const totalItems = blocks.reduce((sum, block) => 
      sum + (canvas[block]?.length || 0), 0
    );
    const depth = Math.min(100, (totalItems / 18) * 100);

    const coherence = calculateCoherenceScore();

    const recommendations: string[] = [];

    blocks.forEach(block => {
      if (!canvas[block] || canvas[block].length === 0) {
        recommendations.push(`Add content to ${BLOCK_TITLES[block]}`);
      } else if (canvas[block].length < 2) {
        recommendations.push(`Expand ${BLOCK_TITLES[block]} with more items`);
      }
    });

    if (coherence < 60) {
      recommendations.push('Ensure customer segments align with value propositions');
    }

    if (canvas.valuePropositions?.length && !canvas.revenueStreams?.length) {
      recommendations.push('Define how your value propositions generate revenue');
    }

    return {
      overall: Math.round((completeness * 0.4 + depth * 0.3 + coherence * 0.3)),
      completeness: Math.round(completeness),
      depth: Math.round(depth),
      coherence: Math.round(coherence),
      recommendations: recommendations.slice(0, 5)
    };
  }, [canvas]);

  const calculateCoherenceScore = (): number => {
    let coherenceScore = 50;

    if (canvas.customerSegments?.length && canvas.valuePropositions?.length) {
      coherenceScore += 15;
    }

    if (canvas.channels?.length && canvas.customerSegments?.length) {
      coherenceScore += 15;
    }

    if (canvas.revenueStreams?.length && canvas.valuePropositions?.length) {
      coherenceScore += 10;
    }

    if (canvas.costStructure?.length && canvas.keyActivities?.length) {
      coherenceScore += 10;
    }

    return Math.min(100, coherenceScore);
  };

  useEffect(() => {
    const newSuggestions = generateProfileBasedSuggestions();
    setSuggestions(newSuggestions);
    setQualityScore(calculateQualityScore());
  }, [generateProfileBasedSuggestions, calculateQualityScore]);

  useEffect(() => {
    if (initialCanvas) {
      setCanvas(initialCanvas);
    }
  }, [initialCanvas]);

  const handleAddToBlock = (block: keyof BusinessCanvasData, value: string) => {
    setCanvas(prev => ({
      ...prev,
      [block]: [...(prev[block] || []), value]
    }));
    setIsDirty(true);
    onCanvasChange?.(canvas);
  };

  const handleRemoveFromBlock = (block: keyof BusinessCanvasData, index: number) => {
    setCanvas(prev => ({
      ...prev,
      [block]: prev[block]?.filter((_, i) => i !== index) || []
    }));
    setIsDirty(true);
    onCanvasChange?.(canvas);
  };

  const handleStartEdit = (block: keyof BusinessCanvasData) => {
    setEditingBlock(block);
    setEditValue(canvas[block]?.join('\n') || '');
  };

  const handleSaveEdit = () => {
    if (editingBlock) {
      const newItems = editValue.split('\n').filter(line => line.trim() !== '');
      setCanvas(prev => ({
        ...prev,
        [editingBlock]: newItems
      }));
      setEditingBlock(null);
      setIsDirty(true);
      onCanvasChange?.(canvas);
    }
  };

  const handleSaveVersion = () => {
    const newVersion: BMCVersion = {
      id: Date.now().toString(),
      timestamp: Date.now(),
      canvas: { ...canvas },
      notes: versionNotes,
      isDraft: false
    };

    setVersions(prev => [newVersion, ...prev]);
    setCurrentVersionId(newVersion.id);
    setIsDirty(false);
    setVersionNotes('');
    onSave?.(canvas, versionNotes);
  };

  const handleExport = async (format: 'pdf' | 'png' | 'json') => {
    setLoading(true);
    try {
      const exportData = {
        format,
        canvas,
        metadata: {
          timestamp: new Date().toISOString(),
          version: currentVersionId,
          profile: {
            user: userProfile ? `${userProfile.first_name ?? ''} ${userProfile.last_name ?? ''}`.trim() : undefined,
            business: businessProfile?.company_name
          }
        }
      };

      if (format === 'json') {
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bmc-export-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
      <div className="max-w-7xl mx-auto p-6">
        {mode === 'overview' && (
          <>
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#1863d6] to-[#151983] rounded-xl flex items-center justify-center shadow-lg shadow-[#1863d6]/30">
                    <LayoutGrid className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900">Business Model Canvas</h1>
                    <p className="text-slate-600 text-sm">
                      {isDirty ? 'Unsaved changes' : 'Last saved: ' + (currentVersionId ? new Date(parseInt(currentVersionId)).toLocaleString() : 'Never')}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setMode('suggestions')}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg hover:border-[#1863d6] hover:text-[#1863d6] transition-all"
                  >
                    <Lightbulb className="w-4 h-4" />
                    AI Suggestions
                    {suggestions.length > 0 && (
                      <span className="px-2 py-0.5 bg-[#1863d6] text-white text-xs rounded-full">
                        {suggestions.length}
                      </span>
                    )}
                  </button>

                  <button
                    onClick={() => setMode('compare')}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg hover:border-[#1863d6] hover:text-[#1863d6] transition-all"
                  >
                    <History className="w-4 h-4" />
                    Versions
                    {versions.length > 0 && (
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded-full">
                        {versions.length}
                      </span>
                    )}
                  </button>

                  <button
                    onClick={() => setMode('export')}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg hover:border-[#1863d6] hover:text-[#1863d6] transition-all"
                  >
                    <Download className="w-4 h-4" />
                    Export
                  </button>

                  <button
                    onClick={handleSaveVersion}
                    disabled={!isDirty}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Save className="w-4 h-4" />
                    Save
                  </button>

                  <button
                    onClick={() => setMode('edit')}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white rounded-lg hover:shadow-md transition-all"
                  >
                    <Edit3 className="w-4 h-4" />
                    Edit Canvas
                  </button>
                </div>
              </div>

              {qualityScore && (
                <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-[#1863d6]" />
                      BMC Quality Score
                    </h3>
                    <div className={`text-3xl font-bold ${getScoreColor(qualityScore.overall)}`}>
                      {qualityScore.overall}%
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-slate-600 mb-1">Completeness</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getScoreBackground(qualityScore.completeness)} transition-all duration-500`}
                            style={{ width: `${qualityScore.completeness}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-slate-700">{qualityScore.completeness}%</span>
                      </div>
                    </div>

                    <div>
                      <div className="text-xs text-slate-600 mb-1">Depth</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getScoreBackground(qualityScore.depth)} transition-all duration-500`}
                            style={{ width: `${qualityScore.depth}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-slate-700">{qualityScore.depth}%</span>
                      </div>
                    </div>

                    <div>
                      <div className="text-xs text-slate-600 mb-1">Coherence</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getScoreBackground(qualityScore.coherence)} transition-all duration-500`}
                            style={{ width: `${qualityScore.coherence}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-slate-700">{qualityScore.coherence}%</span>
                      </div>
                    </div>
                  </div>

                  {qualityScore.recommendations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-slate-200">
                      <div className="text-sm text-slate-700 mb-2 font-medium flex items-center gap-2">
                        <Lightbulb className="w-4 h-4 text-yellow-500" />
                        Improvement Suggestions
                      </div>
                      <ul className="space-y-1">
                        {qualityScore.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-sm text-slate-600 flex items-start gap-2">
                            <ChevronRight className="w-4 h-4 text-[#1863d6] mt-0.5 flex-shrink-0" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 grid-rows-3 bg-gradient-to-br from-slate-100 to-blue-50/50 p-6 rounded-xl shadow-inner">
                <div className="col-span-1 row-span-2">
                  <CanvasBlockView
                    title={BLOCK_TITLES.keyPartners}
                    items={canvas.keyPartners}
                    onAdd={(value) => handleAddToBlock('keyPartners', value)}
                    onRemove={(idx) => handleRemoveFromBlock('keyPartners', idx)}
                    suggestions={suggestions.filter(s => s.block === 'keyPartners')}
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.keyActivities}
                    items={canvas.keyActivities}
                    onAdd={(value) => handleAddToBlock('keyActivities', value)}
                    onRemove={(idx) => handleRemoveFromBlock('keyActivities', idx)}
                    suggestions={suggestions.filter(s => s.block === 'keyActivities')}
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.keyResources}
                    items={canvas.keyResources}
                    onAdd={(value) => handleAddToBlock('keyResources', value)}
                    onRemove={(idx) => handleRemoveFromBlock('keyResources', idx)}
                    suggestions={suggestions.filter(s => s.block === 'keyResources')}
                  />
                </div>

                <div className="col-span-1 row-span-2">
                  <CanvasBlockView
                    title={BLOCK_TITLES.valuePropositions}
                    items={canvas.valuePropositions}
                    onAdd={(value) => handleAddToBlock('valuePropositions', value)}
                    onRemove={(idx) => handleRemoveFromBlock('valuePropositions', idx)}
                    suggestions={suggestions.filter(s => s.block === 'valuePropositions')}
                    highlight
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.customerRelationships}
                    items={canvas.customerRelationships}
                    onAdd={(value) => handleAddToBlock('customerRelationships', value)}
                    onRemove={(idx) => handleRemoveFromBlock('customerRelationships', idx)}
                    suggestions={suggestions.filter(s => s.block === 'customerRelationships')}
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.channels}
                    items={canvas.channels}
                    onAdd={(value) => handleAddToBlock('channels', value)}
                    onRemove={(idx) => handleRemoveFromBlock('channels', idx)}
                    suggestions={suggestions.filter(s => s.block === 'channels')}
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.customerSegments}
                    items={canvas.customerSegments}
                    onAdd={(value) => handleAddToBlock('customerSegments', value)}
                    onRemove={(idx) => handleRemoveFromBlock('customerSegments', idx)}
                    suggestions={suggestions.filter(s => s.block === 'customerSegments')}
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.costStructure}
                    items={canvas.costStructure}
                    onAdd={(value) => handleAddToBlock('costStructure', value)}
                    onRemove={(idx) => handleRemoveFromBlock('costStructure', idx)}
                    suggestions={suggestions.filter(s => s.block === 'costStructure')}
                  />
                </div>

                <div className="col-span-1 row-span-1">
                  <CanvasBlockView
                    title={BLOCK_TITLES.revenueStreams}
                    items={canvas.revenueStreams}
                    onAdd={(value) => handleAddToBlock('revenueStreams', value)}
                    onRemove={(idx) => handleRemoveFromBlock('revenueStreams', idx)}
                    suggestions={suggestions.filter(s => s.block === 'revenueStreams')}
                  />
                </div>
              </div>
            </div>
          </>
        )}

        {mode === 'suggestions' && (
          <BMCSuggestionsPanel
            suggestions={suggestions}
            onApply={(block, suggestion) => handleAddToBlock(block, suggestion)}
            onDismiss={(index) => setSuggestions(prev => prev.filter((_, i) => i !== index))}
            onBack={() => setMode('overview')}
          />
        )}

        {mode === 'compare' && (
          <BMCVersionHistory
            versions={versions}
            currentVersionId={currentVersionId}
            selectedVersions={selectedVersions}
            onSelectVersion={setCurrentVersionId}
            onCompareVersions={setSelectedVersions}
            onRestore={(version) => {
              setCanvas(version.canvas);
              setCurrentVersionId(version.id);
              setMode('overview');
            }}
            onBack={() => setMode('overview')}
          />
        )}

        {mode === 'export' && (
          <BMCExportPanel
            canvas={canvas}
            onExport={handleExport}
            loading={loading}
            onBack={() => setMode('overview')}
          />
        )}

        {mode === 'edit' && (
          <BMCEditMode
            canvas={canvas}
            editingBlock={editingBlock}
            editValue={editValue}
            onStartEdit={handleStartEdit}
            onSaveEdit={handleSaveEdit}
            onCancelEdit={() => setEditingBlock(null)}
            onEditValueChange={setEditValue}
            onAddToBlock={handleAddToBlock}
            onRemoveFromBlock={handleRemoveFromBlock}
            onBack={() => setMode('overview')}
          />
        )}
      </div>
    </div>
  );
};

interface CanvasBlockViewProps {
  title: string;
  items: string[];
  onAdd: (value: string) => void;
  onRemove: (index: number) => void;
  suggestions: BMCSuggestion[];
  highlight?: boolean;
}

const CanvasBlockView: React.FC<CanvasBlockViewProps> = ({
  title,
  items,
  onAdd,
  onRemove,
  suggestions,
  highlight
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [newItem, setNewItem] = useState('');

  const handleAdd = () => {
    if (newItem.trim()) {
      onAdd(newItem.trim());
      setNewItem('');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    onAdd(suggestion);
  };

  return (
    <div className={`bg-white/90 backdrop-blur-sm p-4 rounded-lg shadow-sm border h-full flex flex-col ${highlight ? 'border-[#1863d6]/50 ring-2 ring-[#1863d6]/10' : 'border-slate-200'}`}>
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200">
        <h4 className="font-semibold text-slate-800 text-sm">{title}</h4>
        {suggestions.length > 0 && (
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            className="text-xs text-[#1863d6] hover:text-[#151983] flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" />
            {suggestions.length} {suggestions.length === 1 ? 'suggestion' : 'suggestions'}
            <ChevronDown className={`w-3 h-3 transition-transform ${showSuggestions ? 'rotate-180' : ''}`} />
          </button>
        )}
      </div>

      {showSuggestions && suggestions.length > 0 && (
        <div className="mb-3 p-2 bg-[#1863d6]/5 rounded-lg">
          <div className="text-xs text-[#1863d6] mb-2 font-medium">AI Suggestions:</div>
          <div className="space-y-1">
            {suggestions.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(sug.suggestion)}
                className="w-full text-left text-xs p-2 bg-white rounded hover:bg-[#1863d6]/10 transition-colors flex items-center justify-between"
              >
                <span>{sug.suggestion}</span>
                <Plus className="w-3 h-3 text-[#1863d6]" />
              </button>
            ))}
          </div>
        </div>
      )}

      <ul className="space-y-2 flex-1 overflow-y-auto mb-3">
        {items.map((item, idx) => (
          <li key={idx} className="text-sm text-slate-700 flex items-start gap-2 group">
            <span className="w-1.5 h-1.5 rounded-full bg-[#1863d6] mt-1.5 flex-shrink-0" />
            <span className="flex-1">{item}</span>
            <button
              onClick={() => onRemove(idx)}
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 rounded transition-all"
            >
              <X className="w-3 h-3 text-red-400" />
            </button>
          </li>
        ))}
        {items.length === 0 && (
          <li className="text-sm text-slate-400 italic">No items yet...</li>
        )}
      </ul>

      <div className="flex gap-2">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          placeholder="Add item..."
          className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg field-focus"
        />
        <button
          onClick={handleAdd}
          disabled={!newItem.trim()}
          className="px-3 py-2 bg-[#1863d6] text-white rounded-lg hover:bg-[#1554b8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

interface BMCSuggestionsPanelProps {
  suggestions: BMCSuggestion[];
  onApply: (block: keyof BusinessCanvasData, suggestion: string) => void;
  onDismiss: (index: number) => void;
  onBack: () => void;
}

const BMCSuggestionsPanel: React.FC<BMCSuggestionsPanelProps> = ({
  suggestions,
  onApply,
  onDismiss,
  onBack
}) => {
  const [filter, setFilter] = useState<'all' | 'profile' | 'ai' | 'template'>('all');

  const filteredSuggestions = suggestions.filter(s => 
    filter === 'all' || s.source === filter
  );

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Canvas
        </button>
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-[#1863d6]" />
          AI-Powered Suggestions
        </h2>
        <div className="w-24" />
      </div>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === 'all' ? 'bg-[#1863d6] text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}
        >
          All ({suggestions.length})
        </button>
        <button
          onClick={() => setFilter('profile')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === 'profile' ? 'bg-[#1863d6] text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}
        >
          From Profile ({suggestions.filter(s => s.source === 'profile').length})
        </button>
        <button
          onClick={() => setFilter('ai')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === 'ai' ? 'bg-[#1863d6] text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}
        >
          AI Generated ({suggestions.filter(s => s.source === 'ai').length})
        </button>
        <button
          onClick={() => setFilter('template')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${filter === 'template' ? 'bg-[#1863d6] text-white' : 'bg-white text-slate-600 hover:bg-slate-100'}`}
        >
          Templates ({suggestions.filter(s => s.source === 'template').length})
        </button>
      </div>

      {filteredSuggestions.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-sm">
          <Lightbulb className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-600">No suggestions available. Add more details to your profile to get personalized recommendations.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredSuggestions.map((suggestion, idx) => (
            <div
              key={idx}
              className="bg-white rounded-xl p-4 shadow-sm border border-slate-200 hover:border-[#1863d6]/30 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      suggestion.source === 'profile' ? 'bg-blue-100 text-blue-700' :
                      suggestion.source === 'ai' ? 'bg-purple-100 text-purple-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {suggestion.source === 'profile' ? 'From Profile' :
                       suggestion.source === 'ai' ? 'AI Generated' : 'Template'}
                    </span>
                    <span className="text-xs text-slate-500">{Math.round(suggestion.confidence * 100)}% confidence</span>
                  </div>
                  <div className="text-sm font-medium text-slate-800 mb-1">{BLOCK_TITLES[suggestion.block]}</div>
                  <div className="text-sm text-slate-600">{suggestion.suggestion}</div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => onApply(suggestion.block, suggestion.suggestion)}
                    className="flex items-center gap-1 px-3 py-1.5 bg-[#1863d6] text-white text-sm rounded-lg hover:bg-[#1554b8] transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    Add
                  </button>
                  <button
                    onClick={() => onDismiss(suggestions.indexOf(suggestion))}
                    className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4 text-slate-400" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

interface BMCVersionHistoryProps {
  versions: BMCVersion[];
  currentVersionId: string | null;
  selectedVersions: [string | null, string | null];
  onSelectVersion: (id: string | null) => void;
  onCompareVersions: (versions: [string | null, string | null]) => void;
  onRestore: (version: BMCVersion) => void;
  onBack: () => void;
}

const BMCVersionHistory: React.FC<BMCVersionHistoryProps> = ({
  versions,
  currentVersionId,
  selectedVersions,
  onSelectVersion,
  onCompareVersions,
  onRestore,
  onBack
}) => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Canvas
        </button>
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <History className="w-6 h-6 text-[#1863d6]" />
          Version History
        </h2>
        <div className="w-24" />
      </div>

      {versions.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-sm">
          <History className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-600">No saved versions yet. Save your canvas to track changes over time.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {versions.map((version, idx) => (
            <div
              key={version.id}
              className={`bg-white rounded-xl p-4 shadow-sm border transition-all cursor-pointer ${
                currentVersionId === version.id ? 'border-[#1863d6] ring-2 ring-[#1863d6]/10' : 'border-slate-200 hover:border-[#1863d6]/30'
              } ${selectedVersions.includes(version.id) ? 'bg-[#1863d6]/5' : ''}`}
              onClick={() => onSelectVersion(version.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {currentVersionId === version.id && (
                      <span className="px-2 py-0.5 text-xs bg-[#1863d6] text-white rounded-full">Current</span>
                    )}
                    <span className="text-sm text-slate-600">
                      {new Date(version.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {version.notes && (
                    <p className="text-sm text-slate-800 mb-2">{version.notes}</p>
                  )}
                  <div className="text-xs text-slate-500">
                    {Object.values(version.canvas).reduce((sum, items) => sum + items.length, 0)} items across 9 blocks
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRestore(version);
                    }}
                    className="flex items-center gap-1 px-3 py-1.5 bg-white border border-slate-200 text-slate-700 text-sm rounded-lg hover:border-[#1863d6] hover:text-[#1863d6] transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Restore
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

interface BMCExportPanelProps {
  canvas: BusinessCanvasData;
  onExport: (format: 'pdf' | 'png' | 'json') => void;
  loading: boolean;
  onBack: () => void;
}

const BMCExportPanel: React.FC<BMCExportPanelProps> = ({
  canvas,
  onExport,
  loading,
  onBack
}) => {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Canvas
        </button>
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <Download className="w-6 h-6 text-[#1863d6]" />
          Export Canvas
        </h2>
        <div className="w-24" />
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm">
        <p className="text-slate-600 mb-6">Choose your preferred export format:</p>

        <div className="space-y-4">
          <button
            onClick={() => onExport('json')}
            disabled={loading}
            className="w-full flex items-center gap-4 p-4 border border-slate-200 rounded-xl hover:border-[#1863d6] hover:bg-[#1863d6]/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-slate-600" />
            </div>
            <div className="flex-1">
              <div className="font-medium text-slate-900">JSON Format</div>
              <div className="text-sm text-slate-600">Machine-readable format for integration</div>
            </div>
            <Download className="w-5 h-5 text-slate-400" />
          </button>

          <button
            onClick={() => onExport('png')}
            disabled={loading}
            className="w-full flex items-center gap-4 p-4 border border-slate-200 rounded-xl hover:border-[#1863d6] hover:bg-[#1863d6]/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
              <Image className="w-6 h-6 text-slate-600" />
            </div>
            <div className="flex-1">
              <div className="font-medium text-slate-900">PNG Image</div>
              <div className="text-sm text-slate-600">High-quality image for presentations</div>
            </div>
            <Download className="w-5 h-5 text-slate-400" />
          </button>

          <button
            onClick={() => onExport('pdf')}
            disabled={loading}
            className="w-full flex items-center gap-4 p-4 border border-slate-200 rounded-xl hover:border-[#1863d6] hover:bg-[#1863d6]/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
          >
            <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-slate-600" />
            </div>
            <div className="flex-1">
              <div className="font-medium text-slate-900">PDF Document</div>
              <div className="text-sm text-slate-600">Print-ready document format</div>
            </div>
            <Download className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {loading && (
          <div className="mt-6 flex items-center justify-center gap-2 text-slate-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating export...
          </div>
        )}
      </div>
    </div>
  );
};

interface BMCEditModeProps {
  canvas: BusinessCanvasData;
  editingBlock: keyof BusinessCanvasData | null;
  editValue: string;
  onStartEdit: (block: keyof BusinessCanvasData) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  onEditValueChange: (value: string) => void;
  onAddToBlock: (block: keyof BusinessCanvasData, value: string) => void;
  onRemoveFromBlock: (block: keyof BusinessCanvasData, index: number) => void;
  onBack: () => void;
}

const BMCEditMode: React.FC<BMCEditModeProps> = ({
  canvas,
  editingBlock,
  editValue,
  onStartEdit,
  onSaveEdit,
  onCancelEdit,
  onEditValueChange,
  onAddToBlock,
  onRemoveFromBlock,
  onBack
}) => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Overview
        </button>
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <Edit3 className="w-6 h-6 text-[#1863d6]" />
          Edit Canvas
        </h2>
        <div className="w-24" />
      </div>

      <div className="grid grid-cols-3 gap-4 grid-rows-3 bg-gradient-to-br from-slate-100 to-blue-50/50 p-6 rounded-xl shadow-inner">
        {Object.entries(BLOCK_TITLES).map(([key, title]) => {
          const blockKey = key as keyof BusinessCanvasData;
          const items = canvas[blockKey] || [];
          const isEditing = editingBlock === blockKey;

          return (
            <div key={blockKey} className="bg-white/90 backdrop-blur-sm p-4 rounded-lg shadow-sm border border-slate-200 h-full flex flex-col">
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200">
                <h4 className="font-semibold text-slate-800 text-sm">{title}</h4>
                <button
                  onClick={() => isEditing ? onCancelEdit() : onStartEdit(blockKey)}
                  className={`p-1.5 rounded-lg transition-colors ${
                    isEditing 
                      ? 'bg-red-50 text-red-600 hover:bg-red-100' 
                      : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {isEditing ? <X className="w-3.5 h-3.5" /> : <Edit3 className="w-3.5 h-3.5" />}
                </button>
              </div>

              {isEditing ? (
                <div className="flex-1 flex flex-col gap-2">
                  <textarea
                    value={editValue}
                    onChange={(e) => onEditValueChange(e.target.value)}
                    placeholder="Enter items (one per line)..."
                    className="flex-1 w-full p-3 text-sm border border-[#1863d6]/30 rounded-lg focus:ring-2 focus:ring-[#1863d6]/20 focus:border-[#1863d6] outline-none resize-none bg-[#1863d6]/5"
                    autoFocus
                  />
                  <button
                    onClick={onSaveEdit}
                    className="flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white text-sm rounded-lg hover:shadow-md transition-all"
                  >
                    <Save className="w-4 h-4" />
                    Save Changes
                  </button>
                </div>
              ) : (
                <ul className="space-y-2 flex-1 overflow-y-auto mb-3">
                  {items.map((item, idx) => (
                    <li key={idx} className="text-sm text-slate-700 flex items-start gap-2 group">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#1863d6] mt-1.5 flex-shrink-0" />
                      <span className="flex-1">{item}</span>
                      <button
                        onClick={() => onRemoveFromBlock(blockKey, idx)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-50 rounded transition-all"
                      >
                        <X className="w-3 h-3 text-red-400" />
                      </button>
                    </li>
                  ))}
                  {items.length === 0 && (
                    <li className="text-sm text-slate-400 italic">Click edit to add items...</li>
                  )}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ImprovedBMCWorkflow;
