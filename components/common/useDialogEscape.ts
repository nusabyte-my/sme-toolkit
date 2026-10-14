/**
 * Dialog a11y primitive shared by all modals (4 call sites need lockstep behavior).
 * Adds Escape-to-close while open. Focus trap and focus return stay with each
 * modal's own markup — this hook only standardizes keyboard escape.
 */
import { useEffect } from 'react';

export function useDialogEscape(isOpen: boolean, onClose: () => void): void {
  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);
}
