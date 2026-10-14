import { useCallback, useEffect, useRef, useState } from "react";
import {
  Download,
  ImagePlus,
  Megaphone,
  Play,
  Save,
  Sparkles,
  Video,
  X,
} from "lucide-react";
import { useOwner } from "../../contexts/OwnerContext";
import WorkspaceLoading from '../common/WorkspaceLoading';
import { apiCall, authenticatedFetch } from "../../services/apiClient";
import {
  drawAdFrame,
  renderMotionAd,
  defaultImageStyle,
} from "../../utils/adMedia";
import type {
  AdProfileInput,
  AdProfile,
  AdDraftInput,
  AdDraft,
  AdAsset,
  AdsLibrary,
  AdVideoJob,
} from "../../types/ads";
import type { AgentRun } from "../../types/owner";
import { useUnsavedChanges } from "../../hooks/useUnsavedChanges";
import ImageControls from "./ImageControls";
import VideoControls from "./VideoControls";
import CopyControls from "./CopyControls";
import type { VideoScene } from "../../types/ads";

const blankProfile: AdProfileInput = {
  name: "",
  product: "",
  offer: "",
  audience: "",
  voice: "",
  channel: "Meta",
  cta: "",
  landing_url: "",
  language: "English",
  prohibited_claims: "",
  brand_color: "#7C3AED",
};
const blankDraft: AdDraftInput = {
  profile_id: "",
  title: "",
  headline: "",
  body: "",
  cta: "",
  image_prompt: "",
  video_prompt: "",
  script: "",
  aspect_ratio: "1:1",
  duration: 6,
  asset_id: null,
  video_asset_id: null,
};

