/**
 * Enhanced Social Media Mock Data
 * Comprehensive mock data for 14+ social media platforms
 */

export interface SocialPlatform {
    id: string;
    name: string;
    displayName: string;
    icon: string;
    color: string;
    category: 'social' | 'professional' | 'messaging' | 'content';
    isPopular: boolean;
}

export interface SocialAccount {
    id: string;
    platform: string;
    accountId: string;
    username: string;
    displayName: string;
    avatar: string;
    isConnected: boolean;
    isVerified: boolean;
    accountType: 'personal' | 'business' | 'creator';
    connectedAt?: string;
    lastSynced?: string;
    metrics: {
        followers: number;
        following: number;
        posts: number;
        engagement: number;
        reach?: number;
        impressions?: number;
    };
    recentPosts?: Array<{
        id: string;
        content: string;
        publishedAt: string;
        likes: number;
        comments: number;
        shares: number;
    }>;
}

// All supported platforms
export const SOCIAL_PLATFORMS: SocialPlatform[] = [
    {
        id: 'facebook',
        name: 'Facebook',
        displayName: 'Facebook',
        icon: '📘',
        color: '#1877F2',
        category: 'social',
        isPopular: true,
    },
    {
        id: 'instagram',
        name: 'Instagram',
        displayName: 'Instagram',
        icon: '📷',
        color: '#E4405F',
        category: 'social',
        isPopular: true,
    },
    {
        id: 'twitter',
        name: 'Twitter',
        displayName: 'X (Twitter)',
        icon: '🐦',
        color: '#1DA1F2',
        category: 'social',
        isPopular: true,
    },
    {
        id: 'linkedin',
        name: 'LinkedIn',
        displayName: 'LinkedIn',
        icon: '💼',
        color: '#0A66C2',
        category: 'professional',
        isPopular: true,
    },
    {
        id: 'tiktok',
        name: 'TikTok',
        displayName: 'TikTok',
        icon: '🎵',
        color: '#000000',
        category: 'content',
        isPopular: true,
    },
    {
        id: 'youtube',
        name: 'YouTube',
        displayName: 'YouTube',
        icon: '▶️',
        color: '#FF0000',
        category: 'content',
        isPopular: true,
    },
    {
        id: 'pinterest',
        name: 'Pinterest',
        displayName: 'Pinterest',
        icon: '📌',
        color: '#E60023',
        category: 'content',
        isPopular: false,
    },
    {
        id: 'whatsapp',
        name: 'WhatsApp',
        displayName: 'WhatsApp Business',
        icon: '💬',
        color: '#25D366',
        category: 'messaging',
        isPopular: true,
    },
    {
        id: 'telegram',
        name: 'Telegram',
        displayName: 'Telegram',
        icon: '✈️',
        color: '#0088CC',
        category: 'messaging',
        isPopular: false,
    },
    {
        id: 'discord',
        name: 'Discord',
        displayName: 'Discord',
        icon: '🎮',
        color: '#5865F2',
        category: 'messaging',
        isPopular: false,
    },
    {
        id: 'reddit',
        name: 'Reddit',
        displayName: 'Reddit',
        icon: '🤖',
        color: '#FF4500',
        category: 'social',
        isPopular: false,
    },
    {
        id: 'snapchat',
        name: 'Snapchat',
        displayName: 'Snapchat',
        icon: '👻',
        color: '#FFFC00',
        category: 'social',
        isPopular: false,
    },
    {
        id: 'threads',
        name: 'Threads',
        displayName: 'Threads',
        icon: '🧵',
        color: '#000000',
        category: 'social',
        isPopular: true,
    },
    {
        id: 'mastodon',
        name: 'Mastodon',
        displayName: 'Mastodon',
        icon: '🐘',
        color: '#6364FF',
        category: 'social',
        isPopular: false,
    },
];

