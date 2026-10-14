/**
 * Konva Canvas Editor Component
 * Base Canva-like canvas editor using Konva.js
 * 
 * Phase 1: Foundation Implementation
 * - Basic canvas with undo/redo
 * - Shape tools (rectangle, circle, line)
 * - Text element support
 * - Image upload capability
 * - Background color control
 * - Export functionality
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Stage, Layer, Rect, Text, Image, Transformer, Circle, Line } from 'react-konva';
import Button from '../ui/Button';
import html2canvas from 'html2canvas';
import {
  Pointer, Square, Minus, Type, ImageIcon,
  Circle as CircleIcon, Trash2, Undo2, Redo2, Download,
} from 'lucide-react';

// Types
interface CanvasElement {
  id: string;
  type: 'rect' | 'circle' | 'text' | 'image' | 'line';
  x: number;
  y: number;
  width?: number;
  height?: number;
  rotation?: number;
  scaleX?: number;
  scaleY?: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  text?: string;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string;
  src?: string;
  draggable: boolean;
}

interface Template {
  id: string;
  name: string;
  category: string;
  thumbnail: string;
  width: number;
  height: number;
}

// Predefined templates
const TEMPLATES: Template[] = [
  {
    id: 'social-post-square',
    name: 'Social Media Post',
    category: 'Social Media',
    thumbnail: '📱',
    width: 1200,
    height: 627,
  },
  {
    id: 'presentation-16-9',
    name: 'Presentation 16:9',
    category: 'Presentation',
    thumbnail: '📊',
    width: 1920,
    height: 1080,
  },
  {
    id: 'marketing-banner',
    name: 'Marketing Banner',
    category: 'Marketing',
    thumbnail: '🎨',
    width: 1200,
    height: 400,
  },
  {
    id: 'business-card',
    name: 'Business Card',
    category: 'Business',
    thumbnail: '💼',
    width: 800,
    height: 500,
  },
];

const ImageElement: React.FC<{ src: string; [key: string]: any }> = ({ src, ...props }) => {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  useEffect(() => {
    const img = new window.Image();
    img.crossOrigin = 'anonymous';
    img.src = src;
    img.onload = () => setImage(img);
  }, [src]);
  return image ? <Image image={image} {...props} /> : null;
};

const KonvaCanvasEditor: React.FC = () => {
  const [elements, setElements] = useState<CanvasElement[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [history, setHistory] = useState<CanvasElement[][]>([]);
  const [historyStep, setHistoryStep] = useState<number>(-1);
  const [selectedTool, setSelectedTool] = useState<'select' | 'text' | 'rectangle' | 'circle' | 'line' | 'image'>('select');
  const [backgroundColor, setBackgroundColor] = useState<string>('#ffffff');

  // References
  const stageRef = useRef<any>(null);
  const transformerRef = useRef<any>(null);
  const selectionRectRef = useRef<any>(null);

  // History management
  const MAX_HISTORY = 50;

  const addToHistory = useCallback((newElements: CanvasElement[]) => {
    setHistory(prev => {
      const snapshot = elements;
      const newHistory = [snapshot, ...prev];
      if (newHistory.length > MAX_HISTORY) {
        newHistory.pop();
      }
      setHistoryStep(newHistory.length - 1);
      return newHistory;
    });
    setElements(newElements);
  }, [elements]);

  const undo = useCallback(() => {
    if (historyStep >= 0) {
      setElements(history[historyStep]);
      setHistoryStep(prev => prev - 1);
    }
  }, [history, historyStep]);

  const redo = useCallback(() => {
    if (historyStep < history.length - 2) {
      setElements(history[historyStep + 2]);
      setHistoryStep(prev => prev + 1);
    }
  }, [history, historyStep]);

  // Tool handlers
  const handleToolSelect = useCallback((tool: 'select' | 'text' | 'rectangle' | 'circle' | 'line' | 'image') => {
    setSelectedTool(tool);
    setSelectedIds(new Set());
  }, [selectedIds]);

  // Canvas click handler (deselect when clicking empty space)
  const handleStageClick = useCallback((e: any) => {
    const clickedOnEmpty = e.target === e.target;
    if (clickedOnEmpty) {
      setSelectedIds(new Set());
    }
  }, [selectedIds]);

  // Element selection
  const handleStageMouseDown = useCallback((e: any) => {
    if (e.target === e.target) {
      return;
    }
    const shapeId = e.target.id();
    if (!selectedIds.has(shapeId)) {
      setSelectedIds(new Set([shapeId]));
    }
  }, [selectedIds]);

  // Add rectangle
  const addRectangle = useCallback(() => {
    const id = crypto.randomUUID();
    const rect: CanvasElement = {
      id,
      type: 'rect',
      x: 100,
      y: 100,
      width: 150,
      height: 100,
      fill: 'transparent',
      stroke: '#000000',
      strokeWidth: 2,
      draggable: true,
    };
    addToHistory([rect]);
  }, [addToHistory]);

  // Add circle
  const addCircle = useCallback(() => {
    const id = crypto.randomUUID();
    const circle: CanvasElement = {
      id,
      type: 'circle',
      x: 300,
      y: 200,
      width: 100,
      height: 100,
      fill: 'transparent',
      stroke: '#000000',
      strokeWidth: 2,
      draggable: true,
    };
    addToHistory([circle]);
  }, [addToHistory]);

  // Add text
  const addText = useCallback(() => {
    const id = crypto.randomUUID();
    const text: CanvasElement = {
      id,
      type: 'text',
      x: 200,
      y: 150,
      text: 'Click to edit',
      fontSize: 24,
      fontFamily: 'Arial',
      fill: '#000000',
      draggable: true,
    };
    addToHistory([text]);
  }, [addToHistory]);

  // Add image
  const addImage = useCallback(() => {
    const id = crypto.randomUUID();
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = async (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const dataUrl = event.target.result as string;
          const image: CanvasElement = {
            id,
            type: 'image',
            x: 400,
            y: 100,
            width: 200,
            height: 200,
            src: dataUrl,
            draggable: true,
          };
          addToHistory([image]);
        };
        reader.readAsDataURL(file);
      }
    };
    input.click();
  }, [addToHistory]);

// Delete selected
const deleteSelected = useCallback(() => {
  if (selectedIds.size > 0) {
    const newElements = elements.filter(el => !selectedIds.has(el.id));
    addToHistory(newElements);
    setSelectedIds(new Set());
  }
}, [elements, selectedIds, addToHistory]);

// Update element properties
const updateElement = useCallback((id: string, updates: Partial<CanvasElement>) => {
  setElements(prev => prev.map(el =>
    el.id === id ? { ...el, ...updates } : el
  ));
}, []);

// Background color change
const handleBackgroundColorChange = useCallback((color: string) => {
  setBackgroundColor(color);
}, []);

// Export functionality
const handleExport = useCallback(async (format: 'png' | 'svg' | 'pdf') => {
  if (!stageRef.current) return;

  const dataURL = stageRef.current.toDataURL();

  if (format === 'png') {
    const link = document.createElement('a');
    link.download = `canvas-export-${Date.now()}.png`;
    link.href = dataURL;
    link.click();
  } else if (format === 'svg') {
    const link = document.createElement('a');
    link.download = `canvas-export-${Date.now()}.svg`;
    link.href = dataURL;
    link.click();
  }
}, [stageRef]);

// Template application
const applyTemplate = useCallback((templateId: string) => {
  // Clear current elements
  setElements([]);
  setHistory([[]]);
  setHistoryStep(-1);

  const template = TEMPLATES.find(t => t.id === templateId);
  if (template) {
    stageRef.current.width(template.width);
    stageRef.current.height(template.height);
    // Add template-specific elements
    if (template.category === 'Social Media') {
      // Add some shapes to match template
      addRectangle();
    } else if (template.category === 'Presentation') {
      // Add title box
      const textId = crypto.randomUUID();
      const textElement: CanvasElement = {
        id: textId,
        type: 'text',
        x: template.width / 2,
        y: 80,
        text: 'Your Presentation Title',
        fontSize: 32,
        fontFamily: 'Arial',
        fontWeight: 'bold',
        fill: '#333333',
        draggable: true,
      };
      setElements([textElement]);
    }
  }
}, [stageRef]);

// Delete key handler
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // Delete key
    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedIds.size > 0) {
      e.preventDefault();
      deleteSelected();
    }
    // Undo (Ctrl+Z)
    else if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      undo();
    }
    // Redo (Ctrl+Y or Ctrl+Shift+Z)
    else if ((e.key === 'y' && (e.ctrlKey || e.metaKey)) || (e.key === 'z' && e.ctrlKey)) {
      e.preventDefault();
      redo();
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => {
    window.removeEventListener('keydown', handleKeyDown);
  };
}, []);

return (
  <div className="flex flex-col h-full bg-slate-100">
    {/* Toolbar */}
    <div className="flex items-center gap-2 bg-white border-b p-4 shadow-sm">
      <div className="flex items-center gap-2">
        {/* Selection Tool */}
        <button
          className={`p-2 rounded-lg border-2 transition-colors ${selectedTool === 'select' ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          onClick={() => handleToolSelect('select')}
          title="Select Tool (V)"
        >
<Pointer className="w-5 h-5" />
        </button>

        {/* Rectangle Tool */}
        <button
          className={`p-2 rounded-lg border-2 transition-colors ${selectedTool === 'rectangle' ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          onClick={() => handleToolSelect('rectangle')}
          title="Rectangle Tool (R)"
        >
          <Square className="w-5 h-5" />
        </button>

        {/* Circle Tool */}
        <button
          className={`p-2 rounded-lg border-2 transition-colors ${selectedTool === 'circle' ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          onClick={() => handleToolSelect('circle')}
          title="Circle Tool (C)"
        >
          <CircleIcon className="w-5 h-5" />
        </button>

        {/* Line Tool */}
        <button
          className={`p-2 rounded-lg border-2 transition-colors ${selectedTool === 'line' ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          onClick={() => handleToolSelect('line')}
          title="Line Tool (L)"
        >
          <Minus className="w-5 h-5" />
        </button>

        {/* Text Tool */}
        <button
          className={`p-2 rounded-lg border-2 transition-colors ${selectedTool === 'text' ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          onClick={() => handleToolSelect('text')}
          title="Text Tool (T)"
        >
          <Type className="w-5 h-5" />
        </button>

        {/* Image Tool */}
        <button
          className={`p-2 rounded-lg border-2 transition-colors ${selectedTool === 'image' ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
          onClick={() => handleToolSelect('image')}
          title="Image Tool (I)"
        >
          <ImageIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Background Color Picker */}
      <div className="flex items-center gap-2 ml-4">
        <label className="text-sm font-medium text-slate-700">Background:</label>
        <input
          type="color"
          value={backgroundColor}
          onChange={(e) => handleBackgroundColorChange(e.target.value)}
          className="w-10 h-10 rounded cursor-pointer border-2"
        />
        <button
          onClick={() => setBackgroundColor('#ffffff')}
          className="ml-2 px-3 py-1 text-sm bg-white border rounded"
        >
          Reset
        </button>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={deleteSelected}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
          disabled={selectedIds.size === 0}
          title="Delete Selected (Delete)"
        >
          <Trash2 className="w-5 h-5" />
        </button>

        <button
          onClick={undo}
          className="px-4 py-2 bg-slate-200 rounded hover:bg-slate-300 disabled:opacity-50"
          disabled={historyStep < 0}
          title="Undo (Ctrl+Z)"
        >
          <Undo2 className="w-5 h-5" />
        </button>

        <button
          onClick={redo}
          className="px-4 py-2 bg-slate-200 rounded hover:bg-slate-300 disabled:opacity-50"
          disabled={historyStep >= history.length - 1}
          title="Redo (Ctrl+Y)"
        >
          <Redo2 className="w-5 h-5" />
        </button>

        <button
          onClick={() => handleExport('png')}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center gap-2"
          title="Export as PNG"
        >
          <Download className="w-5 h-5" />
        </button>
      </div>
    </div>

    {/* Canvas Area */}
    <div className="flex-1 bg-slate-200 flex items-center justify-center overflow-auto">
      <Stage
        ref={stageRef}
        width={1000}
        height={700}
        style={{
          border: '2px solid #e2e8f0',
          backgroundColor: backgroundColor,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        }}
        onClick={handleStageClick}
        onMouseDown={handleStageMouseDown}
      >
        {elements.map(el => (
          <React.Fragment key={el.id}>
            {el.type === 'rect' && (
              <Rect
                key={el.id}
                id={el.id}
                x={el.x}
                y={el.y}
                width={el.width}
                height={el.height}
                fill={el.fill}
                stroke={el.stroke}
                strokeWidth={el.strokeWidth}
                rotation={el.rotation || 0}
                scaleX={el.scaleX || 1}
                scaleY={el.scaleY || 1}
                draggable
                onDragEnd={(e) => {
                  updateElement(el.id, {
                    x: e.target.x(),
                    y: e.target.y(),
                  });
                }}
              />
            )}

            {el.type === 'circle' && (
              <Circle
                key={el.id}
                id={el.id}
                x={el.x}
                y={el.y}
                radius={el.width / 2}
                fill={el.fill}
                stroke={el.stroke}
                strokeWidth={el.strokeWidth}
                rotation={el.rotation || 0}
                scaleX={el.scaleX || 1}
                scaleY={el.scaleY || 1}
                draggable
              />
            )}

            {el.type === 'text' && (
              <Text
                key={el.id}
                id={el.id}
                x={el.x}
                y={el.y}
                text={el.text}
                fontSize={el.fontSize}
                fontFamily={el.fontFamily}
                fill={el.fill}
                draggable
                onDragEnd={(e) => {
                  updateElement(el.id, {
                    x: e.target.x(),
                    y: e.target.y(),
                  });
                }}
                onDblClick={() => {
                  // Future: Enable inline editing
                  console.log('Text double-click:', el.id);
                }}
              />
            )}

            {el.type === 'image' && el.src && (
              <ImageElement
                key={el.id}
                id={el.id}
                x={el.x}
                y={el.y}
                width={el.width}
                height={el.height}
                src={el.src}
                draggable
                onDragEnd={(e) => {
                  updateElement(el.id, {
                    x: e.target.x(),
                    y: e.target.y(),
                  });
                }}
              />
            )}

            {el.type === 'line' && (
              <Line
                key={el.id}
                id={el.id}
                x={el.x}
                y={el.y}
                points={[
                  el.x + (el.width || 0),
                  el.y + (el.height || 0),
                  el.x + (el.width || 0) + 100,
                  el.y + (el.height || 0) + 100,
                ]}
                stroke={el.stroke}
                strokeWidth={el.strokeWidth}
                draggable
                onDragEnd={(e) => {
                  updateElement(el.id, {
                    x: e.target.x(),
                    y: e.target.y(),
                  });
                }}
              />
            )}
          </React.Fragment>
        ))}
      </Stage>
    </div>

    {/* Status Bar */}
    <div className="fixed bottom-0 left-0 right-0 p-3 bg-white border-t border-slate-200 flex justify-between items-center">
      <div className="text-sm text-slate-600">
        {elements.length} element(s) • {selectedIds.size} selected •
        Press <kbd className="px-1 py-0.5 bg-slate-100 rounded">Delete</kbd> to remove selected
      </div>
      <div className="flex items-center gap-4">
        <span className="text-slate-400">Canvas: 1000×700px</span>
        <span className="text-slate-400">History: {historyStep + 1} / {history.length}</span>
      </div>
    </div>
  </div>
);
};

export default KonvaCanvasEditor;
