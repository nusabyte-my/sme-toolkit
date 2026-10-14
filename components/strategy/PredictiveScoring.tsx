/**
 * PredictiveScoring Component
 * Displays predictive scoring with radar chart visualization
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState, useEffect } from 'react';
import { AllScores, ScoreData } from '../../types';
import { RotateCcw, TrendingUp } from 'lucide-react';

interface PredictiveScoringProps {
  scores: AllScores | null;
  loading: boolean;
}

const PredictiveScoring: React.FC<PredictiveScoringProps> = ({ scores, loading }) => {
  const [simulatedScores, setSimulatedScores] = useState<AllScores | null>(null);
  
  useEffect(() => {
    if (scores) {
      setSimulatedScores(JSON.parse(JSON.stringify(scores)));
    }
  }, [scores]);

  if (!scores || !simulatedScores) {
    return <div className="text-center p-8 text-[#94a3b8]">No scoring data available.</div>;
  }

  const handleSliderChange = (category: keyof AllScores, delta: number) => {
    if (!simulatedScores) return;
    
    setSimulatedScores(prev => {
      if (!prev) return null;
      const newScores = { ...prev };
      // Clamp between 0 and 100
      const original = scores[category].overall_score;
      newScores[category].overall_score = Math.min(100, Math.max(0, original + delta));
      return newScores;
    });
  };

  const getDelta = (category: keyof AllScores) => {
    return Math.round(simulatedScores[category].overall_score - scores[category].overall_score);
  };

  const categories: (keyof AllScores)[] = [
    'business_health',
    'growth_potential',
    'financial_stability',
    'market_position',
    'operational_efficiency',
    'innovation_readiness'
  ];

  // Helper for Radar Chart SVG
  const getCoordinates = (value: number, index: number, total: number) => {
    const angle = (Math.PI * 2 * index) / total - Math.PI / 2;
    const r = (value / 100) * 100; // Radius scale
    const x = 150 + r * Math.cos(angle);
    const y = 150 + r * Math.sin(angle);
    return { x, y };
  };

  const buildPolygon = (data: AllScores, isSimulated: boolean) => {
    const points = categories.map((cat, i) => {
      const val = data[cat].overall_score;
      const { x, y } = getCoordinates(val, i, categories.length);
      return `${x},${y}`;
    }).join(' ');
    return points;
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-center bg-[#1863d6]/10 p-4 rounded-xl border border-[#1863d6]/30 backdrop-blur-sm">
        <div>
          <h3 className="font-bold text-[#001f3d] flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-[#1863d6]" />
            Predictive Simulator
          </h3>
          <p className="text-[#151983] text-sm mt-1">
            Adjust sliders to see how improvements in specific areas impact your overall business grade.
          </p>
        </div>
        <button
          onClick={() => setSimulatedScores(JSON.parse(JSON.stringify(scores)))}
          className="text-[#1863d6] hover:text-[#151983] text-sm font-medium flex items-center bg-white px-3 py-2 rounded-lg shadow-sm border border-[#1863d6]/30 hover:shadow-md hover:border-[#151983] transition-all duration-200"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset Simulation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
         
        {/* Radar Chart Visualization */}
        <div className="flex justify-center items-center relative aspect-square max-h-[400px]">
          <svg viewBox="0 0 300 300" className="w-full h-full max-w-[350px]">
            {/* Background Webs */}
            {[20, 40, 60, 80, 100].map(r => (
              <circle key={r} cx="150" cy="150" r={r} fill="none" stroke="#e5e7eb" strokeWidth="1" strokeDasharray="4 4" />
            ))}
            
            {/* Axes */}
            {categories.map((_, i) => {
              const { x, y } = getCoordinates(100, i, categories.length);
              return <line key={i} x1="150" y1="150" x2={x} y2={y} stroke="#e5e7eb" strokeWidth="1" />;
            })}
            
            {/* Original Score Polygon */}
            <polygon
              points={buildPolygon(scores, false)}
              fill="rgba(148, 163, 184, 0.2)"
              stroke="#94a3b8"
              strokeWidth="2"
            />
            
            {/* Simulated Score Polygon */}
            <polygon
              points={buildPolygon(simulatedScores, true)}
              fill="rgba(99, 102, 241, 0.3)"
              stroke="#1863d6"
              strokeWidth="2"
              className="transition-all duration-300 ease-out"
            />

            {/* Labels */}
            {categories.map((cat, i) => {
              const { x, y } = getCoordinates(115, i, categories.length);
              return (
                <text 
                  key={i} 
                  x={x} 
                  y={y} 
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  className="text-[8px] uppercase font-bold fill-slate-500"
                >
                  {cat.replace(/_/g, ' ').split(' ').map(w => w[0]).join('')} {/* Initials only for clean look */}
                </text>
              );
            })}
          </svg>
          
          <div className="absolute bottom-0 text-center w-full">
            <div className="flex items-center justify-center gap-4 text-xs">
              <span className="flex items-center"><span className="w-2 h-2 bg-[#94a3b8] rounded-full mr-1"></span> Current</span>
              <span className="flex items-center"><span className="w-2 h-2 bg-[#1863d6] rounded-full mr-1"></span> Simulated</span>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-5 backdrop-blur-sm bg-white/80 border border-[#b6cbe1]/30 rounded-xl p-6 shadow-sm">
          {categories.map((cat) => (
            <div key={cat}>
              <div className="flex justify-between mb-2 text-sm">
                <label className="font-medium text-[#334155] capitalize">{cat.replace(/_/g, ' ')}</label>
                <div className="flex items-center gap-2">
                  <span className="text-[#94a3b8] text-xs">{Math.round(scores[cat].overall_score)}</span>
                  <span className="text-[#64748b]">→</span>
                  <span className={`font-bold ${getDelta(cat) > 0 ? 'text-[#10b981]' : getDelta(cat) < 0 ? 'text-[#ef4444]' : 'text-[#0f172a]'}`}>
                    {Math.round(simulatedScores[cat].overall_score)}
                  </span>
                </div>
              </div>
              <input
                type="range"
                min="-30"
                max="30"
                value={getDelta(cat)}
                onChange={(e) => handleSliderChange(cat, parseInt(e.target.value))}
                className="w-full h-2 bg-[#e2e8f0] rounded-lg appearance-none cursor-pointer accent-[#1863d6]"
              />
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default PredictiveScoring;
