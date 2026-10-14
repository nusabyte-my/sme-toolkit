/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · User profile card */
import React, { useState } from 'react';
import Card from '../../ui/Card';
import Badge from '../../ui/Badge';
import Button from '../../ui/Button';
import { useProfile } from '../../../contexts/ProfileContext';
import { formatDate } from '../../../services/profileService';

interface UserProfileCardProps {
  onEdit?: () => void;
}

const getSkillLabel = (skill: unknown): string => {
  if (typeof skill === 'string') return skill;
  if (skill && typeof skill === 'object') {
    if ('name' in skill && typeof skill.name === 'string') return skill.name;
    if ('skill' in skill && typeof skill.skill === 'string') return skill.skill;
  }
  return String(skill);
};

const UserProfileCard: React.FC<UserProfileCardProps> = ({ onEdit }) => {
  const { userProfile, userProfileLoading, userProfileError, fetchUserProfile } = useProfile();
  const [showFullDetails, setShowFullDetails] = useState(false);

  React.useEffect(() => {
    if (!userProfile && !userProfileLoading && !userProfileError) {
      fetchUserProfile();
    }
  }, [userProfile, userProfileLoading, userProfileError, fetchUserProfile]);

  if (userProfileLoading) {
    return (
      <Card className="h-full bg-card border-border rounded-2xl p-6">
        <div className="animate-pulse space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-muted rounded-full" />
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-muted rounded w-1/3" />
              <div className="h-3 bg-muted rounded w-1/4" />
            </div>
          </div>
          <div className="h-2 bg-muted rounded w-full" />
        </div>
      </Card>
    );
  }

  if (userProfileError) {
    return (
      <Card className="h-full bg-card border-border rounded-2xl p-6">
        <div className="text-center py-8">
          <p className="text-destructive mb-4 text-sm font-medium">{userProfileError}</p>
          <Button size="sm" onClick={fetchUserProfile} className="focus-visible:ring-2 focus-visible:ring-ring">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (!userProfile) {
    return (
      <Card className="h-full bg-card border-border rounded-2xl p-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4 text-sm">No profile data available</p>
          <Button size="sm" onClick={fetchUserProfile} className="focus-visible:ring-2 focus-visible:ring-ring">
            Load Profile
          </Button>
        </div>
      </Card>
    );
  }

  const completionPercentage = userProfile.profile_completion_percentage || 0;
  const completionVariant = completionPercentage >= 80 ? 'success' : completionPercentage >= 50 ? 'warning' : 'error';

  return (
    <Card className="h-full backdrop-blur-sm bg-card border border-border rounded-2xl p-6 shadow-sm">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          {userProfile.avatar_url ? (
            <img
              src={userProfile.avatar_url}
              alt={userProfile.full_name || 'Profile'}
              className="w-12 h-12 rounded-full object-cover ring-2 ring-primary ring-offset-2 ring-offset-background"
            />
          ) : (
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-brand text-white font-bold text-lg flex-shrink-0">
              <span>
                {userProfile.first_name?.[0] || userProfile.email?.[0] || 'U'}
              </span>
            </div>
          )}
          <div className="min-w-0">
            <h3 className="text-lg font-bold font-display text-foreground truncate">
              {userProfile.full_name || `${userProfile.first_name || ''} ${userProfile.last_name || ''}`.trim() || 'User'}
            </h3>
            <p className="text-sm text-muted-foreground truncate">{userProfile.email || 'No email'}</p>
          </div>
        </div>
        <Button size="sm" variant="outline" onClick={onEdit} className="border-border hover:bg-primary/10 hover:border-primary/40 hover:text-primary rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-ring">
          Edit
        </Button>
      </div>

      {/* Profile Completion */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono font-semibold uppercase text-muted-foreground">Profile Completion</span>
          <Badge variant={completionVariant}>
            {completionPercentage}%
          </Badge>
        </div>
        <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
          <div
            className="h-2 rounded-full transition-all duration-500 bg-primary"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Key Information */}
      <div className="space-y-2.5 mb-4 text-xs font-mono">
        {userProfile.job_title && (
          <div className="flex items-center">
            <span className="text-muted-foreground w-24 uppercase">Job Title:</span>
            <span className="text-foreground font-semibold">{userProfile.job_title}</span>
          </div>
        )}
        {userProfile.company_role && (
          <div className="flex items-center">
            <span className="text-muted-foreground w-24 uppercase">Role:</span>
            <span className="text-foreground font-semibold">{userProfile.company_role}</span>
          </div>
        )}
        {userProfile.phone && (
          <div className="flex items-center">
            <span className="text-muted-foreground w-24 uppercase">Phone:</span>
            <span className="text-foreground font-semibold">{userProfile.phone}</span>
          </div>
        )}
        {userProfile.city && userProfile.country && (
          <div className="flex items-center">
            <span className="text-muted-foreground w-24 uppercase">Location:</span>
            <span className="text-foreground font-semibold">
              {userProfile.city}, {userProfile.country}
            </span>
          </div>
        )}
      </div>

      {/* Professional Background */}
      {showFullDetails && (
        <div className="border-t border-border pt-4 space-y-2.5 text-xs font-mono">
          {userProfile.years_of_experience && (
            <div className="flex items-center">
              <span className="text-muted-foreground w-24 uppercase">Experience:</span>
              <span className="text-foreground font-semibold">{userProfile.years_of_experience} years</span>
            </div>
          )}
          {userProfile.education_level && (
            <div className="flex items-center">
              <span className="text-muted-foreground w-24 uppercase">Education:</span>
              <span className="text-foreground font-semibold">{userProfile.education_level}</span>
            </div>
          )}
          {userProfile.field_of_study && (
            <div className="flex items-center">
              <span className="text-muted-foreground w-24 uppercase">Field:</span>
              <span className="text-foreground font-semibold">{userProfile.field_of_study}</span>
            </div>
          )}
          {userProfile.owns_business && (
            <div className="flex items-center">
              <span className="text-muted-foreground w-24 uppercase">Business:</span>
              <Badge variant="success" size="sm">
                Business Owner
              </Badge>
            </div>
          )}
        </div>
      )}

      {/* Skills and Interests */}
      {showFullDetails && (userProfile.interests?.length || userProfile.skills?.length) && (
        <div className="border-t border-border pt-4 mt-4">
          {userProfile.interests && userProfile.interests.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Interests</p>
              <div className="flex flex-wrap gap-1.5">
                {userProfile.interests.slice(0, 5).map((interest, index) => (
                  <Badge key={index} variant="default" size="sm" className="bg-primary/10 text-primary border border-primary/20">
                    {interest}
                  </Badge>
                ))}
                {userProfile.interests.length > 5 && (
                  <Badge variant="default" size="sm" className="bg-muted text-muted-foreground">
                    +{userProfile.interests.length - 5}
                  </Badge>
                )}
              </div>
            </div>
          )}
          {userProfile.skills && userProfile.skills.length > 0 && (
            <div>
              <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Skills</p>
              <div className="flex flex-wrap gap-1.5">
                {userProfile.skills.slice(0, 5).map((skill, index) => (
                  <Badge key={index} variant="default" size="sm" className="bg-rainbow-emerald/10 text-rainbow-emerald border border-rainbow-emerald/20">
                    {getSkillLabel(skill)}
                  </Badge>
                ))}
                {userProfile.skills.length > 5 && (
                  <Badge variant="default" size="sm" className="bg-muted text-muted-foreground">
                    +{userProfile.skills.length - 5}
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Last Updated */}
      <div className="border-t border-border pt-4 mt-4">
        <p className="text-xs text-muted-foreground font-mono">
          Last updated: {userProfile.last_profile_update ? formatDate(userProfile.last_profile_update) : formatDate(userProfile.updated_at)}
        </p>
      </div>

      {/* Show More/Less Button */}
      <div className="mt-4">
        <Button
          size="sm"
          variant="ghost"
          fullWidth
          onClick={() => setShowFullDetails(!showFullDetails)}
          className="text-muted-foreground hover:text-foreground hover:bg-muted rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-ring"
        >
          {showFullDetails ? 'Show Less' : 'Show More Details'}
        </Button>
      </div>
    </Card>
  );
};

export default UserProfileCard;
