/**
 * TemplateLibrary Component - Canva-like template gallery
 * Provides categorized templates for visual generation
 */

import React, { useState } from 'react';
import { Search, Grid, LayoutGrid, Sparkles, Image, Share2, FileText, Presentation, Mail, Tag } from 'lucide-react';

export interface Template {
    id: string;
    name: string;
    category: string;
    subcategory: string;
    thumbnail: string;
    dimensions: { width: number; height: number };
    tags: string[];
    isPremium: boolean;
    uses: number;
}

interface TemplateLibraryProps {
    onSelectTemplate: (template: Template) => void;
    compact?: boolean;
}

const TEMPLATE_CATEGORIES = [
    { id: 'social', name: 'Social Media', icon: Share2, color: 'from-pink-500 to-rose-500' },
    { id: 'marketing', name: 'Marketing', icon: Tag, color: 'from-violet-500 to-purple-500' },
    { id: 'presentation', name: 'Presentations', icon: Presentation, color: 'from-blue-500 to-cyan-500' },
    { id: 'document', name: 'Documents', icon: FileText, color: 'from-emerald-500 to-teal-500' },
    { id: 'email', name: 'Email', icon: Mail, color: 'from-amber-500 to-orange-500' },
];

const MOCK_TEMPLATES: Template[] = [
    // Social Media
    { id: 't1', name: 'Instagram Post - Modern', category: 'social', subcategory: 'instagram', thumbnail: '', dimensions: { width: 1080, height: 1080 }, tags: ['instagram', 'post', 'modern'], isPremium: false, uses: 12500 },
    { id: 't2', name: 'Instagram Story - Gradient', category: 'social', subcategory: 'instagram', thumbnail: '', dimensions: { width: 1080, height: 1920 }, tags: ['instagram', 'story', 'gradient'], isPremium: false, uses: 8700 },
    { id: 't3', name: 'Facebook Cover - Business', category: 'social', subcategory: 'facebook', thumbnail: '', dimensions: { width: 820, height: 312 }, tags: ['facebook', 'cover', 'business'], isPremium: true, uses: 5400 },
    { id: 't4', name: 'LinkedIn Banner - Professional', category: 'social', subcategory: 'linkedin', thumbnail: '', dimensions: { width: 1584, height: 396 }, tags: ['linkedin', 'banner', 'professional'], isPremium: false, uses: 9200 },
    { id: 't5', name: 'Twitter/X Header', category: 'social', subcategory: 'twitter', thumbnail: '', dimensions: { width: 1500, height: 500 }, tags: ['twitter', 'header'], isPremium: false, uses: 6100 },
    { id: 't6', name: 'YouTube Thumbnail', category: 'social', subcategory: 'youtube', thumbnail: '', dimensions: { width: 1280, height: 720 }, tags: ['youtube', 'thumbnail'], isPremium: true, uses: 15300 },
    // Marketing
    { id: 't7', name: 'Product Launch Banner', category: 'marketing', subcategory: 'banners', thumbnail: '', dimensions: { width: 1200, height: 628 }, tags: ['product', 'launch', 'banner'], isPremium: true, uses: 4200 },
    { id: 't8', name: 'Sale Announcement', category: 'marketing', subcategory: 'promotions', thumbnail: '', dimensions: { width: 1080, height: 1080 }, tags: ['sale', 'discount', 'promo'], isPremium: false, uses: 7800 },
    { id: 't9', name: 'Event Flyer - Modern', category: 'marketing', subcategory: 'flyers', thumbnail: '', dimensions: { width: 1080, height: 1350 }, tags: ['event', 'flyer', 'modern'], isPremium: false, uses: 3600 },
    { id: 't10', name: 'Infographic - Business', category: 'marketing', subcategory: 'infographics', thumbnail: '', dimensions: { width: 800, height: 2000 }, tags: ['infographic', 'data', 'business'], isPremium: true, uses: 2900 },
    // Presentations
    { id: 't11', name: 'Pitch Deck - Startup', category: 'presentation', subcategory: 'pitch', thumbnail: '', dimensions: { width: 1920, height: 1080 }, tags: ['pitch', 'startup', 'investor'], isPremium: true, uses: 11200 },
    { id: 't12', name: 'Business Report', category: 'presentation', subcategory: 'reports', thumbnail: '', dimensions: { width: 1920, height: 1080 }, tags: ['report', 'business', 'quarterly'], isPremium: false, uses: 5800 },
    // Documents
    { id: 't13', name: 'Invoice - Professional', category: 'document', subcategory: 'invoices', thumbnail: '', dimensions: { width: 595, height: 842 }, tags: ['invoice', 'billing', 'professional'], isPremium: false, uses: 8400 },
    { id: 't14', name: 'Proposal - Modern', category: 'document', subcategory: 'proposals', thumbnail: '', dimensions: { width: 595, height: 842 }, tags: ['proposal', 'business', 'modern'], isPremium: true, uses: 4100 },
    // Email
    { id: 't15', name: 'Newsletter - Clean', category: 'email', subcategory: 'newsletters', thumbnail: '', dimensions: { width: 600, height: 800 }, tags: ['newsletter', 'email', 'clean'], isPremium: false, uses: 6700 },
    { id: 't16', name: 'Welcome Email', category: 'email', subcategory: 'transactional', thumbnail: '', dimensions: { width: 600, height: 600 }, tags: ['welcome', 'onboarding', 'email'], isPremium: false, uses: 9100 },
];

