/**
 * GoalDashboard Component
 * Displays strategic goals with progress tracking
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState } from 'react';
import { Target, CheckCircle2, AlertTriangle, TrendingUp, ChevronRight, BarChart } from 'lucide-react';
import { Goal } from '../../types';
import { ProgressBar } from './ProgressBar';

interface GoalDashboardProps {
  goals: Goal[];
  loading: boolean;
  onGenerate: () => void;
  contextProvided: boolean;
}

const GoalDashboard: React.FC<GoalDashboardProps> = ({ goals, loading, onGenerate, contextProvided }) => {
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);

  // Goal has no `progress` field — derive it from completed milestones so the
  // UI shows real data instead of a phantom property.
  const goalProgress = (g: Goal): number => {
    const milestones = g.key_milestones || [];
    if (milestones.length === 0) return 0;
    const now = Date.now();
    const done = milestones.filter(m => m.target_date && new Date(m.target_date).getTime() < now).length;
    return Math.round((done / milestones.length) * 100);
  };

  const overallProgress = goals.length > 0
    ? goals.reduce((acc, g) => acc + goalProgress(g), 0) / goals.length
    : 0;

  // Mock predictive data if not present (AI would normally provide this)
  const getSuccessProbability = (goal: Goal) => {
    // Simple heuristic for demo: High priority + high BMC alignment = high probability
    const alignment = goal.bmc_alignment?.alignment_score || 0.5;
    return Math.min(Math.round(alignment * 100 + goalProgress(goal) * 0.2), 95);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      
      {/* KPI Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-[#94a3b8] text-sm font-medium">Active Goals</h4>
            <Target className="w-5 h-5 text-[#1863d6]" />
          </div>
          <p className="text-3xl font-bold text-[#0f172a]">{goals.length}</p>
          <p className="text-xs text-[#64748b] mt-1">Across {new Set(goals.map(g => g.category)).size} categories</p>
        </div>
 
        <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-[#94a3b8] text-sm font-medium">Overall Progress</h4>
            <BarChart className="w-5 h-5 text-[#1863d6]" />
          </div>
          <p className="text-3xl font-bold text-[#0f172a]">{Math.round(overallProgress)}%</p>
          <div className="mt-2">
            <div className="w-full bg-[#e2e8f0] rounded-full h-1.5 overflow-hidden">
              <div className="bg-gradient-to-r from-[#1863d6] to-[#151983] h-1.5 rounded-full transition-all duration-1000" style={{ width: `${overallProgress}%` }}></div>
            </div>
          </div>
        </div>
 
        <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 p-5 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200">
          <div className="flex justify-between items-start mb-2">
            <h4 className="text-[#94a3b8] text-sm font-medium">On Track</h4>
            <CheckCircle2 className="w-5 h-5 text-[#10b981]" />
          </div>
          <p className="text-3xl font-bold text-[#0f172a]">
            {goals.filter(g => goalProgress(g) > 20).length}
          </p>
          <p className="text-xs text-[#10b981] mt-1 flex items-center">
            <TrendingUp className="w-3 h-3 mr-1" /> High Momentum
          </p>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Goals List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-semibold text-[#0f172a]">Strategic Goals</h3>
            <button
              onClick={onGenerate}
              disabled={loading || !contextProvided}
              className="text-xs bg-[#1863d6]/10 text-[#1863d6] px-3 py-1.5 rounded-lg hover:bg-[#1863d6]/20 transition-all duration-200 disabled:opacity-50"
            >
              {loading ? 'Thinking...' : 'Refresh Goals'}
            </button>
          </div>
          
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
            {goals.length === 0 ? (
              <div className="text-center p-8 bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9] rounded-lg border border-dashed border-[#e2e8f0] text-[#94a3b8] text-sm">
                No goals generated yet.
              </div>
            ) : (
              goals.map(goal => (
                <div
                  key={goal.id}
                  onClick={() => setSelectedGoal(goal)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                    selectedGoal?.id === goal.id
                      ? 'bg-[#1863d6]/10 border-[#1863d6] shadow-sm ring-1 ring-[#1863d6]/30'
                      : 'bg-white/80 border-[#e2e8f0] hover:border-[#1863d6] hover:shadow-md'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase font-bold tracking-wide ${
                      goal.priority === 'high' ? 'bg-[#ef4444]/10 text-[#ef4444]' :
                      goal.priority === 'medium' ? 'bg-[#f59e0b]/10 text-[#f59e0b]' :
                      'bg-[#10b981]/10 text-[#10b981]'
                    }`}>
                      {goal.priority}
                    </span>
                    <ChevronRight className={`w-4 h-4 text-[#94a3b8] ${selectedGoal?.id === goal.id ? 'rotate-90 text-[#1863d6]' : ''} transition-transform`} />
                  </div>
                  <h4 className="font-medium text-[#0f172a] text-sm mb-1 line-clamp-2">{goal.title}</h4>
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex-1">
                      <div className="w-full bg-[#e2e8f0] rounded-full h-1 overflow-hidden">
                        <div className="bg-gradient-to-r from-[#1863d6] to-[#151983] h-1 rounded-full" style={{ width: `${goalProgress(goal)}%` }}></div>
                      </div>
                    </div>
                    <span className="text-xs text-[#94a3b8] font-medium">{goalProgress(goal)}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Detail View */}
        <div className="lg:col-span-2">
          {selectedGoal ? (
            <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl p-6 shadow-sm h-full">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-[#0f172a] mb-2">{selectedGoal.title}</h2>
                  <p className="text-[#64748b] text-sm">{selectedGoal.description}</p>
                </div>
                <div className="text-center bg-gradient-to-br from-[#10b981]/10 to-[#059669]/10 p-3 rounded-lg border border-[#10b981]/20">
                  <div className="text-2xl font-bold text-[#10b981]">{getSuccessProbability(selectedGoal)}%</div>
                  <div className="text-[10px] text-[#94a3b8] uppercase tracking-wide font-semibold">Success Prob.</div>
                </div>
              </div>

              {/* Insights Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="text-sm font-semibold text-[#0f172a] mb-3 flex items-center">
                    <CheckCircle2 className="w-4 h-4 text-[#1863d6] mr-2" />
                    Success Metrics (KPIs)
                  </h4>
                  <ul className="space-y-2">
                    {selectedGoal.success_metrics?.map((metric, i) => (
                      <li key={i} className="text-sm text-[#64748b] flex items-start">
                        <span className="w-1.5 h-1.5 bg-[#1863d6] rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                        {metric}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-[#0f172a] mb-3 flex items-center">
                    <AlertTriangle className="w-4 h-4 text-[#f59e0b] mr-2" />
                    Potential Obstacles
                  </h4>
                  <ul className="space-y-2">
                    {selectedGoal.potential_obstacles?.map((obs, i) => (
                      <li key={i} className="text-sm text-[#64748b] flex items-start">
                        <span className="w-1.5 h-1.5 bg-[#f59e0b] rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                        {obs}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Actionable Milestones */}
              <div>
                <h4 className="text-sm font-semibold text-[#0f172a] mb-4">Milestone Timeline</h4>
                <div className="relative border-l-2 border-[#e2e8f0] pl-6 space-y-6 ml-2">
                  {selectedGoal.key_milestones?.map((milestone, i) => (
                    <div key={i} className="relative">
                      <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 border-white bg-gradient-to-br from-[#1863d6] to-[#151983] shadow-sm"></div>
                      <h5 className="text-sm font-medium text-[#0f172a]">{milestone.milestone}</h5>
                      <p className="text-xs text-[#94a3b8] mt-0.5">{milestone.target_date}</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ) : (
            <div className="bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9] border border-dashed border-[#e2e8f0] rounded-xl h-full flex flex-col items-center justify-center text-[#94a3b8] p-8">
              <Target className="w-12 h-12 mb-3 opacity-20 text-[#1863d6]" />
              <p>Select a goal to view actionable insights and predictions.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoalDashboard;
