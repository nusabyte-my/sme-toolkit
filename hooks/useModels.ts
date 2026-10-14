/**
 * useModels Hook
 * React hook for managing AI model selection and preferences
 */

import { useState, useEffect, useCallback } from 'react';
import { authenticatedFetch } from '../services/apiClient';

export interface Model {
    id: string;
    name: string;
    description: string;
    capabilities: string[];
    costPerToken?: number;
    costPerImage?: number;
    costPerSecond?: number;
    performance: { speed: string; quality: string };
    available: boolean;
    category: 'premium' | 'standard' | 'free';
    providerId: string;
}

export interface ModelPreference {
    modality: string;
    modelId: string;
    providerId: string;
}

interface UseModelsReturn {
    models: Record<string, Model[]>;
    preferences: Record<string, ModelPreference>;
    loading: boolean;
    error: string | null;
    getModelsForType: (type: 'llm' | 'image' | 'video') => Model[];
    getSelectedModel: (type: 'llm' | 'image' | 'video') => Model | null;
    setModelPreference: (type: 'llm' | 'image' | 'video', modelId: string, providerId: string) => Promise<void>;
    refreshModels: () => Promise<void>;
}


// Default models for development
const DEFAULT_MODELS: Record<string, Model[]> = {
    llm: [
        { id: 'fiqstr/deepseek-3.2', name: 'Deepseek 3.2', description: 'Fiqstr V2 OpenAI-compatible reasoning model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard', providerId: 'fiqstr-v2' },
        { id: 'fiqstr/glm-5', name: 'Glm 5', description: 'Fiqstr V2 OpenAI-compatible chat model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard', providerId: 'fiqstr-v2' },
        { id: 'fiqstr/minimax-m2.1', name: 'Minimax M2.1', description: 'Fiqstr V2 OpenAI-compatible chat model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard', providerId: 'fiqstr-v2' },
        { id: 'fiqstr/minimax-m2.5', name: 'Minimax M2.5', description: 'Fiqstr V2 OpenAI-compatible chat model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard', providerId: 'fiqstr-v2' },
        { id: 'fiqstr/qwen3-coder-next', name: 'Qwen3 Coder Next', description: 'Fiqstr V2 OpenAI-compatible coding model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard', providerId: 'fiqstr-v2' },
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: 'Fast with excellent quality', capabilities: ['chat', 'code'], costPerToken: 0.00001, performance: { speed: '500 tok/s', quality: 'excellent' }, available: true, category: 'standard', providerId: 'google' },
        { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'High-quality reasoning', capabilities: ['chat', 'code', 'multimodal'], costPerToken: 0.000035, performance: { speed: '50 tok/s', quality: 'excellent' }, available: true, category: 'premium', providerId: 'google' },
        { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', description: 'Ultra-fast open source', capabilities: ['chat', 'code'], costPerToken: 0.00059, performance: { speed: '300 tok/s', quality: 'high' }, available: true, category: 'standard', providerId: 'groq' },
    ],
    image: [
        { id: 'imagen-3', name: 'Imagen 3', description: 'Highest quality images', capabilities: ['text-to-image'], costPerImage: 0.04, performance: { speed: '8s', quality: 'excellent' }, available: true, category: 'premium', providerId: 'google' },
        { id: 'flux-1-schnell', name: 'FLUX Schnell', description: 'Fast generation', capabilities: ['text-to-image'], costPerImage: 0.003, performance: { speed: '2s', quality: 'high' }, available: true, category: 'free', providerId: 'flux' },
    ],
    video: [
        { id: 'veo-3', name: 'Veo 3', description: 'Advanced video generation', capabilities: ['text-to-video'], costPerSecond: 0.05, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'premium', providerId: 'google' },
    ],
};

const DEFAULT_PREFERENCES: Record<string, ModelPreference> = {
    llm: { modality: 'llm', modelId: 'fiqstr/deepseek-3.2', providerId: 'fiqstr-v2' },
    image: { modality: 'image', modelId: 'flux-1-schnell', providerId: 'flux' },
    video: { modality: 'video', modelId: 'veo-3', providerId: 'google' },
};

