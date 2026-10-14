import { useCallback, useEffect, useState } from "react";
import { BarChart3, RefreshCw, Target } from "lucide-react";
import { apiCall } from "../../services/apiClient";
import { useOwner } from "../../contexts/OwnerContext";
import WorkspaceLoading from '../common/WorkspaceLoading';

interface AdMetrics {
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number | null;
  cpc: number | null;
  cpa: number | null;
  cvr: number | null;
  roas: number | null;
}
interface Targets {
  target_cpa: number | null;
  target_roas: number | null;
  min_impressions: number;
  min_conversions: number;
  conversion_lag_days: number;
}
interface AdReport {
  items: {
    platform: string;
    campaign: string;
    creative: string;
    currency: string;
    attribution: string;
    current: AdMetrics;
    previous: AdMetrics;
    state: string;
    notes: string[];
    observed_days: number;
  }[];
  targets: Targets;
  start: string;
  end: string;
  previous_start: string;
  currency: string;
  days: number;
  caveat: string;
}
const blank = {
  day: "",
  platform: "Meta",
  campaign: "",
  creative: "",
  currency: "MYR",
  attribution: "7-day click",
  impressions: "",
  clicks: "",
  conversions: "",
  spend: "",
  revenue: "",
};
export default function AdOptimization() {
  const { overview } = useOwner();
  const [report, setReport] = useState<AdReport | null>(null),
    [days, setDays] = useState(14),
    [form, setForm] = useState(blank),
    [csv, setCsv] = useState("");
  const [targets, setTargets] = useState<Targets>({
    target_cpa: null,
    target_roas: null,
    min_impressions: 1000,
    min_conversions: 10,
    conversion_lag_days: 3,
  });
  const [busy, setBusy] = useState(""),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  const load = useCallback(async () => {
    const next = await apiCall<AdReport>(
      `/api/v1/ad-optimization/?days=${days}`,
    );
    setReport(next);
    setTargets(next.targets);
  }, [days]);
  useEffect(() => {
    let active = true;
    if (overview?.context) {
      apiCall<AdReport>(`/api/v1/ad-optimization/?days=${days}`)
        .then((next) => {
          if (active) {
            setReport(next);
            setTargets(next.targets);
            setError("");
          }
        })
        .catch((err) => {
          if (active) setError(err.message);
        });
      setForm((prev) => ({ ...prev, currency: overview.context!.currency }));
    }
    return () => {
      active = false;
    };
  }, [overview?.context?.id, days]);
  if (!overview?.context)
    return (
      <section className="owner-panel">
        <h2 className="font-display text-2xl font-bold">Ad optimization</h2>
        <p className="my-4">
          Save business context to track campaign efficiency.
        </p>
        <a className="owner-button" href="#/profiles">
          Set up business context
        </a>
      </section>
    );
  if (!report && !error) return <WorkspaceLoading label="ad performance" />;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-primary" />
            Ad optimization
          </h2>
          <p className="text-muted-foreground mt-2 max-w-prose">
            Find where to investigate, what to test and when evidence is too
            weak. No automatic pauses, bids or budget changes.
          </p>
        </div>
        <button
          className="owner-button-secondary"
          disabled={!!busy}
          onClick={() => load().catch((err) => setError(err.message))}
        >
          <RefreshCw className="w-4 h-4" />
          Refresh analysis
        </button>
      </div>
      {error && (
        <p role="alert" className="owner-error">
          {error}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      <form
        className="owner-panel space-y-4"
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy("targets");
          setError("");
          try {
            await apiCall("/api/v1/ad-optimization/targets", "PUT", targets);
            await load();
            setMessage(
              "Decision thresholds saved. Live campaigns are unchanged.",
            );
          } catch (err) {
            setError(
              err instanceof Error
                ? err.message
                : "Targets could not be saved.",
            );
          } finally {
            setBusy("");
          }
        }}
      >
        <h3 className="font-display text-lg font-semibold flex gap-2">
          <Target className="w-5 h-5 text-primary" />
          Your decision thresholds
        </h3>
        <div className="grid sm:grid-cols-2 xl:grid-cols-5 gap-4">
          <label className="owner-label">
            Target CPA ({overview.context.currency})
            <input
              className="owner-input"
              type="number"
              min="0.01"
              step="0.01"
              value={targets.target_cpa ?? ""}
              onChange={(e) =>
                setTargets({
                  ...targets,
                  target_cpa: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </label>
          <label className="owner-label">
            Target ROAS
            <input
              className="owner-input"
              type="number"
              min="0.01"
              step="0.01"
              value={targets.target_roas ?? ""}
              onChange={(e) =>
                setTargets({
                  ...targets,
                  target_roas: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </label>
          <label className="owner-label">
            Minimum impressions
            <input
              className="owner-input"
              type="number"
              min="100"
              max="1000000"
              value={targets.min_impressions}
              onChange={(e) =>
                setTargets({
                  ...targets,
                  min_impressions: Number(e.target.value),
                })
              }
            />
          </label>
          <label className="owner-label">
            Minimum conversions
            <input
              className="owner-input"
              type="number"
              min="1"
              max="1000"
              value={targets.min_conversions}
              onChange={(e) =>
                setTargets({
                  ...targets,
                  min_conversions: Number(e.target.value),
                })
              }
            />
          </label>
          <label className="owner-label">
            Conversion lag (days)
            <input
              className="owner-input"
              type="number"
              min="0"
              max="30"
              value={targets.conversion_lag_days}
              onChange={(e) =>
                setTargets({
                  ...targets,
                  conversion_lag_days: Number(e.target.value),
                })
              }
            />
          </label>
        </div>
        <p className="text-xs text-muted-foreground">
          Targets are your business assumptions, not industry benchmarks. Set
          lag from your actual conversion delay; recent days are excluded from
          decisions.
        </p>
        <button className="owner-button" disabled={!!busy}>
          Save thresholds
        </button>
      </form>
      <details className="owner-panel">
        <summary className="font-display text-lg font-semibold cursor-pointer">
          Add or import daily performance
        </summary>
        <p className="text-sm text-muted-foreground mt-3">
          One row per date/platform/campaign/creative/currency/attribution.
          Re-importing the same daily key updates that row; it never adds a
          duplicate total.
        </p>
        <form
          className="space-y-4 mt-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy("record");
            setError("");
            try {
              await apiCall("/api/v1/ad-optimization/records", "POST", {
                ...form,
                impressions: Number(form.impressions),
                clicks: Number(form.clicks),
                conversions: Number(form.conversions),
                spend: Number(form.spend),
                revenue: Number(form.revenue),
              });
              await load();
              setMessage(
                "Daily performance saved. Recent records may be excluded by conversion lag.",
              );
            } catch (err) {
              setError(err instanceof Error ? err.message : "Record failed.");
            } finally {
              setBusy("");
            }
          }}
        >
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(form).map(([key, value]) => (
              <label className="owner-label capitalize" key={key}>
                {key.replaceAll("_", " ")}
                {key === "platform" ? (
                  <select
                    className="owner-input"
                    value={value}
                    onChange={(e) =>
                      setForm({ ...form, platform: e.target.value })
                    }
                  >
                    {["Meta", "Google", "TikTok", "LinkedIn", "Other"].map(
                      (p) => (
                        <option key={p}>{p}</option>
                      ),
                    )}
                  </select>
                ) : (
                  <input
                    className="owner-input"
                    required
                    type={
                      key === "day"
                        ? "date"
                        : [
                              "impressions",
                              "clicks",
                              "conversions",
                              "spend",
                              "revenue",
                            ].includes(key)
                          ? "number"
                          : "text"
                    }
                    min={
                      [
                        "impressions",
                        "clicks",
                        "conversions",
                        "spend",
                        "revenue",
                      ].includes(key)
                        ? 0
                        : undefined
                    }
                    step={
                      ["spend", "revenue"].includes(key) ? "0.01" : undefined
                    }
                    maxLength={key === "currency" ? 3 : 160}
                    value={value}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        [key]:
                          key === "currency"
                            ? e.target.value.toUpperCase()
                            : e.target.value,
                      })
                    }
                  />
                )}
              </label>
            ))}
          </div>
          <button className="owner-button" disabled={!!busy}>
            Save daily performance
          </button>
        </form>
        <div className="border-t border-border mt-5 pt-5 space-y-3">
          <label className="owner-label">
            CSV data
            <textarea
              className="owner-input font-mono"
              rows={6}
              maxLength={1000000}
              value={csv}
              onChange={(e) => setCsv(e.target.value)}
              placeholder="day,platform,campaign,creative,currency,attribution,impressions,clicks,conversions,spend,revenue"
            />
          </label>
          <label className="owner-label">
            Import CSV file
            <input
              className="owner-input"
              type="file"
              accept=".csv,text/csv"
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                if (file.size > 1000000) {
                  setError("CSV exceeds 1 MB.");
                  return;
                }
                setCsv(await file.text());
              }}
            />
          </label>
          <button
            className="owner-button-secondary"
            disabled={!!busy || !csv.trim()}
            onClick={async () => {
              setBusy("import");
              setError("");
              try {
                const result = await apiCall<{
                  inserted: number;
                  updated: number;
                }>("/api/v1/ad-optimization/import", "POST", { csv_text: csv });
                await load();
                setMessage(
                  `${result.inserted} rows added; ${result.updated} daily rows updated.`,
                );
                setCsv("");
              } catch (err) {
                setError(err instanceof Error ? err.message : "Import failed.");
              } finally {
                setBusy("");
              }
            }}
          >
            Validate and import report
          </button>
        </div>
      </details>
      <section className="owner-panel">
        <div className="flex flex-wrap justify-between gap-4 items-end">
          <div>
            <h3 className="font-display text-lg font-semibold">
              Creative efficiency and next tests
            </h3>
            <p className="text-sm text-muted-foreground mt-2">
              {report
                ? `${report.start}–${report.end}; compared with the previous ${days} days.`
                : "Loading analysis…"}
            </p>
          </div>
          <label className="owner-label">
            Matched window
            <select
              className="owner-input"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            >
              {[7, 14, 30, 90].map((n) => (
                <option key={n} value={n}>
                  {n} days
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="text-xs text-muted-foreground mt-3">{report?.caveat}</p>
        <div className="overflow-x-auto mt-5">
          <table className="w-full text-sm min-w-[800px]">
            <thead className="bg-muted text-left">
              <tr>
                {[
                  "Creative / attribution",
                  "Spend",
                  "CTR",
                  "CPC",
                  "CPA",
                  "CVR",
                  "ROAS",
                  "Decision",
                ].map((label) => (
                  <th key={label} className="p-3">
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {report?.items.map((item, i) => (
                <tr key={i}>
                  <td className="p-3">
                    <p className="font-medium">{item.creative}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.platform} · {item.campaign}
                      <br />
                      {item.attribution} · {item.currency} ·{" "}
                      {item.observed_days} observed days
                    </p>
                  </td>
                  <td className="p-3 tabular-nums">
                    {item.current.spend.toFixed(2)}
                  </td>
                  {(["ctr", "cpc", "cpa", "cvr", "roas"] as const).map(
                    (key) => (
                      <td key={key} className="p-3 tabular-nums">
                        {item.current[key] === null
                          ? "—"
                          : `${item.current[key]}${["ctr", "cvr"].includes(key) ? "%" : ""}`}
                      </td>
                    ),
                  )}
                  <td className="p-3">
                    <span className="font-medium capitalize">
                      {item.state.replaceAll("_", " ")}
                    </span>
                    <details className="mt-2">
                      <summary className="cursor-pointer text-primary">
                        Evidence and next steps
                      </summary>
                      <ul className="mt-3 space-y-2 max-w-sm">
                        {item.notes.map((note) => (
                          <li key={note}>{note}</li>
                        ))}
                      </ul>
                      <p className="mt-2 text-xs">
                        {item.current.impressions} impressions ·{" "}
                        {item.current.clicks} clicks ·{" "}
                        {item.current.conversions} conversions. Attributed
                        revenue {item.current.revenue.toFixed(2)}{" "}
                        {item.currency}.
                      </p>
                      <button
                        className="owner-button-secondary mt-3"
                        disabled={!!busy}
                        onClick={async () => {
                          setBusy("task");
                          try {
                            await apiCall("/api/v1/workspace/tasks", "POST", {
                              title: `Review ${item.creative}`.slice(0, 180),
                              notes: item.notes.join("\n"),
                            });
                            setMessage(
                              "Optimization review added to owner actions.",
                            );
                          } catch (err) {
                            setError(
                              err instanceof Error
                                ? err.message
                                : "Action save failed.",
                            );
                          } finally {
                            setBusy("");
                          }
                        }}
                      >
                        Create review action
                      </button>
                    </details>
                  </td>
                </tr>
              ))}
              {!report?.items.length && (
                <tr>
                  <td
                    colSpan={8}
                    className="p-8 text-center text-muted-foreground"
                  >
                    No mature performance data in this window. Import daily
                    results or adjust conversion lag.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
      <section className="owner-panel">
        <h3 className="font-display font-semibold">Creative experiment loop</h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-prose">
          Choose one change: hook, visual, offer or CTA. Keep the audience,
          attribution window and measurement period comparable. Platform
          delivery is not randomized; this report does not declare statistical
          A/B winners. Check tracking and qualified lead quality before scaling.
        </p>
        <a className="owner-button mt-4" href="#/ads">
          Create the next ad variation
        </a>
      </section>
    </div>
  );
}