const generateGradient = (index: number) => {
    const gradients = [
        'from-pink-400 via-purple-400 to-indigo-400',
        'from-cyan-400 via-blue-400 to-purple-400',
        'from-orange-400 via-red-400 to-pink-400',
        'from-green-400 via-teal-400 to-cyan-400',
        'from-yellow-400 via-orange-400 to-red-400',
        'from-indigo-400 via-purple-400 to-pink-400',
    ];
    return gradients[index % gradients.length];
};

export const TemplateLibrary: React.FC<TemplateLibraryProps> = ({ onSelectTemplate, compact }) => {
    const [selectedCategory, setSelectedCategory] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

    const filteredTemplates = MOCK_TEMPLATES.filter(t => {
        const matchesCategory = selectedCategory === 'all' || t.category === selectedCategory;
        const matchesSearch = searchQuery === '' ||
            t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            t.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesCategory && matchesSearch;
    });

    return (
        <div className={`bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden ${compact ? 'max-h-96' : ''}`}>
            {/* Header */}
            <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                            <LayoutGrid className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-slate-800">Template Library</h3>
                            <p className="text-sm text-slate-500">{filteredTemplates.length} templates available</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button onClick={() => setViewMode('grid')} className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-indigo-100 text-indigo-600' : 'text-slate-400 hover:bg-slate-100'}`}>
                            <Grid className="w-4 h-4" />
                        </button>
                        <button onClick={() => setViewMode('list')} className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'text-slate-400 hover:bg-slate-100'}`}>
                            <LayoutGrid className="w-4 h-4" />
                        </button>
                    </div>
                </div>
                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search templates..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 text-sm transition-all"
                    />
                </div>
            </div>

            {/* Category Tabs */}
            <div className="flex gap-1 p-2 bg-slate-50 border-b border-slate-100 overflow-x-auto">
                <button
                    onClick={() => setSelectedCategory('all')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${selectedCategory === 'all' ? 'bg-indigo-600 text-white shadow' : 'bg-white text-slate-600 hover:bg-slate-100 border'
                        }`}
                >
                    All Templates
                </button>
                {TEMPLATE_CATEGORIES.map(cat => (
                    <button
                        key={cat.id}
                        onClick={() => setSelectedCategory(cat.id)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${selectedCategory === cat.id ? `bg-gradient-to-r ${cat.color} text-white shadow` : 'bg-white text-slate-600 hover:bg-slate-100 border'
                            }`}
                    >
                        <cat.icon className="w-4 h-4" />
                        {cat.name}
                    </button>
                ))}
            </div>

            {/* Templates Grid */}
            <div className={`p-4 overflow-y-auto ${compact ? 'max-h-64' : 'max-h-[500px]'}`}>
                <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4' : 'grid-cols-1'}`}>
                    {filteredTemplates.map((template, index) => (
                        <div
                            key={template.id}
                            onClick={() => onSelectTemplate(template)}
                            className="group relative bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg hover:border-indigo-300 transition-all cursor-pointer"
                        >
                            {/* Thumbnail */}
                            <div className={`relative bg-gradient-to-br ${generateGradient(index)} aspect-video flex items-center justify-center`}>
                                <Image className="w-8 h-8 text-white/50" />
                                {template.isPremium && (
                                    <div className="absolute top-2 right-2 bg-gradient-to-r from-amber-400 to-yellow-500 text-amber-900 text-xs font-semibold px-2 py-0.5 rounded-full flex items-center gap-1">
                                        <Sparkles className="w-3 h-3" /> Premium
                                    </div>
                                )}
                                {/* Hover Overlay */}
                                <div className="absolute inset-0 bg-indigo-600/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                    <span className="text-white font-medium text-sm">Use Template</span>
                                </div>
                            </div>
                            {/* Info */}
                            <div className="p-3">
                                <h4 className="font-medium text-slate-800 text-sm truncate">{template.name}</h4>
                                <div className="flex items-center justify-between mt-1">
                                    <span className="text-xs text-slate-500">{template.dimensions.width}×{template.dimensions.height}</span>
                                    <span className="text-xs text-slate-400">{(template.uses / 1000).toFixed(1)}k uses</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                {filteredTemplates.length === 0 && (
                    <div className="text-center py-12">
                        <Image className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                        <p className="text-slate-500">No templates found</p>
                        <p className="text-sm text-slate-400">Try adjusting your search or category</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TemplateLibrary;
