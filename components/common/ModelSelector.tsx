/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Model selector & AI provider chips */
import React, { useState, useEffect } from 'react';
import { Sparkles, Zap, Image, Video, Bot, ChevronDown, Check } from 'lucide-react';

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
}

export interface ModelProvider {
    id: string;
    name: string;
    type: 'llm' | 'image' | 'video' | 'agent';
    models: Model[];
    logo: string;
    color: string;
    isDefault: boolean;
}

interface ModelSelectorProps {
    type: 'llm' | 'image' | 'video' | 'agent';
    onModelSelect: (providerId: string, modelId: string) => void;
    currentProvider?: string;
    currentModel?: string;
    compact?: boolean;
}

const PROVIDERS: Record<string, ModelProvider[]> = {
    llm: [
        {
            id: 'fiqstr-v2', name: 'Fiqstr V2', type: 'llm', logo: 'F2', color: 'from-primary to-accent', isDefault: true,
            models: [
                { id: 'fiqstr/deepseek-3.2', name: 'Deepseek 3.2', description: 'OpenAI-compatible reasoning model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard' },
                { id: 'fiqstr/glm-5', name: 'Glm 5', description: 'OpenAI-compatible chat model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard' },
                { id: 'fiqstr/minimax-m2.1', name: 'Minimax M2.1', description: 'OpenAI-compatible chat model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard' },
                { id: 'fiqstr/minimax-m2.5', name: 'Minimax M2.5', description: 'OpenAI-compatible chat model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard' },
                { id: 'fiqstr/qwen3-coder-next', name: 'Qwen3 Coder Next', description: 'OpenAI-compatible coding model', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'standard' },
            ]
        },
        {
            id: 'google', name: 'Google Gemini', type: 'llm', logo: 'GG', color: 'from-rainbow-blue to-primary', isDefault: false,
            models: [
                { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: 'Fast with excellent quality', capabilities: ['chat', 'code', 'reasoning'], costPerToken: 0.00001, performance: { speed: '500 tok/s', quality: 'excellent' }, available: true, category: 'standard' },
                { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'High-quality reasoning', capabilities: ['chat', 'code', 'multimodal'], costPerToken: 0.000035, performance: { speed: '50 tok/s', quality: 'excellent' }, available: true, category: 'premium' },
            ]
        },
        {
            id: 'groq', name: 'Groq Cloud', type: 'llm', logo: 'GQ', color: 'from-rainbow-amber to-primary', isDefault: false,
            models: [
                { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', description: 'Ultra-fast open source inference', capabilities: ['chat', 'code'], costPerToken: 0.00059, performance: { speed: '300 tok/s', quality: 'high' }, available: true, category: 'standard' },
            ]
        },
    ],
    image: [
        {
            id: 'google', name: 'Google Imagen', type: 'image', logo: 'GI', color: 'from-rainbow-pink to-primary', isDefault: true,
            models: [
                { id: 'imagen-3', name: 'Imagen 3', description: 'Highest quality images', capabilities: ['text-to-image'], costPerImage: 0.04, performance: { speed: '8s', quality: 'excellent' }, available: true, category: 'premium' },
            ]
        },
        {
            id: 'flux', name: 'FLUX Schnell', type: 'image', logo: 'FX', color: 'from-primary to-accent', isDefault: false,
            models: [
                { id: 'flux-1-schnell', name: 'FLUX Schnell', description: 'Fast generation model', capabilities: ['text-to-image'], costPerImage: 0.003, performance: { speed: '2s', quality: 'high' }, available: true, category: 'free' },
            ]
        },
    ],
    video: [
        {
            id: 'google', name: 'Google Veo', type: 'video', logo: 'GV', color: 'from-rainbow-cyan to-primary', isDefault: true,
            models: [
                { id: 'veo-3', name: 'Veo 3', description: 'Advanced video generation', capabilities: ['text-to-video'], costPerSecond: 0.05, performance: { speed: 'fast', quality: 'excellent' }, available: true, category: 'premium' },
            ]
        },
    ],
    agent: [
        {
            id: 'sme-toolkit', name: 'SME Swarm', type: 'agent', logo: 'SM', color: 'from-primary to-accent', isDefault: true,
            models: [
                { id: 'strategy-advisor', name: 'Strategy Advisor', description: 'Multi-agent analysis and business modeling', capabilities: ['analysis', 'planning'], costPerToken: 0.0015, performance: { speed: 'deep reasoning', quality: 'excellent' }, available: true, category: 'premium' },
            ]
        },
    ],
};

export const ModelSelector: React.FC<ModelSelectorProps> = ({ type, onModelSelect, currentProvider, currentModel, compact }) => {
    const [providers] = useState<ModelProvider[]>(PROVIDERS[type] || []);
    const [selectedProvider, setSelectedProvider] = useState(currentProvider || providers[0]?.id);
    const [selectedModel, setSelectedModel] = useState(currentModel || providers[0]?.models[0]?.id);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        if (selectedProvider && selectedModel) onModelSelect(selectedProvider, selectedModel);
    }, []);

    const currentProv = providers.find(p => p.id === selectedProvider);
    const currentMod = currentProv?.models.find(m => m.id === selectedModel);

    if (compact) {
        return (
            <div className="relative">
                <button 
                    onClick={() => setIsOpen(!isOpen)} 
                    className="flex items-center gap-2 px-3.5 py-2 rounded-xl border border-border bg-card hover:border-primary/40 text-foreground transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring active:scale-95"
                >
                    <span className="w-5 h-5 rounded-md bg-primary/10 text-primary flex items-center justify-center font-mono font-bold text-[10px]">
                        {currentProv?.logo || 'AI'}
                    </span>
                    <span className="text-sm font-semibold">{currentMod?.name || 'Select model'}</span>
                    <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </button>
                {isOpen && (
                    <div className="absolute top-full mt-2 w-72 bg-popover rounded-2xl shadow-xl border border-border z-50 max-h-80 overflow-auto animate-scale-in p-1">
                        {providers.map(p => (
                            <div key={p.id} className="mb-2 last:mb-0">
                                <div className="px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                                    <span className="w-4 h-4 rounded bg-primary/10 text-primary flex items-center justify-center text-[9px] font-bold">
                                        {p.logo}
                                    </span>
                                    {p.name}
                                </div>
                                {p.models.map(m => (
                                    <button 
                                        key={m.id} 
                                        onClick={() => { 
                                            setSelectedProvider(p.id); 
                                            setSelectedModel(m.id); 
                                            onModelSelect(p.id, m.id); 
                                            setIsOpen(false); 
                                        }}
                                        className={`w-full px-3 py-2 text-left hover:bg-muted rounded-xl flex items-center justify-between text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${selectedModel === m.id ? 'bg-primary/10 text-primary font-semibold' : 'text-foreground'}`}
                                    >
                                        <span className="truncate">{m.name}</span>
                                        {selectedModel === m.id && <Check className="w-4 h-4 text-primary flex-shrink-0 ml-2" />}
                                    </button>
                                ))}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="bg-card text-card-foreground rounded-2xl border border-border shadow-sm overflow-hidden">
            <div className="p-4 border-b border-border flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${currentProv?.color || 'from-primary to-accent'} flex items-center justify-center text-white shadow-brand`}>
                    {type === 'llm' ? <Sparkles className="w-5 h-5" /> : type === 'image' ? <Image className="w-5 h-5" /> : type === 'video' ? <Video className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>
                <div>
                    <h3 className="font-bold font-display text-foreground text-sm">Model Selection</h3>
                    <p className="text-xs text-muted-foreground">Choose your high-performance {type} model</p>
                </div>
            </div>
            
            {/* Provider Tabs */}
            <div className="flex gap-2 p-2.5 bg-muted/30 border-b border-border overflow-x-auto">
                {providers.map(p => (
                    <button 
                        key={p.id} 
                        onClick={() => setSelectedProvider(p.id)}
                        className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-mono font-semibold uppercase transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring active:scale-95 ${
                            selectedProvider === p.id 
                                ? 'bg-primary text-primary-foreground shadow-brand' 
                                : 'bg-card text-muted-foreground border border-border hover:border-primary/40 hover:text-foreground'
                        }`}
                    >
                        <span className={`w-4 h-4 rounded flex items-center justify-center text-[9px] font-bold ${selectedProvider === p.id ? 'bg-white/20 text-white' : 'bg-primary/10 text-primary'}`}>
                            {p.logo}
                        </span>
                        {p.name}
                    </button>
                ))}
            </div>

            {/* Models Grid */}
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {currentProv?.models.map(m => (
                    <div 
                        key={m.id} 
                        onClick={() => { setSelectedModel(m.id); onModelSelect(currentProv.id, m.id); }}
                        className={`p-4 rounded-xl border-2 cursor-pointer transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                            selectedModel === m.id 
                                ? 'border-primary bg-primary/10 shadow-xs' 
                                : 'border-border bg-card hover:border-primary/40 hover:-translate-y-0.5'
                        }`}
                    >
                        <div className="flex justify-between items-start mb-1.5">
                            <h4 className="font-bold font-display text-foreground text-sm">{m.name}</h4>
                            {selectedModel === m.id && <Check className="w-4 h-4 text-primary flex-shrink-0" />}
                        </div>
                        <p className="text-xs text-muted-foreground mb-3 line-clamp-2 leading-relaxed">{m.description}</p>
                        <div className="flex items-center gap-2 text-xs">
                            <span className={`px-2 py-0.5 rounded-md font-mono text-[10px] font-bold uppercase border ${
                                m.category === 'premium' ? 'bg-primary/15 text-primary border-primary/30' : 
                                m.category === 'free' ? 'bg-rainbow-emerald/15 text-rainbow-emerald border-rainbow-emerald/30' : 
                                'bg-muted text-muted-foreground border-border'
                            }`}>
                                {m.category}
                            </span>
                            <span className="flex items-center gap-1 font-mono text-muted-foreground text-[11px]">
                                <Zap className="w-3 h-3 text-primary" />
                                {m.performance.speed}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ModelSelector;