const normalizeModel = (model: any): Model => ({
    id: model.id,
    name: model.name,
    description: model.description,
    capabilities: model.capabilities || [],
    costPerToken: model.cost_per_1k_tokens ?? model.costPerToken,
    costPerImage: model.cost_per_image ?? model.costPerImage,
    costPerSecond: model.cost_per_second ?? model.costPerSecond,
    performance: model.performance || { speed: 'unknown', quality: 'unknown' },
    available: model.available ?? true,
    category: model.category || 'standard',
    providerId: model.provider_id ?? model.providerId,
});

const mergeCanonicalModels = (type: 'llm' | 'image' | 'video', fetchedModels: Model[]): Model[] => {
    if (type !== 'llm') return fetchedModels;

    const existingIds = new Set(fetchedModels.map(model => `${model.providerId}:${model.id}`));
    const missingCanonicalModels: Model[] = [];

    for (const model of DEFAULT_MODELS.llm.filter(model => model.providerId === 'fiqstr-v2')) {
        const key = `${model.providerId}:${model.id}`;
        if (!existingIds.has(key)) {
            missingCanonicalModels.push(model);
        }
    }

    return [...missingCanonicalModels, ...fetchedModels];
};

export const useModels = (): UseModelsReturn => {
    const [models, setModels] = useState<Record<string, Model[]>>(DEFAULT_MODELS);
    const [preferences, setPreferences] = useState<Record<string, ModelPreference>>(DEFAULT_PREFERENCES);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchModels = useCallback(async () => {
        try {
            setLoading(true);

            const response = await authenticatedFetch('/api/v1/models/all');

            if (!response.ok) throw new Error('Failed to fetch models');

            const data = await response.json();

            const llmModels = data.llm?.providers?.flatMap((p: any) => p.models.map(normalizeModel)) || DEFAULT_MODELS.llm;
            const imageModels = data.image?.providers?.flatMap((p: any) => p.models.map(normalizeModel)) || DEFAULT_MODELS.image;
            const videoModels = data.video?.providers?.flatMap((p: any) => p.models.map(normalizeModel)) || DEFAULT_MODELS.video;

            setModels({
                llm: mergeCanonicalModels('llm', llmModels),
                image: mergeCanonicalModels('image', imageModels),
                video: mergeCanonicalModels('video', videoModels),
            });
        } catch (err) {
            console.warn('Using default models:', err);
            setModels(DEFAULT_MODELS);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchPreferences = useCallback(async () => {
        try {
            const types = ['llm', 'image', 'video'];
            const prefs: Record<string, ModelPreference> = {};

            for (const type of types) {
                const response = await authenticatedFetch(`/api/v1/models/preference/${type}`);

                if (response.ok) {
                    const data = await response.json();
                    prefs[type] = {
                        modality: type,
                        modelId: data.model_id || DEFAULT_PREFERENCES[type].modelId,
                        providerId: data.provider_id || DEFAULT_PREFERENCES[type].providerId,
                    };
                } else {
                    prefs[type] = DEFAULT_PREFERENCES[type];
                }
            }

            setPreferences(prefs);
        } catch (err) {
            setPreferences(DEFAULT_PREFERENCES);
        }
    }, []);

    const refreshModels = useCallback(async () => {
        await Promise.all([fetchModels(), fetchPreferences()]);
    }, [fetchModels, fetchPreferences]);

    const getModelsForType = useCallback((type: 'llm' | 'image' | 'video'): Model[] => {
        return models[type] || [];
    }, [models]);

    const getSelectedModel = useCallback((type: 'llm' | 'image' | 'video'): Model | null => {
        const pref = preferences[type];
        if (!pref) return null;

        const typeModels = models[type] || [];
        return typeModels.find(m => m.id === pref.modelId) || typeModels[0] || null;
    }, [models, preferences]);

    const setModelPreference = useCallback(async (
        type: 'llm' | 'image' | 'video',
        modelId: string,
        providerId: string
    ): Promise<void> => {
        try {
            const response = await authenticatedFetch('/api/v1/models/preference', 'PUT', {
                modality: type,
                model_id: modelId,
                provider_id: providerId,
            });

            if (!response.ok) throw new Error('Failed to update preference');
        } catch (err) {
            console.warn('Could not save preference to server:', err);
        }

        // Update local state regardless
        setPreferences(prev => ({
            ...prev,
            [type]: { modality: type, modelId, providerId },
        }));
    }, []);

    useEffect(() => {
        refreshModels();
    }, [refreshModels]);

    return {
        models,
        preferences,
        loading,
        error,
        getModelsForType,
        getSelectedModel,
        setModelPreference,
        refreshModels,
    };
};

export default useModels;
