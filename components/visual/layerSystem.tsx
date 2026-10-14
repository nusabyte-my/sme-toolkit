/**
 * Layer System for Konva Canvas Editor
 * Manages different canvas element types and their properties
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Rect, Circle, Text, Image, Line, Transformer, Arrow } from 'react-konva';

interface LayerElement {
  id: string;
  type: 'rect' | 'circle' | 'text' | 'image' | 'line' | 'arrow';
  x: number;
  y: number;
  width?: number;
  height?: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  rotation?: number;
  scaleX?: number;
  scaleY?: number;
  text?: string;
  fontSize?: number;
  fontFamily?: string;
  src?: string;
  deleted?: boolean;
  konvaNode: any;
}

interface LayerSystemProps {
  elements: LayerElement[];
  selectedIds: Set<string>;
  onUpdateElement: (id: string, updates: Partial<LayerElement>) => void;
  onUpdateSelection: (selectedIds: Set<string>) => void;
}

interface LayerTool {
  id: 'select' | 'rect' | 'circle' | 'text' | 'image' | 'line' | 'arrow';
  label: string;
  icon: React.ReactNode;
}

const LAYER_TOOLS: LayerTool[] = [
  { id: 'select', label: 'Select', icon: 'CursorClick' },
  { id: 'rect', label: 'Rectangle', icon: 'Square' },
  { id: 'circle', label: 'Circle', icon: 'Circle' },
  { id: 'text', label: 'Text', icon: 'Type' },
  { id: 'image', label: 'Image', icon: 'Image' },
  { id: 'line', label: 'Line', icon: 'Minus' },
  { id: 'arrow', label: 'Arrow', icon: 'ArrowUp' },
];

const KonvaImageElement: React.FC<{ src: string; [key: string]: any }> = ({ src, ...props }) => {
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  useEffect(() => {
    const img = new window.Image();
    img.crossOrigin = 'anonymous';
    img.src = src;
    img.onload = () => setImage(img);
  }, [src]);
  return image ? <Image image={image} {...props} /> : null;
};

export const LayerSystem: React.FC<LayerSystemProps> = ({
  elements,
  selectedIds,
  onUpdateElement,
  onUpdateSelection,
}) => {
  const [selectedTool, setSelectedTool] = useState<'select' | 'rect' | 'circle' | 'text' | 'image' | 'line' | 'arrow'>('select');

  // Element handlers
  const updateElement = useCallback((id: string, updates: Partial<LayerElement>) => {
    onUpdateElement(id, updates);
  }, [onUpdateElement]);

  const updateSelection = useCallback((ids: Set<string>) => {
    onUpdateSelection(ids);
  }, [onUpdateSelection]);

  // Tool handlers
  const selectAll = useCallback(() => {
    const allIds = new Set(elements.map(el => el.id));
    onUpdateSelection(allIds);
  }, [elements, onUpdateSelection]);

  const deselectAll = useCallback(() => {
    onUpdateSelection(new Set());
  }, [onUpdateSelection]);

  const deleteSelected = useCallback(() => {
    if (selectedIds.size === 0) return;
    
    const remainingElements = elements.filter(el => !selectedIds.has(el.id));
    const deletedIds = Array.from(selectedIds);
    
    onUpdateSelection(new Set());
    
    deletedIds.forEach(id => {
      onUpdateElement(id, { deleted: true });
    });
    
    return deletedIds;
  }, [selectedIds, onUpdateElement]);

  const duplicateSelected = useCallback(() => {
    if (selectedIds.size === 0) return;
    
    const idsToDuplicate = Array.from(selectedIds);
    const currentElements = elements.filter(el => selectedIds.has(el.id));
    
    const duplicatedElements = currentElements.map(el => ({
      ...el,
      id: `${el.id}-dup-${Date.now()}`,
      konvaNode: el.konvaNode,
    }));
    
    onUpdateSelection(new Set([...selectedIds, ...duplicatedElements.map(el => el.id)]));
  }, [selectedIds, elements, onUpdateElement]);

  // Layer grouping
  const getLayeredElements = useCallback((layer: number) => {
    // Elements with z-index for proper layering
    return [...elements].sort((a, b) => {
      const zA = (a as any).zIndex();
      const zB = (b as any).zIndex();
      return zA - zB;
    });
  }, [elements]);

  // Render function for individual elements
  const renderElement = (element: LayerElement): React.ReactNode => {
    switch (element.type) {
      case 'rect':
        return (
          <Rect
            key={element.id}
            id={element.id}
            x={element.x}
            y={element.y}
            width={element.width}
            height={element.height}
            fill={element.fill}
            stroke={element.stroke}
            strokeWidth={element.strokeWidth}
            rotation={element.rotation || 0}
            scaleX={element.scaleX || 1}
            scaleY={element.scaleY || 1}
            draggable
            onDragEnd={(e) => {
              updateElement(element.id, {
                x: e.target.x(),
                y: e.target.y(),
              });
            }}
          />
        );
      
      case 'circle':
        return (
          <Circle
            key={element.id}
            id={element.id}
            x={element.x}
            y={element.y}
            radius={element.width / 2}
            fill={element.fill}
            stroke={element.stroke}
            strokeWidth={element.strokeWidth}
            rotation={element.rotation || 0}
            scaleX={element.scaleX || 1}
            scaleY={element.scaleY || 1}
            draggable
            onDragEnd={(e) => {
              updateElement(element.id, {
                x: e.target.x(),
                y: e.target.y(),
              });
            }}
          />
        );
      
      case 'text':
        return (
          <Text
            key={element.id}
            id={element.id}
            x={element.x}
            y={element.y}
            text={element.text}
            fontSize={element.fontSize}
            fontFamily={element.fontFamily}
            fill={element.fill}
            draggable
            onDragEnd={(e) => {
              updateElement(element.id, {
                x: e.target.x(),
                y: e.target.y(),
              });
            }}
            onDblClick={() => {
              // Future: Open inline editor
              console.log('Text double-click:', element.id);
            }}
          />
        );
      
      case 'image':
        return element.src ? (
          <KonvaImageElement
            key={element.id}
            id={element.id}
            x={element.x}
            y={element.y}
            width={element.width}
            height={element.height}
            src={element.src}
            draggable
            onDragEnd={(e) => {
              updateElement(element.id, {
                x: e.target.x(),
                y: e.target.y(),
              });
            }}
          />
        ) : null;
      
      case 'line':
        return (
          <Line
            key={element.id}
            id={element.id}
            points={[
              element.x + (element.width || 0),
              element.y + (element.height || 0),
              element.x + (element.width || 0) + (element.height || 0),
              element.y + (element.height || 0),
            ]}
            stroke={element.stroke}
            strokeWidth={element.strokeWidth}
            draggable
            onDragEnd={(e) => {
              updateElement(element.id, {
                x: e.target.x(),
                y: e.target.y(),
              });
            }}
          />
        );
      
      case 'arrow':
        return (
          <Arrow
            key={element.id}
            id={element.id}
            x={element.x}
            y={element.y}
            points={[
              element.x,
              element.y,
              element.x + (element.width || 100),
              element.y + (element.height || 100),
            ]}
            pointerLength={10}
            pointerWidth={10}
            draggable
            onDragEnd={(e) => {
              updateElement(element.id, {
                x: e.target.x(),
                y: e.target.y(),
              });
            }}
          />
        );
      
      default:
        return null;
    }
  };

  // Selection box rendering
  const renderSelectionBox = (element: LayerElement): React.ReactNode => {
    const isSelected = selectedIds.has(element.id);
    
    if (!isSelected) return null;
    
    const el = element.konvaNode;
    const box = el.getSelfRect();
    
    return (
      <div
        key={`${element.id}-selection`}
        style={{
          position: 'absolute',
          left: box.x - 4,
          top: box.y - 4,
          width: box.width + 8,
          height: box.height + 8,
          border: '2px dashed #0066ff',
          borderRadius: '4px',
        }}
      >
        <div
          className="absolute top-2 left-2 w-full h-full"
          style={{
            borderColor: isSelected ? '#0066ff' : 'transparent',
            backgroundColor: isSelected ? 'rgba(0, 102, 255, 0.1)' : 'transparent',
          }}
        />
        <div
          className="absolute w-full h-full flex items-center justify-center pointer-events-none"
          style={{
            opacity: isSelected ? 0.3 : 1,
            cursor: 'move',
          }}
        >
          <svg
            viewBox="0 0 100 100"
            className="w-full h-full"
          style={{ overflow: 'visible' }}
          >
            <path
              d={el.getPath()}
              fill="none"
              stroke={isSelected ? '#0066ff' : 'transparent'}
              strokeWidth={2}
              strokeDasharray="4,4"
            />
          </svg>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex gap-2 p-4 border-b bg-white border-slate-200">
        {LAYER_TOOLS.map(tool => (
          <button
            key={tool.id}
            onClick={() => {
              if (tool.id === 'select') {
                selectAll();
              } else if (tool.id === 'image') {
                // Future: Add image handler
              }
            }}
            className={`p-2 rounded-lg border-2 transition-colors ${
              selectedTool === tool.id ? 'bg-indigo-600 text-white' : 'hover:bg-slate-50'
            }`}
            title={tool.label}
          >
            {tool.icon}
          </button>
        ))}
        
        <div className="flex items-center gap-4 ml-4">
          <button
            onClick={deleteSelected}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
            disabled={selectedIds.size === 0}
          >
            <svg className="w-4 h-4" fill="currentColor">
              <path d="M19 7 13l-8 2 12h5v-2H5a3 6H5v5a2.5a12 19 12h5v19 12m9 12m12 5m-19 7a5 7m5.5m5 5m5 5a19m7a5m5" />
            </svg>
          </button>
          
          <button
            onClick={deselectAll}
            className="px-3 py-1 bg-slate-200 text-slate-700 rounded hover:bg-slate-300"
          >
            <svg className="w-4 h-4" fill="currentColor">
              <path d="M4 4 4l4 4v4 4v1.414l4 4v4h1a1 1 1 1 1.41 5a1 4 19 12h5v19 12m9 12m12 5m5" />
            </svg>
            </button>
          
          <button
            onClick={duplicateSelected}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            disabled={selectedIds.size === 0}
          >
            <svg className="w-4 h-4" fill="currentColor">
              <path d="M8 8v8 8m8 8v4h1a1 1 1 1 41 5a1 4 19 12h5v19 12m9 12m12 5m5" />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Canvas Area */}
      <div className="flex-1 bg-slate-100">
        {getLayeredElements(0).map(renderElement)}
      </div>
    </div>
  );
};

export default LayerSystem;
