/* Hallmark · rehaul 2026-10-05 · jebat-creative DNA · Business profile details */
import React, { useState } from 'react';
import Card from '../../ui/Card';
import Badge from '../../ui/Badge';
import Button from '../../ui/Button';
import { useProfile } from '../../../contexts/ProfileContext';
import { formatDate, formatNumber } from '../../../services/profileService';

interface BusinessProfilePanelProps {
  onEdit?: () => void;
}

const getProductDetails = (product: unknown): { name: string; description?: string } => {
  if (product && typeof product === 'object') {
    const name = ('name' in product && typeof product.name === 'string') 
      ? product.name 
      : ('product_name' in product && typeof product.product_name === 'string') 
        ? product.product_name 
        : 'Product';
    const description = ('description' in product && typeof product.description === 'string')
      ? product.description
      : undefined;
    return { name, description };
  }
  return { name: String(product || 'Product') };
};

const BusinessProfilePanel: React.FC<BusinessProfilePanelProps> = ({ onEdit }) => {
  const { businessProfile, businessProfileLoading, businessProfileError, fetchBusinessProfile } = useProfile();
  const [showFullDetails, setShowFullDetails] = useState(false);

  React.useEffect(() => {
    if (!businessProfile && !businessProfileLoading && !businessProfileError) {
      fetchBusinessProfile();
    }
  }, [businessProfile, businessProfileLoading, businessProfileError, fetchBusinessProfile]);

  if (businessProfileLoading) {
    return (
      <Card className="h-full bg-card border-border rounded-2xl p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-muted rounded w-3/4 mb-4" />
          <div className="h-3 bg-muted rounded w-1/2 mb-2" />
          <div className="h-3 bg-muted rounded w-2/3 mb-4" />
          <div className="h-2 bg-muted rounded w-full mb-2" />
          <div className="h-2 bg-muted rounded w-3/4" />
        </div>
      </Card>
    );
  }

  if (businessProfileError) {
    return (
      <Card className="h-full bg-card border-border rounded-2xl p-6">
        <div className="text-center py-8">
          <p className="text-destructive mb-4 text-sm font-medium">{businessProfileError}</p>
          <Button size="sm" onClick={fetchBusinessProfile} className="focus-visible:ring-2 focus-visible:ring-ring">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (!businessProfile) {
    return (
      <Card className="h-full bg-card border-border rounded-2xl p-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground mb-4 text-sm">No business profile data available</p>
          <Button size="sm" onClick={fetchBusinessProfile} className="focus-visible:ring-2 focus-visible:ring-ring">
            Load Business Profile
          </Button>
        </div>
      </Card>
    );
  }

  const completenessScore = businessProfile.profile_completeness_score || 0;
  const completenessVariant = completenessScore >= 80 ? 'success' : completenessScore >= 50 ? 'warning' : 'error';

  return (
    <Card className="h-full backdrop-blur-sm bg-card border border-border rounded-2xl p-6 shadow-sm">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold font-display text-foreground">{businessProfile.company_name || 'Business Profile'}</h3>
          <p className="text-sm text-muted-foreground">{businessProfile.industry || 'Industry not specified'}</p>
        </div>
        <Button size="sm" variant="outline" onClick={onEdit} className="border-border hover:bg-primary/10 hover:border-primary/40 hover:text-primary rounded-xl transition-all focus-visible:ring-2 focus-visible:ring-ring">
          Edit
        </Button>
      </div>

      {/* Profile Completeness */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono font-semibold uppercase text-muted-foreground">Profile Completeness</span>
          <Badge variant={completenessVariant}>
            {completenessScore.toFixed(0)}%
          </Badge>
        </div>
        <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
          <div
            className="h-2 rounded-full transition-all duration-500 bg-primary"
            style={{ width: `${completenessScore}%` }}
          />
        </div>
      </div>

      {/* Business Classification */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {businessProfile.business_type && (
          <div className="bg-muted/40 rounded-xl p-3 border border-border">
            <p className="text-[10px] font-mono uppercase text-muted-foreground mb-1">Business Type</p>
            <p className="text-sm font-semibold text-foreground">{businessProfile.business_type}</p>
          </div>
        )}
        {businessProfile.business_stage && (
          <div className="bg-muted/40 rounded-xl p-3 border border-border">
            <p className="text-[10px] font-mono uppercase text-muted-foreground mb-1">Stage</p>
            <p className="text-sm font-semibold text-foreground">{businessProfile.business_stage}</p>
          </div>
        )}
        {businessProfile.legal_structure && (
          <div className="bg-muted/40 rounded-xl p-3 border border-border">
            <p className="text-[10px] font-mono uppercase text-muted-foreground mb-1">Legal Structure</p>
            <p className="text-sm font-semibold text-foreground">{businessProfile.legal_structure}</p>
          </div>
        )}
        {businessProfile.funding_stage && (
          <div className="bg-muted/40 rounded-xl p-3 border border-border">
            <p className="text-[10px] font-mono uppercase text-muted-foreground mb-1">Funding Stage</p>
            <p className="text-sm font-semibold text-foreground">{businessProfile.funding_stage}</p>
          </div>
        )}
      </div>

      {/* Key Metrics - Rainbow rotation */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {businessProfile.annual_revenue && (
          <div className="text-center bg-primary/10 rounded-xl p-3 border border-primary/20">
            <p className="text-xl font-bold font-display text-primary">
              {businessProfile.revenue_currency || 'RM'}{formatNumber(businessProfile.annual_revenue)}
            </p>
            <p className="text-[10px] font-mono uppercase text-muted-foreground mt-0.5">Annual Revenue</p>
          </div>
        )}
        {businessProfile.team_size && (
          <div className="text-center bg-rainbow-emerald/10 rounded-xl p-3 border border-rainbow-emerald/20">
            <p className="text-xl font-bold font-display text-rainbow-emerald">{formatNumber(businessProfile.team_size)}</p>
            <p className="text-[10px] font-mono uppercase text-muted-foreground mt-0.5">Team Size</p>
          </div>
        )}
        {businessProfile.customer_count && (
          <div className="text-center bg-rainbow-amber/10 rounded-xl p-3 border border-rainbow-amber/20">
            <p className="text-xl font-bold font-display text-rainbow-amber">{formatNumber(businessProfile.customer_count)}</p>
            <p className="text-[10px] font-mono uppercase text-muted-foreground mt-0.5">Customers</p>
          </div>
        )}
      </div>

      {/* Business Description */}
      {businessProfile.business_description && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-1.5">About</p>
          <p className="text-sm text-foreground line-clamp-3 leading-relaxed">
            {businessProfile.business_description}
          </p>
        </div>
      )}

      {/* Mission Statement */}
      {showFullDetails && businessProfile.mission_statement && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-1">Mission</p>
          <p className="text-sm text-foreground italic leading-relaxed">{businessProfile.mission_statement}</p>
        </div>
      )}

      {/* Vision Statement */}
      {showFullDetails && businessProfile.vision_statement && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-1">Vision</p>
          <p className="text-sm text-foreground italic leading-relaxed">{businessProfile.vision_statement}</p>
        </div>
      )}

      {/* Products/Services */}
      {showFullDetails && businessProfile.products_services && businessProfile.products_services.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Products & Services</p>
          <div className="space-y-2">
            {businessProfile.products_services.slice(0, 3).map((rawProduct, index) => {
              const product = getProductDetails(rawProduct);
              return (
                <div key={index} className="bg-muted/40 rounded-xl p-3 border border-border">
                  <p className="text-sm font-semibold text-foreground">{product.name}</p>
                  {product.description && (
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{product.description}</p>
                  )}
                </div>
              );
            })}
            {businessProfile.products_services.length > 3 && (
              <p className="text-xs font-mono text-muted-foreground text-center">
                +{businessProfile.products_services.length - 3} more items
              </p>
            )}
          </div>
        </div>
      )}

      {/* Technology Stack */}
      {showFullDetails && businessProfile.tech_stack && businessProfile.tech_stack.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Technology Stack</p>
          <div className="flex flex-wrap gap-1.5">
            {businessProfile.tech_stack.map((tech, index) => (
              <Badge key={index} variant="default" size="sm" className="bg-primary/10 text-primary border border-primary/20">
                {tech}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Software Tools */}
      {showFullDetails && businessProfile.software_tools && businessProfile.software_tools.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Software Tools</p>
          <div className="flex flex-wrap gap-1.5">
            {businessProfile.software_tools.map((tool, index) => (
              <Badge key={index} variant="default" size="sm" className="bg-rainbow-cyan/10 text-rainbow-cyan border border-rainbow-cyan/20">
                {tool}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Target Market */}
      {showFullDetails && businessProfile.target_market && businessProfile.target_market.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Target Market</p>
          <div className="flex flex-wrap gap-1.5">
            {businessProfile.target_market.map((market, index) => (
              <Badge key={index} variant="default" size="sm" className="bg-muted text-foreground border border-border">
                {market}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Competitive Advantages */}
      {showFullDetails && businessProfile.competitive_advantages && businessProfile.competitive_advantages.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-mono font-semibold uppercase text-muted-foreground mb-2">Competitive Advantages</p>
          <ul className="list-disc list-inside space-y-1 text-sm text-foreground">
            {businessProfile.competitive_advantages.slice(0, 3).map((advantage, index) => (
              <li key={index} className="text-muted-foreground">
                <span className="text-foreground">{advantage}</span>
              </li>
            ))}
            {businessProfile.competitive_advantages.length > 3 && (
              <li className="text-xs font-mono text-muted-foreground">
                +{businessProfile.competitive_advantages.length - 3} more advantages
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Website */}
      {businessProfile.website_url && (
        <div className="mb-4">
          <a
            href={businessProfile.website_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline font-semibold transition-colors"
          >
            Visit Website →
          </a>
        </div>
      )}

      {/* Last Updated */}
      <div className="border-t border-border pt-4">
        <p className="text-xs text-muted-foreground font-mono">
          Last updated: {businessProfile.last_data_refresh ? formatDate(businessProfile.last_data_refresh) : formatDate(businessProfile.updated_at)}
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

export default BusinessProfilePanel;
