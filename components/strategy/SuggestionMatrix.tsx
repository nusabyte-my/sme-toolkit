/**
 * SuggestionMatrix Component
 * Displays strategic prioritization matrix with suggestions
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState } from 'react';
import { BusinessSuggestions, BusinessOpportunity, PartnershipOpportunity, MarketExpansion, InnovationSuggestion } from '../../types';
import { Lightbulb, Users, Globe, Zap, Filter, ArrowUpRight } from 'lucide-react';

interface SuggestionMatrixProps {
  suggestions: BusinessSuggestions;
  loading: boolean;
  onGenerate: () => void;
  contextProvided: boolean;
}

type AnySuggestion = (BusinessOpportunity | PartnershipOpportunity | MarketExpansion | InnovationSuggestion) & {
  category: string;
  x: number;
  y: number;
  description: string;
};

const SuggestionMatrix: React.FC<SuggestionMatrixProps> = ({ suggestions, loading, onGenerate, contextProvided }) => {
  const [filter, setFilter] = useState<string>('all');
  const [selectedItem, setSelectedItem] = useState<AnySuggestion | null>(null);

  // Normalize suggestions into a single array for the matrix
  const allSuggestions: AnySuggestion[] = [
    ...suggestions.new_opportunities.map(s => ({ ...s, category: 'Opportunity', impact: 8, effort: 6 })),
    ...suggestions.partnership_opportunities.map(s => ({ ...s, category: 'Partnership', impact: 6, effort: 4 })),
    ...suggestions.market_expansions.map(s => ({ ...s, category: 'Expansion', impact: 9, effort: 8 })),
    ...suggestions.innovation_suggestions.map(s => ({ ...s, category: 'Innovation', impact: 7, effort: 5 })),
  ].map(s => ({
    ...s,
    // Mock coordinates for the matrix if not present (randomized slightly for demo visual)
    x: Math.random() * 90 + 5, // Effort (0-100)
    y: Math.random() * 90 + 5, // Impact (0-100)
    // Only some union members carry `description` — normalize to an optional string
    description: 'description' in s && s.description ? s.description : s.title,
  }));

  const filtered = filter === 'all' ? allSuggestions : allSuggestions.filter(s => s.category === filter);

  const getIcon = (cat: string) => {
    switch (cat) {
      case 'Opportunity': return Lightbulb;
      case 'Partnership': return Users;
      case 'Expansion': return Globe;
      case 'Innovation': return Zap;
      default: return Lightbulb;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h3 className="font-bold text-[#0f172a] text-lg">Strategic Prioritization Matrix</h3>
        
        <div className="flex gap-2 bg-white/80 backdrop-blur-sm p-1 rounded-lg border border-[#b6cbe1]/30 shadow-sm">
          {['all', 'Opportunity', 'Partnership', 'Expansion', 'Innovation'].map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                filter === cat
                  ? 'bg-[#1863d6]/10 text-[#1863d6]'
                  : 'text-[#64748b] hover:bg-[#f8fafc]'
              }`}
            >
              {cat === 'all' ? 'All' : cat}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* The Matrix Visualization */}
        <div className="lg:col-span-2 relative aspect-[4/3] backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl shadow-sm overflow-hidden">
          {/* Background Grid */}
          <div className="absolute inset-0 grid grid-cols-2 grid-rows-2">
            <div className="border-r border-b border-[#e2e8f0] bg-[#f8fafc]/30 p-2 text-xs text-[#94a3b8] font-medium uppercase">Low Impact / Low Effort</div>
            <div className="border-b border-[#e2e8f0] bg-[#10b981]/10 p-2 text-xs text-[#10b981] font-medium uppercase text-right">High Impact / Low Effort (Quick Wins)</div>
            <div className="border-r border-[#e2e8f0] bg-[#f59e0b]/10 p-2 flex items-end text-xs text-[#f59e0b] font-medium uppercase">Low Impact / High Effort</div>
            <div className="bg-[#1863d6]/10 p-2 flex items-end justify-end text-xs text-[#1863d6] font-medium uppercase">High Impact / High Effort (Big Bets)</div>
          </div>

          {/* Axes Labels */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-bold text-[#94a3b8] tracking-widest uppercase">Effort →</div>
          <div className="absolute left-2 top-1/2 -translate-y-1/2 -rotate-90 text-xs font-bold text-[#94a3b8] tracking-widest uppercase">Impact →</div>

          {/* Data Points */}
          {filtered.map((item, i) => {
            const Icon = getIcon(item.category);
            return (
              <div
                key={i}
                className={`absolute w-8 h-8 rounded-full flex items-center justify-center shadow-sm cursor-pointer transition-transform hover:scale-125 group z-10 ${
                  selectedItem?.title === item.title ? 'ring-4 ring-[#1863d6]/30 z-20' : ''
                }`}
                style={{ left: `${item.x}%`, bottom: `${item.y}%`, backgroundColor: 'white' }}
                onClick={() => setSelectedItem(item)}
              >
                <Icon className={`w-4 h-4 ${
                  item.category === 'Opportunity' ? 'text-[#1863d6]' :
                  item.category === 'Partnership' ? 'text-[#ec4899]' :
                  item.category === 'Expansion' ? 'text-[#f59e0b]' : 'text-[#151983]'
                }`} />
                
                {/* Tooltip */}
                <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-48 bg-[#001f3d] text-white text-xs rounded-lg p-2 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity text-center">
                  <p className="font-bold truncate">{item.title}</p>
                  <p className="text-[#b6cbe1]">{item.category}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Sidebar Detail / List */}
        <div className="lg:col-span-1 backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl p-6 shadow-sm flex flex-col h-full max-h-[600px]">
          {selectedItem ? (
            <div className="animate-in fade-in slide-in-from-right-4">
              <div className="flex justify-between items-start mb-4">
                <span className="text-[10px] uppercase font-bold tracking-wide bg-[#f8fafc] text-[#64748b] px-2 py-1 rounded">
                  {selectedItem.category}
                </span>
                <button onClick={() => setSelectedItem(null)} className="text-[#94a3b8] hover:text-[#64748b] text-sm">Clear</button>
              </div>
              
              <h3 className="text-xl font-bold text-[#0f172a] mb-2">{selectedItem.title}</h3>
              <p className="text-sm text-[#64748b] mb-6">{selectedItem.description}</p>
              
              <div className="space-y-4">
                <div className="p-3 bg-[#1863d6]/10 rounded-lg border border-[#1863d6]/20">
                  <p className="text-xs text-[#1863d6] font-bold uppercase mb-1">Potential Value</p>
                  <p className="font-medium text-[#0f172a]">
                    {(selectedItem as any).potential_value || (selectedItem as any).estimated_value || (selectedItem as any).potential_revenue || 'High Impact'}
                  </p>
                </div>
                
                {(selectedItem as any).required_investments && (
                  <div>
                    <h4 className="text-sm font-semibold text-[#0f172a] mb-2">Requirements</h4>
                    <ul className="list-disc pl-4 space-y-1">
                      {(selectedItem as any).required_investments.map((req: string, i: number) => (
                        <li key={i} className="text-xs text-[#64748b]">{req}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              <button className="w-full mt-6 bg-gradient-to-r from-[#1863d6] to-[#151983] text-white py-2 rounded-lg text-sm font-medium hover:shadow-md transition-all duration-200 flex items-center justify-center">
                Add to Roadmap <ArrowUpRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col h-full">
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-semibold text-[#0f172a]">Top Suggestions</h4>
                <button
                  onClick={onGenerate}
                  className="text-xs text-[#1863d6] hover:underline disabled:opacity-50"
                  disabled={loading || !contextProvided}
                >
                  Regenerate
                </button>
              </div>
              
              <div className="overflow-y-auto pr-2 space-y-3 flex-1">
                {filtered.slice(0, 5).map((item, i) => (
                  <div
                    key={i}
                    onClick={() => setSelectedItem(item)}
                    className="p-3 border border-[#e2e8f0] rounded-lg hover:bg-[#f8fafc] cursor-pointer transition-colors"
                  >
                    <h5 className="text-sm font-medium text-[#0f172a] line-clamp-1">{item.title}</h5>
                    <p className="text-xs text-[#64748b] mt-1 line-clamp-2">{item.description}</p>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-[#e2e8f0] text-center text-xs text-[#94a3b8]">
                Select a bubble on the matrix or an item above for details.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SuggestionMatrix;