// Mock connected accounts
export const MOCK_SOCIAL_ACCOUNTS: SocialAccount[] = [
    {
        id: 'acc-1',
        platform: 'instagram',
        accountId: 'ig-12345',
        username: '@mybusiness',
        displayName: 'My Business',
        avatar: 'https://i.pravatar.cc/150?img=1',
        isConnected: true,
        isVerified: true,
        accountType: 'business',
        connectedAt: '2024-01-15T10:00:00Z',
        lastSynced: '2026-01-15T12:00:00Z',
        metrics: {
            followers: 12500,
            following: 450,
            posts: 342,
            engagement: 4.2,
            reach: 45000,
            impressions: 125000,
        },
        recentPosts: [
            {
                id: 'post-1',
                content: 'Check out our latest product launch! 🚀',
                publishedAt: '2026-01-14T15:30:00Z',
                likes: 542,
                comments: 87,
                shares: 23,
            },
            {
                id: 'post-2',
                content: 'Behind the scenes of our creative process ✨',
                publishedAt: '2026-01-13T10:00:00Z',
                likes: 423,
                comments: 56,
                shares: 12,
            },
        ],
    },
    {
        id: 'acc-2',
        platform: 'facebook',
        accountId: 'fb-67890',
        username: 'mybusinesspage',
        displayName: 'My Business Page',
        avatar: 'https://i.pravatar.cc/150?img=2',
        isConnected: true,
        isVerified: false,
        accountType: 'business',
        connectedAt: '2024-02-01T08:00:00Z',
        lastSynced: '2026-01-15T11:30:00Z',
        metrics: {
            followers: 8900,
            following: 120,
            posts: 256,
            engagement: 3.8,
            reach: 32000,
            impressions: 89000,
        },
    },
    {
        id: 'acc-3',
        platform: 'linkedin',
        accountId: 'li-11223',
        username: 'john-doe',
        displayName: 'John Doe',
        avatar: 'https://i.pravatar.cc/150?img=3',
        isConnected: true,
        isVerified: false,
        accountType: 'personal',
        connectedAt: '2024-03-10T14:00:00Z',
        lastSynced: '2026-01-15T09:00:00Z',
        metrics: {
            followers: 3400,
            following: 890,
            posts: 145,
            engagement: 5.1,
        },
    },
    {
        id: 'acc-4',
        platform: 'twitter',
        accountId: 'tw-44556',
        username: '@mybiz',
        displayName: 'My Business',
        avatar: 'https://i.pravatar.cc/150?img=4',
        isConnected: true,
        isVerified: true,
        accountType: 'business',
        connectedAt: '2024-01-20T16:00:00Z',
        lastSynced: '2026-01-15T13:00:00Z',
        metrics: {
            followers: 15600,
            following: 234,
            posts: 1240,
            engagement: 2.9,
            reach: 67000,
        },
    },
];

// Mock disconnected platforms (available to connect)
export const AVAILABLE_PLATFORMS = SOCIAL_PLATFORMS.filter(
    (platform) => !MOCK_SOCIAL_ACCOUNTS.some((acc) => acc.platform === platform.id)
);

// Helper functions
export const getPlatformById = (id: string): SocialPlatform | undefined => {
    return SOCIAL_PLATFORMS.find((p) => p.id === id);
};

export const getAccountsByPlatform = (platformId: string): SocialAccount[] => {
    return MOCK_SOCIAL_ACCOUNTS.filter((acc) => acc.platform === platformId);
};

export const getConnectedAccounts = (): SocialAccount[] => {
    return MOCK_SOCIAL_ACCOUNTS.filter((acc) => acc.isConnected);
};

export const getTotalFollowers = (): number => {
    return MOCK_SOCIAL_ACCOUNTS.reduce((sum, acc) => sum + acc.metrics.followers, 0);
};

export const getAverageEngagement = (): number => {
    const accounts = MOCK_SOCIAL_ACCOUNTS.filter((acc) => acc.metrics.engagement);
    if (accounts.length === 0) return 0;
    const total = accounts.reduce((sum, acc) => sum + acc.metrics.engagement, 0);
    return Number((total / accounts.length).toFixed(1));
};

// Mock API functions
export const mockConnectPlatform = async (platformId: string): Promise<SocialAccount> => {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const platform = getPlatformById(platformId);
    if (!platform) {
        throw new Error('Platform not found');
    }

    // Create a new mock account
    const newAccount: SocialAccount = {
        id: `acc-${Date.now()}`,
        platform: platformId,
        accountId: `${platformId}-${Math.random().toString(36).substr(2, 9)}`,
        username: `@user_${Math.random().toString(36).substr(2, 5)}`,
        displayName: `${platform.displayName} Account`,
        avatar: `https://i.pravatar.cc/150?img=${Math.floor(Math.random() * 70)}`,
        isConnected: true,
        isVerified: false,
        accountType: 'business',
        connectedAt: new Date().toISOString(),
        lastSynced: new Date().toISOString(),
        metrics: {
            followers: Math.floor(Math.random() * 10000) + 1000,
            following: Math.floor(Math.random() * 1000) + 100,
            posts: Math.floor(Math.random() * 500) + 50,
            engagement: Number((Math.random() * 5 + 1).toFixed(1)),
        },
    };

    MOCK_SOCIAL_ACCOUNTS.push(newAccount);
    return newAccount;
};

export const mockDisconnectPlatform = async (accountId: string): Promise<void> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const index = MOCK_SOCIAL_ACCOUNTS.findIndex((acc) => acc.id === accountId);
    if (index !== -1) {
        MOCK_SOCIAL_ACCOUNTS.splice(index, 1);
    }
};

export const mockSyncAccount = async (accountId: string): Promise<SocialAccount> => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const account = MOCK_SOCIAL_ACCOUNTS.find((acc) => acc.id === accountId);
    if (!account) {
        throw new Error('Account not found');
    }

    // Update metrics slightly
    account.metrics.followers += Math.floor(Math.random() * 100);
    account.metrics.posts += Math.floor(Math.random() * 5);
    account.lastSynced = new Date().toISOString();

    return account;
};

export default {
    SOCIAL_PLATFORMS,
    MOCK_SOCIAL_ACCOUNTS,
    AVAILABLE_PLATFORMS,
    getPlatformById,
    getAccountsByPlatform,
    getConnectedAccounts,
    getTotalFollowers,
    getAverageEngagement,
    mockConnectPlatform,
    mockDisconnectPlatform,
    mockSyncAccount,
};
