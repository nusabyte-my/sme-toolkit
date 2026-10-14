import { createContext, useContext, useState, type ReactNode } from 'react';

type StrategyMode = 'guided' | 'experienced';
const StrategyModeContext = createContext<{ mode: StrategyMode; setMode: (mode: StrategyMode) => void } | null>(null);

export function StrategyModeProvider({ username, children }: { username: string; children: ReactNode }) {
  const key = `sme-strategy-mode:${username}`;
  const [mode, update] = useState<StrategyMode>(() => {
    try { return localStorage.getItem(key) === 'experienced' ? 'experienced' : 'guided'; }
    catch { return 'guided'; }
  });
  const setMode = (value: StrategyMode) => {
    update(value);
    try { localStorage.setItem(key, value); } catch { /* Preference still works for this session. */ }
  };
  return <StrategyModeContext.Provider value={{ mode, setMode }}>{children}</StrategyModeContext.Provider>;
}

export function useStrategyMode() {
  const value = useContext(StrategyModeContext);
  if (!value) throw new Error('StrategyModeProvider is required');
  return value;
}

export function StrategyModeToggle({ disabled = false }: { disabled?: boolean }) {
  const { mode, setMode } = useStrategyMode();
  return <fieldset className="flex flex-wrap gap-2" disabled={disabled}>
    <legend className="text-xs font-medium text-muted-foreground mb-2">Strategy editing style</legend>
    {(['guided', 'experienced'] as const).map(value => <label key={value} className={`relative inline-flex min-h-11 items-center rounded-lg border px-4 text-sm font-medium cursor-pointer ${mode === value ? 'bg-primary/10 border-primary text-primary' : 'border-border hover:bg-muted'}`}>
      <input type="radio" name="strategy-editing-mode" className="mr-2 accent-primary" checked={mode === value} onChange={() => setMode(value)}/>{value === 'guided' ? 'Guided' : 'Experienced'}
    </label>)}
    <p className="basis-full text-xs text-muted-foreground">{mode === 'guided' ? 'Questions and examples, one step at a time.' : 'All fields and tools on one screen.'} Switching keeps your current edits.</p>
  </fieldset>;
}
