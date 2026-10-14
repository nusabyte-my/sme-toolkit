/**
 * GrowthRoadmap Component
 * Displays growth plan with opportunities and projections
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState } from 'react';
import { GrowthPlan, GrowthOpportunity } from '../../types';
import { Calendar, TrendingUp, DollarSign, Clock, Layers } from 'lucide-react';

interface GrowthRoadmapProps {
  plan: GrowthPlan;
  loading: boolean;
  onGenerate: () => void;
  contextProvided: boolean;
}

const GrowthRoadmap: React.FC<GrowthRoadmapProps> = ({ plan, loading, onGenerate, contextProvided }) => {
  const [selectedOpp, setSelectedOpp] = useState<GrowthOpportunity | null>(null);
  const [projectionMode, setProjectionMode] = useState<'conservative' | 'optimistic'>('optimistic');

  // Simple revenue projection simulator based on opportunities
  const calculateProjection = (monthIndex: number) => {
    // Base linear growth
    let growth = (monthIndex + 1) * 5; 
    
    // Add impact from high-confidence opportunities
    plan.growth_opportunities.forEach(opp => {
      // Parse ROI string to number (simplified)
      const roiMatch = opp.expected_roi.match(/(\d+)%/);
      const roi = roiMatch ? parseInt(roiMatch[1]) : 10;
      
      if (monthIndex > 2) { // Lag time
        const factor = projectionMode === 'optimistic' ? 1.5 : 0.8;
        growth += (roi * opp.confidence_score * factor * (monthIndex - 2)) / 10;
      }
    });
    
    return Math.min(Math.round(growth), 100); // Cap at 100 for relative chart
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      {/* Top Section: Timeline & Projections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Revenue Projection Chart */}
        <div className="lg:col-span-2 backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl p-6 shadow-sm relative overflow-hidden hover:shadow-md transition-shadow duration-200">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="font-bold text-[#0f172a] flex items-center">
                <TrendingUp className="w-5 h-5 text-[#1863d6] mr-2" />
                Revenue Projection
              </h3>
              <p className="text-xs text-[#94a3b8]">Based on {plan.growth_opportunities.length} active opportunities</p>
            </div>
            <div className="flex bg-[#e2e8f0] rounded-lg p-1">
              <button
                onClick={() => setProjectionMode('conservative')}
                className={`text-xs px-3 py-1 rounded-md transition-all duration-200 ${projectionMode === 'conservative' ? 'bg-white shadow-sm text-[#0f172a]' : 'text-[#94a3b8] hover:text-[#334155]'}`}
              >
                Conservative
              </button>
              <button
                onClick={() => setProjectionMode('optimistic')}
                className={`text-xs px-3 py-1 rounded-md transition-all duration-200 ${projectionMode === 'optimistic' ? 'bg-white shadow-sm text-[#1863d6]' : 'text-[#94a3b8] hover:text-[#334155]'}`}
              >
                Optimistic
              </button>
            </div>
          </div>

          <div className="h-40 flex items-end justify-between gap-2 mt-4 px-2">
            {[0,1,2,3,4,5].map(m => (
              <div key={m} className="flex-1 flex flex-col justify-end group">
                <div
                  className={`w-full rounded-t-sm transition-all duration-700 ease-out ${projectionMode === 'optimistic' ? 'bg-gradient-to-t from-[#1863d6] to-[#151983]' : 'bg-[#94a3b8]'}`}
                  style={{ height: `${calculateProjection(m)}%` }}
                >
                  <div className="opacity-0 group-hover:opacity-100 absolute -top-8 left-1/2 -translate-x-1/2 bg-[#0f172a] text-white text-[10px] py-1 px-2 rounded pointer-events-none">
                    +{calculateProjection(m)}%
                  </div>
                </div>
                <div className="text-center text-[10px] text-[#94a3b8] mt-2 border-t border-[#e2e8f0] pt-1">
                  M{m+1}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Roadmap Summary Card */}
        <div className="bg-gradient-to-br from-[#001f3d] to-[#151983] text-white p-6 rounded-xl shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold mb-1">{plan.title}</h3>
            <p className="text-[#b6cbe1] text-sm">{plan.timeframe}</p>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#b6cbe1]">Growth Potential</span>
              <span className="text-xl font-bold text-[#10b981]">{Math.round(plan.overall_growth_potential * 100)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
              <div className="bg-gradient-to-r from-[#10b981] to-[#059669] h-1.5 rounded-full" style={{ width: `${plan.overall_growth_potential * 100}%` }}></div>
            </div>
            
            <div className="pt-4 border-t border-white/10">
              <button onClick={onGenerate} className="w-full bg-white/10 hover:bg-white/20 text-white text-sm py-2 rounded-lg transition-all duration-200">
                Regenerate Plan
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Opportunities Grid (Kanban-ish) */}
      <div>
        <h3 className="font-semibold text-[#0f172a] mb-4 flex items-center">
          <Layers className="w-5 h-5 mr-2 text-[#1863d6]" />
          Strategic Opportunities
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plan.growth_opportunities.map(opp => (
            <div
              key={opp.id}
              className={`border rounded-xl p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
                selectedOpp?.id === opp.id ? 'border-[#1863d6] bg-[#1863d6]/10' : 'border-[#e2e8f0] bg-white/80'
              }`}
              onClick={() => setSelectedOpp(opp)}
            >
              <div className="flex justify-between items-start mb-3">
                <div className="bg-[#1863d6]/10 text-[#1863d6] text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wide">
                  {opp.type}
                </div>
                {opp.confidence_score > 0.8 && (
                  <TrendingUp className="w-4 h-4 text-[#10b981]" />
                )}
              </div>
              <h4 className="font-bold text-[#0f172a] mb-2">{opp.title}</h4>
              
              <div className="grid grid-cols-2 gap-2 text-xs mt-4">
                <div className="flex items-center text-[#94a3b8]">
                  <DollarSign className="w-3 h-3 mr-1" />
                  {opp.expected_roi} ROI
                </div>
                <div className="flex items-center text-[#94a3b8]">
                  <Clock className="w-3 h-3 mr-1" />
                  {opp.time_to_market}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detail Panel */}
      {selectedOpp && (
        <div className="bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9] border border-[#e2e8f0] rounded-xl p-6 animate-in slide-in-from-top-2 backdrop-blur-sm">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-bold text-[#0f172a]">Action Plan: {selectedOpp.title}</h3>
            <button onClick={() => setSelectedOpp(null)} className="text-[#94a3b8] hover:text-[#334155] text-sm transition-colors duration-200">Close</button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-sm font-semibold text-[#334155] mb-2 uppercase tracking-wide">Key Actions</h4>
              <ul className="space-y-2">
                {selectedOpp.key_actions.map((action, i) => (
                  <li key={i} className="flex items-start text-sm text-[#64748b]">
                    <span className="w-5 h-5 rounded-full bg-white border border-[#1863d6]/30 text-[#1863d6] flex items-center justify-center text-xs mr-2 flex-shrink-0 font-medium">{i+1}</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-[#334155] mb-2 uppercase tracking-wide">Risk Mitigation</h4>
              <ul className="space-y-2">
                {selectedOpp.mitigation_strategies.map((strat, i) => (
                  <li key={i} className="flex items-start text-sm text-[#64748b]">
                    <span className="w-1.5 h-1.5 bg-[#f59e0b] rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                    {strat}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GrowthRoadmap;
