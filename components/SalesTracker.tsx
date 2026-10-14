import { useCallback, useEffect, useRef, useState } from "react";
import { Download, Plus, RefreshCw } from "lucide-react";
import { apiCall } from "../services/apiClient";
import { useOwner } from "../contexts/OwnerContext";
import type { Sale, SalesSummary } from "../types/owner";
import { useUnsavedChanges } from "../hooks/useUnsavedChanges";
import WorkspaceLoading from './common/WorkspaceLoading';

interface SalesPage {
  items: Sale[];
  total: number;
  page: number;
  size: number;
}
const channels = [
  "manual",
  "shopee",
  "tiktok",
  "lazada",
  "shopify",
  "woocommerce",
  "other",
];
export default function SalesTracker() {
  const { overview, refresh, error: contextError } = useOwner();
  const [page, setPage] = useState(1),
    [days, setDays] = useState(30),
    [platform, setPlatform] = useState(""),
    [status, setStatus] = useState(""),
    [search, setSearch] = useState("");
  const [rows, setRows] = useState<SalesPage | null>(null),
    [summary, setSummary] = useState<SalesSummary | null>(null);
  const [loading, setLoading] = useState(false),
    [busy, setBusy] = useState(""),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [entry, setEntry] = useState(false);
  const [form, setForm] = useState({
    platform: "manual",
    external_id: "",
    amount: "",
    currency: "MYR",
    status: "completed",
    transaction_date: "",
  });
  const [importText, setImportText] = useState("");
  const [importOpen, setImportOpen] = useState(false);
  const request = useRef(0);
  const profileId = overview?.context?.id;
  useUnsavedChanges(!!(entry && (form.amount || form.external_id)) || !!busy);
  useEffect(() => {
    if (overview?.context)
      setForm((prev) => ({ ...prev, currency: overview.context!.currency }));
  }, [overview?.context?.currency]);
  const load = useCallback(async () => {
    if (!profileId) return;
    const id = ++request.current;
    setLoading(true);
    setError("");
    const params = new URLSearchParams({
      page: String(page),
      size: "20",
      days: String(days),
      search,
    });
    if (platform) params.set("platform", platform);
    if (status) params.set("status", status);
    try {
      const [data, totals] = await Promise.all([
        apiCall<SalesPage>(`/api/v1/sales/?${params}`),
        apiCall<SalesSummary>(`/api/v1/sales/summary?days=${days}`),
      ]);
      if (id === request.current) {
        setRows(data);
        setSummary(totals);
        if (page > 1 && !data.items.length)
          setPage(Math.max(1, Math.ceil(data.total / 20)));
      }
    } catch (err) {
      if (id === request.current)
        setError(
          err instanceof Error
            ? err.message
            : "Sales data could not be loaded.",
        );
    } finally {
      if (id === request.current) setLoading(false);
    }
  }, [profileId, page, days, search, platform, status]);
  useEffect(() => {
    const timer = setTimeout(() => void load(), 200);
    return () => {
      clearTimeout(timer);
      request.current++;
    };
  }, [load]);
  if (!profileId)
    return (
      <section className="owner-panel">
        <h2 className="text-2xl font-display font-bold">Sales ledger</h2>
        <p className="my-4">
          {contextError ||
            "Save your business context to start recording sales."}
        </p>
        <a className="text-primary underline" href="#/profiles">
          Open business context
        </a>
      </section>
    );
  if (!rows && !error) return <WorkspaceLoading label="sales ledger" />;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-start gap-4">
        <div>
          <h2 className="text-2xl font-display font-bold">Sales ledger</h2>
          <p className="mt-2 text-muted-foreground">
            {overview?.context?.is_demo ? 'Sample orders for the fictional Meranti enterprise. Calculations use these demo records, not live sales.' : 'Real recorded orders. No simulated sales or currency conversions.'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="owner-button-secondary"
            disabled={loading}
            onClick={() => void load()}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            className="owner-button"
            onClick={() => {
              setEntry(!entry);
              if (!form.transaction_date) {
                const now = new Date();
                setForm((prev) => ({
                  ...prev,
                  transaction_date: new Date(
                    now.getTime() - now.getTimezoneOffset() * 60000,
                  )
                    .toISOString()
                    .slice(0, 16),
                }));
              }
            }}
          >
            <Plus className="w-4 h-4" />
            {entry ? "Close entry" : "Record a sale"}
          </button>
        </div>
      </div>
      <details
        className="owner-panel"
        open={importOpen}
        onToggle={(e) => setImportOpen(e.currentTarget.open)}
      >
        <summary className="font-semibold cursor-pointer">
          Import verified sales CSV
        </summary>
        <p className="text-sm text-muted-foreground mt-3 break-words">
          Required header:
          platform,external_id,amount,currency,status,transaction_date. Dates
          include a timezone offset. Up to 1,000 rows; matching rows are
          skipped, conflicting rows reject the whole import.
        </p>
        <label className="owner-label mt-4">
          CSV data
          <textarea
            className="owner-input font-mono"
            rows={6}
            maxLength={1000000}
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder="platform,external_id,amount,currency,status,transaction_date"
          />
        </label>
        <input
          className="owner-input mt-3"
          type="file"
          aria-label="Choose sales CSV"
          accept=".csv,text/csv"
          onChange={async (e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            if (file.size > 1000000) {
              setError("CSV must be smaller than 1 MB.");
              return;
            }
            setImportText(await file.text());
          }}
        />
        <button
          className="owner-button mt-3"
          disabled={!!busy || !importText.trim()}
          onClick={async () => {
            setBusy("import");
            setError("");
            try {
              const result = await apiCall<{
                inserted: number;
                skipped: number;
              }>("/api/v1/sales/import", "POST", { csv_text: importText });
              await Promise.all([load(), refresh()]);
              setMessage(
                `${result.inserted} sales imported; ${result.skipped} matching rows skipped.`,
              );
              setImportText("");
            } catch (err) {
              setError(err instanceof Error ? err.message : "Import failed.");
            } finally {
              setBusy("");
            }
          }}
        >
          Validate and import sales
        </button>
      </details>
      {error && (
        <p role="alert" className="owner-error">
          {error}
        </p>
      )}
      {message && (
        <p role="status" className="text-sm">
          {message}
        </p>
      )}
      {entry && (
        <form
          className="owner-panel space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy("save");
            setError("");
            try {
              await apiCall("/api/v1/sales/", "POST", {
                ...form,
                external_id: form.external_id.trim() || null,
                amount: Number(form.amount),
                transaction_date: new Date(form.transaction_date).toISOString(),
              });
              setForm((prev) => ({ ...prev, external_id: "", amount: "" }));
              setEntry(false);
              await Promise.all([load(), refresh()]);
              setMessage("Sale saved in your business ledger.");
            } catch (err) {
              setError(
                err instanceof Error ? err.message : "Sale could not be saved.",
              );
            } finally {
              setBusy("");
            }
          }}
        >
          <h3 className="font-display font-semibold">Record a verified sale</h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <label className="owner-label">
              Channel
              <select
                className="owner-input"
                value={form.platform}
                onChange={(e) => setForm({ ...form, platform: e.target.value })}
              >
                {channels.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
            <label className="owner-label">
              Order reference (optional)
              <input
                className="owner-input"
                maxLength={120}
                value={form.external_id}
                onChange={(e) =>
                  setForm({ ...form, external_id: e.target.value })
                }
              />
            </label>
            <label className="owner-label">
              Amount
              <input
                className="owner-input"
                type="number"
                min="0.01"
                max="999999999"
                step="0.01"
                value={form.amount}
                required
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
              />
            </label>
            <label className="owner-label">
              Currency
              <input
                className="owner-input"
                pattern="[A-Z]{3}"
                maxLength={3}
                value={form.currency}
                required
                onChange={(e) =>
                  setForm({ ...form, currency: e.target.value.toUpperCase() })
                }
              />
            </label>
            <label className="owner-label">
              Status
              <select
                className="owner-input"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                {["completed", "pending", "refunded", "cancelled"].map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <label className="owner-label">
              Transaction time
              <input
                className="owner-input"
                type="datetime-local"
                required
                value={form.transaction_date}
                onChange={(e) =>
                  setForm({ ...form, transaction_date: e.target.value })
                }
              />
            </label>
          </div>
          <p className="text-xs text-muted-foreground">
            Input time uses {Intl.DateTimeFormat().resolvedOptions().timeZone};
            reports use {overview.context!.timezone}. Only completed orders
            count toward revenue.
          </p>
          <button className="owner-button" disabled={!!busy}>
            {busy === "save" ? "Saving sale…" : "Save sale"}
          </button>
        </form>
      )}
      {summary && (
        <section
          className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4"
          aria-label="Period summary"
        >
          {[
            [
              "Completed revenue",
              `${summary.currency} ${summary.revenue.toFixed(2)}`,
            ],
            ["All recorded orders", String(summary.orders)],
            ["Pending orders", String(summary.pending_orders)],
            [
              "Average paid order",
              `${summary.currency} ${summary.average_order_value.toFixed(2)}`,
            ],
          ].map(([label, value]) => (
            <div className="owner-panel" key={label}>
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="mt-2 font-display text-2xl font-semibold tabular-nums">
                {value}
              </p>
            </div>
          ))}
        </section>
      )}
      <section className="owner-panel">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <label className="owner-label">
            Search order reference
            <input
              type="search"
              className="owner-input"
              value={search}
              maxLength={120}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
            />
          </label>
          <label className="owner-label">
            Channel
            <select
              className="owner-input"
              value={platform}
              onChange={(e) => {
                setPlatform(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All channels</option>
              {channels.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </label>
          <label className="owner-label">
            Order status
            <select
              className="owner-input"
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All statuses</option>
              {["completed", "pending", "refunded", "cancelled"].map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </label>
          <label className="owner-label">
            Reporting period
            <select
              className="owner-input"
              value={days}
              onChange={(e) => {
                setDays(Number(e.target.value));
                setPage(1);
              }}
            >
              {[7, 30, 90, 365].map((n) => (
                <option key={n} value={n}>
                  Last {n} days
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="flex flex-wrap justify-between items-center gap-3 my-5">
          <p className="text-xs text-muted-foreground max-w-prose">
            Summary covers all channels in the period, independent of table
            filters. {summary?.excluded_currency_orders || 0} other-currency
            orders excluded from revenue. Refunded and cancelled orders
            excluded.
          </p>
          <button
            className="owner-button-secondary"
            disabled={!!busy || !rows?.items.length}
            onClick={() => {
              const quote = (v: string | number) =>
                `"${String(v)
                  .replace(/^[\s]*[=+@-]/, (match) => `'${match}`)
                  .replaceAll('"', '""')}"`;
              const content = [
                [
                  "Reference",
                  "Channel",
                  "Amount",
                  "Currency",
                  "Status",
                  "UTC date",
                ],
                ...(rows?.items || []).map((row) => [
                  row.external_id || row.id,
                  row.platform,
                  row.amount,
                  row.currency,
                  row.status,
                  row.transaction_date,
                ]),
              ]
                .map((row) => row.map(quote).join(","))
                .join("\r\n");
              const url = URL.createObjectURL(
                new Blob(["\uFEFF" + content], {
                  type: "text/csv;charset=utf-8",
                }),
              );
              const a = document.createElement("a");
              a.href = url;
              a.download = `sales-page-${page}.csv`;
              a.click();
              URL.revokeObjectURL(url);
              setMessage(
                `Exported ${rows?.items.length} rows from the current filtered page.`,
              );
            }}
          >
            <Download className="w-4 h-4" />
            Export this page
          </button>
        </div>
        <div className="overflow-x-auto">
          <table
            className="w-full text-sm text-left min-w-[670px]"
            aria-busy={loading}
          >
            <caption className="sr-only">
              Recorded sales, current filtered page
            </caption>
            <thead className="border-y border-border bg-muted">
              <tr>
                {["Reference", "Date", "Channel", "Status", "Amount"].map(
                  (label) => (
                    <th className="px-3 py-3" key={label}>
                      {label}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rows?.items.map((row) => (
                <tr key={row.id}>
                  <td className="p-3 max-w-[200px] break-words">
                    {row.external_id || row.id.slice(0, 8)}
                  </td>
                  <td className="p-3 whitespace-nowrap">
                    {new Date(row.transaction_date).toLocaleString(undefined, {
                      timeZone: overview.context!.timezone,
                    })}
                  </td>
                  <td className="p-3">{row.platform}</td>
                  <td className="p-3">
                    <select
                      className="owner-input min-w-[135px]"
                      aria-label={`Status for ${row.external_id || row.id}`}
                      value={row.status}
                      disabled={!!busy}
                      onChange={async (e) => {
                        const next = e.target.value;
                        setBusy(row.id);
                        setError("");
                        try {
                          await apiCall(`/api/v1/sales/${row.id}`, "PATCH", {
                            status: next,
                          });
                          await Promise.all([load(), refresh()]);
                          setMessage(
                            "Order status updated. Revenue recalculated.",
                          );
                        } catch (err) {
                          setError(
                            err instanceof Error
                              ? err.message
                              : "Status update failed.",
                          );
                        } finally {
                          setBusy("");
                        }
                      }}
                    >
                      {["completed", "pending", "refunded", "cancelled"].map(
                        (s) => (
                          <option key={s}>{s}</option>
                        ),
                      )}
                    </select>
                  </td>
                  <td className="p-3 tabular-nums whitespace-nowrap">
                    {row.currency} {row.amount.toFixed(2)}
                  </td>
                </tr>
              ))}
              {!rows?.items.length && (
                <tr>
                  <td
                    colSpan={5}
                    className="p-8 text-center text-muted-foreground"
                  >
                    {loading
                      ? "Loading recorded sales…"
                      : "No sales match these filters. Record an order or adjust the period."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-muted-foreground">
            {rows?.total || 0} matching orders · page {page} of{" "}
            {Math.max(1, Math.ceil((rows?.total || 0) / 20))}
          </p>
          <div className="flex gap-2">
            <button
              className="owner-button-secondary"
              disabled={loading || page <= 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </button>
            <button
              className="owner-button-secondary"
              disabled={loading || page * 20 >= (rows?.total || 0)}
              onClick={() => setPage(page + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
