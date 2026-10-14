# SME OS — Design System

Updated 7 October 2026 at the user's direction: professional lime-and-graphite workspace. Existing data and creative asset colors are user content, not theme tokens.

## Typography
- Display: Space Grotesk 600/700, roman headings.
- Body: Inter 400/500/600.
- Mono: JetBrains Mono for data/code only.
- Fonts: self-hosted Latin WOFF2 in `public/fonts`; SIL OFL licenses included. System fallback handles other glyphs.

## Palette
- Page: off-white `hsl(90 12% 97%)`; cards white; text graphite `hsl(120 8% 12%)`.
- Links and selected outlines: `--primary: 98 65% 25%`; never pale lime text on white.
- Primary actions: `--action: 80 80% 55%`, hover L47, active L41; `--action-foreground: 120 12% 10%`.
- Neutral border: `hsl(100 8% 83%)`; muted text `hsl(110 5% 36%)`.
- Dark workspace: graphite surfaces at L9/L13; foreground L94; lime-tinted links L65.
- Sidebar: graphite primary-900; selected rows pale lime with dark text.
- Semantic colors remain distinct: red error, amber warning, green success, blue information. Always include a text label.
- Shadows stay subtle and tinted; no decorative glow fields inside working dashboards.

## Verified contrast
- Dark text on the rendered lime action: **11.72:1**.
- Muted workspace text against its light surface: **6.2:1**.
- Keyboard focus: visible 2px green/lime outline, no animated appearance.

## Layout and behavior
- Dashboard: compact heading, four operational indicators, Focus today, sales trend and automation desk. Do not repeat a large marketing hero above every tool.
- Module help and sample walkthrough are available through native disclosures; working controls have priority.
- Image editor: optional library, selected-object inspector and canvas. Selected-layer outline must never enter exports.
- Video editor: preview plus a separate duration-scaled timeline. One horizontal scroll axis for clips; mobile controls stack.
- Navigation shell stays mounted during lazy routes. Loading gear is scoped to content and initial data requests; no skeletons or fake timed progress. Respect reduced motion.
- Forms use visible labels, bounded inputs, clear busy states and actionable error messages. Posted financial records are corrected by reversal, not silently overwritten.
- Strategy tools default to Guided: plain-language task names, focused question groups, labelled examples, progress/back controls and review before save. Experienced exposes the full editor. Both modes share state and saved records; switching must never discard edits. Preference is local to the signed-in account/browser. Quick wins guides priority selection, reviewed assignment and tracking.
- Mobile verified at 320/375/414/768px; no page overflow. Tables/timelines may scroll horizontally in their own labelled work area.

## Commercial surface
- White/graphite base with lime calls to action. Hero: outcome headline beside owner-specific copy, then compact graphite benefit panel beside a real product capture. No gradient headline, decorative glow or invented UI. Desktop captures/mobile close-ups carry sample-data disclosure; native radio selectors switch views without automatic rotation. Full-screen inspection uses a native dialog with Escape and focus return.
- Landing is learn-first: hero/product preview, one practical invoice walkthrough, concise FAQ and optional pilot enquiry. Keep the full tool catalogue and planning brief behind disclosures; do not restore duplicate feature strips, tier cards or repeated pitches. No unverified price, customer, certification or conversion claims.
- Primary intent: Explore demo; secondary learning action: See what you can do. Request a pilot expands the real consent-based enquiry form with a saved reference; no booking/payment promise. Enquiry review is administrator-only.
- Preserve legal links and honest provider/deployment boundaries.
