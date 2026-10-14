import { Settings } from 'lucide-react';

export default function WorkspaceLoading({ label = 'workspace' }: { label?: string }) {
  return <div className="min-h-[360px] grid place-items-center" role="status" aria-live="polite" aria-busy="true">
    <div className="flex flex-col items-center gap-4 text-center py-12">
      <span className="grid place-items-center w-16 h-16 rounded-2xl bg-primary/10 text-primary"><Settings className="w-8 h-8 motion-safe:animate-spin" style={{ animationDuration: '1.6s' }} aria-hidden="true"/></span>
      <p className="font-medium text-sm">Loading {label}…</p>
      <p className="text-xs text-muted-foreground">Your workspace will appear here. You can choose another menu.</p>
    </div>
  </div>;
}
