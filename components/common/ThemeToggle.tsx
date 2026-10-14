/**
 * ThemeToggle Component
 * Toggle button for switching between light/dark/system themes
 */

import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface ThemeToggleProps {
    showLabel?: boolean;
    size?: 'sm' | 'md' | 'lg';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ showLabel = false, size = 'md' }) => {
    const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();

    const sizes = {
        sm: 'w-8 h-8',
        md: 'w-10 h-10',
        lg: 'w-12 h-12',
    };

    const iconSizes = {
        sm: 'w-4 h-4',
        md: 'w-5 h-5',
        lg: 'w-6 h-6',
    };

    return (
        <div className="flex items-center gap-2">
            {/* Simple Toggle */}
            <button
                onClick={toggleTheme}
                className={`${sizes[size]} rounded-xl flex items-center justify-center transition-all duration-300 
          ${resolvedTheme === 'dark'
                        ? 'bg-slate-800 text-yellow-400 hover:bg-slate-700'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                title={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
            >
                {resolvedTheme === 'dark' ? (
                    <Moon className={iconSizes[size]} />
                ) : (
                    <Sun className={iconSizes[size]} />
                )}
            </button>

            {showLabel && (
                <span className="text-sm font-medium text-slate-600 dark:text-slate-300 capitalize">
                    {resolvedTheme} Mode
                </span>
            )}
        </div>
    );
};

/**
 * ThemeSelector Component
 * Dropdown for selecting light/dark/system themes
 */
export const ThemeSelector: React.FC = () => {
    const { theme, setTheme } = useTheme();

    const options = [
        { value: 'light', label: 'Light', icon: Sun },
        { value: 'dark', label: 'Dark', icon: Moon },
        { value: 'system', label: 'System', icon: Monitor },
    ] as const;

    return (
        <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
            {options.map(option => (
                <button
                    key={option.value}
                    onClick={() => setTheme(option.value)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${theme === option.value
                            ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                            : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
                        }`}
                >
                    <option.icon className="w-4 h-4" />
                    <span>{option.label}</span>
                </button>
            ))}
        </div>
    );
};

export default ThemeToggle;
