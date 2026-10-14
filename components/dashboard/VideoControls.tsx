import { useState } from "react";
import { ArrowDown, ArrowUp, Copy, Plus, Scissors, Trash2 } from "lucide-react";
import type { AdAsset, AdDraftInput, VideoScene } from "../../types/ads";

export default function VideoControls({
  draft,
  assets,
  disabled,
  onChange,
  onPreview,
}: {
  draft: AdDraftInput;
  assets: AdAsset[];
  disabled: boolean;
  onChange: (patch: Partial<AdDraftInput>) => void;
  onPreview: (scene: VideoScene) => void;
}) {
  const scenes = draft.scenes || [];
  const [selected, setSelected] = useState("");
  const [split, setSplit] = useState(2);
  const [zoom, setZoom] = useState(48);
  const [playhead, setPlayhead] = useState(0);
  const [error, setError] = useState('');
  const active = scenes.find((scene) => scene.id === selected);
  const total = scenes.reduce((sum, scene) => sum + scene.duration, 0);
  const setScenes = (next: VideoScene[]) => {
    const duration=next.reduce((sum,s)=>sum+s.duration,0);
    if(next.length>20||duration>120||next.some(s=>!Number.isFinite(s.duration)||s.duration<.5||s.duration>30||!Number.isFinite(s.source_start)||s.source_start<0)){
      setError('Use 0.5–30 seconds per clip, at most 20 clips and 120 seconds total.');return;
    }
    setError('');onChange({scenes:next,duration:next.length?duration:draft.duration});
  };
  const update = (patch: Partial<VideoScene>) =>
    setScenes(
      scenes.map((scene) =>
        scene.id === selected ? { ...scene, ...patch } : scene,
      ),
    );
  return (
    <fieldset
      disabled={disabled}
      className="space-y-4 border-t border-border pt-4"
    >
      <legend className="font-display font-semibold pt-4">
        Video timeline
      </legend>
      <p className="text-xs text-muted-foreground">
        Up to 20 scenes / 120 seconds. Each scene can use a different private
        image or video, trim point and caption. Source audio and soundtrack are
        mixed at export.
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="owner-button-secondary"
          disabled={scenes.length >= 20 || total > 116}
          onClick={() => {
            const scene: VideoScene = {
              id: crypto.randomUUID(),
              caption: draft.headline || "",
              duration: 4,
              source_start: 0,
              asset_id: draft.video_asset_id || draft.asset_id,
              transition: "cut",
            };
            setScenes([...scenes, scene]);
            setSelected(scene.id);
          }}
        >
          <Plus className="w-4 h-4" />
          Add scene
        </button>
        <button
          type="button"
          className="owner-button-secondary"
          onClick={() => {
            const lines = draft.script.split("\n").filter(Boolean).slice(0, 20);
            if (!lines.length) return;
            if(scenes.length&&!confirm('Replace the current timeline with scenes from the script? Undo can restore it.'))return;
            const next = lines.map((caption) => ({
              id: crypto.randomUUID(),
              caption,
              duration: 4,
              source_start: 0,
              asset_id: draft.asset_id,
              transition: "fade" as const,
            }));
            setScenes(next);
            setSelected(next[0].id);
          }}
        >
          Build from script
        </button>
        <span className="self-center text-sm tabular-nums">
          {total.toFixed(1)}s / 120s
        </span>
      </div>
      {error&&<p className="owner-error" role="alert">{error}</p>}
      <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
        <label className="text-xs flex gap-2 items-center">Timeline zoom<input aria-label="Timeline zoom" type="range" min="48" max="120" step="12" value={zoom} onChange={e=>setZoom(Number(e.target.value))}/></label>
        <label className="text-xs w-full sm:flex-1 min-w-0">Playhead {playhead.toFixed(1)}s
          <input aria-label="Timeline playhead" className="w-full accent-primary" type="range" min="0" max={total||1} step="0.1" value={Math.min(playhead,total)} disabled={!scenes.length} onChange={e=>{
            const time=Number(e.target.value);setPlayhead(time);let elapsed=0;
            const scene=scenes.find(s=>{elapsed+=s.duration;return time<elapsed;})||scenes.at(-1);
            if(scene){
              setSelected(scene.id);setSplit(Math.max(.5,Math.min(scene.duration-.5,time-(elapsed-scene.duration))));
              onPreview({...scene,source_start:scene.source_start+Math.max(0,time-(elapsed-scene.duration))});
            }
          }}/>
        </label>
      </div>
      <div className="overflow-x-auto">
        <div className="relative py-2" style={{width:Math.max(400,total*zoom)}}>
          <div className="relative h-6 text-[10px] text-muted-foreground border-b border-border">{Array.from({length:Math.ceil(total)+1},(_,second)=><span key={second} className="absolute border-l border-border pl-1" style={{left:second*zoom}}>{second%5===0?`${second}s`:''}</span>)}</div>
          <div className="flex gap-0.5 py-3">
          {scenes.map((scene, index) => (
            <button
              type="button"
              draggable={!disabled}
              onDragStart={event=>event.dataTransfer.setData('text/plain',scene.id)}
              onDragOver={event=>event.preventDefault()}
              onDrop={event=>{event.preventDefault();const id=event.dataTransfer.getData('text/plain');const source=scenes.find(s=>s.id===id);if(!source||id===scene.id)return;const next=scenes.filter(s=>s.id!==id);next.splice(next.findIndex(s=>s.id===scene.id),0,source);setScenes(next);}}
              aria-pressed={selected===scene.id}
              className={`rounded-lg p-2 text-left border shrink-0 overflow-hidden ${selected === scene.id ? "border-primary bg-primary/10" : "border-border bg-muted"}`}
              style={{width:Math.max(18,scene.duration*zoom-2)}}
              key={scene.id}
              onClick={() => {
                setSelected(scene.id);
                onPreview(scene);
              }}
            >
              <span className="block text-xs text-muted-foreground">
                Scene {index + 1} · {scene.duration}s
              </span>
              <span className="block text-sm mt-1 truncate">
                {scene.caption || "No caption"}
              </span>
              <span className="block text-xs mt-2 text-muted-foreground">
                {scene.transition} · trim {scene.source_start}s
              </span>
            </button>
          ))}
          </div><div className="pointer-events-none absolute top-0 bottom-0 w-px bg-primary" style={{left:playhead*zoom}}/>
        </div>
      </div>
      <p className="text-xs text-muted-foreground">Drag clips to reorder, or use Earlier/Later. Clip widths represent duration. Scrub the playhead to preview; render for real-time playback.</p>
      {active && (
        <div className="space-y-4">
          <label className="owner-label">
            Scene caption
            <textarea
              className="owner-input"
              rows={3}
              maxLength={500}
              value={active.caption}
              onChange={(e) => update({ caption: e.target.value })}
            />
          </label>
          <label className="owner-label">
            Scene media
            <select
              className="owner-input"
              value={active.asset_id || ""}
              onChange={(e) => update({ asset_id: e.target.value || null })}
            >
              <option value="">Use main image / video</option>
              {assets
                .filter(
                  (a) =>
                    a.mime.startsWith("image/") || a.mime.startsWith("video/"),
                )
                .map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
            </select>
          </label>
          <div className="grid sm:grid-cols-3 gap-3">
            <label className="owner-label">
              Scene duration
              <input
                className="owner-input"
                type="number"
                min="0.5"
                max="30"
                step="0.5"
                value={active.duration}
                onChange={(e) => update({ duration: Number(e.target.value) })}
              />
            </label>
            <label className="owner-label">
              Trim start (seconds)
              <input
                className="owner-input"
                type="number"
                min="0"
                max="3600"
                step="0.1"
                value={active.source_start}
                onChange={(e) =>
                  update({ source_start: Number(e.target.value) })
                }
              />
            </label>
            <label className="owner-label">
              Caption transition
              <select
                className="owner-input"
                value={active.transition}
                onChange={(e) =>
                  update({
                    transition: e.target.value as VideoScene["transition"],
                  })
                }
              >
                <option value="cut">Cut</option>
                <option value="fade">Fade in</option>
              </select>
            </label>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="owner-button-secondary"
              disabled={scenes.indexOf(active)===0}
              onClick={() => {
                const index = scenes.indexOf(active);
                if (index === 0) return;
                const next = [...scenes];
                [next[index - 1], next[index]] = [next[index], next[index - 1]];
                setScenes(next);
              }}
            >
              <ArrowUp className="w-4 h-4" />
              Earlier
            </button>
            <button
              type="button"
              className="owner-button-secondary"
              disabled={scenes.indexOf(active)===scenes.length-1}
              onClick={() => {
                const index = scenes.indexOf(active);
                if (index === scenes.length - 1) return;
                const next = [...scenes];
                [next[index + 1], next[index]] = [next[index], next[index + 1]];
                setScenes(next);
              }}
            >
              <ArrowDown className="w-4 h-4" />
              Later
            </button>
            <button
              type="button"
              className="owner-button-secondary"
              disabled={scenes.length >= 20 || total + active.duration > 120}
              onClick={() => {
                const copy = { ...active, id: crypto.randomUUID() };
                setScenes([
                  ...scenes.slice(0, scenes.indexOf(active) + 1),
                  copy,
                  ...scenes.slice(scenes.indexOf(active) + 1),
                ]);
                setSelected(copy.id);
              }}
            >
              <Copy className="w-4 h-4" />
              Duplicate
            </button>
            <button
              type="button"
              className="owner-button-secondary"
              onClick={() => {
                setScenes(scenes.filter((s) => s.id !== active.id));
                setSelected("");
              }}
            >
              <Trash2 className="w-4 h-4" />
              Remove
            </button>
          </div>
          <div className="flex flex-wrap gap-3 items-end">
            <label className="owner-label">
              Split after (seconds)
              <input
                className="owner-input"
                type="number"
                min="0.5"
                step="0.5"
                max={active.duration - 0.5}
                value={split}
                onChange={(e) => setSplit(Number(e.target.value))}
              />
            </label>
            <button
              type="button"
              className="owner-button-secondary"
              disabled={
                !Number.isFinite(split) || split < 0.5 ||
                split > active.duration - 0.5 ||
                scenes.length >= 20
              }
              onClick={() => {
                const index = scenes.indexOf(active);
                const right = {
                  ...active,
                  id: crypto.randomUUID(),
                  duration: active.duration - split,
                  source_start: active.source_start + split,
                };
                setScenes([
                  ...scenes.slice(0, index),
                  { ...active, duration: split },
                  right,
                  ...scenes.slice(index + 1),
                ]);
              }}
            >
              <Scissors className="w-4 h-4" />
              Split scene
            </button>
          </div>
        </div>
      )}
      <div className="grid sm:grid-cols-2 gap-4 border-t border-border pt-4">
        <label className="owner-label sm:col-span-2">
          Soundtrack
          <select
            className="owner-input"
            value={draft.audio_asset_id || ""}
            onChange={(e) =>
              onChange({ audio_asset_id: e.target.value || null })
            }
          >
            <option value="">No soundtrack</option>
            {assets
              .filter((a) => a.mime.startsWith("audio/"))
              .map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
          </select>
        </label>
        <label className="owner-label">
          Soundtrack volume {Math.round((draft.audio_volume ?? 0.5) * 100)}%
          <input
            className="w-full accent-primary"
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={draft.audio_volume ?? 0.5}
            onChange={(e) => onChange({ audio_volume: Number(e.target.value) })}
          />
        </label>
        <label className="owner-label">
          Source video volume {Math.round((draft.source_volume ?? 0) * 100)}%
          <input
            className="w-full accent-primary"
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={draft.source_volume ?? 0}
            onChange={(e) =>
              onChange({ source_volume: Number(e.target.value) })
            }
          />
        </label>
      </div>
    </fieldset>
  );
}
