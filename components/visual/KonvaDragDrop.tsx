/**
 * Drag and Drop Integration for Konva Canvas
 * Uses Konva-native drag events with snap-to-grid and guideline snapping
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Rect, Circle, Text, Image, Line } from 'react-konva';

interface LayerElement {
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
  src?: string;
}

interface KonvaDragDropProps {
  enabled: boolean;
  snapToGrid: boolean;
  snapToGuidelines: boolean;
  allowGrouping: boolean;
  allowNestedGroups: boolean;
  collisionThreshold: number;
  elements: LayerElement[];
  updateElement: (id: string, attrs: Partial<LayerElement>) => void;
}

interface DropTarget {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

const DEFAULT_CONFIG = {
  enabled: true,
  snapToGrid: true,
  snapToGuidelines: true,
  allowGrouping: true,
  allowNestedGroups: false,
  collisionThreshold: 5,
};

const GRID_SIZE = 20;

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

const snapToGridValue = (val: number, gridSize: number): number =>
  Math.round(val / gridSize) * gridSize;

export const KonvaDragDrop: React.FC<KonvaDragDropProps> = ({
  enabled = DEFAULT_CONFIG.enabled,
  snapToGrid = DEFAULT_CONFIG.snapToGrid,
  snapToGuidelines = DEFAULT_CONFIG.snapToGuidelines,
  collisionThreshold = DEFAULT_CONFIG.collisionThreshold,
  elements,
  updateElement,
}) => {
  const [dragging, setDragging] = useState(false);
  const [draggedElementId, setDraggedElementId] = useState<string | null>(null);

  const handleDragStart = useCallback((e: any) => {
    const shape = e.target;
    const id = shape.id();
    setDragging(true);
    setDraggedElementId(id);
  }, []);

  const handleDragMove = useCallback((e: any) => {
    if (!snapToGrid) return;
    const shape = e.target;
    const newX = snapToGridValue(shape.x(), GRID_SIZE);
    const newY = snapToGridValue(shape.y(), GRID_SIZE);
    shape.position({ x: newX, y: newY });
  }, [snapToGrid]);

  const handleDragEnd = useCallback((e: any) => {
    const shape = e.target;
    const id = shape.id();

    let newX = shape.x();
    let newY = shape.y();

    if (snapToGrid) {
      newX = snapToGridValue(newX, GRID_SIZE);
      newY = snapToGridValue(newY, GRID_SIZE);
    }

    updateElement(id, { x: newX, y: newY });

    setDragging(false);
    setDraggedElementId(null);
  }, [snapToGrid, updateElement]);

  const renderElement = (el: LayerElement) => {
    const commonProps = {
      key: el.id,
      id: el.id,
      x: el.x,
      y: el.y,
      fill: el.fill,
      stroke: el.stroke,
      strokeWidth: el.strokeWidth,
      rotation: el.rotation || 0,
      scaleX: el.scaleX || 1,
      scaleY: el.scaleY || 1,
      draggable: enabled,
      onDragStart: handleDragStart,
      onDragMove: handleDragMove,
      onDragEnd: handleDragEnd,
    };

    switch (el.type) {
      case 'rect':
        return (
          <Rect
            {...commonProps}
            width={el.width || 100}
            height={el.height || 100}
          />
        );

      case 'circle':
        return (
          <Circle
            {...commonProps}
            radius={(el.width || 100) / 2}
          />
        );

      case 'text':
        return (
          <Text
            {...commonProps}
            text={el.text || ''}
            fontSize={el.fontSize || 16}
            fontFamily={el.fontFamily || 'Arial'}
          />
        );

      case 'image':
        return el.src ? (
          <KonvaImageElement
            {...commonProps}
            width={el.width || 100}
            height={el.height || 100}
            src={el.src}
          />
        ) : null;

      case 'line':
        return (
          <Line
            {...commonProps}
            points={[
              el.x,
              el.y,
              el.x + (el.width || 100),
              el.y + (el.height || 100),
            ]}
          />
        );

      default:
        return null;
    }
  };

  return <>{elements.map(renderElement)}</>;
};

export default KonvaDragDrop;
