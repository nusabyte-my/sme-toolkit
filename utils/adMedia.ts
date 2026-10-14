import type {
  AdDraftInput,
  AdProfileInput,
  ImageStyle,
  VideoScene,
} from "../types/ads";
import { authenticatedFetch } from "../services/apiClient";

export const defaultImageStyle: ImageStyle = {
  brightness: 100,
  contrast: 100,
  saturation: 100,
  grayscale: 0,
  blur: 0,
  rotation: 0,
  flip_x: false,
  zoom: 1,
  focal_x: 50,
  focal_y: 50,
  overlay: 0.75,
  text_x: 6.5,
  text_y: 47,
  font_scale: 1,
  text_color: "#FFFFFF",
};

export function drawAdFrame(
  canvas: HTMLCanvasElement,
  draft: AdDraftInput,
  profile: AdProfileInput,
  source: HTMLImageElement | HTMLVideoElement | null,
  scene?: string,
  opacity = 1,
) {
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Canvas rendering unavailable.");
  const sizes = {
    "1:1": [1080, 1080],
    "4:5": [1080, 1350],
    "9:16": [1080, 1920],
    "16:9": [1920, 1080],
  } as const;
  const [width, height] = sizes[draft.aspect_ratio];
  if (canvas.width !== width) canvas.width = width;
  if (canvas.height !== height) canvas.height = height;
  const style = { ...defaultImageStyle, ...draft.image_style };
  const pad = width * 0.065;
  ctx.fillStyle = profile.brand_color;
  ctx.fillRect(0, 0, width, height);
  if (source) {
    const sw =
        source instanceof HTMLVideoElement
          ? source.videoWidth
          : source.naturalWidth,
      sh =
        source instanceof HTMLVideoElement
          ? source.videoHeight
          : source.naturalHeight;
    if (sw && sh) {
      const rotated = style.rotation % 180 !== 0;
      const scale =
        Math.max(width / (rotated ? sh : sw), height / (rotated ? sw : sh)) *
        style.zoom;
      ctx.save();
      ctx.translate(
        width / 2 + ((50 - style.focal_x) / 100) * width,
        height / 2 + ((50 - style.focal_y) / 100) * height,
      );
      ctx.rotate((style.rotation * Math.PI) / 180);
      ctx.scale(style.flip_x ? -1 : 1, 1);
      ctx.filter = `brightness(${style.brightness}%) contrast(${style.contrast}%) saturate(${style.saturation}%) grayscale(${style.grayscale}%) blur(${style.blur}px)`;
      ctx.drawImage(
        source,
        (-sw * scale) / 2,
        (-sh * scale) / 2,
        sw * scale,
        sh * scale,
      );
      ctx.restore();
    }
  }
  const shade = ctx.createLinearGradient(0, 0, 0, height);
  shade.addColorStop(0, `rgba(0,0,0,${style.overlay * 0.2})`);
  shade.addColorStop(1, `rgba(0,0,0,${style.overlay})`);
  ctx.fillStyle = shade;
  ctx.fillRect(0, 0, width, height);
  ctx.textBaseline = "top";
  ctx.fillStyle = style.text_color;
  ctx.font = `600 ${width * 0.025}px Inter,sans-serif`;
  ctx.fillText(profile.name, pad, pad, width - pad * 2);
  const headline = scene ?? draft.headline ?? profile.product;
  const x = (width * style.text_x) / 100;
  const available = width - x - pad;
  let fontSize = width * 0.064 * style.font_scale;
  let lines: string[] = [];
  do {
    ctx.font = `700 ${fontSize}px "Space Grotesk",sans-serif`;
    lines = [];
    let line = "";
    for (const word of headline.split(/\s+/)) {
      const next = line ? `${line} ${word}` : word;
      if (ctx.measureText(next).width > available && line) {
        lines.push(line);
        line = word;
      } else line = next;
    }
    if (line) lines.push(line);
    if (lines.length * fontSize * 1.16 <= height * 0.32) break;
    fontSize -= 2;
  } while (fontSize > 24);
  ctx.globalAlpha = opacity;
  ctx.font = `700 ${fontSize}px "Space Grotesk",sans-serif`;
  let y = (height * style.text_y) / 100;
  for (const line of lines) {
    ctx.fillText(line, x, y, available);
    y += fontSize * 1.16;
  }
  ctx.globalAlpha = 1;
  const cta = draft.cta || profile.cta;
  if (cta) {
    ctx.font = `600 ${width * 0.03}px Inter,sans-serif`;
    const boxWidth = Math.min(
      width - pad * 2,
      ctx.measureText(cta).width + pad,
    );
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(pad, height - pad * 2.2, boxWidth, pad * 0.9);
    ctx.fillStyle = "#16101F";
    ctx.fillText(cta, pad * 1.5, height - pad * 1.97, boxWidth - pad);
  }
  ctx.fillStyle = style.text_color;
  ctx.font = `400 ${width * 0.019}px Inter,sans-serif`;
  ctx.fillText(profile.landing_url, pad, height - pad * 0.6, width - pad * 2);
  for (const layer of draft.layers || []) {
    if (!layer.visible) continue;
    ctx.save();
    ctx.globalAlpha = layer.opacity;
    ctx.fillStyle = layer.color;
    if (layer.type === "rectangle")
      ctx.fillRect(
        (width * layer.x) / 100,
        (height * layer.y) / 100,
        (width * layer.width) / 100,
        (height * layer.height) / 100,
      );
    else {
      ctx.font = `600 ${(width * layer.font_size) / 100}px Inter,sans-serif`;
      let offset = 0;
      for (const line of layer.text.split("\n")) {
        ctx.fillText(
          line,
          (width * layer.x) / 100,
          (height * layer.y) / 100 + offset,
          (width * layer.width) / 100,
        );
        offset += ((width * layer.font_size) / 100) * 1.2;
      }
    }
    ctx.restore();
  }
}

