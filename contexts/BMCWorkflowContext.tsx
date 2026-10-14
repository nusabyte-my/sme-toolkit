import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { BusinessCanvasData } from '../types';
import type { UserProfile, BusinessProfile } from '../types/profiles';

interface BMCVersion {
  id: string;
  timestamp: number;
  canvas: BusinessCanvasData;
  notes?: string;
  isDraft?: boolean;
}

interface BMCWorkflowContextType {
  canvas: BusinessCanvasData;
  versions: BMCVersion[];
  currentVersionId: string | null;
  isDirty: boolean;
  qualityScore: number | null;

  setCanvas: (canvas: BusinessCanvasData) => void;
  updateBlock: (block: keyof BusinessCanvasData, items: string[]) => void;
  addToBlock: (block: keyof BusinessCanvasData, item: string) => void;
  removeFromBlock: (block: keyof BusinessCanvasData, index: number) => void;
  
  saveVersion: (notes?: string) => void;
  restoreVersion: (versionId: string) => void;
  deleteVersion: (versionId: string) => void;
  
  calculateQualityScore: () => number;
  clearCanvas: () => void;
  
  loadFromProfile: (userProfile: UserProfile, businessProfile: BusinessProfile) => void;
}

const BMCWorkflowContext = createContext<BMCWorkflowContextType | null>(null);

interface BMCWorkflowProviderProps {
  children: ReactNode;
  initialCanvas?: BusinessCanvasData;
}

const INITIAL_CANVAS: BusinessCanvasData = {
  keyPartners: [],
  keyActivities: [],
  keyResources: [],
  valuePropositions: [],
  customerRelationships: [],
  channels: [],
  customerSegments: [],
  costStructure: [],
  revenueStreams: []
};

export const BMCWorkflowProvider: React.FC<BMCWorkflowProviderProps> = ({ 
  children, 
  initialCanvas 
}) => {
  const [canvas, setCanvasState] = useState<BusinessCanvasData>(initialCanvas || INITIAL_CANVAS);
  const [versions, setVersions] = useState<BMCVersion[]>([]);
  const [currentVersionId, setCurrentVersionId] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [qualityScore, setQualityScore] = useState<number | null>(null);

  const setCanvas = useCallback((newCanvas: BusinessCanvasData) => {
    setCanvasState(newCanvas);
    setIsDirty(true);
    setQualityScore(calculateQualityScoreInternal(newCanvas));
  }, []);

  const updateBlock = useCallback((block: keyof BusinessCanvasData, items: string[]) => {
    setCanvasState(prev => ({
      ...prev,
      [block]: items
    }));
    setIsDirty(true);
  }, []);

  const addToBlock = useCallback((block: keyof BusinessCanvasData, item: string) => {
    setCanvasState(prev => ({
      ...prev,
      [block]: [...(prev[block] || []), item]
    }));
    setIsDirty(true);
  }, []);

  const removeFromBlock = useCallback((block: keyof BusinessCanvasData, index: number) => {
    setCanvasState(prev => ({
      ...prev,
      [block]: prev[block]?.filter((_, i) => i !== index) || []
    }));
    setIsDirty(true);
  }, []);

  const calculateQualityScoreInternal = (canvasData: BusinessCanvasData): number => {
    const blocks = Object.keys(canvasData) as (keyof BusinessCanvasData)[];

    const completeness = (blocks.filter(block => 
      canvasData[block] && canvasData[block].length > 0
    ).length / blocks.length) * 100;

    const totalItems = blocks.reduce((sum, block) => 
      sum + (canvasData[block]?.length || 0), 0
    );
    const depth = Math.min(100, (totalItems / 18) * 100);

    const coherence = calculateCoherenceScoreInternal(canvasData);

    return Math.round((completeness * 0.4 + depth * 0.3 + coherence * 0.3));
  };

  const calculateCoherenceScoreInternal = (canvasData: BusinessCanvasData): number => {
    let coherenceScore = 50;

    if (canvasData.customerSegments?.length && canvasData.valuePropositions?.length) {
      coherenceScore += 15;
    }

    if (canvasData.channels?.length && canvasData.customerSegments?.length) {
      coherenceScore += 15;
    }

    if (canvasData.revenueStreams?.length && canvasData.valuePropositions?.length) {
      coherenceScore += 10;
    }

    if (canvasData.costStructure?.length && canvasData.keyActivities?.length) {
      coherenceScore += 10;
    }

    return Math.min(100, coherenceScore);
  };

  const saveVersion = useCallback((notes?: string) => {
    const newVersion: BMCVersion = {
      id: Date.now().toString(),
      timestamp: Date.now(),
      canvas: { ...canvas },
      notes,
      isDraft: false
    };

    setVersions(prev => [newVersion, ...prev]);
    setCurrentVersionId(newVersion.id);
    setIsDirty(false);
    setQualityScore(calculateQualityScoreInternal(canvas));
  }, [canvas]);

  const restoreVersion = useCallback((versionId: string) => {
    const version = versions.find(v => v.id === versionId);
    if (version) {
      setCanvasState(version.canvas);
      setCurrentVersionId(versionId);
      setIsDirty(false);
      setQualityScore(calculateQualityScoreInternal(version.canvas));
    }
  }, [versions]);

  const deleteVersion = useCallback((versionId: string) => {
    setVersions(prev => prev.filter(v => v.id !== versionId));
    if (currentVersionId === versionId) {
      setCurrentVersionId(null);
    }
  }, [currentVersionId]);

  const clearCanvas = useCallback(() => {
    setCanvasState(INITIAL_CANVAS);
    setCurrentVersionId(null);
    setIsDirty(false);
    setQualityScore(0);
  }, []);

  const loadFromProfile = useCallback((userProfile: UserProfile, businessProfile: BusinessProfile) => {
    // BusinessProfile has no products array — derive value props from the business
    // description sentences (honest derivation instead of a phantom field).
    const derivedValueProps = (businessProfile.business_description || '')
      .split(/[.,\n]/)
      .map(s => s.trim())
      .filter(Boolean)
      .slice(0, 4);

    const profileBasedCanvas: BusinessCanvasData = {
      keyPartners: [],
      keyActivities: [],
      keyResources: [],
      valuePropositions: derivedValueProps,
      customerRelationships: [],
      channels: [],
      customerSegments: businessProfile.industry ? [`${businessProfile.industry} customers`] : [],
      costStructure: [],
      revenueStreams: businessProfile.industry ? [`Revenue from ${businessProfile.industry} offerings`] : []
    };

    setCanvasState(profileBasedCanvas);
    setIsDirty(true);
  }, []);

  const value: BMCWorkflowContextType = {
    canvas,
    versions,
    currentVersionId,
    isDirty,
    qualityScore,
    setCanvas,
    updateBlock,
    addToBlock,
    removeFromBlock,
    saveVersion,
    restoreVersion,
    deleteVersion,
    calculateQualityScore: useCallback(() => calculateQualityScoreInternal(canvas), [canvas]),
    clearCanvas,
    loadFromProfile
  };

  return (
    <BMCWorkflowContext.Provider value={value}>
      {children}
    </BMCWorkflowContext.Provider>
  );
};

export const useBMCWorkflow = () => {
  const context = useContext(BMCWorkflowContext);
  if (!context) {
    throw new Error('useBMCWorkflow must be used within a BMCWorkflowProvider');
  }
  return context;
};
