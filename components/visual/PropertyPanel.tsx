/**
 * PropertyPanel Component
 * Context-aware property panel for the visual editor
 */

import React, { useState } from 'react';
import {
    ChevronDown, ChevronRight, Palette, Type, Square,
    Move, RotateCw, Maximize2, AlignLeft, AlignCenter,
    AlignRight, Bold, Italic, Underline, Layers
} from 'lucide-react';

interface ElementProperties {
    id: string;
    type: 'rectangle' | 'circle' | 'text' | 'image' | 'line';
    x: number;
    y: number;
    width: number;
    height: number;
    rotation: number;
    opacity: number;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    cornerRadius?: number;
    // Text properties
    text?: string;
    fontSize?: number;
    fontFamily?: string;
    fontWeight?: string;
    textAlign?: 'left' | 'center' | 'right';
    // Image properties
    src?: string;
}

interface PropertyPanelProps {
    selectedElement: ElementProperties | null;
    onPropertyChange: (property: string, value: any) => void;
}

const COLOR_PRESETS = [
    '#000000', '#ffffff', '#ef4444', '#f97316', '#eab308',
    '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899',
];

const FONT_FAMILIES = [
    'Inter', 'Roboto', 'Open Sans', 'Montserrat', 'Poppins',
    'Playfair Display', 'Lora', 'Source Code Pro',
];

