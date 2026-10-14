export interface AdProfileInput {
  name: string;
  product: string;
  offer: string;
  audience: string;
  voice: string;
  channel: "Meta" | "Google" | "TikTok" | "LinkedIn" | "Other";
  cta: string;
  landing_url: string;
  language: string;
  prohibited_claims: string;
  brand_color: string;
}
export interface AdProfile extends AdProfileInput {
  id: string;
  created_at: string;
  updated_at: string;
}
export interface ImageStyle {
  brightness: number;
  contrast: number;
  saturation: number;
  grayscale: number;
  blur: number;
  rotation: 0 | 90 | 180 | 270;
  flip_x: boolean;
  zoom: number;
  focal_x: number;
  focal_y: number;
  overlay: number;
  text_x: number;
  text_y: number;
  font_scale: number;
  text_color: string;
}
export interface CreativeLayer {
  id: string;
  type: "text" | "rectangle";
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  font_size: number;
  color: string;
  opacity: number;
  visible: boolean;
}
export interface VideoScene {
  id: string;
  caption: string;
  duration: number;
  source_start: number;
  asset_id: string | null;
  transition: "cut" | "fade";
}
export interface AdDraftInput {
  profile_id: string;
  title: string;
  headline: string;
  body: string;
  cta: string;
  image_prompt: string;
  video_prompt: string;
  script: string;
  aspect_ratio: "1:1" | "4:5" | "9:16" | "16:9";
  duration: number;
  asset_id: string | null;
  video_asset_id: string | null;
  image_style?: ImageStyle;
  layers?: CreativeLayer[];
  scenes?: VideoScene[];
  audio_asset_id?: string | null;
  audio_volume?: number;
  source_volume?: number;
  copy_framework?: "AIDA" | "PAS" | "BAB" | "Direct";
  copy_variants?: string[];
}
export interface AdDraft extends AdDraftInput {
  id: string;
  status: "draft" | "approved";
  profile_snapshot: AdProfileInput;
  created_at: string;
  updated_at: string;
}
export interface AdAsset {
  id: string;
  name: string;
  mime: string;
  created_at: string;
}
export interface AdVideoJob {
  id: string;
  status: "submitting" | "processing" | "completed" | "failed";
  error: string | null;
  asset_id: string | null;
  prompt: string;
  created_at: string;
}
export interface AdsLibrary {
  profiles: AdProfile[];
  drafts: AdDraft[];
  assets: AdAsset[];
  jobs: AdVideoJob[];
  capabilities: {
    ai_available: boolean;
    ai_provider: string | null;
    image_available: boolean;
    video_available: boolean;
    image_model: string;
    video_model: string;
    mp4_available: boolean;
  };
}
