export interface SEOMetadata {
  title: string;
  description: string;
  keywords?: string;
  canonical?: string;
  ogImage?: string;
  twitterImage?: string;
  noIndex?: boolean;
}

export interface OpenGraphData {
  title: string;
  description: string;
  url: string;
  image?: string;
  type?: 'website' | 'article' | 'product';
  siteName?: string;
}

export interface TwitterCardData {
  card?: 'summary' | 'summary_large_image' | 'app' | 'player';
  title: string;
  description: string;
  image?: string;
  url?: string;
}

export interface BreadcrumbItem {
  name: string;
  url: string;
}

export interface FAQItem {
  question: string;
  answer: string;
}

export const generateMetaTags = (metadata: SEOMetadata): Record<string, string> => {
  const tags: Record<string, string> = {
    title: metadata.title,
    description: metadata.description,
  };

  if (metadata.keywords) {
    tags.keywords = metadata.keywords;
  }

  if (metadata.canonical) {
    tags.canonical = metadata.canonical;
  }

  if (metadata.noIndex) {
    tags.robots = 'noindex, nofollow';
  } else {
    tags.robots = 'index, follow';
  }

  return tags;
};

export const generateOpenGraphTags = (data: OpenGraphData): Record<string, string> => {
  const tags: Record<string, string> = {
    'og:title': data.title,
    'og:description': data.description,
    'og:url': data.url,
    'og:type': data.type || 'website',
  };

  if (data.image) {
    tags['og:image'] = data.image;
    tags['og:image:width'] = '1200';
    tags['og:image:height'] = '630';
  }

  if (data.siteName) {
    tags['og:site_name'] = data.siteName;
  }

  return tags;
};

export const generateTwitterCardTags = (data: TwitterCardData): Record<string, string> => {
  const tags: Record<string, string> = {
    'twitter:card': data.card || 'summary_large_image',
    'twitter:title': data.title,
    'twitter:description': data.description,
  };

  if (data.image) {
    tags['twitter:image'] = data.image;
  }

  if (data.url) {
    tags['twitter:url'] = data.url;
  }

  return tags;
};

export const generateOrganizationSchema = (data: {
  name: string;
  url: string;
  logo?: string;
  description?: string;
  sameAs?: string[];
  contactEmail?: string;
}): string => {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: data.name,
    url: data.url,
    ...(data.logo && { logo: data.logo }),
    ...(data.description && { description: data.description }),
    ...(data.sameAs && { sameAs: data.sameAs }),
    ...(data.contactEmail && {
      contactPoint: {
        '@type': 'ContactPoint',
        contactType: 'customer service',
        email: data.contactEmail,
      },
    }),
  };

  return JSON.stringify(schema);
};

export const generateSoftwareApplicationSchema = (data: {
  name: string;
  description?: string;
  applicationCategory?: string;
  operatingSystem?: string;
  offers?: {
    price: string;
    priceCurrency: string;
    availability?: string;
  };
  aggregateRating?: {
    ratingValue: string;
    ratingCount: string;
  };
}): string => {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: data.name,
    ...(data.description && { description: data.description }),
    ...(data.applicationCategory && { applicationCategory: data.applicationCategory }),
    ...(data.operatingSystem && { operatingSystem: data.operatingSystem }),
    ...(data.offers && {
      offers: {
        '@type': 'Offer',
        price: data.offers.price,
        priceCurrency: data.offers.priceCurrency,
        ...(data.offers.availability && { availability: data.offers.availability }),
      },
    }),
    ...(data.aggregateRating && {
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: data.aggregateRating.ratingValue,
        ratingCount: data.aggregateRating.ratingCount,
      },
    }),
  };

  return JSON.stringify(schema);
};

export const generateBreadcrumbSchema = (items: BreadcrumbItem[]): string => {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };

  return JSON.stringify(schema);
};

export const generateFAQSchema = (faqs: FAQItem[]): string => {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(faq => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  };

  return JSON.stringify(schema);
};

export const generateWebSiteSchema = (data: {
  name: string;
  url: string;
  description?: string;
  potentialAction?: {
    target: string;
    queryInput: string;
  };
}): string => {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: data.name,
    url: data.url,
    ...(data.description && { description: data.description }),
    ...(data.potentialAction && {
      potentialAction: {
        '@type': 'SearchAction',
        target: data.potentialAction.target,
        'query-input': data.potentialAction.queryInput,
      },
    }),
  };

  return JSON.stringify(schema);
};

