import { AppView } from '../../types';

export interface WorkspaceGuideContent {
  headline: string;
  summary: string;
  capabilities: [string, string, string];
  tryIt: string;
  boundary: string;
}

export const workspaceGuide: Partial<Record<AppView, WorkspaceGuideContent>> = {
  [AppView.BILLING]: {
    headline: 'From agreed work to recorded payment.',
    summary: 'Create quotations, record acceptance, convert to invoices and post received payments to bookkeeping.',
    capabilities: ['Save customer snapshots and cent-safe totals', 'Issue, accept and convert quotations', 'Record partial payments and print documents'],
    tryIt: 'Issue the sample quotation, record the customer decision, create an invoice and record a received payment. Inspect the resulting journals in Bookkeeping.',
    boundary: 'No customer charge, tax filing or authority e-invoice submission. Tax rates and acceptance evidence are owner-supplied.',
  },
  [AppView.CHANNELS]: {
    headline: 'Connect the agent. Keep control of delivery.',
    summary: 'Verify Telegram or Meta WhatsApp credentials, register signed webhooks and review the inbox and outgoing drafts.',
    capabilities: ['Connect verified provider identities', 'Choose manual, draft or automatic inbound replies', 'Review delivery receipts and uncertain sends'],
    tryIt: 'Create an agent in chat, add its public customer facts, then connect a real bot or business number outside demo mode. Start with draft automation before enabling auto-reply.',
    boundary: 'Requires encrypted credential storage, public HTTPS callbacks and provider permissions. No fake QR pairing or autonomous access to private owner records.',
  },
  [AppView.BOOKKEEPING]: {
    headline: 'Keep the books balanced. Keep the history.',
    summary: 'Post receipts, payments and balanced journals; review profit-and-loss and reconcile supplied bank closing balances.',
    capabilities: ['Post balanced entries and reversals', 'Review profit-and-loss and trial balance', 'Reconcile bank balances and export journals'],
    tryIt: 'Open the sample books, record a small expense, inspect the updated reports and reverse the entry if needed. Sales ledger figures are not copied automatically.',
    boundary: 'Posted records only. No bank feed, tax filing or statutory financial-statement certification.',
  },
  [AppView.HR]: {
    headline: 'People records with a clear next action.',
    summary: 'Manage employee details, reporting lines, onboarding tasks and reviewed annual or unpaid leave.',
    capabilities: ['Maintain private employee records', 'Reserve and review leave allowances', 'Assign onboarding tasks and deadlines'],
    tryIt: 'Open a sample employee, review pending leave and complete an onboarding task. People review automation flags overdue work without approving anything.',
    boundary: 'Owner-managed HR. Monday–Friday leave model; no holiday calendar, payroll, statutory accrual or employee self-service.',
  },
  [AppView.DASHBOARD]: {
    headline: 'See the business. Choose the next move.',
    summary: 'Sales, review queues and owner actions in one operating view. Start with the evidence, then open the work that needs you.',
    capabilities: ['Compare reporting periods', 'Inspect revenue by channel', 'Assign the next owner action'],
    tryIt: 'Compare 7 and 30 days of Meranti’s sample sales. Open the pending orders, then inspect the saved advisor findings.',
    boundary: 'Recorded revenue is not profit or verified cash receipts.',
  },
  [AppView.PROFILES]: {
    headline: 'Give every decision the same starting point.',
    summary: 'Define what you sell, who buys it and what you can honestly claim. One saved context grounds the rest of your workspace.',
    capabilities: ['Set products and audience', 'Capture brand voice and proof', 'Choose reporting currency and timezone'],
    tryIt: 'Read Meranti’s Team Welcome Kit offer and evidence constraints. These facts also appear in its ad profile and advisor snapshots.',
    boundary: 'Updating context does not rewrite previous advisor evidence.',
  },
  [AppView.AGENT_FORGE]: {
    headline: 'Describe the work. Build the agent.',
    summary: 'Create scoped agents through guided or AI chat, inspect tool activity and approve proposed business changes.',
    capabilities: ['Create agents in a persistent conversation', 'Choose tools, schedules and public channel facts', 'Review proposals and consult 18 specialist advisors'],
    tryIt: 'Type /create to name an agent, describe its purpose and choose tool names. Approve its specification, open its chat and send /run. Use the Advisors tab for saved specialist findings.',
    boundary: 'Guided mode is deterministic. AI chat requires a valid provider. No shell/code execution; writes require owner approval and customer replies cannot read private tools.',
  },
  [AppView.AUTOMATIONS]: {
    headline: 'Let the checks repeat. Not the busywork.',
    summary: 'Convert recurring evidence checks into internal tasks and owner briefings. Preview first; enable only the schedules you need.',
    capabilities: ['Preview 12 recurring checks', 'Choose cadence and pause anytime', 'Inspect deduplicated activity'],
    tryIt: 'Preview overdue lead follow-ups, enable the paused rule, then Check now. The new task appears in Quick wins; repeat checks do not duplicate it.',
    boundary: 'Schedules run while the API is available. Nothing is sent, published or spent.',
  },
  [AppView.SALES]: {
    headline: 'Turn every recorded order into a clearer picture.',
    summary: 'Bring manual sales and verified exports into a single ledger, without mixing currencies or counting pending orders as revenue.',
    capabilities: ['Record and filter orders', 'Import and export CSV', 'Review payment-status changes'],
    tryIt: 'Filter Meranti’s pending orders. Mark one completed after your simulated review, then see the owner overview recalculate.',
    boundary: 'Sample marketplace rows are not live seller connections.',
  },
  [AppView.ECOMMERCE]: {
    headline: 'Know which channel is carrying the business.',
    summary: 'Compare the channels represented in your ledger. Separate recorded performance from connections that still need setup.',
    capabilities: ['Compare channel revenue', 'Inspect order mix', 'Identify live-integration prerequisites'],
    tryIt: 'Compare the sample retail, Shopee and Lazada records. Change the reporting window to see the channel mix update.',
    boundary: 'Seller OAuth and verified webhooks are required for live order sync.',
  },
  [AppView.LEADS]: {
    headline: 'Keep the next conversation from slipping away.',
    summary: 'Manage an enquiry from first contact to a decision, with its notes, stage and next follow-up in the same record.',
    capabilities: ['Search the sales pipeline', 'Record stage and context', 'Schedule a precise follow-up'],
    tryIt: 'Open Aina’s sample corporate enquiry. Move its follow-up into the future, then rerun Lead Follow-up to see it leave the overdue queue.',
    boundary: 'A saved reminder does not send email or WhatsApp.',
  },
  [AppView.ADS]: {
    headline: 'One offer. Every creative decision connected.',
    summary: 'Build the ad profile first, then move through copy, visual composition and a scene-based video using one saved library.',
    capabilities: ['Define the offer and audience', 'Edit copy, image and video', 'Save versions for owner review'],
    tryIt: 'Open Team Welcome Kit in Saved creative drafts. Explore its copy variants, visual canvas and three-scene timeline.',
    boundary: 'Approval is internal review, not an ad-platform launch.',
  },
  [AppView.AD_OPTIMIZATION]: {
    headline: 'Find the spend that needs a closer look.',
    summary: 'Compare attributed performance with your own targets. Data thresholds and conversion lag keep weak signals from becoming confident claims.',
    capabilities: ['Track CTR, CPA and ROAS', 'Compare mature reporting windows', 'Turn review flags into owner tasks'],
    tryIt: 'Compare Kit contents with Broad gifting. The synthetic broad-audience report breaches Meranti’s sample CPA and ROAS targets.',
    boundary: 'Attributed ROAS is not profit, causality or permission to scale automatically.',
  },
  [AppView.SOCIAL_STUDIO]: {
    headline: 'Build a campaign your team can actually review.',
    summary: 'Keep channel copy, planned dates and approval decisions together before anything reaches a public feed.',
    capabilities: ['Draft channel-specific campaigns', 'Filter planned dates and status', 'Approve, archive and export copy'],
    tryIt: 'Open the Team Welcome Kit launch draft, refine its caption and approve it. Campaign review reminders then exclude that approved draft.',
    boundary: 'Planned dates are internal reminders, not scheduled platform publishing.',
  },
  [AppView.MARKETING_COPY]: {
    headline: 'Find the words. Keep the facts.',
    summary: 'Write and compare hooks, bodies and calls to action against a saved offer, audience and brand voice.',
    capabilities: ['Use Direct, AIDA, PAS or BAB', 'Keep reusable copy variants', 'Check length and unsupported claims'],
    tryIt: 'Open a sample creative, compare its variants and change the headline. The same saved draft is available in Visual and Video studios.',
    boundary: 'Demo copy is owner-authored sample content, never presented as a successful AI generation.',
  },
  [AppView.MARKETING_VISUAL]: {
    headline: 'Make the creative yours, down to the last layer.',
    summary: 'Compose a usable ad asset with image controls, editable typography and ordered overlays—not just a generation prompt.',
    capabilities: ['Crop, rotate and adjust the image', 'Position text and graphic layers', 'Export PNG or WebP'],
    tryIt: 'Open Team Welcome Kit, move the headline, adjust the crop and export the composed sample artwork.',
    boundary: 'AI image generation needs valid provider access outside the demo. Manual editing works without it.',
  },
  [AppView.MARKETING_VIDEO]: {
    headline: 'Shape the story, scene by scene.',
    summary: 'Arrange media, timing and captions on a real timeline. Preview your sequence before rendering a file.',
    capabilities: ['Split, reorder and trim scenes', 'Mix source audio and soundtrack', 'Export WebM, MP4 and captions'],
    tryIt: 'Open the three-scene welcome-kit draft. Change a caption, scrub the timeline, then render a short sample video.',
    boundary: 'MP4 needs FFmpeg. Provider-generated footage and voiceover are not simulated.',
  },
  [AppView.BMC_HUB]: {
    headline: 'Put the whole business on one working canvas.',
    summary: 'Connect customers, value, delivery and economics. Use nine concrete decisions instead of a loose collection of ideas.',
    capabilities: ['Edit all nine canvas blocks', 'Keep multiple saved canvases', 'Export the business model'],
    tryIt: 'Open Meranti operating model. Compare its corporate buyers, delivery activities and revenue streams before changing the strategy.',
    boundary: 'A completed canvas is a plan, not validation of demand or margins.',
  },
  [AppView.STRATEGY]: {
    headline: 'Make the tradeoff visible before the commitment.',
    summary: 'Record the goal, evidence, alternatives and constraints behind a decision, then name the smallest next action.',
    capabilities: ['Compare strategic options', 'Record targets and review dates', 'Save the decision and next action'],
    tryIt: 'Open Choose the next channel test. See why the sample company chose a corporate pilot rather than a broad paid launch.',
    boundary: 'AI challenges are optional and disabled in demo; saved decision records remain editable.',
  },
  [AppView.IDEATION]: {
    headline: 'Give the idea a test, not just a title.',
    summary: 'Start with a customer problem. Name the risky assumption, design a small experiment and decide what evidence would change your mind.',
    capabilities: ['Frame the customer problem', 'Separate assumptions from evidence', 'Define an experiment and success metric'],
    tryIt: 'Open Refill reminder insert. Tighten its interview experiment without turning five opinions into a market-size claim.',
    boundary: 'An idea brief is not a guaranteed business opportunity.',
  },
  [AppView.SEO_STUDIO]: {
    headline: 'Give the page a clear search identity.',
    summary: 'Prepare titles, descriptions, canonical URLs and structured data from business facts you control.',
    capabilities: ['Write page metadata', 'Preview search presentation', 'Export Organization JSON-LD'],
    tryIt: 'Open Team Welcome Kit page, adjust its title and inspect the generated structured data.',
    boundary: 'The .example domain is fictional. No live crawl, ranking or rich-result guarantee.',
  },
  [AppView.MARKET_RESEARCH]: {
    headline: 'Keep the source beside the conclusion.',
    summary: 'Build a research notebook that makes the difference between observed evidence and a working assumption impossible to miss.',
    capabilities: ['Save sources and dates', 'Separate observations and hypotheses', 'Record decision implications'],
    tryIt: 'Open Corporate buyer interview plan. Its missing source and evidence are intentional; Research Quality identifies those gaps.',
    boundary: 'No invented interviews, market size or independently verified sources.',
  },
  [AppView.QUICKWINS]: {
    headline: 'Turn “we should” into someone’s next action.',
    summary: 'Bring attention items, advisor findings and recurring checks into a reviewable action board with ownership and deadlines.',
    capabilities: ['Prioritize evidence-backed work', 'Assign a person and due date', 'Track open, active and completed actions'],
    tryIt: 'Find the follow-up task created by an automation. Assign it, set a date and complete it; its history remains in Automations.',
    boundary: 'Completing an action records progress; it does not execute an external change.',
  },
};

export const demoJourney = [
  { view: AppView.DASHBOARD, label: 'Read the business' },
  { view: AppView.LEADS, label: 'Review an enquiry' },
  { view: AppView.SALES, label: 'Inspect the orders' },
  { view: AppView.MARKETING_COPY, label: 'Shape the campaign' },
  { view: AppView.AD_OPTIMIZATION, label: 'Question the spend' },
  { view: AppView.AGENT_FORGE, label: 'Run an advisor' },
  { view: AppView.AUTOMATIONS, label: 'Automate a check' },
  { view: AppView.QUICKWINS, label: 'Own the next action' },
];
