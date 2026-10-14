/**
 * Performance Monitoring Utility
 * Tracks Web Vitals and provides performance metrics for the application
 */

export interface WebVitals {
  // Core Web Vitals
  LCP?: number; // Largest Contentful Paint (target: < 2.5s)
  FID?: number; // First Input Delay (target: < 100ms)
  CLS?: number; // Cumulative Layout Shift (target: < 0.1)
  
  // Other metrics
  FCP?: number; // First Contentful Paint
  TTFB?: number; // Time to First Byte
  TTI?: number; // Time to Interactive
}

export interface PerformanceMetrics {
  webVitals: WebVitals;
  navigationTiming: PerformanceNavigationTiming | null;
  resourceTiming: PerformanceResourceTiming[];
  memoryUsage?: {
    usedJSHeapSize: number;
    totalJSHeapSize: number;
    jsHeapSizeLimit: number;
  };
}

/**
 * Measure Largest Contentful Paint (LCP)
 */
const measureLCP = (): Promise<number> => {
  return new Promise((resolve) => {
    if (!('PerformanceObserver' in window)) {
      resolve(0);
      return;
    }

    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;
        resolve(lastEntry?.startTime || 0);
        observer.disconnect();
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (error) {
      console.warn('LCP measurement failed:', error);
      resolve(0);
    }
  });
};

/**
 * Measure First Input Delay (FID)
 */
const measureFID = (): Promise<number> => {
  return new Promise((resolve) => {
    if (!('PerformanceObserver' in window)) {
      resolve(0);
      return;
    }

    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const firstEntry = entries[0] as any;
        resolve(firstEntry?.processingStart - firstEntry?.startTime || 0);
        observer.disconnect();
      });

      observer.observe({ entryTypes: ['first-input'] });
    } catch (error) {
      console.warn('FID measurement failed:', error);
      resolve(0);
    }
  });
};

/**
 * Measure Cumulative Layout Shift (CLS)
 */
const measureCLS = (): Promise<number> => {
  return new Promise((resolve) => {
    if (!('PerformanceObserver' in window)) {
      resolve(0);
      return;
    }

    try {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
      });

      observer.observe({ entryTypes: ['layout-shift'] });

      // Resolve after 5 seconds
      setTimeout(() => {
        observer.disconnect();
        resolve(clsValue);
      }, 5000);
    } catch (error) {
      console.warn('CLS measurement failed:', error);
      resolve(0);
    }
  });
};

/**
 * Measure First Contentful Paint (FCP)
 */
const measureFCP = (): number => {
  if (!('PerformanceObserver' in window)) {
    return 0;
  }

  try {
    const entries = performance.getEntriesByName('first-contentful-paint', 'paint');
    return entries[0]?.startTime || 0;
  } catch (error) {
    console.warn('FCP measurement failed:', error);
    return 0;
  }
};

/**
 * Measure Time to First Byte (TTFB)
 */
const measureTTFB = (): number => {
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  if (!navigation) return 0;
  return navigation.responseStart - navigation.requestStart;
};

/**
 * Measure Time to Interactive (TTI)
 */
const measureTTI = (): Promise<number> => {
  return new Promise((resolve) => {
    if (!('PerformanceObserver' in window)) {
      resolve(0);
      return;
    }

    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const longTasks = entries.filter((entry: any) => entry.duration > 50);
        
        if (longTasks.length === 0) {
          const fcp = measureFCP();
          resolve(fcp + 100); // Approximate TTI
          observer.disconnect();
        }
      });

      observer.observe({ entryTypes: ['longtask'] });

      // Fallback: resolve after 3 seconds
      setTimeout(() => {
        observer.disconnect();
        const fcp = measureFCP();
        resolve(fcp + 100);
      }, 3000);
    } catch (error) {
      console.warn('TTI measurement failed:', error);
      resolve(0);
    }
  });
};

/**
 * Get navigation timing
 */
const getNavigationTiming = (): PerformanceNavigationTiming | null => {
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  return navigation || null;
};

/**
 * Get resource timing
 */
const getResourceTiming = (): PerformanceResourceTiming[] => {
  return performance.getEntriesByType('resource') as PerformanceResourceTiming[];
};

/**
 * Get memory usage (Chrome only)
 */
const getMemoryUsage = () => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    return {
      usedJSHeapSize: memory.usedJSHeapSize,
      totalJSHeapSize: memory.totalJSHeapSize,
      jsHeapSizeLimit: memory.jsHeapSizeLimit,
    };
  }
  return undefined;
};

/**
 * Collect all performance metrics
 */
export const collectPerformanceMetrics = async (): Promise<PerformanceMetrics> => {
  const [lcp, fid, cls, tti] = await Promise.all([
    measureLCP(),
    measureFID(),
    measureCLS(),
    measureTTI(),
  ]);

  return {
    webVitals: {
      LCP: lcp,
      FID: fid,
      CLS: cls,
      FCP: measureFCP(),
      TTFB: measureTTFB(),
      TTI: tti,
    },
    navigationTiming: getNavigationTiming(),
    resourceTiming: getResourceTiming(),
    memoryUsage: getMemoryUsage(),
  };
};

/**
 * Log performance metrics to console
 */
