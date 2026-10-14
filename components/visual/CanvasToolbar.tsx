/**
 * CanvasToolbar Component
 * Toolbar for the visual editor with tools, actions, and model selector
 */

import React, { useState } from 'react';
import {
    MousePointer2, Square, Circle, Type, Image, Minus, Move,
    RotateCcw, RotateCw, ZoomIn, ZoomOut, Download, Upload,
    Layers, Grid3X3, Palette, Wand2, Trash2, Copy, ClipboardPaste,
    AlignLeft, AlignCenter, AlignRight, FlipHorizontal, FlipVertical,
    Save, Share2, Settings, ChevronDown
} from 'lucide-react';

export type CanvasTool = 'select' | 'rectangle' | 'circle' | 'text' | 'image' | 'line' | 'move';

interface CanvasToolbarProps {
    activeTool: CanvasTool;
    onToolChange: (tool: CanvasTool) => void;
    zoom: number;
    onZoomChange: (zoom: number) => void;
    onUndo?: () => void;
    onRedo?: () => void;
    onExport?: () => void;
    onImport?: () => void;
    onSave?: () => void;
    onAIGenerate?: () => void;
    canUndo?: boolean;
    canRedo?: boolean;
    hasSelection?: boolean;
    onCopy?: () => void;
    onPaste?: () => void;
    onDelete?: () => void;
    onDuplicate?: () => void;
}

const TOOLS = [
    { id: 'select' as const, icon: MousePointer2, label: 'Select', shortcut: 'V' },
    { id: 'rectangle' as const, icon: Square, label: 'Rectangle', shortcut: 'R' },
    { id: 'circle' as const, icon: Circle, label: 'Circle', shortcut: 'O' },
    { id: 'text' as const, icon: Type, label: 'Text', shortcut: 'T' },
    { id: 'image' as const, icon: Image, label: 'Image', shortcut: 'I' },
    { id: 'line' as const, icon: Minus, label: 'Line', shortcut: 'L' },
    { id: 'move' as const, icon: Move, label: 'Pan', shortcut: 'H' },
];

export const CanvasToolbar: React.FC<CanvasToolbarProps> = ({
    activeTool,
    onToolChange,
    zoom,
    onZoomChange,
    onUndo,
    onRedo,
    onExport,
    onImport,
    onSave,
    onAIGenerate,
    canUndo = false,
    canRedo = false,
    hasSelection = false,
    onCopy,
    onPaste,
    onDelete,
    onDuplicate,
}) => {
    const [showZoomMenu, setShowZoomMenu] = useState(false);

    const zoomOptions = [25, 50, 75, 100, 125, 150, 200, 300];

    return (
        <div className="flex items-center justify-between p-2 bg-white border-b border-slate-200">
            {/* Left: Tools */}
            <div className="flex items-center gap-1">
                {TOOLS.map(tool => (
                    <button
                        key={tool.id}
                        onClick={() => onToolChange(tool.id)}
                        title={`${tool.label} (${tool.shortcut})`}
                        className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${activeTool === tool.id
                                ? 'bg-indigo-100 text-indigo-600 shadow-sm'
                                : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700'
                            }`}
                    >
                        <tool.icon className="w-5 h-5" />
                    </button>
                ))}

                <div className="w-px h-8 bg-slate-200 mx-2" />

                {/* AI Generate */}
                <button
                    onClick={onAIGenerate}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
                >
                    <Wand2 className="w-4 h-4" />
                    <span className="text-sm font-medium">AI Generate</span>
                </button>
            </div>

            {/* Center: History & Clipboard */}
            <div className="flex items-center gap-1">
                <button
                    onClick={onUndo}
                    disabled={!canUndo}
                    title="Undo (Ctrl+Z)"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <RotateCcw className="w-4 h-4" />
                </button>
                <button
                    onClick={onRedo}
                    disabled={!canRedo}
                    title="Redo (Ctrl+Y)"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <RotateCw className="w-4 h-4" />
                </button>

                <div className="w-px h-6 bg-slate-200 mx-1" />

                <button
                    onClick={onCopy}
                    disabled={!hasSelection}
                    title="Copy (Ctrl+C)"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <Copy className="w-4 h-4" />
                </button>
                <button
                    onClick={onPaste}
                    title="Paste (Ctrl+V)"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100"
                >
                    <ClipboardPaste className="w-4 h-4" />
                </button>
                <button
                    onClick={onDelete}
                    disabled={!hasSelection}
                    title="Delete (Del)"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-red-50 hover:text-red-500 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>

            {/* Right: Zoom & Actions */}
            <div className="flex items-center gap-2">
                {/* Zoom Controls */}
                <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-1">
                    <button
                        onClick={() => onZoomChange(Math.max(25, zoom - 25))}
                        className="w-8 h-8 rounded flex items-center justify-center text-slate-600 hover:bg-white hover:shadow-sm transition-all"
                    >
                        <ZoomOut className="w-4 h-4" />
                    </button>
                    <div className="relative">
                        <button
                            onClick={() => setShowZoomMenu(!showZoomMenu)}
                            className="flex items-center gap-1 px-2 py-1 min-w-[60px] justify-center text-sm font-medium text-slate-700"
                        >
                            {zoom}%
                            <ChevronDown className="w-3 h-3" />
                        </button>
                        {showZoomMenu && (
                            <div className="absolute top-full left-0 mt-1 w-24 bg-white rounded-lg shadow-xl border z-50">
                                {zoomOptions.map(z => (
                                    <button
                                        key={z}
                                        onClick={() => { onZoomChange(z); setShowZoomMenu(false); }}
                                        className={`w-full px-3 py-2 text-left text-sm hover:bg-indigo-50 ${z === zoom ? 'text-indigo-600 bg-indigo-50' : 'text-slate-700'}`}
                                    >
                                        {z}%
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <button
                        onClick={() => onZoomChange(Math.min(300, zoom + 25))}
                        className="w-8 h-8 rounded flex items-center justify-center text-slate-600 hover:bg-white hover:shadow-sm transition-all"
                    >
                        <ZoomIn className="w-4 h-4" />
                    </button>
                </div>

                <div className="w-px h-8 bg-slate-200" />

                {/* File Actions */}
                <button
                    onClick={onImport}
                    title="Import"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100"
                >
                    <Upload className="w-4 h-4" />
                </button>
                <button
                    onClick={onExport}
                    title="Export"
                    className="w-9 h-9 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100"
                >
                    <Download className="w-4 h-4" />
                </button>
                <button
                    onClick={onSave}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                    <Save className="w-4 h-4" />
                    <span className="text-sm font-medium">Save</span>
                </button>
            </div>
        </div>
    );
};

export default CanvasToolbar;
