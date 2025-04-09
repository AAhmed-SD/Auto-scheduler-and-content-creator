export interface User {
  id: string;
  email: string;
  name: string;
  photoURL?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface SocialMediaMetrics {
  platform: string;
  followers: number;
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    saves: number;
  };
  reach: {
    organic: number;
    paid: number;
    viral: number;
  };
  growth: {
    newFollowers: number;
    unfollowers: number;
    netGrowth: number;
  };
  topPosts: {
    id: string;
    type: string;
    engagement: number;
    reach: number;
    date: Date;
  }[];
  lastUpdated: Date;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  isPrivate: boolean;
  allowedUsers: string[];
  settings: {
    [key: string]: any;
  };
  socialMedia: {
    [platform: string]: {
      connected: boolean;
      credentials?: {
        [key: string]: string;
      };
      lastSync: Date;
    };
  };
  analyticsSettings: {
    autoSync: boolean;
    syncFrequency: 'daily' | 'weekly' | 'monthly';
    metricsToTrack: string[];
    customMetrics?: {
      [key: string]: {
        name: string;
        formula: string;
      };
    };
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface Content {
  id: string;
  projectId: string;
  type: 'text' | 'image' | 'video';
  content: string;
  metadata: {
    [key: string]: any;
  };
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  scheduledFor?: Date;
  publishedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface Schedule {
  id: string;
  projectId: string;
  platform: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  time: string;
  timezone: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Analytics {
  id: string;
  projectId: string;
  contentId: string;
  platform: string;
  metrics: {
    [key: string]: number;
  };
  date: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface AnalyticsDashboard {
  id: string;
  userId: string;
  selectedProjects: string[];
  viewSettings: {
    defaultView: 'overview' | 'project' | 'comparison';
    timeRange: '7d' | '30d' | '90d' | 'custom';
    metricsDisplay: string[];
    chartPreferences: {
      [key: string]: any;
    };
  };
  lastViewed: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface AnalyticsReport {
  id: string;
  projectIds: string[];
  period: {
    start: Date;
    end: Date;
  };
  summary: {
    totalPosts: number;
    totalEngagement: number;
    averageEngagement: number;
    bestPerformingPost: {
      id: string;
      projectId: string;
      engagement: number;
    };
    worstPerformingPost: {
      id: string;
      projectId: string;
      engagement: number;
    };
    followerGrowth: number;
    reachGrowth: number;
  };
  projectBreakdown: {
    [projectId: string]: {
      name: string;
      posts: number;
      engagement: number;
      reach: number;
      growth: number;
      platformBreakdown: {
        [platform: string]: {
          posts: number;
          engagement: number;
          reach: number;
          growth: number;
        };
      };
      contentTypeBreakdown: {
        [type: string]: {
          count: number;
          averageEngagement: number;
        };
      };
    };
  };
  trends: {
    engagement: number[];
    reach: number[];
    growth: number[];
  };
  recommendations: {
    bestPostingTimes: string[];
    bestContentTypes: string[];
    suggestedImprovements: string[];
    projectSpecific: {
      [projectId: string]: {
        improvements: string[];
        opportunities: string[];
      };
    };
  };
  createdAt: Date;
  updatedAt: Date;
} 