/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Social media accounts & sync overview */
import React, { useEffect, useRef, useState } from 'react';
import {
  Share2, Plus, RefreshCw, TrendingUp, Users,
  CheckCircle, Settings
} from 'lucide-react';
import BrandIcon from '../../ui/BrandIcon';
import Card from '../../ui/Card';
import Button from '../../ui/Button';
import {
  SOCIAL_PLATFORMS,
  getConnectedAccounts,
  getTotalFollowers,
  getAverageEngagement,
  mockConnectPlatform,
  mockDisconnectPlatform,
  mockSyncAccount,
  type SocialAccount,
} from '../../../services/mock/socialMediaMockData';

interface SocialMediaSectionProps {
  onAdd?: () => void;
  onEdit?: (account: SocialAccount) => void;
}

const SocialMediaSection: React.FC<SocialMediaSectionProps> = ({ onEdit }) => {
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [pendingRemoval, setPendingRemoval] = useState<{ account: SocialAccount; index: number } | null>(null);
  const undoTimerRef = useRef<number | null>(null);

  // Clear the undo timer on unmount
  useEffect(() => () => {
    if (undoTimerRef.current) {
      window.clearTimeout(undoTimerRef.current);
    }
  }, []);

  // Load mock data
  useEffect(() => {
    const timer = setTimeout(() => {
      setAccounts(getConnectedAccounts());
      setLoading(false);
    }, 400);
    return () => clearTimeout(timer);
  }, []);

  const handleConnect = async (platformId: string) => {
    setConnecting(platformId);
    try {
      const newAccount = await mockConnectPlatform(platformId);
      setAccounts(prev => [...prev, newAccount]);
    } catch {
      // Connect failed
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = (accountId: string) => {
    const targetIndex = accounts.findIndex(acc => acc.id === accountId);
    if (targetIndex === -1) return;

    const removedAccount = accounts[targetIndex];

    if (undoTimerRef.current) {
      window.clearTimeout(undoTimerRef.current);
    }

    setAccounts(prev => prev.filter(acc => acc.id !== accountId));
    setPendingRemoval({ account: removedAccount, index: targetIndex });

    undoTimerRef.current = window.setTimeout(async () => {
      try {
        await mockDisconnectPlatform(accountId);
      } catch {
        // Disconnect failed
      } finally {
        setPendingRemoval(null);
        undoTimerRef.current = null;
      }
    }, 5000);
  };

  const handleUndoRemoval = () => {
    if (!pendingRemoval) return;

    if (undoTimerRef.current) {
      window.clearTimeout(undoTimerRef.current);
      undoTimerRef.current = null;
    }

    setAccounts(prev => {
      const next = [...prev];
      next.splice(pendingRemoval.index, 0, pendingRemoval.account);
      return next;
    });

    setPendingRemoval(null);
  };

  const handleSync = async (accountId: string) => {
    setSyncing(accountId);
    try {
      const updated = await mockSyncAccount(accountId);
      setAccounts(prev => prev.map(acc => acc.id === accountId ? updated : acc));
    } catch {
      // Sync failed
    } finally {
      setSyncing(null);
    }
  };

  const connectedPlatformIds = accounts.map(acc => acc.platform);
  const availablePlatforms = SOCIAL_PLATFORMS.filter(
    p => !connectedPlatformIds.includes(p.id)
  );

  if (loading) {
    return (
      <Card className="p-6 bg-card border-border rounded-2xl">
        <div className="flex items-center justify-center py-12">
          <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview - Rotate rainbow hues */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border border-border p-5 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-1">Connected Platforms</p>
              <p className="text-3xl font-bold font-display text-primary">{accounts.length}</p>
              <p className="text-xs text-muted-foreground mt-1">of {SOCIAL_PLATFORMS.length} supported</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shadow-xs">
              <Share2 className="w-6 h-6" />
            </div>
          </div>
        </Card>

        <Card className="bg-card border border-border p-5 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-1">Total Followers</p>
              <p className="text-3xl font-bold font-display text-rainbow-cyan">{getTotalFollowers().toLocaleString()}</p>
              <p className="text-xs text-muted-foreground mt-1">across all channels</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rainbow-cyan/10 border border-rainbow-cyan/20 flex items-center justify-center text-rainbow-cyan shadow-xs">
              <Users className="w-6 h-6" />
            </div>
          </div>
        </Card>

        <Card className="bg-card border border-border p-5 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-1">Avg. Engagement</p>
              <p className="text-3xl font-bold font-display text-rainbow-pink">{getAverageEngagement()}%</p>
              <p className="text-xs text-muted-foreground mt-1">audience interaction rate</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rainbow-pink/10 border border-rainbow-pink/20 flex items-center justify-center text-rainbow-pink shadow-xs">
              <TrendingUp className="w-6 h-6" />
            </div>
          </div>
        </Card>
      </div>

      {/* Undo banner — Nielsen #3 visible removal feedback */}
      {pendingRemoval && (
        <div role="status" aria-live="polite" className="flex items-center justify-between gap-4 rounded-xl border border-warning/30 bg-warning/10 px-4 py-3 text-foreground animate-fade-in">
          <p className="text-sm">
            <span className="font-semibold">{pendingRemoval.account.displayName}</span> disconnected. Reconnects automatically in 5 seconds unless you undo.
          </p>
          <button
            onClick={handleUndoRemoval}
            className="shrink-0 rounded-lg bg-warning text-white px-3 py-1.5 text-xs font-semibold hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-opacity"
          >
            Undo
          </button>
        </div>
      )}

      {/* Connected Accounts */}
      {accounts.length > 0 && (
        <Card padding="none" className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold font-display text-foreground flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-rainbow-emerald" />
                Connected Accounts
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => accounts.forEach(acc => handleSync(acc.id))}
                className="border-border hover:bg-muted hover:border-primary/40 rounded-xl focus-visible:ring-2 focus-visible:ring-ring whitespace-nowrap"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Sync All
              </Button>
            </div>
          </div>

          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {accounts.map((account) => {
              const platform = SOCIAL_PLATFORMS.find(p => p.id === account.platform);
              if (!platform) return null;

              return (
                <div
                  key={account.id}
                  className="border border-border rounded-xl p-4 bg-muted/20 hover:border-primary/40 hover:shadow-xs transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-card border border-border shadow-xs">
                        <BrandIcon platform={platform.id} className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-foreground text-sm">{account.displayName}</h4>
                          {account.isVerified && (
                            <CheckCircle className="w-3.5 h-3.5 text-primary" />
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground font-mono">{account.username.startsWith('@') ? account.username : `@${account.username}`}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => onEdit?.(account)}
                      aria-label={`Settings for ${account.displayName}`}
                      className="p-1.5 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-3 gap-2 mb-3 bg-card p-2 rounded-lg border border-border/60">
                    <div className="text-center">
                      <p className="text-[10px] font-mono text-muted-foreground uppercase">Followers</p>
                      <p className="text-sm font-bold font-mono text-foreground">
                        {account.metrics.followers.toLocaleString()}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-[10px] font-mono text-muted-foreground uppercase">Posts</p>
                      <p className="text-sm font-bold font-mono text-foreground">
                        {account.metrics.posts.toLocaleString()}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-[10px] font-mono text-muted-foreground uppercase">Engagement</p>
                      <p className="text-sm font-bold font-mono text-rainbow-emerald">
                        {account.metrics.engagement}%
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 rounded-lg text-xs"
                      onClick={() => handleSync(account.id)}
                      disabled={syncing === account.id}
                    >
                      <RefreshCw className={`w-3.5 h-3.5 mr-1 ${syncing === account.id ? 'animate-spin' : ''}`} />
                      {syncing === account.id ? 'Syncing...' : 'Sync'}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="rounded-lg text-xs border-border text-muted-foreground hover:text-destructive hover:border-destructive/40"
                      onClick={() => handleDisconnect(account.id)}
                    >
                      Disconnect
                    </Button>
                  </div>

                  {account.lastSynced && (
                    <p className="text-[10px] font-mono text-muted-foreground mt-2">
                      Last synced: {new Date(account.lastSynced).toLocaleString()}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Available Platforms */}
      {availablePlatforms.length > 0 && (
        <Card padding="none" className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6 border-b border-border">
            <h3 className="text-lg font-bold font-display text-foreground flex items-center gap-2">
              <Plus className="w-5 h-5 text-primary" />
              Available Platforms
            </h3>
            <p className="text-sm text-muted-foreground mt-0.5">
              Connect more platforms to expand your multi-channel sales reach
            </p>
          </div>

          <div className="p-6 grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            {availablePlatforms.map((platform) => (
              <button
                key={platform.id}
                onClick={() => handleConnect(platform.id)}
                disabled={connecting === platform.id}
                title={`Connect ${platform.displayName}`}
                className="group flex flex-col items-center gap-2 p-4 border-2 border-dashed border-border rounded-xl hover:border-primary/40 hover:bg-primary/5 hover:-translate-y-0.5 transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-card border border-border shadow-xs group-hover:border-primary/30 transition-colors">
                  {connecting === platform.id ? (
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-hidden="true"></div>
                  ) : (
                    <BrandIcon platform={platform.id} className="w-5 h-5" />
                  )}
                </div>
                <span className="w-full text-xs font-semibold text-foreground text-center truncate">
                  {platform.displayName}
                </span>
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default SocialMediaSection;
