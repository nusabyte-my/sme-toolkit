/**
 * AI Background Generator Component
 * Generates AI-powered backgrounds for the visual editor
 */

import React, { useState } from 'react';
import { Sparkles, Wand2, Palette, Image, Loader2, RefreshCw, Download, Check } from 'lucide-react';

interface Background {
    id: string;
    url: string;
    prompt: string;
    style: string;
}

interface AIBackgroundGeneratorProps {
    onSelectBackground: (backgroundUrl: string) => void;
    onClose?: () => void;
}

const STYLE_PRESETS = [
    { id: 'minimal', name: 'Minimal', description: 'Clean, simple backgrounds', examples: ['soft gradients', 'subtle textures', 'geometric'] },
    { id: 'professional', name: 'Professional', description: 'Corporate and business-ready', examples: ['office', 'abstract corporate', 'tech'] },
    { id: 'creative', name: 'Creative', description: 'Bold and artistic', examples: ['vibrant colors', 'artistic patterns', 'dynamic'] },
    { id: 'nature', name: 'Nature', description: 'Natural landscapes', examples: ['forests', 'mountains', 'oceanic'] },
    { id: 'abstract', name: 'Abstract', description: 'Modern abstract art', examples: ['geometric', 'fluid', 'digital art'] },
    { id: 'gradient', name: 'Gradient', description: 'Smooth color transitions', examples: ['mesh gradients', 'duotone', 'aurora'] },
];

const QUICK_PROMPTS = [
    'Soft pastel gradient with geometric shapes',
    'Professional dark blue corporate background',
    'Vibrant sunset gradient with mesh pattern',
    'Minimalist white texture with subtle shadows',
    'Abstract purple and blue fluid art',
    'Nature-inspired green forest blur',
    'Tech-style grid with neon accents',
    'Elegant marble texture in white and gold',
];

// Mock generated backgrounds
const MOCK_BACKGROUNDS: Background[] = [
    { id: 'bg1', url: '', prompt: 'Soft gradient', style: 'gradient' },
    { id: 'bg2', url: '', prompt: 'Professional', style: 'professional' },
    { id: 'bg3', url: '', prompt: 'Abstract art', style: 'abstract' },
    { id: 'bg4', url: '', prompt: 'Nature blur', style: 'nature' },
];

export const AIBackgroundGenerator: React.FC<AIBackgroundGeneratorProps> = ({ onSelectBackground, onClose }) => {
    const [prompt, setPrompt] = useState('');
    const [selectedStyle, setSelectedStyle] = useState('minimal');
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedBackgrounds, setGeneratedBackgrounds] = useState<Background[]>(MOCK_BACKGROUNDS);
    const [selectedBg, setSelectedBg] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        setIsGenerating(true);

        // Simulate AI generation delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        // In production, this would call the AI image generation API
        const newBackground: Background = {
            id: `bg-${Date.now()}`,
            url: '',
            prompt: prompt,
            style: selectedStyle,
        };

        setGeneratedBackgrounds(prev => [newBackground, ...prev].slice(0, 8));
        setIsGenerating(false);
    };

    const handleSelectQuickPrompt = (quickPrompt: string) => {
        setPrompt(quickPrompt);
    };

    const getGradientForStyle = (style: string, index: number) => {
        const gradients: Record<string, string[]> = {
            minimal: ['from-slate-100 to-slate-200', 'from-gray-100 to-gray-200'],
            professional: ['from-slate-700 to-slate-900', 'from-blue-900 to-slate-800'],
            creative: ['from-pink-500 via-purple-500 to-indigo-500', 'from-orange-400 via-red-500 to-pink-500'],
            nature: ['from-green-400 to-emerald-600', 'from-cyan-400 to-blue-600'],
            abstract: ['from-violet-500 via-purple-500 to-fuchsia-500', 'from-indigo-500 via-purple-500 to-pink-500'],
            gradient: ['from-rose-400 via-fuchsia-500 to-indigo-500', 'from-amber-400 via-orange-500 to-red-500'],
        };
        const styleGradients = gradients[style] || gradients.minimal;
        return styleGradients[index % styleGradients.length];
    };

    return (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden max-w-2xl w-full">
            {/* Header */}
            <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-violet-50 to-purple-50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                            <Wand2 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-slate-800">AI Background Generator</h3>
                            <p className="text-sm text-slate-500">Generate custom backgrounds with AI</p>
                        </div>
                    </div>
                    {onClose && (
                        <button onClick={onClose} className="text-slate-400 hover:text-slate-600">×</button>
                    )}
                </div>
            </div>

            <div className="p-4 space-y-4">
                {/* Style Presets */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Style</label>
                    <div className="grid grid-cols-3 gap-2">
                        {STYLE_PRESETS.map(style => (
                            <button
                                key={style.id}
                                onClick={() => setSelectedStyle(style.id)}
                                className={`p-3 rounded-xl border-2 text-left transition-all ${selectedStyle === style.id
                                        ? 'border-violet-500 bg-violet-50'
                                        : 'border-slate-200 hover:border-violet-300'
                                    }`}
                            >
                                <p className="font-medium text-sm text-slate-800">{style.name}</p>
                                <p className="text-xs text-slate-500">{style.description}</p>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Prompt Input */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Describe your background</label>
                    <div className="relative">
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="E.g., Soft gradient with subtle geometric patterns..."
                            className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-violet-300 focus:ring-2 focus:ring-violet-100 resize-none h-20"
                        />
                        <button
                            onClick={handleGenerate}
                            disabled={isGenerating || !prompt.trim()}
                            className="absolute bottom-3 right-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 disabled:opacity-50 hover:shadow-lg transition-all"
                        >
                            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                            {isGenerating ? 'Generating...' : 'Generate'}
                        </button>
                    </div>
                </div>

                {/* Quick Prompts */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Quick prompts</label>
                    <div className="flex flex-wrap gap-2">
                        {QUICK_PROMPTS.slice(0, 4).map((qp, i) => (
                            <button
                                key={i}
                                onClick={() => handleSelectQuickPrompt(qp)}
                                className="px-3 py-1.5 bg-slate-100 hover:bg-violet-100 text-slate-600 hover:text-violet-700 rounded-full text-xs transition-colors"
                            >
                                {qp.slice(0, 30)}...
                            </button>
                        ))}
                    </div>
                </div>

                {/* Generated Backgrounds */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Generated backgrounds</label>
                    <div className="grid grid-cols-4 gap-2">
                        {generatedBackgrounds.map((bg, index) => (
                            <button
                                key={bg.id}
                                onClick={() => { setSelectedBg(bg.id); onSelectBackground(bg.url || `gradient-${bg.style}`); }}
                                className={`relative aspect-video rounded-lg overflow-hidden border-2 transition-all ${selectedBg === bg.id ? 'border-violet-500 ring-2 ring-violet-200' : 'border-slate-200 hover:border-violet-300'
                                    }`}
                            >
                                <div className={`absolute inset-0 bg-gradient-to-br ${getGradientForStyle(bg.style, index)}`} />
                                {selectedBg === bg.id && (
                                    <div className="absolute inset-0 bg-violet-500/20 flex items-center justify-center">
                                        <Check className="w-6 h-6 text-white" />
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
                {onClose && (
                    <button onClick={onClose} className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
                        Cancel
                    </button>
                )}
                <button
                    onClick={() => selectedBg && onSelectBackground(selectedBg)}
                    disabled={!selectedBg}
                    className="px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-lg font-medium disabled:opacity-50 hover:shadow-lg transition-all"
                >
                    Apply Background
                </button>
            </div>
        </div>
    );
};

export default AIBackgroundGenerator;