export async function renderMotionAd(
  canvas: HTMLCanvasElement,
  draft: AdDraftInput,
  profile: AdProfileInput,
  image: HTMLImageElement | null,
  video: HTMLVideoElement | null,
  onProgress: (progress: number) => void,
  signal: AbortSignal,
): Promise<Blob> {
  if (!canvas.captureStream || typeof MediaRecorder === "undefined")
    throw new Error(
      "Use current desktop Chrome or Edge for native video rendering.",
    );
  const mime = [
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm",
  ].find((type) => MediaRecorder.isTypeSupported(type));
  if (!mime) throw new Error("WebM recording unavailable.");
  const scenes: VideoScene[] = draft.scenes?.length
    ? draft.scenes
    : draft.script
        .split("\n")
        .filter(Boolean)
        .map((caption, i, rows) => ({
          id: String(i),
          caption,
          duration: draft.duration / rows.length,
          source_start: 0,
          asset_id: null,
          transition: "cut",
        }));
  if (!scenes.length)
    scenes.push({
      id: "default",
      caption: draft.headline || profile.product,
      duration: draft.duration,
      source_start: 0,
      asset_id: null,
      transition: "cut",
    });
  const duration = scenes.reduce((sum, scene) => sum + scene.duration, 0);
  if (!Number.isFinite(duration) || duration <= 0 || duration > 120)
    throw new Error("Timeline must be between 0 and 120 seconds.");
  if (
    scenes.some(
      (scene) =>
        !Number.isFinite(scene.duration) ||
        scene.duration < 0.5 ||
        scene.duration > 30 ||
        !Number.isFinite(scene.source_start) ||
        scene.source_start < 0,
    )
  )
    throw new Error(
      "Each scene needs a 0.5–30 second duration and a valid trim start.",
    );
  const loaded = new Map<string, HTMLImageElement | HTMLVideoElement>();
  const urls: string[] = [];
  const sources: HTMLMediaElement[] = [];
  let audioContext: AudioContext | null = null;
  let soundtrack: HTMLAudioElement | null = null;
  let stream: MediaStream | null = null;
  let timer: number | undefined;
  let workingVideo: HTMLVideoElement | null = null;
  try {
    if (video) {
      workingVideo = document.createElement("video");
      workingVideo.preload = "auto";
      workingVideo.playsInline = true;
      await new Promise<void>((resolve, reject) => {
        workingVideo!.onloadeddata = () => resolve();
        workingVideo!.onerror = () =>
          reject(new Error("Source video could not be decoded."));
        workingVideo!.src = video.currentSrc || video.src;
      });
    }
    for (const id of [
      ...new Set(
        scenes
          .map((scene) => scene.asset_id)
          .filter((id): id is string => !!id),
      ),
    ]) {
      if (signal.aborted) throw new Error("Rendering cancelled.");
      const blob = await (
        await authenticatedFetch(`/api/v1/ads/assets/${id}`)
      ).blob();
      const url = URL.createObjectURL(blob);
      urls.push(url);
      const element = blob.type.startsWith("video/")
        ? document.createElement("video")
        : new Image();
      await new Promise<void>((resolve, reject) => {
        if (element instanceof HTMLVideoElement) {
          element.onloadeddata = () => resolve();
          element.onerror = () =>
            reject(new Error("A timeline video could not be decoded."));
          element.preload = "auto";
          element.playsInline = true;
        } else {
          element.onload = () => resolve();
          element.onerror = () =>
            reject(new Error("A timeline image could not be decoded."));
        }
        element.src = url;
      });
      loaded.set(id, element);
    }
    if (draft.audio_asset_id) {
      const blob = await (
        await authenticatedFetch(`/api/v1/ads/assets/${draft.audio_asset_id}`)
      ).blob();
      const url = URL.createObjectURL(blob);
      urls.push(url);
      soundtrack = new Audio(url);
      soundtrack.loop = true;
      await new Promise<void>((resolve, reject) => {
        soundtrack!.onloadeddata = () => resolve();
        soundtrack!.onerror = () =>
          reject(new Error("Soundtrack could not be decoded."));
      });
    }
    const videos = [
      ...new Set(
        [workingVideo, ...loaded.values()].filter(
          (item): item is HTMLVideoElement => item instanceof HTMLVideoElement,
        ),
      ),
    ];
    sources.push(...videos);
    if (soundtrack) sources.push(soundtrack);
    const withAudio = !!soundtrack || (draft.source_volume || 0) > 0;
    let audioDestination: MediaStreamAudioDestinationNode | undefined;
    if (withAudio) {
      audioContext = new AudioContext();
      await audioContext.resume();
      audioDestination = audioContext.createMediaStreamDestination();
      for (const media of sources) {
        const input = audioContext.createMediaElementSource(media);
        const gain = audioContext.createGain();
        gain.gain.value =
          media === soundtrack
            ? (draft.audio_volume ?? 0.5)
            : (draft.source_volume ?? 0);
        input.connect(gain);
        gain.connect(audioDestination);
        media.muted = false;
      }
    } else videos.forEach((v) => (v.muted = true));
    const ends: number[] = [];
    let total = 0;
    scenes.forEach((scene) => {
      total += scene.duration;
      ends.push(total);
    });
    let activeIndex = -1;
    let activeSource: HTMLImageElement | HTMLVideoElement | null = null;
    const activate = async (index: number) => {
      if (activeSource instanceof HTMLVideoElement) activeSource.pause();
      const scene = scenes[index];
      activeSource = scene.asset_id
        ? loaded.get(scene.asset_id) || null
        : workingVideo || image;
      if (activeSource instanceof HTMLVideoElement) {
        if (
          Number.isFinite(activeSource.duration) &&
          scene.source_start + scene.duration > activeSource.duration + 0.05
        )
          throw new Error(
            `Scene ${index + 1} exceeds the source video. Adjust trim start or duration.`,
          );
        activeSource.currentTime = scene.source_start;
        activeSource.loop = false;
        await activeSource.play();
      }
      activeIndex = index;
    };
    await activate(0);
    drawAdFrame(canvas, draft, profile, activeSource, scenes[0].caption);
    stream = canvas.captureStream(24);
    audioDestination?.stream
      .getAudioTracks()
      .forEach((track) => stream!.addTrack(track));
    const recorder = new MediaRecorder(stream, {
      mimeType: mime,
      videoBitsPerSecond: 4_000_000,
    });
    const chunks: Blob[] = [];
    return await new Promise<Blob>((resolve, reject) => {
      let failed = false;
      const stop = () => {
        clearInterval(timer);
        if (recorder.state !== "inactive") recorder.stop();
      };
      const abort = () => {
        failed = true;
        stop();
        reject(new Error("Rendering cancelled."));
      };
      signal.addEventListener("abort", abort, { once: true });
      recorder.ondataavailable = (event) => {
        if (event.data.size) chunks.push(event.data);
      };
      recorder.onerror = () => {
        failed = true;
        stop();
        reject(new Error("Video recorder failed."));
      };
      recorder.onstop = () => {
        signal.removeEventListener("abort", abort);
        if (!failed) {
          const blob = new Blob(chunks, { type: "video/webm" });
          if (!blob.size) reject(new Error("Video is empty."));
          else resolve(blob);
        }
      };
      recorder.start(250);
      soundtrack?.play().catch(() => {
        failed = true;
        stop();
        reject(
          new Error(
            "Soundtrack playback was blocked. Retry from a user click.",
          ),
        );
      });
      let started = performance.now();
      let switching = false;
      timer = window.setInterval(async () => {
        if (switching) return;
        const elapsed = (performance.now() - started) / 1000;
        if (elapsed >= duration) {
          onProgress(100);
          stop();
          return;
        }
        const index = ends.findIndex((end) => elapsed < end);
        if (index !== activeIndex) {
          switching = true;
          const pauseStart = performance.now();
          try {
            await activate(index);
            started += performance.now() - pauseStart;
          } catch (err) {
            failed = true;
            stop();
            reject(err);
            return;
          } finally {
            switching = false;
          }
        }
        const local = elapsed - (index ? ends[index - 1] : 0);
        const opacity =
          scenes[index].transition === "fade" ? Math.min(1, local / 0.35) : 1;
        drawAdFrame(
          canvas,
          draft,
          profile,
          activeSource,
          scenes[index].caption,
          opacity,
        );
        onProgress(Math.floor((elapsed / duration) * 100));
      }, 1000 / 24);
      if (signal.aborted) abort();
    });
  } finally {
    clearInterval(timer);
    sources.forEach((media) => media.pause());
    stream?.getTracks().forEach((track) => track.stop());
    await audioContext?.close();
    urls.forEach((url) => URL.revokeObjectURL(url));
  }
}
