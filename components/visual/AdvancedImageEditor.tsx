/**
 * AdvancedImageEditor Component
 * Displays advanced image editor with layers and filters
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Undo, Redo, Layers, Sliders, Image as ImageIcon, Type, Square,
  Download, Eye, EyeOff, Trash2, Move, Plus, ChevronUp, ChevronDown
} from 'lucide-react';

interface Layer {
  id: string;
  type: 'image' | 'text' | 'shape';
  content: string; // URL for image, text content for text
  visible: boolean;
  x: number;
  y: number;
  width?: number;
  height?: number;
  style?: React.CSSProperties;
}

interface FilterState {
  brightness: number;
  contrast: number;
  saturation: number;
  blur: number;
  sepia: number;
  grayscale: number;
}

const DEFAULT_FILTERS: FilterState = {
  brightness: 100,
  contrast: 100,
  saturation: 100,
  blur: 0,
  sepia: 0,
  grayscale: 0
};

const PRESET_FILTERS = [
  { label: 'None', settings: DEFAULT_FILTERS },
  { label: 'Vivid', settings: { ...DEFAULT_FILTERS, contrast: 120, saturation: 130 } },
  { label: 'B&W', settings: { ...DEFAULT_FILTERS, grayscale: 100, contrast: 110 } },
  { label: 'Vintage', settings: { ...DEFAULT_FILTERS, sepia: 60, brightness: 90, contrast: 90 } },
  { label: 'Soft', settings: { ...DEFAULT_FILTERS, brightness: 110, saturation: 80, blur: 0.5 } },
];

interface AdvancedImageEditorProps {
  initialImage: string | null;
  onClose?: () => void;
}

const AdvancedImageEditor: React.FC<AdvancedImageEditorProps> = ({ initialImage }) => {
  // State
  const [layers, setLayers] = useState<Layer[]>([]);
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [history, setHistory] = useState<{ layers: Layer[], filters: FilterState }[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [activeTab, setActiveTab] = useState<'adjust' | 'filters' | 'layers'>('adjust');

  // Initialize with base image
  useEffect(() => {
    if (initialImage) {
      const baseLayer: Layer = {
        id: 'bg',
        type: 'image',
        content: initialImage,
        visible: true,
        x: 0,
        y: 0,
        width: 100, // %
        height: 100 // %
      };
      setLayers([baseLayer]);
      addToHistory([baseLayer], DEFAULT_FILTERS);
    }
  }, [initialImage]);

  // History Management
  const addToHistory = (newLayers: Layer[], newFilters: FilterState) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ layers: JSON.parse(JSON.stringify(newLayers)), filters: { ...newFilters } });
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const handleUndo = () => {
    if (historyIndex > 0) {
      const prev = history[historyIndex - 1];
      setLayers(prev.layers);
      setFilters(prev.filters);
      setHistoryIndex(historyIndex - 1);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const next = history[historyIndex + 1];
      setLayers(next.layers);
      setFilters(next.filters);
      setHistoryIndex(historyIndex + 1);
    }
  };

  const updateFilters = (key: keyof FilterState, value: number) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    // Debounce history update for sliders in a real app, simplified here
  };

  const commitFilterChange = () => {
    addToHistory(layers, filters);
  };

  const addLayer = (type: 'text' | 'shape') => {
    const newLayer: Layer = {
      id: Date.now().toString(),
      type,
      content: type === 'text' ? 'New Text' : '',
      visible: true,
      x: 20, // %
      y: 20, // %
      style: type === 'shape' ? { backgroundColor: '#6366f1', width: '100px', height: '100px' } : { fontSize: '24px', color: '#000000', fontWeight: 'bold' }
    };
    const newLayers = [...layers, newLayer];
    setLayers(newLayers);
    setSelectedLayerId(newLayer.id);
    addToHistory(newLayers, filters);
  };

  const updateLayer = (id: string, updates: Partial<Layer>) => {
    const newLayers = layers.map(l => l.id === id ? { ...l, ...updates } : l);
    setLayers(newLayers);
  };

  const deleteLayer = (id: string) => {
    if (id === 'bg') return;
    const newLayers = layers.filter(l => l.id !== id);
    setLayers(newLayers);
    setSelectedLayerId(null);
    addToHistory(newLayers, filters);
  };

  const moveLayer = (id: string, direction: -1 | 1) => {
    const index = layers.findIndex(l => l.id === id);
    if (index === -1) return;
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= layers.length) return;
    
    const newLayers = [...layers];
    const temp = newLayers[index];
    newLayers[index] = newLayers[newIndex];
    newLayers[newIndex] = temp;
    setLayers(newLayers);
    addToHistory(newLayers, filters);
  };

  // --- Render Helpers ---

  const getFilterString = () => {
    return `
      brightness(${filters.brightness}%) 
      contrast(${filters.contrast}%) 
      saturate(${filters.saturation}%) 
      blur(${filters.blur}px) 
      sepia(${filters.sepia}%) 
      grayscale(${filters.grayscale}%)
    `;
  };

  return (
    <div className="flex flex-col h-[600px] bg-[#f8fafc] border border-[#e2e8f0] rounded-xl overflow-hidden">
      
      {/* Toolbar */}
      <div className="h-12 backdrop-blur-sm bg-white/80 border-b border-[#e2e8f0] flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <button onClick={handleUndo} disabled={historyIndex <= 0} className="p-1.5 hover:bg-[#f8fafc] rounded text-[#64748b] disabled:opacity-30">
            <Undo className="w-4 h-4" />
          </button>
          <button onClick={handleRedo} disabled={historyIndex >= history.length - 1} className="p-1.5 hover:bg-[#f8fafc] rounded text-[#64748b] disabled:opacity-30">
            <Redo className="w-4 h-4" />
          </button>
          <div className="w-px h-6 bg-[#e2e8f0] mx-2" />
          <button onClick={() => addLayer('text')} className="p-1.5 hover:bg-[#f8fafc] rounded text-[#64748b] flex items-center gap-1 text-xs font-medium">
            <Type className="w-4 h-4" /> Add Text
          </button>
          <button onClick={() => addLayer('shape')} className="p-1.5 hover:bg-[#f8fafc] rounded text-[#64748b] flex items-center gap-1 text-xs font-medium">
            <Square className="w-4 h-4" /> Add Shape
          </button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#94a3b8]">
            {layers.length} Layers • {Math.round(100 * (historyIndex + 1) / (history.length || 1))}% History
          </span>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        
        {/* Canvas Area */}
        <div className="flex-1 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-[#e2e8f0] flex items-center justify-center p-8 relative overflow-hidden">
          <div
            className="relative shadow-2xl bg-white"
            style={{
              width: '100%',
              height: '100%',
              maxWidth: '800px',
              maxHeight: '600px',
              aspectRatio: '16/9' // Default, assumes landscape
            }}
          >
            {/* Base Image Layer (special handling for filters) */}
            {layers.find(l => l.id === 'bg') && (
              <img
                src={layers.find(l => l.id === 'bg')!.content}
                alt="Base"
                className="absolute inset-0 w-full h-full object-contain"
                style={{
                  filter: getFilterString(),
                  visibility: layers.find(l => l.id === 'bg')!.visible ? 'visible' : 'hidden'
                }}
              />
            )}

            {/* Other Layers */}
            {layers.filter(l => l.id !== 'bg').map(layer => (
              layer.visible && (
                <div
                  key={layer.id}
                  className={`absolute cursor-move group ${selectedLayerId === layer.id ? 'ring-2 ring-[#1863d6]' : ''}`}
                  style={{
                    left: `${layer.x}%`,
                    top: `${layer.y}%`,
                    ...layer.style
                  }}
                  onClick={(e) => { e.stopPropagation(); setSelectedLayerId(layer.id); }}
                  // Draggable logic would go here
                >
                  {layer.type === 'text' ? layer.content : null}
                  {/* Layer resize handles would go here */}
                </div>
              )
            ))}
          </div>
        </div>

        {/* Sidebar Controls */}
        <div className="w-72 backdrop-blur-sm bg-white/80 border-l border-[#e2e8f0] flex flex-col">
          <div className="flex border-b border-[#e2e8f0]">
            <button
              onClick={() => setActiveTab('adjust')}
              className={`flex-1 py-3 text-xs font-medium border-b-2 ${activeTab === 'adjust' ? 'border-[#1863d6] text-[#1863d6]' : 'border-transparent text-[#64748b] hover:text-[#0f172a]'}`}
            >
              Adjust
            </button>
            <button
              onClick={() => setActiveTab('filters')}
              className={`flex-1 py-3 text-xs font-medium border-b-2 ${activeTab === 'filters' ? 'border-[#1863d6] text-[#1863d6]' : 'border-transparent text-[#64748b] hover:text-[#0f172a]'}`}
            >
              Filters
            </button>
            <button
              onClick={() => setActiveTab('layers')}
              className={`flex-1 py-3 text-xs font-medium border-b-2 ${activeTab === 'layers' ? 'border-[#1863d6] text-[#1863d6]' : 'border-transparent text-[#64748b] hover:text-[#0f172a]'}`}
            >
              Layers
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            
            {activeTab === 'adjust' && (
              <div className="space-y-4">
                {[
                  { label: 'Brightness', key: 'brightness', min: 0, max: 200 },
                  { label: 'Contrast', key: 'contrast', min: 0, max: 200 },
                  { label: 'Saturation', key: 'saturation', min: 0, max: 200 },
                  { label: 'Blur', key: 'blur', min: 0, max: 10 },
                  { label: 'Sepia', key: 'sepia', min: 0, max: 100 },
                ].map(control => (
                  <div key={control.key}>
                    <div className="flex justify-between mb-1">
                      <label className="text-xs font-medium text-[#334155]">{control.label}</label>
                      <span className="text-xs text-[#94a3b8]">{filters[control.key as keyof FilterState]}</span>
                    </div>
                    <input
                      type="range"
                      min={control.min}
                      max={control.max}
                      step={control.key === 'blur' ? 0.1 : 1}
                      value={filters[control.key as keyof FilterState]}
                      onChange={(e) => updateFilters(control.key as keyof FilterState, Number(e.target.value))}
                      onMouseUp={commitFilterChange}
                      className="w-full h-1.5 bg-[#e2e8f0] rounded-lg appearance-none cursor-pointer accent-[#1863d6]"
                    />
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'filters' && (
              <div className="grid grid-cols-2 gap-3">
                {PRESET_FILTERS.map(preset => (
                  <button
                    key={preset.label}
                    onClick={() => {
                      setFilters(preset.settings);
                      addToHistory(layers, preset.settings);
                    }}
                    className="p-3 rounded-lg border border-[#e2e8f0] hover:border-[#1863d6] hover:bg-[#1863d6]/10 transition-colors text-center"
                  >
                    <div className="w-full h-12 bg-[#e2e8f0] rounded-md mb-2 overflow-hidden relative">
                       {/* Mini preview could go here */}
                       <div
                         className="absolute inset-0 bg-gradient-to-br from-[#1863d6] to-[#151983]"
                         style={{
                           filter: `
                             brightness(${preset.settings.brightness}%)
                             contrast(${preset.settings.contrast}%)
                             saturate(${preset.settings.saturation}%)
                             sepia(${preset.settings.sepia}%)
                           `
                         }}
                       />
                    </div>
                    <span className="text-xs font-medium text-[#0f172a]">{preset.label}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'layers' && (
              <div className="space-y-2">
                {[...layers].reverse().map((layer, i) => ( // Reverse to show top layer first
                  <div
                    key={layer.id}
                    onClick={() => setSelectedLayerId(layer.id)}
                    className={`p-3 rounded-lg border flex items-center gap-3 transition-colors ${selectedLayerId === layer.id ? 'border-[#1863d6] bg-[#1863d6]/10' : 'border-[#e2e8f0] bg-white hover:bg-[#f8fafc]'}`}
                  >
                    <div className="p-1.5 bg-[#f8fafc] rounded text-[#94a3b8]">
                      {layer.id === 'bg' ? <ImageIcon className="w-4 h-4" /> : layer.type === 'text' ? <Type className="w-4 h-4" /> : <Square className="w-4 h-4" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium text-[#0f172a] truncate">
                        {layer.id === 'bg' ? 'Background' : layer.type === 'text' ? layer.content : 'Shape'}
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button onClick={(e) => { e.stopPropagation(); updateLayer(layer.id, { visible: !layer.visible }); }} className="p-1 text-[#94a3b8] hover:text-[#64748b]">
                        {layer.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                      </button>
                      {layer.id !== 'bg' && (
                        <>
                          <div className="flex flex-col">
                             <button onClick={(e) => { e.stopPropagation(); moveLayer(layer.id, 1); }} className="p-0.5 text-[#94a3b8] hover:text-[#1863d6]"><ChevronUp className="w-3 h-3" /></button>
                             <button onClick={(e) => { e.stopPropagation(); moveLayer(layer.id, -1); }} className="p-0.5 text-[#94a3b8] hover:text-[#1863d6]"><ChevronDown className="w-3 h-3" /></button>
                          </div>
                          <button onClick={(e) => { e.stopPropagation(); deleteLayer(layer.id); }} className="p-1 text-[#94a3b8] hover:text-[#ef4444]">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};

export default AdvancedImageEditor;
