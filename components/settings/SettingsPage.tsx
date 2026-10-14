/**
 * Settings Page Component
 * User preferences and account settings with dark mode toggle
 */

import React, { useState } from 'react';
import { Settings, User, Bell, Shield, CreditCard, Palette, Globe, Key, LogOut, ChevronRight, Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface SettingsPageProps {
    user?: { name: string; email: string };
    onLogout?: () => void;
}

type SettingsTab = 'account' | 'appearance' | 'notifications' | 'billing' | 'security';

export const SettingsPage: React.FC<SettingsPageProps> = ({ user, onLogout }) => {
    const [activeTab, setActiveTab] = useState<SettingsTab>('appearance');
    const { theme, setTheme, resolvedTheme } = useTheme();

    const tabs = [
        { id: 'account' as const, label: 'Account', icon: User },
        { id: 'appearance' as const, label: 'Appearance', icon: Palette },
        { id: 'notifications' as const, label: 'Notifications', icon: Bell },
        { id: 'billing' as const, label: 'Billing', icon: CreditCard },
        { id: 'security' as const, label: 'Security', icon: Shield },
    ];

    const renderContent = () => {
        switch (activeTab) {
            case 'appearance':
                return (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-1">Theme</h3>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Customize how SME Toolkit looks on your device</p>
                            <div className="grid grid-cols-3 gap-4">
                                {[
                                    { value: 'light', label: 'Light', icon: Sun, preview: 'bg-white border-slate-200' },
                                    { value: 'dark', label: 'Dark', icon: Moon, preview: 'bg-slate-900 border-slate-700' },
                                    { value: 'system', label: 'System', icon: Monitor, preview: 'bg-gradient-to-r from-white to-slate-900' },
                                ].map(option => (
                                    <button
                                        key={option.value}
                                        onClick={() => setTheme(option.value as any)}
                                        className={`p-4 rounded-xl border-2 transition-all ${theme === option.value
                                                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                                                : 'border-slate-200 dark:border-slate-700 hover:border-indigo-300'
                                            }`}
                                    >
                                        <div className={`w-full h-20 rounded-lg mb-3 ${option.preview} border`} />
                                        <div className="flex items-center justify-center gap-2">
                                            <option.icon className={`w-4 h-4 ${theme === option.value ? 'text-indigo-600' : 'text-slate-400'}`} />
                                            <span className={`font-medium ${theme === option.value ? 'text-indigo-600' : 'text-slate-700 dark:text-slate-300'}`}>
                                                {option.label}
                                            </span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
                            <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-1">Language</h3>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Choose your preferred language</p>
                            <select className="w-full max-w-xs px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100">
                                <option value="en">English</option>
                                <option value="ms">Bahasa Malaysia</option>
                                <option value="zh">中文</option>
                            </select>
                        </div>

                        <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
                            <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-1">Density</h3>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Adjust the UI density</p>
                            <div className="flex gap-3">
                                {['Compact', 'Comfortable', 'Spacious'].map(density => (
                                    <button
                                        key={density}
                                        className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-indigo-300 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
                                    >
                                        {density}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                );

            case 'account':
                return (
                    <div className="space-y-6">
                        <div className="flex items-center gap-6 p-6 bg-slate-50 dark:bg-slate-800 rounded-xl">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-2xl font-bold">
                                {user?.name?.charAt(0) || 'U'}
                            </div>
                            <div>
                                <h3 className="text-xl font-semibold text-slate-800 dark:text-slate-100">{user?.name || 'User'}</h3>
                                <p className="text-slate-500 dark:text-slate-400">{user?.email || 'user@example.com'}</p>
                                <button className="mt-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium">Change avatar</button>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Full Name</label>
                                <input type="text" defaultValue={user?.name} className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Email</label>
                                <input type="email" defaultValue={user?.email} className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100" />
                            </div>
                        </div>

                        <button className="px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-600 text-white rounded-xl font-medium hover:shadow-lg transition-all">
                            Save Changes
                        </button>
                    </div>
                );

            default:
                return (
                    <div className="text-center py-12">
                        <p className="text-slate-500 dark:text-slate-400">This section is under development</p>
                    </div>
                );
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
            <div className="max-w-5xl mx-auto p-6">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center">
                            <Settings className="w-5 h-5 text-white" />
                        </div>
                        Settings
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">Manage your account and preferences</p>
                </div>

                <div className="flex gap-8">
                    {/* Sidebar */}
                    <div className="w-64 flex-shrink-0">
                        <nav className="space-y-1">
                            {tabs.map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all ${activeTab === tab.id
                                            ? 'bg-white dark:bg-slate-800 shadow text-indigo-600 dark:text-indigo-400'
                                            : 'text-slate-600 dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50'
                                        }`}
                                >
                                    <tab.icon className={`w-5 h-5 ${activeTab === tab.id ? 'text-indigo-500' : ''}`} />
                                    <span className="font-medium">{tab.label}</span>
                                    <ChevronRight className={`w-4 h-4 ml-auto ${activeTab === tab.id ? 'text-indigo-400' : 'text-slate-300 dark:text-slate-600'}`} />
                                </button>
                            ))}
                        </nav>

                        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
                            <button
                                onClick={onLogout}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                            >
                                <LogOut className="w-5 h-5" />
                                <span className="font-medium">Sign Out</span>
                            </button>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
                        {renderContent()}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
