/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Profile editor modal */
import React, { useState, useEffect } from 'react';
import Card from '../../ui/Card';
import Button from '../../ui/Button';
import Input from '../../ui/Input';
import Badge from '../../ui/Badge';
import { useProfile } from '../../../contexts/ProfileContext';
import { useDialogEscape } from '../../common/useDialogEscape';
import { X, Check, AlertTriangle } from 'lucide-react';
import type { UserProfileUpdate, BusinessProfileUpdate } from '../../../types/profiles';

interface ProfileEditorProps {
  isOpen: boolean;
  onClose: () => void;
  profileType: 'user' | 'business';
}

const ProfileEditor: React.FC<ProfileEditorProps> = ({ isOpen, onClose, profileType }) => {
  const { userProfile, businessProfile, updateUserProfileData, updateBusinessProfileData } = useProfile();
  const [activeTab, setActiveTab] = useState('basic');
  const [saving, setSaving] = useState(false);
  const [autoSave, setAutoSave] = useState(true);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  useDialogEscape(isOpen, onClose);

  // User Profile Form State
  const [userFormData, setUserFormData] = useState<UserProfileUpdate>({});
  const [userErrors, setUserErrors] = useState<Record<string, string>>({});

  // Business Profile Form State
  const [businessFormData, setBusinessFormData] = useState<BusinessProfileUpdate>({});
  const [businessErrors, setBusinessErrors] = useState<Record<string, string>>({});

  // Initialize form data when profile loads
  useEffect(() => {
    if (profileType === 'user' && userProfile) {
      setUserFormData({
        first_name: userProfile.first_name,
        last_name: userProfile.last_name,
        email: userProfile.email,
        phone: userProfile.phone,
        job_title: userProfile.job_title,
        company_role: userProfile.company_role,
        years_of_experience: userProfile.years_of_experience,
        education_level: userProfile.education_level,
        field_of_study: userProfile.field_of_study,
        interests: userProfile.interests,
        skills: userProfile.skills,
        learning_goals: userProfile.learning_goals,
        business_challenges: userProfile.business_challenges,
      });
    } else if (profileType === 'business' && businessProfile) {
      setBusinessFormData({
        company_name: businessProfile.company_name,
        industry: businessProfile.industry,
        business_stage: businessProfile.business_stage,
        business_type: businessProfile.business_type,
        legal_structure: businessProfile.legal_structure,
        registration_number: businessProfile.registration_number,
        tax_id: businessProfile.tax_id,
        website_url: businessProfile.website_url,
        business_description: businessProfile.business_description,
        mission_statement: businessProfile.mission_statement,
        vision_statement: businessProfile.vision_statement,
        team_size: businessProfile.team_size,
        annual_revenue: businessProfile.annual_revenue,
        revenue_currency: businessProfile.revenue_currency,
        profit_margin: businessProfile.profit_margin,
        funding_stage: businessProfile.funding_stage,
        funding_amount: businessProfile.funding_amount,
        customer_count: businessProfile.customer_count,
        target_market: businessProfile.target_market,
        competitive_advantages: businessProfile.competitive_advantages,
        tech_stack: businessProfile.tech_stack,
        software_tools: businessProfile.software_tools,
        short_term_goals: businessProfile.short_term_goals,
        long_term_goals: businessProfile.long_term_goals,
        current_challenges: businessProfile.current_challenges,
        growth_opportunities: businessProfile.growth_opportunities,
      });
    }
  }, [profileType, userProfile, businessProfile, isOpen]);

  // Auto-save effect
  useEffect(() => {
    if (!autoSave) return;

    const timer = setTimeout(async () => {
      if (profileType === 'user' && Object.keys(userFormData).length > 0) {
        await handleSaveUser();
      } else if (profileType === 'business' && Object.keys(businessFormData).length > 0) {
        await handleSaveBusiness();
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [userFormData, businessFormData, autoSave, profileType]);

  const handleSaveUser = async () => {
    setSaving(true);
    setSaveStatus('saving');
    try {
      await updateUserProfileData(userFormData);
      setSaveStatus('saved');
      setUserErrors({});
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (error) {
      setSaveStatus('error');
      if (error instanceof Error) {
        const errors: Record<string, string> = {};
        errors.general = error.message;
        setUserErrors(errors);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleSaveBusiness = async () => {
    setSaving(true);
    setSaveStatus('saving');
    try {
      await updateBusinessProfileData(businessFormData);
      setSaveStatus('saved');
      setBusinessErrors({});
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (error) {
      setSaveStatus('error');
      if (error instanceof Error) {
        const errors: Record<string, string> = {};
        errors.general = error.message;
        setBusinessErrors(errors);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleUserInputChange = (field: string, value: unknown) => {
    setUserFormData(prev => ({ ...prev, [field]: value }));
    setUserErrors(prev => ({ ...prev, [field]: '' }));
  };

  const handleBusinessInputChange = (field: string, value: unknown) => {
    setBusinessFormData(prev => ({ ...prev, [field]: value }));
    setBusinessErrors(prev => ({ ...prev, [field]: '' }));
  };

  const handleArrayInput = (
    field: string,
    value: string,
    index: number,
    type: 'user' | 'business'
  ) => {
    if (type === 'user') {
      const current = userFormData as Record<string, unknown>;
      const arr = Array.isArray(current[field]) ? (current[field] as string[]) : [];
      const newArray = [...arr];
      newArray[index] = value;
      setUserFormData(prev => ({ ...prev, [field]: newArray }));
    } else {
      const current = businessFormData as Record<string, unknown>;
      const arr = Array.isArray(current[field]) ? (current[field] as string[]) : [];
      const newArray = [...arr];
      newArray[index] = value;
      setBusinessFormData(prev => ({ ...prev, [field]: newArray }));
    }
  };

  const addArrayItem = (field: string, type: 'user' | 'business') => {
    if (type === 'user') {
      const current = userFormData as Record<string, unknown>;
      const arr = Array.isArray(current[field]) ? (current[field] as string[]) : [];
      setUserFormData(prev => ({ ...prev, [field]: [...arr, ''] }));
    } else {
      const current = businessFormData as Record<string, unknown>;
      const arr = Array.isArray(current[field]) ? (current[field] as string[]) : [];
      setBusinessFormData(prev => ({ ...prev, [field]: [...arr, ''] }));
    }
  };

  const removeArrayItem = (field: string, index: number, type: 'user' | 'business') => {
    if (type === 'user') {
      const current = userFormData as Record<string, unknown>;
      const arr = Array.isArray(current[field]) ? (current[field] as string[]) : [];
      const newArray = arr.filter((_, i) => i !== index);
      setUserFormData(prev => ({ ...prev, [field]: newArray }));
    } else {
      const current = businessFormData as Record<string, unknown>;
      const arr = Array.isArray(current[field]) ? (current[field] as string[]) : [];
      const newArray = arr.filter((_, i) => i !== index);
      setBusinessFormData(prev => ({ ...prev, [field]: newArray }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <Card role="dialog" aria-modal="true" aria-labelledby="profile-editor-title" className="w-full max-w-4xl max-h-[90vh] overflow-y-auto backdrop-blur-md bg-card/95 border border-border shadow-brand-lg rounded-2xl p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 border-b border-border pb-4">
          <div>
            <h2 id="profile-editor-title" className="text-xl font-bold font-display text-foreground">
              Edit {profileType === 'user' ? 'User' : 'Business'} Profile
            </h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {profileType === 'user' ? 'Update your personal and operator credentials' : 'Update your company structure and market footprint'}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {/* Auto-save toggle */}
            <label className="flex items-center space-x-2 text-sm cursor-pointer select-none">
              <input
                type="checkbox"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
                className="rounded border-border text-primary focus:ring-2 focus:ring-ring"
              />
              <span className="text-foreground text-xs font-mono font-medium">Auto-save</span>
            </label>
            {/* Save status */}
            {saveStatus === 'saved' && (
              <Badge variant="success" size="sm" className="flex items-center gap-1 font-mono">
                <Check className="w-3.5 h-3.5" /> Saved
              </Badge>
            )}
            {saveStatus === 'error' && (
              <Badge variant="error" size="sm" className="flex items-center gap-1 font-mono">
                <AlertTriangle className="w-3.5 h-3.5" /> Error
              </Badge>
            )}
            <Button size="sm" variant="ghost" onClick={onClose} aria-label="Close profile editor" className="p-2 hover:bg-muted text-muted-foreground hover:text-foreground rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-border mb-6">
          <nav className="flex space-x-6">
            <button
              className={`pb-3 px-1 text-sm font-semibold border-b-2 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                activeTab === 'basic'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setActiveTab('basic')}
            >
              Basic Info
            </button>
            <button
              className={`pb-3 px-1 text-sm font-semibold border-b-2 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                activeTab === 'details'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setActiveTab('details')}
            >
              Details
            </button>
            <button
              className={`pb-3 px-1 text-sm font-semibold border-b-2 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                activeTab === 'advanced'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
              onClick={() => setActiveTab('advanced')}
            >
              Advanced
            </button>
          </nav>
        </div>

        {/* Form Content */}
        <div className="space-y-6">
          {profileType === 'user' ? (
            <>
              {/* Basic Info Tab */}
              {activeTab === 'basic' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="First Name"
                    value={userFormData.first_name || ''}
                    onChange={(e) => handleUserInputChange('first_name', e.target.value)}
                    error={userErrors.first_name}
                  />
                  <Input
                    label="Last Name"
                    value={userFormData.last_name || ''}
                    onChange={(e) => handleUserInputChange('last_name', e.target.value)}
                    error={userErrors.last_name}
                  />
                  <Input
                    label="Email"
                    type="email"
                    value={userFormData.email || ''}
                    onChange={(e) => handleUserInputChange('email', e.target.value)}
                    error={userErrors.email}
                  />
                  <Input
                    label="Phone"
                    type="tel"
                    value={userFormData.phone || ''}
                    onChange={(e) => handleUserInputChange('phone', e.target.value)}
                    error={userErrors.phone}
                  />
                  <Input
                    label="Job Title"
                    value={userFormData.job_title || ''}
                    onChange={(e) => handleUserInputChange('job_title', e.target.value)}
                    error={userErrors.job_title}
                  />
                  <Input
                    label="Company Role"
                    value={userFormData.company_role || ''}
                    onChange={(e) => handleUserInputChange('company_role', e.target.value)}
                    error={userErrors.company_role}
                  />
                </div>
              )}

              {/* Details Tab */}
              {activeTab === 'details' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Years of Experience"
                    type="number"
                    value={userFormData.years_of_experience || ''}
                    onChange={(e) => handleUserInputChange('years_of_experience', parseInt(e.target.value) || undefined)}
                    error={userErrors.years_of_experience}
                  />
                  <Input
                    label="Education Level"
                    value={userFormData.education_level || ''}
                    onChange={(e) => handleUserInputChange('education_level', e.target.value)}
                    error={userErrors.education_level}
                  />
                  <Input
                    label="Field of Study"
                    value={userFormData.field_of_study || ''}
                    onChange={(e) => handleUserInputChange('field_of_study', e.target.value)}
                    error={userErrors.field_of_study}
                  />
                </div>
              )}

              {/* Advanced Tab */}
              {activeTab === 'advanced' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Interests</label>
                    <div className="space-y-2">
                      {(userFormData.interests || []).map((interest, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Input
                            value={interest}
                            onChange={(e) => handleArrayInput('interests', e.target.value, index, 'user')}
                            fullWidth
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeArrayItem('interests', index, 'user')}
                            className="hover:bg-destructive/10 text-muted-foreground hover:text-destructive rounded-lg"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      <Button size="sm" variant="outline" onClick={() => addArrayItem('interests', 'user')} className="rounded-xl border-border hover:border-primary/40 hover:text-primary">
                        + Add Interest
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Learning Goals</label>
                    <div className="space-y-2">
                      {(userFormData.learning_goals || []).map((goal, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Input
                            value={goal}
                            onChange={(e) => handleArrayInput('learning_goals', e.target.value, index, 'user')}
                            fullWidth
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeArrayItem('learning_goals', index, 'user')}
                            className="hover:bg-destructive/10 text-muted-foreground hover:text-destructive rounded-lg"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      <Button size="sm" variant="outline" onClick={() => addArrayItem('learning_goals', 'user')} className="rounded-xl border-border hover:border-primary/40 hover:text-primary">
                        + Add Goal
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Business Challenges</label>
                    <div className="space-y-2">
                      {(userFormData.business_challenges || []).map((challenge, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Input
                            value={challenge}
                            onChange={(e) => handleArrayInput('business_challenges', e.target.value, index, 'user')}
                            fullWidth
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeArrayItem('business_challenges', index, 'user')}
                            className="hover:bg-destructive/10 text-muted-foreground hover:text-destructive rounded-lg"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      <Button size="sm" variant="outline" onClick={() => addArrayItem('business_challenges', 'user')} className="rounded-xl border-border hover:border-primary/40 hover:text-primary">
                        + Add Challenge
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Business Profile Form */}
              {activeTab === 'basic' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Company Name"
                    value={businessFormData.company_name || ''}
                    onChange={(e) => handleBusinessInputChange('company_name', e.target.value)}
                    error={businessErrors.company_name}
                  />
                  <Input
                    label="Industry"
                    value={businessFormData.industry || ''}
                    onChange={(e) => handleBusinessInputChange('industry', e.target.value)}
                    error={businessErrors.industry}
                  />
                  <Input
                    label="Business Stage"
                    value={businessFormData.business_stage || ''}
                    onChange={(e) => handleBusinessInputChange('business_stage', e.target.value)}
                    error={businessErrors.business_stage}
                  />
                  <Input
                    label="Business Type"
                    value={businessFormData.business_type || ''}
                    onChange={(e) => handleBusinessInputChange('business_type', e.target.value)}
                    error={businessErrors.business_type}
                  />
                  <Input
                    label="Legal Structure"
                    value={businessFormData.legal_structure || ''}
                    onChange={(e) => handleBusinessInputChange('legal_structure', e.target.value)}
                    error={businessErrors.legal_structure}
                  />
                  <Input
                    label="Website URL"
                    type="url"
                    value={businessFormData.website_url || ''}
                    onChange={(e) => handleBusinessInputChange('website_url', e.target.value)}
                    error={businessErrors.website_url}
                  />
                </div>
              )}

              {/* Details Tab */}
              {activeTab === 'details' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Business Description</label>
                    <textarea
                      className="w-full px-3.5 py-2.5 border border-border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary text-sm bg-muted/30 transition-all text-foreground"
                      rows={4}
                      value={businessFormData.business_description || ''}
                      onChange={(e) => handleBusinessInputChange('business_description', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Mission Statement</label>
                    <textarea
                      className="w-full px-3.5 py-2.5 border border-border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary text-sm bg-muted/30 transition-all text-foreground"
                      rows={3}
                      value={businessFormData.mission_statement || ''}
                      onChange={(e) => handleBusinessInputChange('mission_statement', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Vision Statement</label>
                    <textarea
                      className="w-full px-3.5 py-2.5 border border-border rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary text-sm bg-muted/30 transition-all text-foreground"
                      rows={3}
                      value={businessFormData.vision_statement || ''}
                      onChange={(e) => handleBusinessInputChange('vision_statement', e.target.value)}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      label="Team Size"
                      type="number"
                      value={businessFormData.team_size || ''}
                      onChange={(e) => handleBusinessInputChange('team_size', parseInt(e.target.value) || undefined)}
                      error={businessErrors.team_size}
                    />
                    <Input
                      label="Annual Revenue"
                      type="number"
                      value={businessFormData.annual_revenue || ''}
                      onChange={(e) => handleBusinessInputChange('annual_revenue', parseFloat(e.target.value) || undefined)}
                      error={businessErrors.annual_revenue}
                    />
                    <Input
                      label="Customer Count"
                      type="number"
                      value={businessFormData.customer_count || ''}
                      onChange={(e) => handleBusinessInputChange('customer_count', parseInt(e.target.value) || undefined)}
                      error={businessErrors.customer_count}
                    />
                  </div>
                </div>
              )}

              {/* Advanced Tab */}
              {activeTab === 'advanced' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Target Market</label>
                    <div className="space-y-2">
                      {(businessFormData.target_market || []).map((market, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Input
                            value={market}
                            onChange={(e) => handleArrayInput('target_market', e.target.value, index, 'business')}
                            fullWidth
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeArrayItem('target_market', index, 'business')}
                            className="hover:bg-destructive/10 text-muted-foreground hover:text-destructive rounded-lg"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      <Button size="sm" variant="outline" onClick={() => addArrayItem('target_market', 'business')} className="rounded-xl border-border hover:border-primary/40 hover:text-primary">
                        + Add Target Market
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Competitive Advantages</label>
                    <div className="space-y-2">
                      {(businessFormData.competitive_advantages || []).map((advantage, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Input
                            value={advantage}
                            onChange={(e) => handleArrayInput('competitive_advantages', e.target.value, index, 'business')}
                            fullWidth
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeArrayItem('competitive_advantages', index, 'business')}
                            className="hover:bg-destructive/10 text-muted-foreground hover:text-destructive rounded-lg"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      <Button size="sm" variant="outline" onClick={() => addArrayItem('competitive_advantages', 'business')} className="rounded-xl border-border hover:border-primary/40 hover:text-primary">
                        + Add Advantage
                      </Button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">Technology Stack</label>
                    <div className="space-y-2">
                      {(businessFormData.tech_stack || []).map((tech, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Input
                            value={tech}
                            onChange={(e) => handleArrayInput('tech_stack', e.target.value, index, 'business')}
                            fullWidth
                          />
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeArrayItem('tech_stack', index, 'business')}
                            className="hover:bg-destructive/10 text-muted-foreground hover:text-destructive rounded-lg"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                      <Button size="sm" variant="outline" onClick={() => addArrayItem('tech_stack', 'business')} className="rounded-xl border-border hover:border-primary/40 hover:text-primary">
                        + Add Technology
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-6 pt-6 border-t border-border">
          <div>
            {userErrors.general && (
              <p className="text-sm text-destructive font-medium">{userErrors.general}</p>
            )}
            {businessErrors.general && (
              <p className="text-sm text-destructive font-medium">{businessErrors.general}</p>
            )}
          </div>
          <div className="flex items-center space-x-3">
            <Button size="md" variant="outline" onClick={onClose} className="rounded-xl border-border hover:bg-muted focus-visible:ring-2 focus-visible:ring-ring">
              Cancel
            </Button>
            {!autoSave && (
              <Button
                size="md"
                onClick={profileType === 'user' ? handleSaveUser : handleSaveBusiness}
                loading={saving}
                className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-brand rounded-xl font-semibold focus-visible:ring-2 focus-visible:ring-ring active:scale-95"
              >
                Save Changes
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ProfileEditor;