export const PropertyPanel: React.FC<PropertyPanelProps> = ({
    selectedElement,
    onPropertyChange,
}) => {
    const [expandedSections, setExpandedSections] = useState<string[]>(['position', 'appearance']);

    const toggleSection = (section: string) => {
        setExpandedSections(prev =>
            prev.includes(section)
                ? prev.filter(s => s !== section)
                : [...prev, section]
        );
    };

    if (!selectedElement) {
        return (
            <div className="w-72 bg-white border-l border-slate-200 p-4">
                <div className="text-center py-12">
                    <Layers className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                    <p className="text-slate-500 font-medium">No Selection</p>
                    <p className="text-sm text-slate-400 mt-1">Select an element to edit its properties</p>
                </div>
            </div>
        );
    }

    const Section: React.FC<{ title: string; id: string; icon: React.ReactNode; children: React.ReactNode }> =
        ({ title, id, icon, children }) => {
            const isExpanded = expandedSections.includes(id);
            return (
                <div className="border-b border-slate-100">
                    <button
                        onClick={() => toggleSection(id)}
                        className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            {icon}
                            <span className="text-sm font-medium text-slate-700">{title}</span>
                        </div>
                        {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                    </button>
                    {isExpanded && <div className="px-4 pb-4">{children}</div>}
                </div>
            );
        };

    return (
        <div className="w-72 bg-white border-l border-slate-200 overflow-y-auto">
            {/* Header */}
            <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
                <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${selectedElement.type === 'rectangle' ? 'bg-blue-100 text-blue-600' :
                            selectedElement.type === 'circle' ? 'bg-pink-100 text-pink-600' :
                                selectedElement.type === 'text' ? 'bg-violet-100 text-violet-600' :
                                    'bg-slate-100 text-slate-600'
                        }`}>
                        {selectedElement.type === 'rectangle' && <Square className="w-4 h-4" />}
                        {selectedElement.type === 'text' && <Type className="w-4 h-4" />}
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-slate-800 capitalize">{selectedElement.type}</p>
                        <p className="text-xs text-slate-400">ID: {selectedElement.id.slice(0, 8)}</p>
                    </div>
                </div>
            </div>

            {/* Position & Size */}
            <Section title="Position & Size" id="position" icon={<Move className="w-4 h-4 text-slate-400" />}>
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">X</label>
                        <input
                            type="number"
                            value={selectedElement.x}
                            onChange={(e) => onPropertyChange('x', Number(e.target.value))}
                            className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">Y</label>
                        <input
                            type="number"
                            value={selectedElement.y}
                            onChange={(e) => onPropertyChange('y', Number(e.target.value))}
                            className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">Width</label>
                        <input
                            type="number"
                            value={selectedElement.width}
                            onChange={(e) => onPropertyChange('width', Number(e.target.value))}
                            className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                        />
                    </div>
                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">Height</label>
                        <input
                            type="number"
                            value={selectedElement.height}
                            onChange={(e) => onPropertyChange('height', Number(e.target.value))}
                            className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                        />
                    </div>
                </div>
                <div className="mt-3">
                    <label className="text-xs text-slate-500 mb-1 block">Rotation</label>
                    <div className="flex items-center gap-2">
                        <input
                            type="range"
                            min="0"
                            max="360"
                            value={selectedElement.rotation}
                            onChange={(e) => onPropertyChange('rotation', Number(e.target.value))}
                            className="flex-1"
                        />
                        <span className="text-sm text-slate-600 w-12 text-right">{selectedElement.rotation}°</span>
                    </div>
                </div>
            </Section>

            {/* Appearance */}
            <Section title="Appearance" id="appearance" icon={<Palette className="w-4 h-4 text-slate-400" />}>
                <div className="space-y-3">
                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">Fill Color</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="color"
                                value={selectedElement.fill || '#3b82f6'}
                                onChange={(e) => onPropertyChange('fill', e.target.value)}
                                className="w-10 h-10 rounded-lg border border-slate-200 cursor-pointer"
                            />
                            <div className="flex flex-wrap gap-1">
                                {COLOR_PRESETS.map(color => (
                                    <button
                                        key={color}
                                        onClick={() => onPropertyChange('fill', color)}
                                        className="w-6 h-6 rounded-md border border-slate-200 hover:scale-110 transition-transform"
                                        style={{ backgroundColor: color }}
                                    />
                                ))}
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">Stroke</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="color"
                                value={selectedElement.stroke || '#000000'}
                                onChange={(e) => onPropertyChange('stroke', e.target.value)}
                                className="w-10 h-10 rounded-lg border border-slate-200 cursor-pointer"
                            />
                            <input
                                type="number"
                                value={selectedElement.strokeWidth || 0}
                                onChange={(e) => onPropertyChange('strokeWidth', Number(e.target.value))}
                                className="w-16 px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                                min="0"
                                max="20"
                            />
                            <span className="text-xs text-slate-400">px</span>
                        </div>
                    </div>

                    <div>
                        <label className="text-xs text-slate-500 mb-1 block">Opacity</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={selectedElement.opacity * 100}
                                onChange={(e) => onPropertyChange('opacity', Number(e.target.value) / 100)}
                                className="flex-1"
                            />
                            <span className="text-sm text-slate-600 w-12 text-right">{Math.round(selectedElement.opacity * 100)}%</span>
                        </div>
                    </div>

                    {(selectedElement.type === 'rectangle') && (
                        <div>
                            <label className="text-xs text-slate-500 mb-1 block">Corner Radius</label>
                            <input
                                type="range"
                                min="0"
                                max="50"
                                value={selectedElement.cornerRadius || 0}
                                onChange={(e) => onPropertyChange('cornerRadius', Number(e.target.value))}
                                className="w-full"
                            />
                        </div>
                    )}
                </div>
            </Section>

            {/* Text Properties */}
            {selectedElement.type === 'text' && (
                <Section title="Typography" id="typography" icon={<Type className="w-4 h-4 text-slate-400" />}>
                    <div className="space-y-3">
                        <div>
                            <label className="text-xs text-slate-500 mb-1 block">Font Family</label>
                            <select
                                value={selectedElement.fontFamily || 'Inter'}
                                onChange={(e) => onPropertyChange('fontFamily', e.target.value)}
                                className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                            >
                                {FONT_FAMILIES.map(font => (
                                    <option key={font} value={font}>{font}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex gap-2">
                            <div className="flex-1">
                                <label className="text-xs text-slate-500 mb-1 block">Size</label>
                                <input
                                    type="number"
                                    value={selectedElement.fontSize || 16}
                                    onChange={(e) => onPropertyChange('fontSize', Number(e.target.value))}
                                    className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
                                />
                            </div>
                            <div className="flex gap-1 items-end">
                                <button
                                    onClick={() => onPropertyChange('fontWeight', selectedElement.fontWeight === 'bold' ? 'normal' : 'bold')}
                                    className={`w-8 h-8 rounded-lg flex items-center justify-center ${selectedElement.fontWeight === 'bold' ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-600'}`}
                                >
                                    <Bold className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="text-xs text-slate-500 mb-1 block">Alignment</label>
                            <div className="flex gap-1">
                                {[
                                    { value: 'left', icon: AlignLeft },
                                    { value: 'center', icon: AlignCenter },
                                    { value: 'right', icon: AlignRight },
                                ].map(align => (
                                    <button
                                        key={align.value}
                                        onClick={() => onPropertyChange('textAlign', align.value)}
                                        className={`flex-1 h-8 rounded-lg flex items-center justify-center ${selectedElement.textAlign === align.value ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                            }`}
                                    >
                                        <align.icon className="w-4 h-4" />
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </Section>
            )}
        </div>
    );
};

export default PropertyPanel;
