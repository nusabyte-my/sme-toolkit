/**
 * OpportunityCard Component
 * Displays business opportunities with metrics
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { TrendingUp, DollarSign, Clock, AlertTriangle } from 'lucide-react';
import { cn } from '../../utils/cn';
import type { BusinessOpportunity, PartnershipOpportunity, MarketExpansion, InnovationSuggestion } from '../../types';

interface OpportunityCardProps {
  opportunity: BusinessOpportunity | PartnershipOpportunity | MarketExpansion | InnovationSuggestion;
  className?: string;
  onClick?: () => void;
  showFeasibility?: boolean;
}

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
  opportunity,
  className,
  onClick,
  showFeasibility = true,
}) => {
  const getFeasibilityColor = (score: number): string => {
    if (score >= 0.8) return 'bg-[#10b981]/10 text-[#10b981] border-[#10b981]/20';
    if (score >= 0.6) return 'bg-[#f59e0b]/10 text-[#f59e0b] border-[#f59e0b]/20';
    return 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20';
  };

  const getFeasibilityLabel = (score: number): string => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  const isBusinessOpportunity = 'potential_revenue' in opportunity;
  const isPartnership = 'partner_type' in opportunity;
  const isMarketExpansion = 'target_market' in opportunity;
  const isInnovation = 'development_effort' in opportunity;

  return (
    <div
      className={cn(
        'backdrop-blur-sm bg-white/80 rounded-lg border border-[#b6cbe1]/30 p-5 hover:shadow-md transition-shadow duration-200 cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-[#0f172a] text-lg">{opportunity.title}</h3>
          <span className="inline-block mt-1 px-2 py-0.5 bg-[#e2e8f0] text-[#64748b] text-xs rounded-md">
            {opportunity.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </span>
        </div>
        {showFeasibility && 'feasibility_score' in opportunity && (
          <span
            className={cn(
              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border',
              getFeasibilityColor(opportunity.feasibility_score)
            )}
          >
            {getFeasibilityLabel(opportunity.feasibility_score)}
          </span>
        )}
      </div>

      {/* Description — only BusinessOpportunity and InnovationSuggestion carry it */}
      {'description' in opportunity && opportunity.description && (
        <p className="text-sm text-[#64748b] mb-4 line-clamp-2">
          {opportunity.description}
        </p>
      )}

      {/* Key metrics */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {isBusinessOpportunity && (
          <>
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-[#10b981]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Potential Revenue</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {(opportunity as BusinessOpportunity).potential_revenue}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#1863d6]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Success Rate</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {Math.round((opportunity as BusinessOpportunity).success_probability * 100)}%
                </p>
              </div>
            </div>
          </>
        )}

        {isPartnership && (
          <>
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-[#10b981]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Estimated Value</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {(opportunity as PartnershipOpportunity).estimated_value}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#1863d6]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Alignment</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {Math.round((opportunity as PartnershipOpportunity).alignment_score * 100)}%
                </p>
              </div>
            </div>
          </>
        )}

        {isMarketExpansion && (
          <>
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-[#10b981]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Market Size</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {(opportunity as MarketExpansion).market_size}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#1863d6]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Growth Rate</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {(opportunity as MarketExpansion).growth_rate}
                </p>
              </div>
            </div>
          </>
        )}

        {isInnovation && (
          <>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#1863d6]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Potential Impact</p>
                <p className="text-sm font-medium text-[#0f172a]">
                  {(opportunity as InnovationSuggestion).potential_impact}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#9333ea]" />
              <div>
                <p className="text-xs text-[#94a3b8]">Effort</p>
                <p className="text-sm font-medium text-[#0f172a] capitalize">
                  {(opportunity as InnovationSuggestion).development_effort}
                </p>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Investment/Time */}
      {('investment_required' in opportunity || 'time_to_market' in opportunity) && (
        <div className="flex items-center gap-4 text-sm text-[#64748b] mb-4">
          {'investment_required' in opportunity && (
            <div className="flex items-center gap-1">
              <DollarSign className="w-4 h-4 text-[#94a3b8]" />
              <span>Investment: {(opportunity as any).investment_required}</span>
            </div>
          )}
          {'time_to_market' in opportunity && (
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4 text-[#94a3b8]" />
              <span>Time: {(opportunity as any).time_to_market}</span>
            </div>
          )}
        </div>
      )}

      {/* Risks */}
      {'risks' in opportunity && (opportunity as any).risks.length > 0 && (
        <div className="mt-3 pt-3 border-t border-[#e2e8f0]">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-[#f59e0b]" />
            <span className="text-sm font-medium text-[#334155]">Risks</span>
          </div>
          <ul className="space-y-1">
            {(opportunity as any).risks.map((risk: string, idx: number) => (
              <li key={idx} className="text-xs text-[#64748b] flex items-start gap-2">
                <span className="text-[#f59e0b]">•</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
