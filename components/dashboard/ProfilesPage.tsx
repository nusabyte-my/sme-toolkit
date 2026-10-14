import { useEffect, useState } from "react";
import { Building2, Image as ImageIcon, Save, Trash2 } from "lucide-react";
import { useOwner } from "../../contexts/OwnerContext";
import { apiCall } from "../../services/apiClient";
import type { BusinessContext, BusinessContextInput } from "../../types/owner";
import { useUnsavedChanges } from "../../hooks/useUnsavedChanges";

const empty: BusinessContextInput = {
  company_name: "",
  industry: "",
  business_description: "",
  products_services: "",
  target_market: "",
  brand_voice: "",
  goals: "",
  currency: "MYR",
  timezone: "Asia/Kuala_Lumpur",
  website: "",
  proof_points: "",
  constraints: "",
  logo_data_url: "",
};
export default function ProfilesPage() {
  const { overview, loading, error: loadError, refresh } = useOwner();
  const [form, setForm] = useState(empty);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [logoError, setLogoError] = useState("");
  useEffect(() => {
    if (!dirty && overview?.context) {
      const { id, updated_at, is_demo, ...values } = overview.context;
      setForm({ ...empty, ...values, logo_data_url: values.logo_data_url || "" });
    }
  }, [overview, dirty]);
  useUnsavedChanges(dirty || busy);
  const set = (key: keyof BusinessContextInput, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setDirty(true);
    setMessage("");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <Building2 className="h-7 w-7 text-primary shrink-0" />
        <div>
          <h2 className="text-2xl font-display font-bold">Business context</h2>
          <p className="mt-1 text-muted-foreground max-w-prose">
            Tell the workspace what you sell, who you serve, and what you want
            to improve. Agents and ad profiles use these facts.
          </p>
        </div>
      </div>
      {loadError && (
        <div className="owner-error" role="alert">
          {loadError}
          <button className="ml-3 underline" onClick={() => void refresh()}>
            Retry loading
          </button>
        </div>
      )}
      <form
        className="owner-panel space-y-6"
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          setError("");
          setMessage("");
          try {
            await apiCall<BusinessContext>(
              "/api/v1/owner/context",
              "PUT",
              form,
            );
            setDirty(false);
            await refresh();
            setMessage(
              "Business context saved. New agent runs will use these facts.",
            );
          } catch (err) {
            setError(
              err instanceof Error
                ? err.message
                : "Save failed. Your edits are still here.",
            );
          } finally {
            setBusy(false);
          }
        }}
      >
        <fieldset
          disabled={busy || (loading && !overview)}
          className="space-y-5"
        >
          <legend className="font-display font-semibold mb-4">
            Business identity
          </legend>
          <div className="grid md:grid-cols-2 gap-5">
            <div className="md:col-span-2">
              <label className="owner-label">
                Company logo
                <span className="text-xs font-normal text-muted-foreground block mt-0.5">
                  PNG, JPEG, or WebP (max 200KB). Displayed on your quotations and invoices.
                </span>
              </label>
              <div className="mt-2 flex flex-wrap items-center gap-4">
                {form.logo_data_url ? (
                  <div className="flex items-center gap-3">
                    <img
                      src={form.logo_data_url}
                      alt="Company logo"
                      className="w-16 h-16 rounded border border-border object-contain bg-background p-1 shadow-sm"
                    />
                    <button
                      type="button"
                      className="owner-button-secondary !py-1 !px-2.5 text-xs text-destructive hover:text-destructive flex items-center gap-1.5"
                      onClick={() => {
                        set("logo_data_url", "");
                        setLogoError("");
                      }}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Remove logo
                    </button>
                  </div>
                ) : (
                  <div className="w-16 h-16 rounded border border-dashed border-border flex items-center justify-center text-muted-foreground bg-muted/30">
                    <ImageIcon className="w-6 h-6 opacity-40" />
                  </div>
                )}
                <div className="flex-1 min-w-[200px]">
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    className="block w-full text-xs text-muted-foreground file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-secondary file:text-secondary-foreground hover:file:bg-secondary/80 cursor-pointer"
                    onChange={(e) => {
                      setLogoError("");
                      const file = e.target.files?.[0];
                      if (!file) return;
                      const validTypes = ["image/png", "image/jpeg", "image/webp"];
                      if (!validTypes.includes(file.type)) {
                        setLogoError("Please select a PNG, JPEG, or WebP image.");
                        e.target.value = "";
                        return;
                      }
                      if (file.size > 200 * 1024) {
                        setLogoError("Logo file must be smaller than 200KB.");
                        e.target.value = "";
                        return;
                      }
                      const reader = new FileReader();
                      reader.onload = () => {
                        if (typeof reader.result === "string") {
                          set("logo_data_url", reader.result);
                        }
                      };
                      reader.onerror = () => {
                        setLogoError("Failed to read image file.");
                      };
                      reader.readAsDataURL(file);
                    }}
                  />
                  {logoError && (
                    <p className="text-xs text-destructive mt-1 font-medium">{logoError}</p>
                  )}
                </div>
              </div>
            </div>
            <label className="owner-label">
              Business name (required)
              <input
                className="owner-input"
                value={form.company_name}
                onChange={(e) => set("company_name", e.target.value)}
                required
                maxLength={160}
              />
            </label>
            <label className="owner-label">
              Industry
              <input
                className="owner-input"
                value={form.industry}
                onChange={(e) => set("industry", e.target.value)}
                maxLength={160}
                placeholder="Retail, professional services, food…"
              />
            </label>
            <label className="owner-label md:col-span-2">
              What does your business do?
              <textarea
                className="owner-input"
                rows={3}
                value={form.business_description}
                onChange={(e) => set("business_description", e.target.value)}
                maxLength={4000}
              />
            </label>
            <label className="owner-label">
              Products and services
              <textarea
                className="owner-input"
                rows={4}
                value={form.products_services}
                onChange={(e) => set("products_services", e.target.value)}
                maxLength={4000}
              />
            </label>
            <label className="owner-label">
              Target customers
              <textarea
                className="owner-input"
                rows={4}
                value={form.target_market}
                onChange={(e) => set("target_market", e.target.value)}
                maxLength={2000}
              />
            </label>
            <label className="owner-label">
              Business goals
              <textarea
                className="owner-input"
                rows={3}
                value={form.goals}
                onChange={(e) => set("goals", e.target.value)}
                maxLength={2000}
              />
            </label>
            <label className="owner-label">
              Brand voice and boundaries
              <textarea
                className="owner-input"
                rows={3}
                value={form.brand_voice}
                onChange={(e) => set("brand_voice", e.target.value)}
                maxLength={1000}
                placeholder="Tone, languages, claims to avoid…"
              />
            </label>
            <label className="owner-label">
              Reporting currency
              <input
                className="owner-input"
                value={form.currency}
                onChange={(e) => set("currency", e.target.value.toUpperCase())}
                pattern="[A-Z]{3}"
                maxLength={3}
                required
              />
              <span className="text-xs text-muted-foreground">
                ISO code, such as MYR, USD or SGD. Different currencies are not
                combined.
              </span>
            </label>
            <label className="owner-label">
              Business timezone
              <input
                className="owner-input"
                value={form.timezone}
                onChange={(e) => set("timezone", e.target.value)}
                maxLength={80}
                required
              />
              <span className="text-xs text-muted-foreground">
                IANA timezone, such as Asia/Kuala_Lumpur or Europe/London.
              </span>
            </label>
            <label className="owner-label md:col-span-2">
              Website (optional)
              <input
                className="owner-input"
                type="url"
                value={form.website}
                onChange={(e) => set("website", e.target.value)}
                maxLength={500}
                placeholder="https://your-business.com"
              />
            </label>
            <label className="owner-label">
              Verified proof points
              <textarea
                className="owner-input"
                rows={4}
                maxLength={4000}
                value={form.proof_points}
                onChange={(e) => set("proof_points", e.target.value)}
              />
              <span className="text-xs text-muted-foreground">
                Only claims, certifications or testimonials you can
                substantiate. Used to ground ad copy.
              </span>
            </label>
            <label className="owner-label">
              Operating constraints
              <textarea
                className="owner-input"
                rows={4}
                maxLength={4000}
                value={form.constraints}
                onChange={(e) => set("constraints", e.target.value)}
              />
              <span className="text-xs text-muted-foreground">
                Capacity, budget, regulatory limits and promises agents must not
                make.
              </span>
            </label>
          </div>
        </fieldset>
        <p className="text-sm text-muted-foreground">
          Keep passwords, API keys and sensitive customer information out of
          business context. AI requests may send these facts to your configured
          provider.
        </p>
        {error && (
          <p className="owner-error" role="alert">
            {error}
          </p>
        )}
        {message && (
          <p role="status" className="text-sm text-foreground">
            {message}
          </p>
        )}
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="owner-button"
            disabled={busy || !form.company_name.trim()}
          >
            <Save className="w-4 h-4" />
            {busy ? "Saving context…" : "Save business context"}
          </button>
          <span className="text-xs text-muted-foreground">
            {dirty
              ? "Unsaved changes — save before leaving this page."
              : overview?.context
                ? `Last saved ${new Date(overview.context.updated_at).toLocaleString()}`
                : "No business saved yet."}
          </span>
        </div>
      </form>
    </div>
  );
}