export const getPageMetadata = (pageName: string): SEOMetadata => {
  const baseUrl = 'https://sme-toolkit.com';
  
  const metadataMap: Record<string, SEOMetadata> = {
    landing: {
      title: 'SME OS — Run the Business. Not the Busywork.',
      description: 'Keep customer follow-ups, invoices and daily tasks in one workspace. See real examples, then try the sample business. No signup or card.',
      keywords: 'SME OS, business operating workspace, sales CRM, marketing operations, business pilot',
      canonical: `${baseUrl}/`,
    },
    dashboard: {
      title: 'Dashboard - SME Toolkit',
      description: 'Your business at a glance. Track growth, manage goals, and see what needs your attention.',
      keywords: 'business dashboard, SME dashboard, business overview, growth tracking',
      canonical: `${baseUrl}/dashboard`,
    },
    bmc: {
      title: 'Business Model Canvas - SME Toolkit',
      description: 'Map out your business model in minutes. AI-guided canvas builder that makes strategy simple.',
      keywords: 'business model canvas, BMC, business planning, strategy canvas',
      canonical: `${baseUrl}/bmc-hub`,
    },
    leads: {
      title: 'Lead Manager - SME Toolkit',
      description: 'Track and nurture your leads. Simple CRM built for SMEs, not sales teams.',
      keywords: 'lead management, CRM, lead tracking, customer management, small business CRM',
      canonical: `${baseUrl}/leads`,
    },
    sales: {
      title: 'Sales Dashboard - SME Toolkit',
      description: 'Track your sales across channels. See what\'s working and where to focus.',
      keywords: 'sales tracking, sales dashboard, e-commerce analytics, SME sales',
      canonical: `${baseUrl}/sales`,
    },
    copywriter: {
      title: 'Content Studio - SME Toolkit',
      description: 'Create content that connects. Generate emails, social posts, and marketing copy that sounds like you.',
      keywords: 'content creation, AI writing, marketing content, social media posts, email marketing',
      canonical: `${baseUrl}/content-studio`,
    },
    visual: {
      title: 'Visual Studio - SME Toolkit',
      description: 'Design visuals for your business. Social media graphics, ads, and branding made simple.',
      keywords: 'visual design, graphic design, social media images, ad banners, AI design',
      canonical: `${baseUrl}/visual-studio`,
    },
    video: {
      title: 'Video Studio - SME Toolkit',
      description: 'Create short videos for your business. Scripts, storyboards, and generation in one place.',
      keywords: 'video creation, video marketing, short videos, business videos',
      canonical: `${baseUrl}/video-studio`,
    },
    strategy: {
      title: 'Strategy Advisor - SME Toolkit',
      description: 'Get practical advice for your business. Growth plans, goals, and insights tailored to your SME.',
      keywords: 'business strategy, growth planning, business advice, strategic planning',
      canonical: `${baseUrl}/strategy`,
    },
    profiles: {
      title: 'Profiles - SME Toolkit',
      description: 'Manage your business and team profiles. Keep everything in one place.',
      keywords: 'business profiles, team management, profile management',
      canonical: `${baseUrl}/profiles`,
    },
  };

  return metadataMap[pageName] || metadataMap.landing;
};

