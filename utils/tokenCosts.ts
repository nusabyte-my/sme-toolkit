export interface ImageCostParams {
  resolution: '512x512' | '1024x1024' | '2048x2048' | '4096x4096';
  quality: 'standard' | 'hd' | '4k';
}

export interface VideoCostParams {
  duration: '5s' | '15s' | '30s' | '60s';
  resolution: '480p' | '720p' | '1080p';
}

const IMAGE_BASE = 50;
const VIDEO_BASE = 200;

const IMAGE_RESOLUTION_MULTIPLIER: Record<string, number> = {
  '512x512': 0.5,
  '1024x1024': 1.0,
  '2048x2048': 2.0,
  '4096x4096': 4.0,
};

const IMAGE_QUALITY_MULTIPLIER: Record<string, number> = {
  standard: 1.0,
  hd: 2.0,
  '4k': 4.0,
};

const VIDEO_DURATION_MULTIPLIER: Record<string, number> = {
  '5s': 0.5,
  '15s': 1.0,
  '30s': 2.0,
  '60s': 4.0,
};

const VIDEO_RESOLUTION_MULTIPLIER: Record<string, number> = {
  '480p': 1.0,
  '720p': 1.5,
  '1080p': 2.0,
};

export function calculateImageCost(params: ImageCostParams): number {
  return Math.round(
    IMAGE_BASE *
    (IMAGE_RESOLUTION_MULTIPLIER[params.resolution] ?? 1.0) *
    (IMAGE_QUALITY_MULTIPLIER[params.quality] ?? 1.0)
  );
}

export function calculateVideoCost(params: VideoCostParams): number {
  return Math.round(
    VIDEO_BASE *
    (VIDEO_DURATION_MULTIPLIER[params.duration] ?? 1.0) *
    (VIDEO_RESOLUTION_MULTIPLIER[params.resolution] ?? 1.0)
  );
}

export const TOKEN_COSTS = {
  text_llm: 10,
  image_generation: calculateImageCost,
  video_generation: calculateVideoCost,
  agent_orchestration: 50,
  profile_analysis: 25,
} as const;

export function estimateCost(
  serviceType: string,
  params?: ImageCostParams | VideoCostParams
): number {
  const cost = TOKEN_COSTS[serviceType as keyof typeof TOKEN_COSTS];
  // Cost entries are either flat numbers or param-driven calculators.
  if (typeof cost === 'function') {
    return cost(params as never);
  }
  return cost ?? 10;
}
