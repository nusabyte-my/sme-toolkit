import { useState } from "react";
import { ArrowDown, ArrowUp, Plus, Trash2 } from "lucide-react";
import type { AdDraftInput, CreativeLayer, ImageStyle } from "../../types/ads";
import { defaultImageStyle } from "../../utils/adMedia";

interface Props {
  draft: AdDraftInput;
  disabled: boolean;
  onChange: (patch: Partial<AdDraftInput>) => void;
  selected: string;
  onSelect: (id: string) => void;
}
export default function ImageControls({ draft, disabled, onChange, selected, onSelect: setSelected }: Props) {
  const [panel, setPanel] = useState<'layers'|'adjust'>('layers');
  const style = { ...defaultImageStyle, ...draft.image_style };
  const layers = draft.layers || [];
  const active = layers.find((layer) => layer.id === selected);
  const styleValue = (
    key: keyof ImageStyle,
    value: number | string | boolean,
  ) => onChange({ image_style: { ...style, [key]: value } });
  const updateLayer = (patch: Partial<CreativeLayer>) =>
    onChange({
      layers: layers.map((layer) =>
        layer.id === selected ? { ...layer, ...patch } : layer,
      ),
    });
  return (
    <fieldset
      className="space-y-4 border-t border-border pt-4"
      disabled={disabled}
    >
      <legend className="font-display font-semibold pt-4">
        Composition and layers
      </legend>
      <div className="flex gap-2"><button type="button" className={panel==='layers'?'owner-button':'owner-button-secondary'} aria-pressed={panel==='layers'} onClick={()=>setPanel('layers')}>Layers</button><button type="button" className={panel==='adjust'?'owner-button':'owner-button-secondary'} aria-pressed={panel==='adjust'} onClick={()=>setPanel('adjust')}>Adjust image</button></div>
      {panel==='adjust'&&<>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="owner-button-secondary"
          onClick={() => onChange({ image_style: { ...defaultImageStyle } })}
        >
          Reset adjustments
        </button>
        <button
          type="button"
          className="owner-button-secondary"
          onClick={() =>
            styleValue(
              "rotation",
              ((style.rotation + 90) % 360) as ImageStyle["rotation"],
            )
          }
        >
          Rotate 90°
        </button>
        <button
          type="button"
          className="owner-button-secondary"
          aria-pressed={style.flip_x}
          onClick={() => styleValue("flip_x", !style.flip_x)}
        >
          Flip horizontal
        </button>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {(
          [
            ["brightness", "Brightness", 0, 200, 1],
            ["contrast", "Contrast", 0, 200, 1],
            ["saturation", "Saturation", 0, 200, 1],
            ["grayscale", "Grayscale", 0, 100, 1],
            ["blur", "Blur", 0, 12, 0.2],
            ["zoom", "Crop zoom", 1, 3, 0.05],
            ["focal_x", "Crop X", 0, 100, 1],
            ["focal_y", "Crop Y", 0, 100, 1],
            ["overlay", "Background shade", 0, 1, 0.05],
            ["text_x", "Headline X", 0, 70, 1],
            ["text_y", "Headline Y", 0, 80, 1],
            ["font_scale", "Headline size", 0.4, 2, 0.05],
          ] as const
        ).map(([key, label, min, max, step]) => (
          <label className="owner-label" key={key}>
            {label}{" "}
            <span className="text-xs text-muted-foreground">{style[key]}</span>
            <input
              className="w-full accent-primary"
              type="range"
              min={min}
              max={max}
              step={step}
              value={style[key]}
              onChange={(e) => styleValue(key, Number(e.target.value))}
            />
          </label>
        ))}
        <label className="owner-label">
          Headline colour
          <input
            className="owner-input h-11"
            type="color"
            value={style.text_color}
            onChange={(e) => styleValue("text_color", e.target.value)}
          />
        </label>
      </div>
      </>}
      {panel==='layers'&&<>
      <button type="button" className={`w-full text-left text-sm p-3 rounded-lg border ${selected==='headline'?'border-primary bg-primary/10':'border-border'}`} onClick={()=>setSelected('headline')}>Headline · {draft.headline||'No headline yet'}</button>
      <div className="border-t border-border pt-4 space-y-3">
        <h4 className="font-semibold text-sm">
          Overlay layers · {layers.length}/20
        </h4>
        <div className="flex flex-wrap gap-2">
          {(["text", "rectangle"] as const).map((type) => (
            <button
              type="button"
              className="owner-button-secondary"
              key={type}
              disabled={layers.length >= 20}
              onClick={() => {
                const layer: CreativeLayer = {
                  id: crypto.randomUUID(),
                  type,
                  text: type === "text" ? "Your supporting message" : "",
                  x: 10,
                  y: 20,
                  width: 65,
                  height: 12,
                  font_size: 4,
                  color: type === "text" ? "#FFFFFF" : "#A3E635",
                  opacity: 1,
                  visible: true,
                };
                onChange({ layers: [...layers, layer] });
                setSelected(layer.id);
              }}
            >
              <Plus className="w-4 h-4" />
              Add {type}
            </button>
          ))}
        </div>
        <div className="space-y-1">
          {layers.map((layer, index) => (
            <div
              key={layer.id}
              className={`flex gap-2 items-center p-2 border rounded-lg ${selected === layer.id ? "border-primary" : "border-border"}`}
            >
              <input
                type="checkbox"
                checked={layer.visible}
                aria-label={`Show layer ${index + 1}`}
                onChange={(e) =>
                  onChange({
                    layers: layers.map((item) =>
                      item.id === layer.id
                        ? { ...item, visible: e.target.checked }
                        : item,
                    ),
                  })
                }
              />
              <button
                type="button"
                className="flex-1 text-left text-sm truncate"
                onClick={() => setSelected(layer.id)}
              >
                {index + 1}.{" "}
                {layer.type === "text"
                  ? layer.text || "Text layer"
                  : "Rectangle"}
              </button>
              <button
                type="button"
                className="p-2"
                aria-label={`Move layer ${index + 1} down`}
                disabled={index === 0}
                onClick={() => {
                  const next = [...layers];
                  [next[index - 1], next[index]] = [
                    next[index],
                    next[index - 1],
                  ];
                  onChange({ layers: next });
                }}
              >
                <ArrowDown className="w-4 h-4" />
              </button>
              <button
                type="button"
                className="p-2"
                aria-label={`Move layer ${index + 1} up`}
                disabled={index === layers.length - 1}
                onClick={() => {
                  const next = [...layers];
                  [next[index + 1], next[index]] = [
                    next[index],
                    next[index + 1],
                  ];
                  onChange({ layers: next });
                }}
              >
                <ArrowUp className="w-4 h-4" />
              </button>
              <button
                type="button"
                className="p-2 text-destructive"
                aria-label={`Delete layer ${index + 1}`}
                onClick={() =>
                  onChange({
                    layers: layers.filter((item) => item.id !== layer.id),
                  })
                }
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">Select a layer here or on the canvas. Drag to position; arrow keys move it precisely. Undo restores deleted layers.</p>
        {active && (
          <div className="space-y-3 bg-muted/40 p-3 rounded-lg">
            {active.type === "text" && (
              <label className="owner-label">
                Layer text
                <textarea
                  className="owner-input"
                  rows={2}
                  maxLength={400}
                  value={active.text}
                  onChange={(e) => updateLayer({ text: e.target.value })}
                />
              </label>
            )}
            <div className="grid grid-cols-2 gap-3">
              {(
                ["x", "y", "width", "height", "font_size", "opacity"] as const
              ).map((key) => (
                <label className="owner-label" key={key}>
                  {key.replace("_", " ")}
                  <input
                    className="owner-input"
                    type="number"
                    step={key === "opacity" ? 0.1 : 1}
                    min={
                      key === "width" || key === "height" || key === "font_size"
                        ? 1
                        : 0
                    }
                    max={key === "opacity" ? 1 : key === "font_size" ? 15 : 100}
                    value={active[key]}
                    onChange={(e) =>
                      updateLayer({ [key]: Number(e.target.value) })
                    }
                  />
                </label>
              ))}
              <label className="owner-label">
                Layer colour
                <input
                  className="owner-input h-11"
                  type="color"
                  value={active.color}
                  onChange={(e) => updateLayer({ color: e.target.value })}
                />
              </label>
            </div>
          </div>
        )}
      </div>
      </>}
    </fieldset>
  );
}
