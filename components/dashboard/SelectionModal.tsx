/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Selection modal & Nielsen cancel patterns */
import React, { useState } from 'react';
import { X, Check } from 'lucide-react';
import { useDialogEscape } from '../common/useDialogEscape';

interface SelectionModalProps<T> {
  title: string;
  items: T[];
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (selectedItems: T[]) => void;
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function SelectionModal<T>({ 
  title, 
  items, 
  isOpen, 
  onClose, 
  onConfirm, 
  renderItem, 
  keyExtractor 
}: SelectionModalProps<T>) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  useDialogEscape(isOpen, onClose);

  if (!isOpen) return null;

  const toggleSelection = (id: string) => {
    const newSelection = new Set(selectedIds);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    setSelectedIds(newSelection);
  };

  const handleConfirm = () => {
    const selectedItems = items.filter(item => selectedIds.has(keyExtractor(item)));
    onConfirm(selectedItems);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div 
        role="dialog" 
        aria-modal="true" 
        aria-labelledby="selection-modal-title" 
        className="backdrop-blur-md bg-card/95 rounded-2xl shadow-brand-lg border border-border w-full max-w-2xl max-h-[80vh] flex flex-col animate-in zoom-in-95 duration-200 overflow-hidden"
      >
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h3 id="selection-modal-title" className="text-xl font-bold font-display text-foreground">{title}</h3>
          <button 
            onClick={onClose} 
            aria-label="Close selection dialog" 
            className="p-2 hover:bg-muted text-muted-foreground hover:text-foreground rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {items.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">No items generated.</div>
          ) : (
            items.map(item => {
              const id = keyExtractor(item);
              const isSelected = selectedIds.has(id);
              return (
                <div
                  key={id}
                  role="checkbox"
                  aria-checked={isSelected}
                  tabIndex={0}
                  onClick={() => toggleSelection(id)}
                  onKeyDown={(e) => {
                    if (e.key === ' ' || e.key === 'Enter') {
                      e.preventDefault();
                      toggleSelection(id);
                    }
                  }}
                  className={`flex items-start gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                    isSelected
                      ? 'border-primary bg-primary/10 shadow-xs'
                      : 'border-border hover:border-primary/40 hover:bg-muted/40'
                  }`}
                >
                  <div className={`mt-0.5 w-5 h-5 rounded-md border flex items-center justify-center flex-shrink-0 transition-colors ${
                    isSelected ? 'bg-primary border-primary text-white' : 'border-border bg-card'
                  }`}>
                    {isSelected && <Check className="w-3.5 h-3.5" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    {renderItem(item)}
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="p-4 px-6 border-t border-border flex items-center justify-between bg-muted/30">
          <span className="text-xs font-mono text-muted-foreground">
            {selectedIds.size} of {items.length} selected
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-muted-foreground hover:text-foreground hover:bg-muted font-medium text-sm rounded-xl transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={selectedIds.size === 0}
              className="px-5 py-2 bg-gradient-cta text-white font-semibold text-sm rounded-xl hover:opacity-95 shadow-brand disabled:opacity-40 disabled:cursor-not-allowed transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring active:scale-95"
            >
              Confirm Selection ({selectedIds.size})
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SelectionModal;