export const getPageOpenGraphData = (pageName: string): OpenGraphData => {
  const baseUrl = 'https://sme-toolkit.com';
  
  const ogDataMap: Record<string, OpenGraphData> = {
    landing: {
      title: 'SME OS — Run the Business. Not the Busywork.',
      description: 'Keep customer follow-ups, invoices and daily tasks in one workspace. See real examples, then try the sample business. No signup or card.',
      url: `${baseUrl}/`,
      image: `${baseUrl}/meranti-workspace.webp`,
      type: 'website',
      siteName: 'SME OS',
    },
    dashboard: {
      title: 'Dashboard - SME Toolkit',
      description: 'Your business at a glance.',
      url: `${baseUrl}/dashboard`,
      image: `${baseUrl}/og-dashboard.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    bmc: {
      title: 'Business Model Canvas - SME Toolkit',
      description: 'Map out your business model in minutes.',
      url: `${baseUrl}/bmc-hub`,
      image: `${baseUrl}/og-bmc.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    leads: {
      title: 'Lead Manager - SME Toolkit',
      description: 'Track and nurture your leads.',
      url: `${baseUrl}/leads`,
      image: `${baseUrl}/og-leads.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    sales: {
      title: 'Sales Dashboard - SME Toolkit',
      description: 'Track your sales across channels.',
      url: `${baseUrl}/sales`,
      image: `${baseUrl}/og-sales.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    copywriter: {
      title: 'Content Studio - SME Toolkit',
      description: 'Create content that connects.',
      url: `${baseUrl}/content-studio`,
      image: `${baseUrl}/og-copywriter.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    visual: {
      title: 'Visual Studio - SME Toolkit',
      description: 'Design visuals for your business.',
      url: `${baseUrl}/visual-studio`,
      image: `${baseUrl}/og-visual.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    video: {
      title: 'Video Studio - SME Toolkit',
      description: 'Create short videos for your business.',
      url: `${baseUrl}/video-studio`,
      image: `${baseUrl}/og-video.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    strategy: {
      title: 'Strategy Advisor - SME Toolkit',
      description: 'Get practical advice for your business.',
      url: `${baseUrl}/strategy`,
      image: `${baseUrl}/og-strategy.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
    profiles: {
      title: 'Profiles - SME Toolkit',
      description: 'Manage your business and team profiles.',
      url: `${baseUrl}/profiles`,
      image: `${baseUrl}/og-profiles.png`,
      type: 'website',
      siteName: 'SME Toolkit',
    },
  };

  return ogDataMap[pageName] || ogDataMap.landing;
};

export const getPageTwitterCardData = (pageName: string): TwitterCardData => {
  const baseUrl = 'https://sme-toolkit.com';
  
  const twitterDataMap: Record<string, TwitterCardData> = {
    landing: {
      card: 'summary_large_image',
      title: 'SME OS — Run the Business. Not the Busywork.',
      description: 'Keep customer follow-ups, invoices and daily tasks in one workspace. See real examples, then try the sample business. No signup or card.',
      image: `${baseUrl}/meranti-workspace.webp`,
      url: `${baseUrl}/`,
    },
    dashboard: {
      card: 'summary_large_image',
      title: 'Dashboard - SME Toolkit',
      description: 'Your business at a glance.',
      image: `${baseUrl}/twitter-dashboard.png`,
      url: `${baseUrl}/dashboard`,
    },
    bmc: {
      card: 'summary_large_image',
      title: 'Business Model Canvas - SME Toolkit',
      description: 'Map out your business model in minutes.',
      image: `${baseUrl}/twitter-bmc.png`,
      url: `${baseUrl}/bmc-hub`,
    },
    leads: {
      card: 'summary_large_image',
      title: 'Lead Manager - SME Toolkit',
      description: 'Track and nurture your leads.',
      image: `${baseUrl}/twitter-leads.png`,
      url: `${baseUrl}/leads`,
    },
    sales: {
      card: 'summary_large_image',
      title: 'Sales Dashboard - SME Toolkit',
      description: 'Track your sales across channels.',
      image: `${baseUrl}/twitter-sales.png`,
      url: `${baseUrl}/sales`,
    },
    copywriter: {
      card: 'summary_large_image',
      title: 'Content Studio - SME Toolkit',
      description: 'Create content that connects.',
      image: `${baseUrl}/twitter-copywriter.png`,
      url: `${baseUrl}/content-studio`,
    },
    visual: {
      card: 'summary_large_image',
      title: 'Visual Studio - SME Toolkit',
      description: 'Design visuals for your business.',
      image: `${baseUrl}/twitter-visual.png`,
      url: `${baseUrl}/visual-studio`,
    },
    video: {
      card: 'summary_large_image',
      title: 'Video Studio - SME Toolkit',
      description: 'Create short videos for your business.',
      image: `${baseUrl}/twitter-video.png`,
      url: `${baseUrl}/video-studio`,
    },
    strategy: {
      card: 'summary_large_image',
      title: 'Strategy Advisor - SME Toolkit',
      description: 'Get practical advice for your business.',
      image: `${baseUrl}/twitter-strategy.png`,
      url: `${baseUrl}/strategy`,
    },
    profiles: {
      card: 'summary_large_image',
      title: 'Profiles - SME Toolkit',
      description: 'Manage your business and team profiles.',
      image: `${baseUrl}/twitter-profiles.png`,
      url: `${baseUrl}/profiles`,
    },
  };

  return twitterDataMap[pageName] || twitterDataMap.landing;
};

export const getBreadcrumbs = (pageName: string): BreadcrumbItem[] => {
  const baseUrl = 'https://sme-toolkit.com';
  
  const breadcrumbMap: Record<string, BreadcrumbItem[]> = {
    landing: [
      { name: 'Home', url: `${baseUrl}/` },
    ],
    dashboard: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Dashboard', url: `${baseUrl}/dashboard` },
    ],
    bmc: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Business Model Canvas', url: `${baseUrl}/bmc-hub` },
    ],
    leads: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Lead Manager', url: `${baseUrl}/leads` },
    ],
    sales: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Sales Dashboard', url: `${baseUrl}/sales` },
    ],
    copywriter: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Content Studio', url: `${baseUrl}/content-studio` },
    ],
    visual: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Visual Studio', url: `${baseUrl}/visual-studio` },
    ],
    video: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Video Studio', url: `${baseUrl}/video-studio` },
    ],
    strategy: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Strategy Advisor', url: `${baseUrl}/strategy` },
    ],
    profiles: [
      { name: 'Home', url: `${baseUrl}/` },
      { name: 'Profiles', url: `${baseUrl}/profiles` },
    ],
  };

  return breadcrumbMap[pageName] || breadcrumbMap.landing;
};

export const validateTitleLength = (title: string): { valid: boolean; length: number; message?: string } => {
  const length = title.length;
  if (length < 30) {
    return { valid: false, length, message: 'Title is too short (minimum 30 characters)' };
  }
  if (length > 60) {
    return { valid: false, length, message: 'Title is too long (maximum 60 characters)' };
  }
  return { valid: true, length };
};

export const validateDescriptionLength = (description: string): { valid: boolean; length: number; message?: string } => {
  const length = description.length;
  if (length < 120) {
    return { valid: false, length, message: 'Description is too short (minimum 120 characters)' };
  }
  if (length > 160) {
    return { valid: false, length, message: 'Description is too long (maximum 160 characters)' };
  }
  return { valid: true, length };
};