export const logPerformanceMetrics = async (): Promise<void> => {
  const metrics = await collectPerformanceMetrics();
  
  console.group('📊 Performance Metrics');
  
  console.group('Core Web Vitals');
  console.log(`LCP (Largest Contentful Paint): ${metrics.webVitals.LCP?.toFixed(0)}ms ${metrics.webVitals.LCP && metrics.webVitals.LCP < 2500 ? '✅' : '⚠️'}`);
  console.log(`FID (First Input Delay): ${metrics.webVitals.FID?.toFixed(0)}ms ${metrics.webVitals.FID && metrics.webVitals.FID < 100 ? '✅' : '⚠️'}`);
  console.log(`CLS (Cumulative Layout Shift): ${metrics.webVitals.CLS?.toFixed(3)} ${metrics.webVitals.CLS && metrics.webVitals.CLS < 0.1 ? '✅' : '⚠️'}`);
  console.groupEnd();
  
  console.group('Other Metrics');
  console.log(`FCP (First Contentful Paint): ${metrics.webVitals.FCP?.toFixed(0)}ms`);
  console.log(`TTFB (Time to First Byte): ${metrics.webVitals.TTFB?.toFixed(0)}ms`);
  console.log(`TTI (Time to Interactive): ${metrics.webVitals.TTI?.toFixed(0)}ms`);
  console.groupEnd();
  
  if (metrics.memoryUsage) {
    console.group('Memory Usage');
    console.log(`Used JS Heap: ${(metrics.memoryUsage.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`Total JS Heap: ${(metrics.memoryUsage.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`JS Heap Limit: ${(metrics.memoryUsage.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`);
    console.groupEnd();
  }
  
  console.groupEnd();
};

/**
 * Send performance metrics to analytics service
 */
export const sendPerformanceMetrics = async (analyticsEndpoint?: string): Promise<void> => {
  const metrics = await collectPerformanceMetrics();
  
  if (analyticsEndpoint) {
    try {
      await fetch(analyticsEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metrics),
      });
    } catch (error) {
      console.warn('Failed to send performance metrics:', error);
    }
  }
};

/**
 * Initialize performance monitoring
 */
export const initPerformanceMonitoring = (options: {
  logToConsole?: boolean;
  sendToAnalytics?: boolean;
  analyticsEndpoint?: string;
  autoReport?: boolean;
} = {}): void => {
  const {
    logToConsole = true,
    sendToAnalytics = false,
    analyticsEndpoint,
    autoReport = false,
  } = options;

  // Wait for page to load
  if (document.readyState === 'complete') {
    collectAndReportMetrics(logToConsole, sendToAnalytics, analyticsEndpoint);
  } else {
    window.addEventListener('load', () => {
      collectAndReportMetrics(logToConsole, sendToAnalytics, analyticsEndpoint);
    });
  }

  // Auto-report on route changes (if using client-side routing)
  if (autoReport) {
    let lastUrl = window.location.href;
    
    const observer = new MutationObserver(() => {
      if (window.location.href !== lastUrl) {
        lastUrl = window.location.href;
        setTimeout(() => {
          collectAndReportMetrics(logToConsole, sendToAnalytics, analyticsEndpoint);
        }, 1000);
      }
    });
    
    observer.observe(document.body, {
      subtree: true,
      childList: true,
    });
  }
};

/**
 * Collect and report metrics
 */
const collectAndReportMetrics = async (
  logToConsole: boolean,
  sendToAnalytics: boolean,
  analyticsEndpoint?: string
): Promise<void> => {
  if (logToConsole) {
    await logPerformanceMetrics();
  }
  
  if (sendToAnalytics && analyticsEndpoint) {
    await sendPerformanceMetrics(analyticsEndpoint);
  }
};

/**
 * Measure custom performance mark
 */
export const markPerformance = (name: string): void => {
  if ('performance' in window && 'mark' in performance) {
    performance.mark(name);
  }
};

/**
 * Measure performance between two marks
 */
export const measurePerformance = (name: string, startMark: string, endMark: string): number => {
  if ('performance' in window && 'measure' in performance) {
    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name)[0];
      return measure?.duration || 0;
    } catch (error) {
      console.warn('Performance measurement failed:', error);
      return 0;
    }
  }
  return 0;
};

/**
 * Clear performance marks and measures
 */
export const clearPerformanceMarks = (names?: string[]): void => {
  if ('performance' in window && 'clearMarks' in performance) {
    if (names) {
      names.forEach(n => performance.clearMarks(n));
    } else {
      performance.clearMarks();
    }
  }
  if ('performance' in window && 'clearMeasures' in performance) {
    if (names) {
      names.forEach(n => performance.clearMeasures(n));
    } else {
      performance.clearMeasures();
    }
  }
};

/**
 * Get performance score (0-100)
 */
export const getPerformanceScore = async (): Promise<number> => {
  const metrics = await collectPerformanceMetrics();
  
  let score = 100;
  
  // LCP score (0-40 points)
  if (metrics.webVitals.LCP) {
    if (metrics.webVitals.LCP < 2500) {
      score -= 0;
    } else if (metrics.webVitals.LCP < 4000) {
      score -= 20;
    } else {
      score -= 40;
    }
  }
  
  // FID score (0-30 points)
  if (metrics.webVitals.FID) {
    if (metrics.webVitals.FID < 100) {
      score -= 0;
    } else if (metrics.webVitals.FID < 300) {
      score -= 15;
    } else {
      score -= 30;
    }
  }
  
  // CLS score (0-30 points)
  if (metrics.webVitals.CLS) {
    if (metrics.webVitals.CLS < 0.1) {
      score -= 0;
    } else if (metrics.webVitals.CLS < 0.25) {
      score -= 15;
    } else {
      score -= 30;
    }
  }
  
  return Math.max(0, score);
};

/**
 * Export performance metrics as JSON
 */
export const exportPerformanceMetrics = async (): Promise<string> => {
  const metrics = await collectPerformanceMetrics();
  return JSON.stringify(metrics, null, 2);
};