export default function AdsStudio({
  initialTab = "profile",
}: {
  initialTab?: "profile" | "copy" | "image" | "video";
}) {
  const { overview, refresh: refreshOwner } = useOwner();
  const [library, setLibrary] = useState<AdsLibrary | null>(null);
  const [profile, setProfile] = useState<AdProfileInput>(blankProfile),
    [profileId, setProfileId] = useState("");
  const [draft, setDraft] = useState<AdDraftInput>(blankDraft),
    [draftId, setDraftId] = useState("");
  const [tab, setTab] = useState<"profile" | "copy" | "image" | "video">(
    initialTab,
  );
  const [busy, setBusy] = useState(""),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const [dirty, setDirty] = useState(false),
    [profileDirty, setProfileDirty] = useState(false),
    [progress, setProgress] = useState(0);
  const [image, setImage] = useState<HTMLImageElement | null>(null),
    [sourceVideo, setSourceVideo] = useState<HTMLVideoElement | null>(null);
  const [imageUrl, setImageUrl] = useState(""),
    [videoUrl, setVideoUrl] = useState("");
  const [rendered, setRendered] = useState<Blob | null>(null),
    [renderUrl, setRenderUrl] = useState("");
  const canvas = useRef<HTMLCanvasElement>(null),
    renderController = useRef<AbortController | null>(null),
    mounted = useRef(true);
  const request = useRef(0);
  const previewRequest = useRef(0);
  const [history, setHistory] = useState<AdDraftInput[]>([]);
  const [future, setFuture] = useState<AdDraftInput[]>([]);
  const [assetSearch, setAssetSearch] = useState("");
  const [selectedLayer, setSelectedLayer] = useState('headline');
  const [canvasZoom, setCanvasZoom] = useState(100);
  const [showLibrary, setShowLibrary] = useState(false);
  const drag = useRef<{draft:AdDraftInput;id:string;x:number;y:number;originX:number;originY:number}|null>(null);
  const context = overview?.context;
  const reload = useCallback(async () => {
    const id = ++request.current;
    const next = await apiCall<AdsLibrary>("/api/v1/ads/");
    if (mounted.current && id === request.current) setLibrary(next);
    return next;
  }, []);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      request.current++;
      renderController.current?.abort();
    };
  }, []);
  useEffect(() => {
    if (context)
      void reload().catch((err) =>
        setError(
          err instanceof Error
            ? err.message
            : "Ads library could not be loaded.",
        ),
      );
  }, [context?.id, reload]);
  useEffect(() => {
    if (context && !profileId && !profileDirty)
      setProfile({
        ...blankProfile,
        name: context.company_name,
        product: context.products_services,
        audience: context.target_market,
        voice: context.brand_voice,
        landing_url: context.website,
      });
  }, [context, profileId, profileDirty]);
  useUnsavedChanges(dirty || profileDirty || !!busy);
  useEffect(() => {
    let active = true;
    let url = "";
    setImage(null);
    setImageUrl("");
    if (draft.asset_id)
      authenticatedFetch(`/api/v1/ads/assets/${draft.asset_id}`)
        .then((r) => r.blob())
        .then((blob) => {
          if (!active) return;
          url = URL.createObjectURL(blob);
          const img = new Image();
          img.onload = () => {
            if (active) {
              setImage(img);
              setImageUrl(url);
            }
          };
          img.onerror = () => {
            if (active)
              setError(
                "This image could not be decoded. Choose a PNG, JPEG or WebP asset.",
              );
          };
          img.src = url;
        })
        .catch((err) => {
          if (active) setError(err.message);
        });
    return () => {
      active = false;
      if (url) URL.revokeObjectURL(url);
    };
  }, [draft.asset_id]);
  useEffect(() => {
    let active = true;
    let url = "";
    setSourceVideo(null);
    setVideoUrl("");
    if (draft.video_asset_id)
      authenticatedFetch(`/api/v1/ads/assets/${draft.video_asset_id}`)
        .then((r) => r.blob())
        .then((blob) => {
          if (!active) return;
          url = URL.createObjectURL(blob);
          const video = document.createElement("video");
          video.muted = true;
          video.playsInline = true;
          video.preload = "auto";
          video.onloadeddata = () => {
            if (active) {
              setSourceVideo(video);
              setVideoUrl(url);
            }
          };
          video.onerror = () => {
            if (active)
              setError(
                "This video could not be decoded. Choose a supported MP4 or WebM.",
              );
          };
          video.src = url;
        })
        .catch((err) => {
          if (active) setError(err.message);
        });
    return () => {
      active = false;
      if (url) URL.revokeObjectURL(url);
    };
  }, [draft.video_asset_id]);
  useEffect(() => {
    if (canvas.current && tab !== "profile")
      drawAdFrame(
        canvas.current,
        draft,
        profile,
        tab === "video" ? sourceVideo || image : image,
      );
  }, [draft, profile, image, sourceVideo, tab, library]);
  useEffect(() => {
    if (!rendered) {
      setRenderUrl("");
      return;
    }
    const url = URL.createObjectURL(rendered);
    setRenderUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [rendered]);
  const patchDraft = (patch: Partial<AdDraftInput>) => {
    setHistory((previous) => [...previous.slice(-39), structuredClone(draft)]);
    setFuture([]);
    setDraft((previous) => ({ ...previous, ...patch }));
    setDirty(true);
    setRendered(null);
    setMessage("");
  };
  const change = (key: keyof AdDraftInput, value: string | number | null) =>
    patchDraft({ [key]: value });
  const canvasPoint = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const rect=event.currentTarget.getBoundingClientRect();
    return {x:(event.clientX-rect.left)/rect.width*100,y:(event.clientY-rect.top)/rect.height*100};
  };
  const moveObject = (value:AdDraftInput, id:string, x:number, y:number):AdDraftInput => id==='headline'
    ? {...value,image_style:{...defaultImageStyle,...value.image_style,text_x:Math.max(0,Math.min(70,x)),text_y:Math.max(0,Math.min(80,y))}}
    : {...value,layers:value.layers?.map(layer=>layer.id===id?{...layer,x:Math.max(0,Math.min(100-layer.width,x)),y:Math.max(0,Math.min(100-layer.height,y))}:layer)};
  const finishDrag = (event:React.PointerEvent<HTMLCanvasElement>, cancelled=false) => {
    const active=drag.current;if(!active)return;
    if(cancelled)setDraft(active.draft);
    else {setHistory(previous=>[...previous.slice(-39),active.draft]);setFuture([]);setDirty(true);setRendered(null);}
    drag.current=null;
    if(event.currentTarget.hasPointerCapture(event.pointerId))event.currentTarget.releasePointerCapture(event.pointerId);
  };
  const changeProfile = (key: keyof AdProfileInput, value: string) => {
    setProfile((prev) => ({ ...prev, [key]: value }));
    setProfileDirty(true);
    setRendered(null);
    setMessage("");
  };
  const act = async (name: string, work: () => Promise<void>) => {
    if (busy) return;
    setBusy(name);
    setError("");
    setMessage("");
    try {
      await work();
    } catch (err) {
      if (mounted.current)
        setError(
          err instanceof Error
            ? err.message
            : "Action failed. Your existing work is unchanged.",
        );
    } finally {
      if (mounted.current) setBusy("");
    }
  };
  const upload = async (blob: Blob, name: string) => {
    const data = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1]);
      reader.onerror = () => reject(new Error("The file could not be read."));
      reader.readAsDataURL(blob);
    });
    const result = await apiCall<AdAsset>("/api/v1/ads/assets", "POST", {
      name,
      mime: blob.type.split(";")[0],
      data,
    });
    await reload();
    return result;
  };
  const download = (blob: Blob, name: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.click();
    URL.revokeObjectURL(url);
  };
  const chooseProfile = (id: string) => {
    if (
      (dirty || profileDirty) &&
      !window.confirm("Discard unsaved editor changes?")
    )
      return;
    const next = library?.profiles.find((p) => p.id === id);
    if (next) {
      const { id: ignore, created_at, updated_at, ...values } = next;
      setProfile(values);
    } else
      setProfile({
        ...blankProfile,
        name: context?.company_name || "",
        product: context?.products_services || "",
        audience: context?.target_market || "",
        voice: context?.brand_voice || "",
      });
    setProfileId(id);
    setDraft({ ...blankDraft, profile_id: id, cta: next?.cta || "" });
    setDraftId("");
    setDirty(false);
    setProfileDirty(false);
    setRendered(null);
    setTab(id ? (initialTab === "profile" ? "copy" : initialTab) : "profile");
    setHistory([]);
    setFuture([]);
  };
  const saveDraft = async () => {
    if (!profileId) throw new Error("Save an advertising profile first.");
    if (profileDirty)
      throw new Error("Save your profile changes before saving this draft.");
    const saved = await apiCall<AdDraft>(
      draftId ? `/api/v1/ads/drafts/${draftId}` : "/api/v1/ads/drafts",
      draftId ? "PUT" : "POST",
      { ...draft, profile_id: profileId },
    );
    setDraftId(saved.id);
    setDirty(false);
    await reload();
    setMessage("Creative draft saved. Edits require a fresh approval.");
  };
  const previewScene = async (scene: VideoScene) => {
    const sequence = ++previewRequest.current;
    let url = '';
    try {
      let source: HTMLImageElement | HTMLVideoElement | null = sourceVideo || image;
      if (scene.asset_id) {
        const blob = await (await authenticatedFetch(`/api/v1/ads/assets/${scene.asset_id}`)).blob();
        url = URL.createObjectURL(blob);
        if (blob.type.startsWith('video/')) {
          const media = document.createElement('video');
          media.muted = true;
          await new Promise<void>((resolve,reject)=>{
            media.onloadeddata=()=>resolve();
            media.onerror=()=>reject(new Error('Scene video cannot be decoded'));
            media.src=url;
          });
          const seek = Math.min(scene.source_start, Math.max(0, media.duration - .02));
          if (seek > 0) await new Promise<void>((resolve,reject)=>{
            media.onseeked=()=>resolve();
            media.onerror=()=>reject(new Error('Scene preview seek failed'));
            media.currentTime=seek;
          });
          source=media;
        } else {
          const media=new Image();media.src=url;await media.decode();source=media;
        }
      }
      if(sequence===previewRequest.current && mounted.current && canvas.current)
        drawAdFrame(canvas.current,draft,profile,source,scene.caption);
    } catch(err) {
      if(sequence===previewRequest.current && mounted.current)
        setError(err instanceof Error?err.message:'Scene preview failed.');
    } finally {
      if(url)URL.revokeObjectURL(url);
    }
  };
  if (!context)
    return (
      <section className="owner-panel">
        <h2 className="font-display text-2xl font-bold">Ads Studio</h2>
        <p className="mt-3 text-muted-foreground">
          Save your business context first, then create ad profiles and
          creatives.
        </p>
        <a className="owner-button mt-5" href="#/profiles">
          Set up business context
        </a>
      </section>
    );
  if (!library && !error) return <WorkspaceLoading label="creative library" />;
  const selectedDraft = library?.drafts.find((d) => d.id === draftId);
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold flex items-center gap-2">
            <Megaphone className="w-6 h-6 text-primary" />
            {initialTab === "copy"
              ? "Copywriting engine"
              : initialTab === "image"
                ? "Image editor"
                : initialTab === "video"
                  ? "Video editor"
                  : "Ads Studio"}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">Design on the canvas. Refine the selected object. Save and export when ready.</p>
        </div>
        <button
          className="owner-button-secondary"
          disabled={!!busy}
          onClick={() =>
            void act("refresh", async () => {
              await reload();
              setMessage("Ads library refreshed.");
            })
          }
        >
          Refresh library
        </button>
        <a className="owner-button-secondary" href="#/ad-optimization">
          Review ad performance
        </a>
      </div>
      {error && (
        <p className="owner-error" role="alert">
          {error}
        </p>
      )}
      {message && (
        <p className="text-sm" role="status">
          {message}
        </p>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <button
          className="owner-button-secondary"
          disabled={!!busy || !history.length}
          onClick={() => {
            const previous = history.at(-1)!;
            setFuture((next) => [structuredClone(draft), ...next]);
            setHistory((next) => next.slice(0, -1));
            setDraft(previous);
            setDirty(true);
            setRendered(null);
          }}
        >
          Undo edit
        </button>
        <button
          className="owner-button-secondary"
          disabled={!!busy || !future.length}
          onClick={() => {
            setHistory((next) => [...next, structuredClone(draft)]);
            setDraft(future[0]);
            setFuture((next) => next.slice(1));
            setDirty(true);
            setRendered(null);
          }}
        >
          Redo edit
        </button>
        <span className="text-xs text-muted-foreground">
          {initialTab === "profile"
            ? "Shared creative workspace"
            : `${initialTab === "copy" ? "Copywriting" : initialTab === "image" ? "Image" : "Video"} editor · shared profiles and private assets`}
        </span>
        <button className="owner-button-secondary" onClick={()=>setShowLibrary(!showLibrary)} aria-expanded={showLibrary}>{showLibrary?'Hide library':'Open library'}</button>
      </div>
      <div className={showLibrary?'grid xl:grid-cols-[240px_minmax(0,1fr)] gap-5':'min-w-0'}>
        <aside hidden={!showLibrary} className="owner-panel !p-4 space-y-5">
          <label className="owner-label">
            Advertising profile
            <select
              className="owner-input"
              value={profileId}
              disabled={!!busy}
              onChange={(e) => chooseProfile(e.target.value)}
            >
              <option value="">Create new profile</option>
              {library?.profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <button
            className="owner-button-secondary w-full"
            disabled={!!busy}
            onClick={() => setTab("profile")}
          >
            Edit profile
          </button>
          <div className="border-t border-border pt-4">
            <h3 className="text-sm font-semibold">Saved creative drafts</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Latest 100 drafts
            </p>
            <button
              className="text-primary text-sm underline mt-3"
              disabled={!!busy}
              onClick={() => {
                if (dirty && !confirm("Discard unsaved draft changes?")) return;
                setDraft({
                  ...blankDraft,
                  profile_id: profileId,
                  cta: profile.cta,
                });
                setDraftId("");
                setDirty(false);
                setRendered(null);
                setTab(initialTab === "profile" ? "copy" : initialTab);
                setHistory([]);
                setFuture([]);
              }}
            >
              Start new creative
            </button>
            <div className="mt-3 divide-y divide-border">
              {library?.drafts
                .filter((d) => !profileId || d.profile_id === profileId)
                .map((item) => (
                  <button
                    key={item.id}
                    disabled={!!busy}
                    className={`w-full py-3 text-left text-sm ${item.id === draftId ? "text-primary font-semibold" : "hover:text-primary"}`}
                    onClick={() => {
                      if (
                        (dirty || profileDirty) &&
                        !confirm("Discard unsaved editor changes?")
                      )
                        return;
                      const {
                        id,
                        status,
                        profile_snapshot,
                        created_at,
                        updated_at,
                        ...values
                      } = item;
                      setDraft(values);
                      setDraftId(id);
                      setProfileId(item.profile_id);
                      const currentProfile = library?.profiles.find(
                        (profile) => profile.id === item.profile_id,
                      );
                      if (currentProfile) {
                        const { id, created_at, updated_at, ...profileFields } =
                          currentProfile;
                        setProfile(profileFields);
                      } else setProfile(profile_snapshot);
                      setDirty(false);
                      setProfileDirty(false);
                      setRendered(null);
                      setTab(initialTab === "profile" ? "copy" : initialTab);
                      setHistory([]);
                      setFuture([]);
                      setShowLibrary(false);
                      setSelectedLayer('headline');
                    }}
                  >
                    <span className="block break-words">{item.title}</span>
                    <span className="block text-xs text-muted-foreground mt-1">
                      {item.status} ·{" "}
                      {new Date(item.updated_at).toLocaleDateString()}
                    </span>
                  </button>
                ))}
            </div>
          </div>
          <section className="border-t border-border pt-4 space-y-3">
            <h3 className="font-semibold text-sm">Private asset library</h3>
            <label className="owner-label">
              Find assets
              <input
                className="owner-input"
                type="search"
                value={assetSearch}
                onChange={(e) => setAssetSearch(e.target.value)}
              />
            </label>
            <div className="max-h-72 overflow-y-auto space-y-2">
              {library?.assets
                .filter((asset) =>
                  asset.name.toLowerCase().includes(assetSearch.toLowerCase()),
                )
                .map((asset) => (
                  <button
                    key={asset.id}
                    disabled={!!busy}
                    className="block w-full p-2 text-left text-xs border border-border rounded-lg hover:border-primary"
                    onClick={() => {
                      change(
                        asset.mime.startsWith("audio/")
                          ? "audio_asset_id"
                          : asset.mime.startsWith("video/")
                            ? "video_asset_id"
                            : "asset_id",
                        asset.id,
                      );
                      setTab(
                        asset.mime.startsWith("image/") ? "image" : "video",
                      );
                    }}
                  >
                    <span className="block font-medium truncate">
                      {asset.name}
                    </span>
                    <span className="text-muted-foreground">{asset.mime}</span>
                  </button>
                ))}
            </div>
          </section>
          <p className="text-xs text-muted-foreground">
            {context?.is_demo ? 'Sample creative library. Edit and export locally; paid AI generation is disabled in the demo.' : 'Manual copy, PNG and WebM creation do not need AI credentials. Provider generation may incur charges.'}
          </p>
        </aside>
        <div className="min-w-0 space-y-5">
          <div
            className="flex flex-wrap gap-2"
            aria-label="Creative editor sections"
          >
            {(["profile", "copy", "image", "video"] as const).map((section) => (
              <button
                key={section}
                className={
                  tab === section ? "owner-button" : "owner-button-secondary"
                }
                aria-pressed={tab === section}
                disabled={!!busy}
                onClick={() => setTab(section)}
              >
                {section === "profile"
                  ? "Ad profile"
                  : section === "copy"
                    ? "Copy editor"
                    : section === "image"
                      ? "Image editor"
                      : "Video editor"}
              </button>
            ))}
          </div>
          {tab === "profile" ? (
            <form
              className="owner-panel space-y-5"
              onSubmit={(event) => {
                event.preventDefault();
                void act("profile", async () => {
                  const saved = await apiCall<AdProfile>(
                    profileId
                      ? `/api/v1/ads/profiles/${profileId}`
                      : "/api/v1/ads/profiles",
                    profileId ? "PUT" : "POST",
                    profile,
                  );
                  setProfileId(saved.id);
                  setDraft((prev) => ({
                    ...prev,
                    profile_id: saved.id,
                    cta: prev.cta || saved.cta,
                  }));
                  setProfileDirty(false);
                  await reload();
                  setMessage(
                    "Advertising profile saved. Choose Copy, Image or Video to create a draft.",
                  );
                });
              }}
            >
              <h3 className="font-display text-lg font-semibold">
                Reusable advertising profile
              </h3>
              <div className="grid sm:grid-cols-2 gap-4">
                <label className="owner-label">
                  Profile name
                  <input
                    disabled={!!busy}
                    className="owner-input"
                    required
                    maxLength={120}
                    value={profile.name}
                    onChange={(e) => changeProfile("name", e.target.value)}
                  />
                </label>
                <label className="owner-label">
                  Primary channel
                  <select
                    disabled={!!busy}
                    className="owner-input"
                    value={profile.channel}
                    onChange={(e) => changeProfile("channel", e.target.value)}
                  >
                    {["Meta", "Google", "TikTok", "LinkedIn", "Other"].map(
                      (v) => (
                        <option key={v}>{v}</option>
                      ),
                    )}
                  </select>
                </label>
                {[
                  ["product", "Product / service (required)", 2000],
                  ["offer", "Offer and proof points", 2000],
                  ["audience", "Target audience (required)", 2000],
                  ["voice", "Brand voice", 1000],
                  [
                    "prohibited_claims",
                    "Prohibited claims / required disclaimers",
                    2000,
                  ],
                ].map(([key, label, max]) => (
                  <label
                    key={key}
                    className={`owner-label ${key === "prohibited_claims" ? "sm:col-span-2" : ""}`}
                  >
                    {label}
                    <textarea
                      disabled={!!busy}
                      className="owner-input"
                      rows={3}
                      required={key === "product" || key === "audience"}
                      maxLength={Number(max)}
                      value={profile[key as keyof AdProfileInput]}
                      onChange={(e) =>
                        changeProfile(
                          key as keyof AdProfileInput,
                          e.target.value,
                        )
                      }
                    />
                  </label>
                ))}
                <label className="owner-label">
                  Call to action
                  <input
                    disabled={!!busy}
                    className="owner-input"
                    maxLength={100}
                    value={profile.cta}
                    onChange={(e) => changeProfile("cta", e.target.value)}
                    placeholder="Book a consultation"
                  />
                </label>
                <label className="owner-label">
                  Landing page URL
                  <input
                    disabled={!!busy}
                    className="owner-input"
                    type="url"
                    maxLength={500}
                    value={profile.landing_url}
                    onChange={(e) =>
                      changeProfile("landing_url", e.target.value)
                    }
                  />
                </label>
                <label className="owner-label">
                  Language
                  <input
                    disabled={!!busy}
                    className="owner-input"
                    maxLength={80}
                    value={profile.language}
                    onChange={(e) => changeProfile("language", e.target.value)}
                  />
                </label>
                <label className="owner-label">
                  Brand colour
                  <input
                    disabled={!!busy}
                    className="owner-input h-12"
                    type="color"
                    value={profile.brand_color}
                    onChange={(e) =>
                      changeProfile("brand_color", e.target.value)
                    }
                  />
                </label>
              </div>
              <p className="text-xs text-muted-foreground">
                Use verified product facts. Do not enter credentials or private
                customer data. Generation sends this profile to your configured
                provider.
              </p>
              <button className="owner-button" disabled={!!busy}>
                <Save className="w-4 h-4" />
                {busy === "profile" ? "Saving…" : "Save ad profile"}
              </button>
            </form>
          ) : (
            <>
              {!profileId && (
                <p className="owner-error">
                  Save an ad profile before generating or saving creatives.
                </p>
              )}
              <section className="owner-panel space-y-4">
                <div className="grid sm:grid-cols-[minmax(0,1fr)_180px] gap-4">
                  <label className="owner-label">
                    Creative name
                    <input
                      disabled={!!busy}
                      className="owner-input"
                      value={draft.title}
                      maxLength={160}
                      onChange={(e) => change("title", e.target.value)}
                    />
                  </label>
                  <label className="owner-label">
                    Format
                    <select
                      disabled={!!busy}
                      className="owner-input"
                      value={draft.aspect_ratio}
                      onChange={(e) => change("aspect_ratio", e.target.value)}
                    >
                      {["1:1", "4:5", "9:16", "16:9"].map((r) => (
                        <option key={r}>{r}</option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="flex flex-wrap gap-3 items-center">
                  <button
                    className="owner-button"
                    disabled={!!busy || !profileId || !draft.title.trim()}
                    onClick={() => void act("save", saveDraft)}
                  >
                    <Save className="w-4 h-4" />
                    Save creative
                  </button>
                  <button
                    className="owner-button-secondary"
                    disabled={
                      !!busy ||
                      !draftId ||
                      dirty ||
                      profileDirty ||
                      selectedDraft?.status === "approved"
                    }
                    onClick={() =>
                      void act("approve", async () => {
                        await apiCall(
                          `/api/v1/ads/drafts/${draftId}`,
                          "PATCH",
                          { status: "approved" },
                        );
                        await reload();
                        setMessage(
                          "Creative approved internally. Nothing has been published.",
                        );
                      })
                    }
                  >
                    Approve saved creative
                  </button>
                  <span className="text-xs text-muted-foreground">
                    {dirty || profileDirty
                      ? "Unsaved edits"
                      : selectedDraft?.status || "New creative"}{" "}
                    · approval is review only
                  </span>
                </div>
              </section>
              <div className={tab==='copy'?'grid lg:grid-cols-2 gap-5':'creative-workbench'}>
                <section className="owner-panel editor-inspector min-w-0 space-y-4">
                  <label className="owner-label">
                    Headline
                    <input
                      disabled={!!busy}
                      className="owner-input"
                      value={draft.headline}
                      maxLength={200}
                      onChange={(e) => change("headline", e.target.value)}
                    />
                    <span className="text-xs text-muted-foreground">
                      {draft.headline.length} characters
                      {profile.channel === "Google"
                        ? " · search-ad headline limit: 30"
                        : ""}
                    </span>
                  </label>
                  <label className="owner-label">
                    Call to action
                    <input
                      disabled={!!busy}
                      className="owner-input"
                      value={draft.cta}
                      maxLength={100}
                      onChange={(e) => change("cta", e.target.value)}
                    />
                  </label>
                  {tab === "copy" && (
                    <>
                      <label className="owner-label">
                        Ad copy
                        <textarea
                          disabled={!!busy}
                          className="owner-input"
                          rows={10}
                          value={draft.body}
                          maxLength={10000}
                          onChange={(e) => change("body", e.target.value)}
                        />
                      </label>
                      <p className="text-xs text-muted-foreground">
                        {profile.channel === "Google"
                          ? "Google search descriptions: 90 characters each."
                          : "Check destination platform limits before publishing."}{" "}
                        No performance guarantees or invented testimonials.
                      </p>
                      <CopyControls
                        draft={draft}
                        profile={profile}
                        disabled={!!busy}
                        onChange={patchDraft}
                        onGenerate={async (instruction) => {
                          await act("copy", async () => {
                            if (!profileId || profileDirty)
                              throw new Error(
                                "Save the advertising profile before AI generation.",
                              );
                            const result = await apiCall<AgentRun>(
                              "/api/v1/ads/copy",
                              "POST",
                              {
                                profile_id: profileId,
                                prompt: instruction.slice(0, 4000),
                              },
                            );
                            if (result.status === "failed")
                              throw new Error(
                                result.error || "Generation failed",
                              );
                            patchDraft({ body: result.output });
                            await refreshOwner();
                            setMessage(
                              "Copy assistant result loaded. Review before saving.",
                            );
                          });
                        }}
                      />
                      <button
                        className="owner-button-secondary"
                        disabled={
                          !!busy ||
                          !profileId ||
                          profileDirty ||
                          !library?.capabilities.ai_available
                        }
                        onClick={() =>
                          void act("copy", async () => {
                            const result = await apiCall<AgentRun>(
                              "/api/v1/ads/copy",
                              "POST",
                              {
                                profile_id: profileId,
                                prompt:
                                  `Write a headline, primary copy and CTA for this ad. Creative: ${draft.title}. Current draft to improve: ${draft.body}`.slice(
                                    0,
                                    4000,
                                  ),
                              },
                            );
                            if (result.status === "failed")
                              throw new Error(
                                result.error || "Generation failed",
                              );
                            change("body", result.output);
                            await refreshOwner();
                            setMessage(
                              "Generated copy is editable. Review facts, then save.",
                            );
                          })
                        }
                      >
                        <Sparkles className="w-4 h-4" />
                        {busy === "copy" ? "Generating…" : "Generate copy"}
                      </button>
                      <button
                        className="owner-button-secondary ml-2"
                        disabled={!draft.body}
                        onClick={() =>
                          download(
                            new Blob(
                              [
                                `${draft.headline}\n\n${draft.body}\n\n${draft.cta}\n${profile.landing_url}`,
                              ],
                              { type: "text/plain" },
                            ),
                            "ad-copy.txt",
                          )
                        }
                      >
                        Export copy
                      </button>
                      {!library?.capabilities.ai_available && (
                        <p className="text-xs text-muted-foreground">
                          AI copy provider is not configured. Write and save
                          copy manually.
                        </p>
                      )}
                    </>
                  )}
                  {(tab === "image" || tab === "video") && (
                    <>
                      <label className="owner-label">
                        Image / product asset
                        <select
                          className="owner-input"
                          value={draft.asset_id || ""}
                          disabled={!!busy}
                          onChange={(e) =>
                            change("asset_id", e.target.value || null)
                          }
                        >
                          <option value="">Brand-colour background</option>
                          {library?.assets
                            .filter((a) => a.mime.startsWith("image/"))
                            .map((a) => (
                              <option key={a.id} value={a.id}>
                                {a.name}
                              </option>
                            ))}
                        </select>
                      </label>
                      <details><summary className="cursor-pointer text-sm font-medium min-h-11 py-3">Upload media</summary>
                      <label className="owner-label">
                        Upload a real image or video
                        <input
                          disabled={!!busy}
                          className="owner-input"
                          type="file"
                          accept="image/png,image/jpeg,image/webp,video/mp4,video/webm,audio/mpeg,audio/wav,audio/ogg,audio/webm"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            e.target.value = "";
                            if (file)
                              void act("upload", async () => {
                                if (file.size > 30 * 1024 * 1024)
                                  throw new Error(
                                    "Files must be smaller than 30 MB.",
                                  );
                                const asset = await upload(file, file.name);
                                change(
                                  asset.mime.startsWith("audio/")
                                    ? "audio_asset_id"
                                    : asset.mime.startsWith("video/")
                                      ? "video_asset_id"
                                      : "asset_id",
                                  asset.id,
                                );
                                setMessage(
                                  "Asset uploaded. Save your creative to keep this selection.",
                                );
                              });
                          }}
                        />
                        <span className="text-xs text-muted-foreground">
                          Images up to 10 MB; videos up to 30 MB. Upload only
                          assets you have permission to use.
                        </span>
                      </label>
                      </details>
                      <details open={tab==='image'} key={`layers-${tab}`}><summary className="cursor-pointer text-sm font-medium min-h-11 py-3">{tab==='image'?'Canvas objects and adjustments':'Video frame styling'}</summary>
                      <ImageControls
                        draft={draft}
                        disabled={!!busy}
                        onChange={patchDraft}
                        selected={selectedLayer}
                        onSelect={setSelectedLayer}
                      />
                      </details>
                    </>
                  )}
                  {tab === "image" && (
                    <details><summary className="cursor-pointer text-sm font-medium min-h-11 py-3">AI image generation</summary><div className="space-y-4">
                      <label className="owner-label">
                        Image direction / edit instruction
                        <textarea
                          disabled={!!busy}
                          className="owner-input"
                          rows={5}
                          value={draft.image_prompt}
                          maxLength={4000}
                          onChange={(e) =>
                            change("image_prompt", e.target.value)
                          }
                        />
                      </label>
                      <p className="text-xs text-muted-foreground">
                        Selected image is sent as a reference. Headline and CTA
                        are rendered as editable overlays, not invented by the
                        model.
                      </p>
                      <button
                        className="owner-button-secondary"
                        disabled={
                          !!busy ||
                          !profileId ||
                          profileDirty ||
                          draft.image_prompt.trim().length < 3 ||
                          !library?.capabilities.image_available
                        }
                        onClick={() =>
                          void act("image", async () => {
                            const asset = await apiCall<AdAsset>(
                              "/api/v1/ads/image",
                              "POST",
                              {
                                profile_id: profileId,
                                prompt: draft.image_prompt,
                                aspect_ratio: draft.aspect_ratio,
                                asset_id: draft.asset_id,
                              },
                            );
                            await reload();
                            change("asset_id", asset.id);
                            setMessage(
                              "Generated image saved to your asset library. Review the image and save your creative.",
                            );
                          })
                        }
                      >
                        <ImagePlus className="w-4 h-4" />
                        {busy === "image"
                          ? "Generating image…"
                          : "Generate / edit image"}
                      </button>
                      <p className="text-xs text-muted-foreground">
                        {library?.capabilities.image_available
                          ? `Model: ${library.capabilities.image_model}. Generation may incur charges.`
                          : "AI image generation needs GEMINI_API_KEY on the server. Manual image composition works now."}
                      </p>
                    </div></details>
                  )}
                  {tab === "video" && (
                    <>
                      <label className="owner-label">
                        Video source (optional)
                        <select
                          className="owner-input"
                          disabled={!!busy}
                          value={draft.video_asset_id || ""}
                          onChange={(e) =>
                            change("video_asset_id", e.target.value || null)
                          }
                        >
                          <option value="">
                            Animate the selected image / background
                          </option>
                          {library?.assets
                            .filter((a) => a.mime.startsWith("video/"))
                            .map((a) => (
                              <option key={a.id} value={a.id}>
                                {a.name}
                              </option>
                            ))}
                        </select>
                      </label>
                      <details><summary className="cursor-pointer text-sm font-medium min-h-11 py-3">Script and fallback duration</summary><div className="space-y-3">
                      <label className="owner-label">
                        Scene captions — one scene per line
                        <textarea
                          disabled={!!busy}
                          className="owner-input"
                          rows={5}
                          maxLength={4000}
                          value={draft.script}
                          onChange={(e) => change("script", e.target.value)}
                          placeholder="Introduce the product\nExplain the offer\nInvite the next action"
                        />
                      </label>
                      <label className="owner-label">
                        Duration (seconds)
                        <input
                          disabled={!!busy || !!draft.scenes?.length}
                          className="owner-input"
                          type="number"
                          min={0.5}
                          max={120}
                          value={draft.duration}
                          onChange={(e) =>
                            change("duration", Number(e.target.value))
                          }
                        />
                      </label>
                      <p className="text-xs text-muted-foreground">
                        Timeline scenes override the equal-duration script.
                        Soundtrack and source audio use the volume controls
                        above. Rendering validates trim bounds.
                      </p>
                      </div></details>
                      <button
                        className="owner-button"
                        disabled={
                          !!busy || draft.duration < 0.5 || draft.duration > 120
                        }
                        onClick={() =>
                          void act("render", async () => {
                            if (!canvas.current) return;
                            const controller = new AbortController();
                            renderController.current = controller;
                            setProgress(0);
                            await document.fonts.ready;
                            const blob = await renderMotionAd(
                              canvas.current,
                              draft,
                              profile,
                              image,
                              sourceVideo,
                              setProgress,
                              controller.signal,
                            );
                            setRendered(blob);
                            setMessage(
                              "Video rendered. Preview it, then download or save it to your library.",
                            );
                          })
                        }
                      >
                        <Play className="w-4 h-4" />
                        {busy === "render"
                          ? `Rendering ${progress}%`
                          : "Render motion ad"}
                      </button>
                      <button
                        type="button"
                        className="owner-button-secondary"
                        disabled={
                          !!busy ||
                          !(draft.scenes?.length || draft.script.trim())
                        }
                        onClick={() => {
                          const scenes = draft.scenes?.length
                            ? draft.scenes
                            : draft.script
                                .split("\n")
                                .filter(Boolean)
                                .map((caption) => ({
                                  caption,
                                  duration:
                                    draft.duration /
                                    draft.script.split("\n").filter(Boolean)
                                      .length,
                                }));
                          let elapsed = 0;
                          const stamp = (seconds: number) =>
                            new Date(Math.round(seconds * 1000))
                              .toISOString()
                              .slice(11, 23)
                              .replace(".", ",");
                          const subtitles = scenes
                            .map((scene, index) => {
                              const start = elapsed;
                              elapsed += scene.duration;
                              return `${index + 1}\n${stamp(start)} --> ${stamp(elapsed)}\n${scene.caption}\n`;
                            })
                            .join("\n");
                          download(
                            new Blob([subtitles], { type: "text/plain" }),
                            "ad-captions.srt",
                          );
                        }}
                      >
                        Export captions SRT
                      </button>
                      {busy === "render" && (
                        <button
                          className="owner-button-secondary ml-2"
                          onClick={() => renderController.current?.abort()}
                        >
                          <X className="w-4 h-4" />
                          Cancel render
                        </button>
                      )}
                      <details className="border-t border-border pt-4">
                        <summary className="font-semibold text-sm cursor-pointer">
                          Generate AI footage with Veo
                        </summary>
                        <label className="owner-label mt-4">
                          Video prompt
                          <textarea
                            disabled={!!busy}
                            className="owner-input"
                            rows={4}
                            maxLength={4000}
                            value={draft.video_prompt}
                            onChange={(e) =>
                              change("video_prompt", e.target.value)
                            }
                          />
                        </label>
                        <p className="text-xs text-muted-foreground mt-2">
                          AI footage supports 9:16 or 16:9, 4/6/8 seconds.
                          Provider charges may apply. Model:{" "}
                          {library?.capabilities.video_model}. Check an existing
                          job rather than resubmitting.
                        </p>
                        <button
                          className="owner-button-secondary mt-3"
                          disabled={
                            !!busy ||
                            !profileId ||
                            profileDirty ||
                            !library?.capabilities.video_available ||
                            draft.video_prompt.trim().length < 3 ||
                            !["9:16", "16:9"].includes(draft.aspect_ratio) ||
                            ![4, 6, 8].includes(draft.duration)
                          }
                          onClick={() =>
                            void act("video", async () => {
                              const job = await apiCall<AdVideoJob>(
                                "/api/v1/ads/video",
                                "POST",
                                {
                                  profile_id: profileId,
                                  prompt: draft.video_prompt,
                                  aspect_ratio: draft.aspect_ratio,
                                  duration: draft.duration,
                                  request_id: crypto.randomUUID(),
                                },
                              );
                              await reload();
                              if (job.status === "failed")
                                throw new Error(
                                  job.error || "Submission failed",
                                );
                              setMessage(
                                "Video job submitted. Use Check status below; the job survives reload.",
                              );
                            })
                          }
                        >
                          <Video className="w-4 h-4" />
                          Generate AI footage
                        </button>
                        {!library?.capabilities.video_available && (
                          <p className="text-xs text-muted-foreground mt-2">
                            Configure GEMINI_API_KEY and enabled Veo billing to
                            generate footage.
                          </p>
                        )}
                      </details>
                    </>
                  )}
                </section>
                <section className="owner-panel editor-stage min-w-0 space-y-4">
                  <h3 className="font-display text-lg font-semibold">
                    Creative preview
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Actual composition, not a platform screenshot.{" "}
                    {draft.aspect_ratio} · {profile.name}
                  </p>
                  {tab==='image'&&<div className="flex flex-wrap items-center justify-between gap-3"><span className="text-xs font-medium">Selected: {selectedLayer==='headline'?'Headline':draft.layers?.find(l=>l.id===selectedLayer)?.text||'Shape'}</span><label className="flex items-center gap-2 text-xs">Canvas zoom<select className="owner-input !w-auto" value={canvasZoom} onChange={e=>setCanvasZoom(Number(e.target.value))}>{[75,100,125,150].map(value=><option key={value} value={value}>{value}%</option>)}</select></label></div>}
                  <div className="editor-canvas-surface overflow-x-auto p-3 sm:p-5 rounded-xl bg-muted">
                  <div className="relative mx-auto" style={{width:`${canvasZoom}%`,maxWidth:canvasZoom===100?(draft.aspect_ratio==='9:16'?300:draft.aspect_ratio==='4:5'?420:760):undefined,minWidth:canvasZoom>100?`${canvasZoom}%`:undefined}}>
                  <canvas
                    ref={canvas}
                    className="block w-full h-auto shadow-sm touch-none"
                    aria-label="Ad creative preview"
                    tabIndex={0}
                    onPointerDown={event=>{
                      if(tab!=='image'||busy)return;
                      const point=canvasPoint(event);
                      const hit=[...(draft.layers||[])].reverse().find(l=>l.visible&&point.x>=l.x&&point.x<=l.x+l.width&&point.y>=l.y&&point.y<=l.y+l.height);
                      const id=hit?.id||'headline';setSelectedLayer(id);
                      const style={...defaultImageStyle,...draft.image_style};
                      drag.current={draft:structuredClone(draft),id,x:point.x,y:point.y,originX:hit?.x??style.text_x,originY:hit?.y??style.text_y};
                      event.currentTarget.setPointerCapture(event.pointerId);
                    }}
                    onPointerMove={event=>{if(!drag.current)return;const point=canvasPoint(event);const active=drag.current;setDraft(moveObject(active.draft,active.id,active.originX+point.x-active.x,active.originY+point.y-active.y));}}
                    onPointerUp={event=>finishDrag(event)}
                    onPointerCancel={event=>finishDrag(event,true)}
                    onLostPointerCapture={()=>{if(drag.current){setDraft(drag.current.draft);drag.current=null;}}}
                    onKeyDown={event=>{
                      if(tab!=='image'||busy||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
                      event.preventDefault();const layer=draft.layers?.find(l=>l.id===selectedLayer);const style={...defaultImageStyle,...draft.image_style};const step=event.shiftKey?5:1;
                      const value=moveObject(draft,layer?layer.id:'headline',(layer?.x??style.text_x)+(event.key==='ArrowLeft'?-step:event.key==='ArrowRight'?step:0),(layer?.y??style.text_y)+(event.key==='ArrowUp'?-step:event.key==='ArrowDown'?step:0));
                      patchDraft(value);
                    }}
                  />
                  {tab==='image'&&selectedLayer!=='headline'&&draft.layers?.filter(layer=>layer.id===selectedLayer&&layer.visible).map(layer=><div key={layer.id} className="pointer-events-none absolute border-2 border-primary" style={{left:`${layer.x}%`,top:`${layer.y}%`,width:`${layer.width}%`,height:`${layer.height}%`}}/>)}
                  </div></div>
                  {tab === "image" && (
                    <p className="text-xs text-muted-foreground">
                      Select a layer or the headline, then drag on the canvas. Arrow keys move 1%; Shift moves 5%. Undo restores the previous position.
                    </p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    <button
                      className="owner-button-secondary"
                      disabled={!!busy}
                      onClick={() =>
                        void act("png", async () => {
                          if (!canvas.current) return;
                          await document.fonts.ready;
                          drawAdFrame(canvas.current, draft, profile, image);
                          const blob = await new Promise<Blob>(
                            (resolve, reject) =>
                              canvas.current!.toBlob(
                                (value) =>
                                  value
                                    ? resolve(value)
                                    : reject(new Error("PNG export failed.")),
                                "image/png",
                              ),
                          );
                          download(blob, "ad-creative.png");
                          setMessage(
                            "PNG exported at full composition resolution.",
                          );
                        })
                      }
                    >
                      <Download className="w-4 h-4" />
                      Export PNG
                    </button>
                    <button
                      className="owner-button-secondary"
                      disabled={!!busy}
                      onClick={() =>
                        void act("webp", async () => {
                          if (!canvas.current) return;
                          const blob = await new Promise<Blob>(
                            (resolve, reject) =>
                              canvas.current!.toBlob(
                                (value) =>
                                  value
                                    ? resolve(value)
                                    : reject(new Error("Image export failed")),
                                "image/webp",
                                0.9,
                              ),
                          );
                          download(blob, "ad-creative.webp");
                        })
                      }
                    >
                      Export WebP
                    </button>
                    <button
                      className="owner-button-secondary"
                      disabled={!!busy}
                      onClick={() =>
                        void act("save-image", async () => {
                          if (!canvas.current) return;
                          const blob = await new Promise<Blob>(
                            (resolve, reject) =>
                              canvas.current!.toBlob(
                                (value) =>
                                  value
                                    ? resolve(value)
                                    : reject(new Error("PNG export failed")),
                                "image/png",
                              ),
                          );
                          await upload(
                            blob,
                            `${draft.title || "Creative"} composition.png`,
                          );
                          setMessage(
                            "Composed image saved in the private asset library.",
                          );
                        })
                      }
                    >
                      Save composed image
                    </button>
                    {rendered && (
                      <>
                        <button
                          className="owner-button-secondary"
                          onClick={() => download(rendered, "motion-ad.webm")}
                        >
                          <Download className="w-4 h-4" />
                          Download WebM
                        </button>
                        <button
                          className="owner-button-secondary"
                          disabled={!!busy}
                          onClick={() =>
                            void act("save-video", async () => {
                              const asset = await upload(
                                rendered,
                                "Rendered motion ad.webm",
                              );
                              change("video_asset_id", asset.id);
                              setMessage(
                                "Rendered video saved in your asset library. Save the creative to attach it.",
                              );
                            })
                          }
                        >
                          Save video asset
                        </button>
                        <button
                          className="owner-button-secondary"
                          disabled={
                            !!busy || !library?.capabilities.mp4_available
                          }
                          onClick={() =>
                            void act("mp4", async () => {
                              const source = await upload(
                                rendered,
                                "Timeline export.webm",
                              );
                              const converted = await apiCall<AdAsset>(
                                `/api/v1/ads/assets/${source.id}/mp4`,
                                "POST",
                              );
                              const blob = await (
                                await authenticatedFetch(
                                  `/api/v1/ads/assets/${converted.id}`,
                                )
                              ).blob();
                              download(blob, "ad-video.mp4");
                              await reload();
                              setMessage(
                                "MP4 exported with H.264 video and AAC audio.",
                              );
                            })
                          }
                        >
                          Export MP4
                        </button>
                      </>
                    )}
                  </div>
                  {renderUrl && (
                    <video
                      src={renderUrl}
                      controls
                      className="w-full max-h-96"
                      aria-label="Rendered silent motion ad"
                    />
                  )}
                  {videoUrl && !renderUrl && (
                    <video
                      src={videoUrl}
                      controls
                      className="w-full max-h-96"
                      aria-label="Source video preview"
                    />
                  )}
                  {selectedDraft && (
                    <details className="text-sm">
                      <summary className="cursor-pointer">
                        Saved profile snapshot
                      </summary>
                      <p className="text-muted-foreground mt-2 whitespace-pre-wrap">
                        {selectedDraft.profile_snapshot.name}\n
                        {selectedDraft.profile_snapshot.product}\nAudience:{" "}
                        {selectedDraft.profile_snapshot.audience}
                      </p>
                    </details>
                  )}
                  {imageUrl && (
                    <p className="text-xs text-muted-foreground">
                      Image asset loaded from your private library.
                    </p>
                  )}
                </section>
              </div>
              {tab==='video'&&<section className="owner-panel editor-timeline"><VideoControls draft={draft} assets={library?.assets||[]} disabled={!!busy} onChange={patchDraft} onPreview={scene=>void previewScene(scene)}/></section>}
            </>
          )}
          {library?.jobs.length ? (
            <section className="owner-panel">
              <h3 className="font-display text-lg font-semibold">
                AI video jobs
              </h3>
              <div className="divide-y divide-border mt-3">
                {library.jobs.map((job) => (
                  <div className="py-4 space-y-2" key={job.id}>
                    <div className="flex flex-wrap justify-between gap-3">
                      <p className="text-sm font-medium break-words">
                        {job.prompt}
                      </p>
                      <span className="text-xs">{job.status}</span>
                    </div>
                    {job.error && (
                      <p className="text-sm text-destructive">{job.error}</p>
                    )}
                    <div className="flex flex-wrap gap-2">
                      {job.status === "processing" && (
                        <button
                          className="owner-button-secondary"
                          disabled={!!busy}
                          onClick={() =>
                            void act(job.id, async () => {
                              const next = await apiCall<AdVideoJob>(
                                `/api/v1/ads/video/${job.id}/check`,
                                "POST",
                              );
                              await reload();
                              setMessage(
                                next.status === "processing"
                                  ? "The provider is still generating. Check again shortly."
                                  : next.status === "completed"
                                    ? "Video saved to your private asset library."
                                    : next.error || "Video generation failed.",
                              );
                            })
                          }
                        >
                          Check status
                        </button>
                      )}
                      {job.asset_id && (
                        <>
                          <button
                            className="owner-button-secondary"
                            onClick={() => {
                              change("video_asset_id", job.asset_id);
                              setTab("video");
                            }}
                          >
                            Use in editor
                          </button>
                          <button
                            className="owner-button-secondary"
                            disabled={!!busy}
                            onClick={() =>
                              void act("download", async () => {
                                const response = await authenticatedFetch(
                                  `/api/v1/ads/assets/${job.asset_id}`,
                                );
                                download(
                                  await response.blob(),
                                  "generated-ad.mp4",
                                );
                              })
                            }
                          >
                            Download MP4
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </div>
      </div>
    </div>
  );
}
