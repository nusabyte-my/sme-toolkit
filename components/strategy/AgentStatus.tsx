/**
 * AgentStatus Component
 * Displays agent status with progress indicators
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React from 'react';
import { CheckCircle2, Clock, XCircle, Loader2, AlertCircle } from 'lucide-react';
import { cn } from '../../utils/cn';
import type { AgentStatus as AgentStatusType } from '../../types';

interface AgentStatusProps {
  agents: AgentStatusType[];
  className?: string;
  showProgress?: boolean;
  compact?: boolean;
}

export const AgentStatus: React.FC<AgentStatusProps> = ({
  agents,
  className,
  showProgress = true,
  compact = false,
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-[#10b981]" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-[#1863d6] animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-[#ef4444]" />;
      case 'idle':
      default:
        return <Clock className="w-5 h-5 text-[#94a3b8]" />;
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-[#10b981]/10 text-[#10b981] border-[#10b981]/20';
      case 'running':
        return 'bg-[#1863d6]/10 text-[#1863d6] border-[#1863d6]/20';
      case 'failed':
        return 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20';
      case 'idle':
      default:
        return 'bg-[#94a3b8]/10 text-[#94a3b8] border-[#94a3b8]/20';
    }
  };

  const getStatusLabel = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'running':
        return 'Running';
      case 'failed':
        return 'Failed';
      case 'idle':
      default:
        return 'Idle';
    }
  };

  if (compact) {
    return (
      <div className={cn('flex flex-wrap gap-2', className)}>
        {agents.map((agent, index) => (
          <div
            key={index}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium border',
              getStatusColor(agent.status)
            )}
          >
            {getStatusIcon(agent.status)}
            <span className="truncate max-w-[150px]">{agent.agent_name}</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {agents.map((agent, index) => (
        <div
          key={index}
          className="backdrop-blur-sm bg-white/80 rounded-lg border border-[#b6cbe1]/30 p-4"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              {getStatusIcon(agent.status)}
              <div>
                <h4 className="font-semibold text-[#0f172a]">{agent.agent_name}</h4>
                <span
                  className={cn(
                    'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border mt-1',
                    getStatusColor(agent.status)
                  )}
                >
                  {getStatusLabel(agent.status)}
                </span>
              </div>
            </div>
            {agent.status === 'failed' && (
              <AlertCircle className="w-5 h-5 text-[#ef4444]" />
            )}
          </div>

          {/* Progress bar */}
          {showProgress && agent.status !== 'idle' && (
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-[#64748b]">Progress</span>
                <span className="text-xs font-medium text-[#334155]">
                  {Math.round(agent.progress)}%
                </span>
              </div>
              <div className="w-full bg-[#e2e8f0] rounded-full overflow-hidden h-2">
                <div
                  className={cn(
                    'h-full rounded-full transition-all duration-300',
                    agent.status === 'completed' && 'bg-[#10b981]',
                    agent.status === 'running' && 'bg-[#1863d6]',
                    agent.status === 'failed' && 'bg-[#ef4444]'
                  )}
                  style={{ width: `${agent.progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Message */}
          {agent.message && (
            <p className="text-sm text-[#64748b] mb-2">{agent.message}</p>
          )}

          {/* Error */}
          {agent.error && (
            <div className="mt-2 p-3 bg-[#ef4444]/10 border border-[#ef4444]/20 rounded-md">
              <p className="text-sm text-[#ef4444] font-medium mb-1">Error:</p>
              <p className="text-sm text-[#ef4444]">{agent.error}</p>
            </div>
          )}

          {/* Result preview */}
          {agent.result && agent.status === 'completed' && (
            <div className="mt-2 p-3 bg-[#10b981]/10 border border-[#10b981]/20 rounded-md">
              <p className="text-sm text-[#10b981] font-medium mb-1">Result:</p>
              <p className="text-sm text-[#10b981] truncate">
                {typeof agent.result === 'string'
                  ? agent.result
                  : JSON.stringify(agent.result).substring(0, 200)}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
