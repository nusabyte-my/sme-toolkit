/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Social media connection editor */
import React, { useState, useEffect } from 'react';
import Card from '../../ui/Card';
import Button from '../../ui/Button';
import Input from '../../ui/Input';
import { useProfile } from '../../../contexts/ProfileContext';
import { useDialogEscape } from '../../common/useDialogEscape';
import { getPlatformColor } from '../../../services/profileService';
import { X, Check } from 'lucide-react';

interface SocialMediaEditorProps {
  isOpen: boolean;
  onClose: () => void;
  editingProfile?: Record<string, unknown> | null;
}

const SocialMediaEditor: React.FC<SocialMediaEditorProps> = ({ isOpen, onClose, editingProfile }) => {
  const { addSocialMediaProfile, updateSocialMediaProfile } = useProfile();
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useDialogEscape(isOpen, onClose);

  const [formData, setFormData] = useState({
    platform_name: '',
    platform_display_name: '',
    platform_icon: '',
    handle: '',
    profile_url: '',
    account_id: '',
    account_type: '',
    api_key: '',
    is_primary: false,
    auto_sync_enabled: false,
    sync_frequency: 'daily',
    metrics: {
      followers: 0,
      following: 0,
      posts: 0,
      engagement_rate: 0,
    },
  });

  const platforms = [
    { name: 'facebook', displayName: 'Facebook', tag: 'FB' },
    { name: 'instagram', displayName: 'Instagram', tag: 'IG' },
    { name: 'twitter', displayName: 'Twitter/X', tag: 'X' },
    { name: 'linkedin', displayName: 'LinkedIn', tag: 'IN' },
    { name: 'youtube', displayName: 'YouTube', tag: 'YT' },
    { name: 'tiktok', displayName: 'TikTok', tag: 'TT' },
    { name: 'pinterest', displayName: 'Pinterest', tag: 'PIN' },
    { name: 'snapchat', displayName: 'Snapchat', tag: 'SNAP' },
    { name: 'reddit', displayName: 'Reddit', tag: 'RD' },
    { name: 'whatsapp', displayName: 'WhatsApp', tag: 'WA' },
    { name: 'telegram', displayName: 'Telegram', tag: 'TG' },
    { name: 'discord', displayName: 'Discord', tag: 'DC' },
  ];

  const syncFrequencies = [
    { value: 'hourly', label: 'Every hour' },
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
  ];

  const accountTypes = [
    { value: 'personal', label: 'Personal' },
    { value: 'business', label: 'Business' },
    { value: 'creator', label: 'Creator' },
  ];

  // Initialize form when editing
  useEffect(() => {
    if (editingProfile) {
      const syncSettings = (typeof editingProfile.sync_settings === 'object' && editingProfile.sync_settings !== null)
        ? (editingProfile.sync_settings as Record<string, unknown>)
        : {};
      const metrics = (typeof editingProfile.metrics === 'object' && editingProfile.metrics !== null)
        ? (editingProfile.metrics as Record<string, number>)
        : {};

      setFormData({
        platform_name: String(editingProfile.platform_name || ''),
        platform_display_name: String(editingProfile.platform_display_name || ''),
        platform_icon: String(editingProfile.platform_icon || ''),
        handle: String(editingProfile.handle || ''),
        profile_url: String(editingProfile.profile_url || ''),
        account_id: String(editingProfile.account_id || ''),
        account_type: String(editingProfile.account_type || ''),
        api_key: String(syncSettings.api_key || ''),
        is_primary: Boolean(editingProfile.is_primary),
        auto_sync_enabled: Boolean(editingProfile.auto_sync_enabled),
        sync_frequency: String(editingProfile.sync_frequency || 'daily'),
        metrics: {
          followers: metrics.followers || 0,
          following: metrics.following || 0,
          posts: metrics.posts || 0,
          engagement_rate: metrics.engagement_rate || 0,
        },
      });
    } else {
      setFormData({
        platform_name: '',
        platform_display_name: '',
        platform_icon: '',
        handle: '',
        profile_url: '',
        account_id: '',
        account_type: '',
        api_key: '',
        is_primary: false,
        auto_sync_enabled: false,
        sync_frequency: 'daily',
        metrics: {
          followers: 0,
          following: 0,
          posts: 0,
          engagement_rate: 0,
        },
      });
    }
    setErrors({});
  }, [editingProfile, isOpen]);

  const handleInputChange = (field: string, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: '' }));

    if (field === 'platform_name') {
      const selected = platforms.find(p => p.name === value);
      if (selected) {
        setFormData(prev => ({
          ...prev,
          platform_name: String(value),
          platform_display_name: selected.displayName,
          platform_icon: selected.tag,
        }));
      }
    }
  };

  const handleMetricsChange = (field: string, value: number) => {
    setFormData(prev => ({
      ...prev,
      metrics: {
        ...prev.metrics,
        [field]: value || 0,
      },
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.platform_name) {
      newErrors.platform_name = 'Platform is required';
    }
    if (!formData.handle.trim()) {
      newErrors.handle = 'Handle/Username is required';
    }
    if (formData.profile_url && !isValidUrl(formData.profile_url)) {
      newErrors.profile_url = 'Please enter a valid URL';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidUrl = (url: string): boolean => {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSaving(true);
    try {
      const profilePayload = {
        platform_name: formData.platform_name,
        platform_display_name: formData.platform_display_name,
        platform_icon: formData.platform_icon,
        handle: formData.handle.replace(/^@/, ''),
        profile_url: formData.profile_url || undefined,
        account_id: formData.account_id || undefined,
        account_type: formData.account_type || undefined,
        is_primary: formData.is_primary,
        auto_sync_enabled: formData.auto_sync_enabled,
        sync_frequency: formData.sync_frequency,
        sync_settings: formData.api_key ? { api_key: formData.api_key } : undefined,
        metrics: formData.metrics,
      };

      if (editingProfile && typeof editingProfile.id === 'string') {
        await updateSocialMediaProfile(editingProfile.id, profilePayload);
      } else {
        await addSocialMediaProfile(profilePayload);
      }

      onClose();
    } catch (error) {
      if (error instanceof Error) {
        setErrors({ general: error.message });
      }
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  const selectedPlatform = platforms.find(p => p.name === formData.platform_name);
  const platformColor = selectedPlatform ? getPlatformColor(selectedPlatform.name) : 'bg-primary';

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <Card role="dialog" aria-modal="true" aria-labelledby="social-editor-title" className="w-full max-w-2xl max-h-[90vh] overflow-y-auto backdrop-blur-md bg-card/95 border border-border shadow-brand-lg rounded-2xl p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 border-b border-border pb-4">
          <div>
            <h2 id="social-editor-title" className="text-xl font-bold font-display text-foreground">
              {editingProfile ? 'Edit' : 'Add'} Social Media Profile
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {editingProfile ? 'Update your social media synchronization settings' : 'Connect a verified social channel to SME OS'}
            </p>
          </div>
          <Button size="sm" variant="ghost" onClick={onClose} aria-label="Close social media editor" className="p-2 hover:bg-muted text-muted-foreground hover:text-foreground rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Platform Preview */}
        {selectedPlatform && (
          <div className={`mb-6 p-4 rounded-xl ${platformColor} text-white shadow-sm flex items-center space-x-3`}>
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center font-mono font-bold text-sm">
              {selectedPlatform.tag}
            </div>
            <div>
              <p className="text-base font-bold font-display">{selectedPlatform.displayName}</p>
              {formData.handle && (
                <p className="text-xs opacity-90 font-mono">@{formData.handle.replace(/^@/, '')}</p>
              )}
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.general && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-3 text-destructive text-sm font-medium">
              {errors.general}
            </div>
          )}

          {/* Platform Selection */}
          <div>
            <label className="block text-xs font-mono font-semibold uppercase text-foreground mb-1.5">Platform *</label>
            <select
              className="w-full px-3.5 py-2.5 border border-border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary text-sm bg-muted/30 text-foreground transition-all"
              value={formData.platform_name}
              onChange={(e) => handleInputChange('platform_name', e.target.value)}
              disabled={Boolean(editingProfile)}
            >
              <option value="">Select a platform</option>
              {platforms.map((platform) => (
                <option key={platform.name} value={platform.name}>
                  [{platform.tag}] {platform.displayName}
                </option>
              ))}
            </select>
            {errors.platform_name && (
              <p className="mt-1 text-xs text-destructive font-mono">{errors.platform_name}</p>
            )}
          </div>

          {/* Handle */}
          <Input
            label="Handle / Username *"
            placeholder="@username"
            value={formData.handle}
            onChange={(e) => handleInputChange('handle', e.target.value)}
            error={errors.handle}
            leftElement={<span className="text-xs font-mono text-muted-foreground">@</span>}
          />

          {/* Profile URL */}
          <Input
            label="Profile URL"
            type="url"
            placeholder="https://..."
            value={formData.profile_url}
            onChange={(e) => handleInputChange('profile_url', e.target.value)}
            error={errors.profile_url}
          />

          {/* Account ID */}
          <Input
            label="Account ID"
            placeholder="Optional internal account ID"
            value={formData.account_id}
            onChange={(e) => handleInputChange('account_id', e.target.value)}
          />

          {/* Account Type */}
          <div>
            <label className="block text-xs font-mono font-semibold uppercase text-foreground mb-1.5">Account Type</label>
            <select
              className="w-full px-3.5 py-2.5 border border-border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary text-sm bg-muted/30 text-foreground transition-all"
              value={formData.account_type}
              onChange={(e) => handleInputChange('account_type', e.target.value)}
            >
              <option value="">Select account type</option>
              {accountTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sync Frequency */}
          <div>
            <label className="block text-xs font-mono font-semibold uppercase text-foreground mb-1.5">Sync Frequency</label>
            <select
              className="w-full px-3.5 py-2.5 border border-border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary text-sm bg-muted/30 text-foreground transition-all"
              value={formData.sync_frequency}
              onChange={(e) => handleInputChange('sync_frequency', e.target.value)}
            >
              {syncFrequencies.map((freq) => (
                <option key={freq.value} value={freq.value}>
                  {freq.label}
                </option>
              ))}
            </select>
          </div>

          {/* Metrics (Optional) */}
          <div className="border-t border-border pt-4">
            <p className="text-xs font-mono font-semibold uppercase text-foreground mb-3">Current Metrics (Optional)</p>
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Followers"
                type="number"
                value={formData.metrics.followers || ''}
                onChange={(e) => handleMetricsChange('followers', parseInt(e.target.value) || 0)}
              />
              <Input
                label="Following"
                type="number"
                value={formData.metrics.following || ''}
                onChange={(e) => handleMetricsChange('following', parseInt(e.target.value) || 0)}
              />
              <Input
                label="Posts"
                type="number"
                value={formData.metrics.posts || ''}
                onChange={(e) => handleMetricsChange('posts', parseInt(e.target.value) || 0)}
              />
              <Input
                label="Engagement Rate (%)"
                type="number"
                step="0.01"
                value={formData.metrics.engagement_rate || ''}
                onChange={(e) => handleMetricsChange('engagement_rate', parseFloat(e.target.value) || 0)}
              />
            </div>
          </div>

          {/* Checkboxes */}
          <div className="space-y-2 border-t border-border pt-4">
            <label className="flex items-center space-x-2 text-sm text-foreground cursor-pointer select-none">
              <input
                type="checkbox"
                checked={formData.is_primary}
                onChange={(e) => handleInputChange('is_primary', e.target.checked)}
                className="rounded border-border text-primary focus:ring-2 focus:ring-ring"
              />
              <span>Set as primary account for this platform</span>
            </label>
            <label className="flex items-center space-x-2 text-sm text-foreground cursor-pointer select-none">
              <input
                type="checkbox"
                checked={formData.auto_sync_enabled}
                onChange={(e) => handleInputChange('auto_sync_enabled', e.target.checked)}
                className="rounded border-border text-primary focus:ring-2 focus:ring-ring"
              />
              <span>Enable automatic synchronization</span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-border">
            <Button size="md" variant="outline" onClick={onClose} className="rounded-xl border-border hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring">
              Cancel
            </Button>
            <Button size="md" loading={saving} className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-brand rounded-xl font-semibold focus-visible:ring-2 focus-visible:ring-ring active:scale-95">
              <Check className="w-4 h-4 mr-1.5" />
              {editingProfile ? 'Save Changes' : 'Connect Account'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default SocialMediaEditor;
