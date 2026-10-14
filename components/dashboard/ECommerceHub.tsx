import { RefreshCw, Store, ArrowRight, Unplug } from "lucide-react";
import { useOwner } from "../../contexts/OwnerContext";

export function ECommerceHub() {
  const { overview, loading, error, refresh, days, setDays } = useOwner();
  const summary = overview?.sales;
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl font-bold">
            Marketplace monitor
          </h2>
          <p className="text-muted-foreground mt-2">
            Compare recorded sales by channel. External stores are not
            connected.
          </p>
        </div>
        <label className="owner-label">
          Comparison period
          <select
            className="owner-input"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            {[7, 30, 90, 365].map((n) => (
              <option key={n} value={n}>
                Last {n} days
              </option>
            ))}
          </select>
        </label>
        <button
          className="owner-button-secondary"
          onClick={() => void refresh()}
          disabled={loading}
        >
          <RefreshCw className="w-4 h-4" />
          {loading ? "Refreshing…" : "Refresh ledger"}
        </button>
      </div>
      {error && (
        <p role="alert" className="owner-error">
          {error}
        </p>
      )}
      <section className="owner-panel flex flex-col sm:flex-row items-start gap-4">
        <Unplug className="w-7 h-7 text-primary shrink-0" />
        <div>
          <h3 className="font-display text-lg font-semibold">
            Live marketplace sync is not configured
          </h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-prose">
            Shopee, TikTok Shop, Lazada, Shopify and WooCommerce require
            verified seller authorization and provider-specific integrations. No
            orders are fetched, stores linked, or shipping labels issued by this
            portal yet.
          </p>
          <a
            href={overview?.context ? "#/sales" : "#/profiles"}
            className="owner-button mt-4"
          >
            {overview?.context
              ? "Record verified orders"
              : "Set up business context"}
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>
      <section className="owner-panel">
        <h3 className="font-display text-lg font-semibold">
          Recorded channel performance
        </h3>
        <p className="text-sm text-muted-foreground mt-2">
          Last {summary?.days || 30} calendar days · completed revenue in{" "}
          {summary?.currency || "your reporting currency"}.{" "}
          {summary?.excluded_currency_orders || 0} other-currency orders
          excluded from money totals.
        </p>
        <div className="overflow-x-auto mt-5">
          <table className="w-full text-sm">
            <caption className="sr-only">
              Revenue and orders by recorded channel
            </caption>
            <thead className="bg-muted text-left">
              <tr>
                <th className="p-3">Channel</th>
                <th className="p-3">Recorded orders</th>
                <th className="p-3 text-right">Completed revenue</th>
                <th className="p-3 text-right">Revenue share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {summary?.by_platform.map((row) => (
                <tr key={row.platform}>
                  <td className="p-3 capitalize">{row.platform}</td>
                  <td className="p-3 tabular-nums">{row.orders}</td>
                  <td className="p-3 text-right tabular-nums">
                    {summary.currency} {row.revenue.toFixed(2)}
                  </td>
                  <td className="p-3 text-right tabular-nums">
                    {summary.revenue
                      ? `${((row.revenue / summary.revenue) * 100).toFixed(1)}%`
                      : "—"}
                  </td>
                </tr>
              ))}
              {!summary?.by_platform.length && (
                <tr>
                  <td
                    colSpan={4}
                    className="p-8 text-center text-muted-foreground"
                  >
                    {loading
                      ? "Loading channel data…"
                      : "No recorded channel sales in this period."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
      <section className="owner-panel">
        <h3 className="font-display text-lg font-semibold">
          Channel decisions
        </h3>
        <p className="text-sm text-muted-foreground mt-2">
          {summary?.revenue && summary.by_platform[0]
            ? `${summary.by_platform[0].platform} contributes ${((summary.by_platform[0].revenue / summary.revenue) * 100).toFixed(1)}% of recorded completed revenue. Compare acquisition cost and refunds before shifting budget.`
            : "Import verified channel sales to establish a comparison baseline."}
        </p>
        <div className="flex flex-wrap gap-3 mt-4">
          <a className="owner-button-secondary" href="#/sales">
            Import channel orders
          </a>
          <a className="owner-button-secondary" href="#/ad-optimization">
            Review ad efficiency
          </a>
        </div>
      </section>
      <section className="owner-panel">
        <h3 className="font-display text-lg font-semibold">
          Connection requirements
        </h3>
        <div className="divide-y divide-border mt-3">
          {[
            ["Shopee", "Approved partner application and seller authorization"],
            [
              "TikTok Shop",
              "Partner app approval, seller consent and signed webhooks",
            ],
            ["Lazada", "Open Platform app and seller OAuth"],
            ["Shopify", "Store app installation and orders permissions"],
            [
              "WooCommerce",
              "Store REST credentials and HTTPS webhook verification",
            ],
          ].map(([name, detail]) => (
            <div key={name} className="flex items-start gap-3 py-4">
              <Store className="w-5 h-5 text-primary shrink-0" />
              <div className="flex-1">
                <p className="font-medium text-sm">{name}</p>
                <p className="text-xs text-muted-foreground mt-1">{detail}</p>
              </div>
              <span className="text-xs text-muted-foreground">
                Not connected
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
