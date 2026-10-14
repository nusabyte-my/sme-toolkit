/**
 * CostingAdvisor Component
 * Displays financial analysis and costing recommendations
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState } from 'react';
import { DollarSign, PieChart, TrendingUp, ArrowRight, Loader2, Send } from 'lucide-react';
import { CostingAnalysis } from '../../types';

interface CostingAdvisorProps {
  onAnalyze: (data: any) => Promise<void>;
  loading: boolean;
  analysis: CostingAnalysis | null;
  defaultContext: string;
}

const CostingAdvisor: React.FC<CostingAdvisorProps> = ({ 
  onAnalyze, 
  loading, 
  analysis,
  defaultContext 
}) => {
  const [step, setStep] = useState<'input' | 'results'>('input');
  const [financialContext, setFinancialContext] = useState(defaultContext);
  
  // Simple structured inputs for more precise AI guidance
  const [fixedCosts, setFixedCosts] = useState('');
  const [variableCosts, setVariableCosts] = useState('');
  const [revenue, setRevenue] = useState('');

  const handleSubmit = async () => {
    // Combine structured data with free text context
    const combinedContext = `
      Context: ${financialContext}
      Financial Data Provided:
      - Estimated Fixed Costs: ${fixedCosts}
      - Estimated Variable Costs: ${variableCosts}
      - Current/Projected Revenue: ${revenue}
    `.trim();

    await onAnalyze({ context: combinedContext });
    setStep('results');
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-[#e2e8f0] bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9]">
           <h3 className="font-semibold text-[#0f172a] flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-[#1863d6]" />
              Costing & Financial Analysis
           </h3>
           <p className="text-sm text-[#94a3b8] mt-1">
              Provide your financial details to get a breakdown of costs, pricing strategies, and break-even analysis.
           </p>
        </div>
         
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-[#334155] mb-2">Business Context</label>
            <textarea
              value={financialContext}
              onChange={(e) => setFinancialContext(e.target.value)}
              className="w-full p-3 border border-[#e2e8f0] rounded-lg text-sm focus:ring-2 focus:ring-[#1863d6]/50 focus:border-[#1863d6] outline-none h-24 resize-none bg-white/50 backdrop-blur-sm transition-all duration-200"
              placeholder="Describe your business model, product/service, and target market..."
            />
          </div>
 
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#334155] mb-2">Est. Fixed Costs (Monthly)</label>
              <input
                value={fixedCosts}
                onChange={(e) => setFixedCosts(e.target.value)}
                className="w-full p-2.5 border border-[#e2e8f0] rounded-lg text-sm focus:ring-2 focus:ring-[#1863d6]/50 focus:border-[#1863d6] outline-none bg-white/50 backdrop-blur-sm transition-all duration-200"
                placeholder="e.g. $5000 (Rent, Salaries)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#334155] mb-2">Est. Variable Costs (Per Unit)</label>
              <input
                value={variableCosts}
                onChange={(e) => setVariableCosts(e.target.value)}
                className="w-full p-2.5 border border-[#e2e8f0] rounded-lg text-sm focus:ring-2 focus:ring-[#1863d6]/50 focus:border-[#1863d6] outline-none bg-white/50 backdrop-blur-sm transition-all duration-200"
                placeholder="e.g. $10 (Materials, Shipping)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#334155] mb-2">Target Price / Revenue</label>
              <input
                value={revenue}
                onChange={(e) => setRevenue(e.target.value)}
                className="w-full p-2.5 border border-[#e2e8f0] rounded-lg text-sm focus:ring-2 focus:ring-[#1863d6]/50 focus:border-[#1863d6] outline-none bg-white/50 backdrop-blur-sm transition-all duration-200"
                placeholder="e.g. $50/unit"
              />
            </div>
          </div>
 
          <div className="flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-gradient-to-r from-[#1863d6] to-[#151983] text-white px-6 py-2.5 rounded-lg font-medium hover:from-[#151983] hover:to-[#001f3d] transition-all duration-200 disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-[#1863d6]/30"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              Analyze Finances
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Cost Structure Card */}
          <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200">
            <h4 className="font-semibold text-[#0f172a] mb-4 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-[#1863d6]" />
              Cost Structure Breakdown
            </h4>
            
            <div className="space-y-4">
               <div className="flex justify-between items-center p-3 bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9] rounded-lg border border-[#e2e8f0]">
                  <span className="text-sm text-[#64748b]">Fixed Costs</span>
                  <span className="font-bold text-[#0f172a]">{analysis.current_cost_structure.fixed_costs.total}</span>
               </div>
               <div className="pl-4 space-y-2 border-l-2 border-[#e2e8f0]">
                  {analysis.current_cost_structure.fixed_costs.breakdown.map((item, i) => (
                    <div key={i} className="flex justify-between text-xs">
                      <span className="text-[#94a3b8]">{item.category}</span>
                      <span className="font-medium text-[#334155]">{item.amount} ({item.percentage}%)</span>
                    </div>
                  ))}
               </div>
 
               <div className="flex justify-between items-center p-3 bg-gradient-to-br from-[#f8fafc] to-[#f1f5f9] rounded-lg border border-[#e2e8f0]">
                  <span className="text-sm text-[#64748b]">Variable Costs</span>
                  <span className="font-bold text-[#0f172a]">{analysis.current_cost_structure.variable_costs.total}</span>
               </div>
               <div className="pl-4 space-y-2 border-l-2 border-[#e2e8f0]">
                  {analysis.current_cost_structure.variable_costs.breakdown.map((item, i) => (
                    <div key={i} className="flex justify-between text-xs">
                      <span className="text-[#94a3b8]">{item.category}</span>
                      <span className="font-medium text-[#334155]">{item.amount} ({item.percentage}%)</span>
                    </div>
                  ))}
               </div>
 
               <div className="mt-4 pt-4 border-t border-[#e2e8f0] flex justify-between items-center">
                  <span className="font-medium text-[#0f172a]">Total Monthly Cost</span>
                  <span className="text-xl font-bold text-[#1863d6]">{analysis.current_cost_structure.total_monthly_cost}</span>
               </div>
            </div>
          </div>

          {/* Pricing Strategy Card */}
          <div className="backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200">
            <h4 className="font-semibold text-[#0f172a] mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#10b981]" />
              Recommended Pricing
            </h4>
            
            <div className="space-y-4">
              {analysis.pricing_strategies.map((strat, idx) => (
                <div key={idx} className="p-4 border border-[#e2e8f0] rounded-lg hover:border-[#1863d6]/30 transition-all duration-200">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-medium text-[#1863d6] capitalize">{strat.strategy.replace(/_/g, ' ')}</h5>
                    <span className="bg-[#1863d6]/10 text-[#1863d6] px-2 py-1 rounded text-xs font-bold">
                      {strat.recommended_price}
                    </span>
                  </div>
                  <p className="text-sm text-[#64748b] mb-3 leading-relaxed">{strat.rationale}</p>
                  <div className="flex items-center gap-4 text-xs text-[#94a3b8]">
                     <span>Margin: <span className="font-medium text-[#0f172a]">{strat.expected_margin}</span></span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Optimization Opportunities */}
          <div className="md:col-span-2 bg-gradient-to-r from-[#1863d6]/10 to-[#3b82f6]/10 border border-[#1863d6]/30 rounded-xl p-6 backdrop-blur-sm">
             <h4 className="font-semibold text-[#001f3d] mb-4 flex items-center gap-2">
                <ArrowRight className="w-4 h-4" />
                Optimization Opportunities
             </h4>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               {analysis.optimization_opportunities.map((opp, idx) => (
                  <div key={idx} className="bg-white/80 backdrop-blur-sm p-4 rounded-lg border border-[#1863d6]/20 hover:shadow-md transition-shadow duration-200">
                     <div className="flex justify-between mb-1">
                       <span className="font-medium text-[#0f172a]">{opp.area}</span>
                       <span className="text-[#10b981] font-bold">Save {opp.potential_savings}</span>
                     </div>
                     <div className="w-full bg-[#e2e8f0] rounded-full h-1.5 mb-2 overflow-hidden">
                        <div className="bg-gradient-to-r from-[#10b981] to-[#059669] h-1.5 rounded-full" style={{ width: `${opp.savings_percentage}%` }}></div>
                     </div>
                     <p className="text-xs text-[#94a3b8]">
                        Current spend: {opp.current_cost}. Impact in {opp.time_to_impact}.
                     </p>
                  </div>
               ))}
             </div>
          </div>

        </div>
      )}
    </div>
  );
};

export default CostingAdvisor;
