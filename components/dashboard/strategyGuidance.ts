import { AppView } from '../../types';

export const strategyMenu = [
  { view: AppView.BMC_HUB, label: 'Understand my business', hint: 'Customers, delivery and money' },
  { view: AppView.MARKET_RESEARCH, label: 'Research my market', hint: 'Questions, sources and findings' },
  { view: AppView.IDEATION, label: 'Test a business idea', hint: 'Problem, idea and a small test' },
  { view: AppView.STRATEGY, label: 'Choose my next direction', hint: 'Goal, options and next action' },
  { view: AppView.SEO_STUDIO, label: 'Help customers find me', hint: 'Page content and search details' },
  { view: AppView.QUICKWINS, label: 'Pick my next action', hint: 'Choose, assign and follow through' },
];

type Question = { key: string; question: string; help: string; example?: string };
type Step = { title: string; description: string; questions: Question[] };
type Guide = { title: string; description: string; titleExample: string; steps: Step[] };
export const strategyGuidance: Record<'canvas' | 'strategy' | 'ideation' | 'seo' | 'research', Guide> = {
  canvas: {
    title: 'Understand how your business works', description: 'Start with your customers. Then connect what you deliver, what you need and how you earn.', titleExample: 'Our corporate gift business',
    steps: [
      { title: 'Who do you help?', description: 'Be specific about the buyer and why they would choose you.', questions: [
        { key: 'customers', question: 'Who are your main customers?', help: 'Name a group with a shared need, not everyone.', example: 'Office managers buying welcome gifts for new employees.' },
        { key: 'value', question: 'What problem do you solve for them?', help: 'Describe the useful result, not only the product.', example: 'Ready-to-deliver welcome kits so the office manager does not coordinate five suppliers.' },
      ] },
      { title: 'How do you deliver?', description: 'Describe how customers find you and what happens after they buy.', questions: [
        { key: 'channels', question: 'Where do customers find and buy from you?', help: 'List the channels you use or plan to test.', example: 'Referrals, our website and direct enquiries.' },
        { key: 'relationships', question: 'How do you help customers before and after a sale?', help: 'Think about advice, updates, support and repeat orders.', example: 'A named contact confirms artwork and follows up after delivery.' },
        { key: 'activities', question: 'What work must happen to fulfil the promise?', help: 'List the important work, not every small task.', example: 'Source products, confirm artwork, pack kits and arrange delivery.' },
      ] },
      { title: 'What do you need?', description: 'Separate the things you own from the people you rely on.', questions: [
        { key: 'resources', question: 'What people, equipment or knowledge do you need?', help: 'Include resources that are hard to replace.', example: 'A packing team, design files and reliable stock records.' },
        { key: 'partners', question: 'Which suppliers or partners matter most?', help: 'Name their role and why you need them.', example: 'A local printer for branding and a courier for delivery.' },
      ] },
      { title: 'How does the money work?', description: 'Write what you know. Mark estimates rather than presenting them as facts.', questions: [
        { key: 'revenue', question: 'What do customers pay you for?', help: 'Describe the pricing model; use your own verified amounts if available.', example: 'Per-kit orders plus separately agreed custom printing.' },
        { key: 'costs', question: 'What are your main costs?', help: 'Include product, people, delivery and overhead costs.', example: 'Products, packaging, printing, labour and delivery.' },
      ] },
    ],
  },
  strategy: {
    title: 'Choose your next business direction', description: 'Set a goal, compare realistic options and decide what to do next.', titleExample: 'Choose our next sales channel',
    steps: [
      { title: 'What do you want to change?', description: 'A useful goal has a starting point and a way to measure progress.', questions: [
        { key: 'goal', question: 'What result do you want for the business?', help: 'Choose one business outcome.', example: 'Build a more predictable flow of repeat corporate orders.' },
        { key: 'baseline', question: 'Where are you starting from?', help: 'Use recorded facts. Say what is unknown.', example: 'Most orders currently come from referrals; repeat-order rate not yet measured.' },
        { key: 'target', question: 'What would count as progress?', help: 'Set your own measurable target; this is a goal, not a forecast.', example: 'An owner-set target for repeat customers or qualified enquiries.' },
        { key: 'deadline', question: 'When will you review the result?', help: 'Pick a date to compare progress with the starting point.' },
      ] },
      { title: 'What are your choices?', description: 'Compare alternatives using the same goal and constraints.', questions: [
        { key: 'constraints', question: 'What limits your decision?', help: 'Consider money, capacity, time and commitments.', example: 'One salesperson, limited stock and no confirmed advertising budget.' },
        { key: 'options', question: 'Which options could work, and what are the tradeoffs?', help: 'Include what you give up with each choice.', example: 'A small corporate pilot offers direct feedback; a broad campaign reaches more people but needs spend.' },
        { key: 'evidence', question: 'What facts support these options?', help: 'Add source links, dated observations or recorded results. Keep assumptions separate.', example: 'Link to your customer notes or comparable campaign results.' },
      ] },
      { title: 'What will you do next?', description: 'Make a decision you can revisit as evidence changes.', questions: [
        { key: 'decision', question: 'Which direction will you try, and why?', help: 'A provisional decision is fine; explain what would change it.', example: 'Try a small corporate pilot before committing to paid acquisition.' },
        { key: 'next_action', question: 'What is the first concrete action?', help: 'Name the work, who owns it and when it should happen.', example: 'The sales owner prepares a pilot offer for review on the agreed date.' },
      ] },
    ],
  },
  ideation: {
    title: 'Turn an idea into a small test', description: 'Start with a customer problem, not a feature list. Decide what evidence would make the idea worth pursuing.', titleExample: 'Test a refill reminder service',
    steps: [
      { title: 'Whose problem is it?', description: 'Describe a real situation you have observed or still need to investigate.', questions: [
        { key: 'audience', question: 'Who has this problem?', help: 'Choose a specific group.', example: 'Customers who reorder the same office supplies.' },
        { key: 'problem', question: 'What makes their current task difficult?', help: 'Describe the task and frustration; do not assume every customer agrees.', example: 'They notice supplies are low only after running out.' },
      ] },
      { title: 'What could help?', description: 'State the idea and the assumption most likely to make it fail.', questions: [
        { key: 'idea', question: 'What is your proposed idea?', help: 'Explain it in one or two plain sentences.', example: 'Offer an opt-in reminder before customers usually reorder.' },
        { key: 'benefit', question: 'How would the customer benefit?', help: 'Describe a result they would notice.', example: 'They can reorder before supplies run out.' },
        { key: 'assumptions', question: 'What must be true for this to work?', help: 'Mark untested beliefs clearly.', example: 'Customers want reminders and their reorder timing is predictable.' },
      ] },
      { title: 'How will you test it?', description: 'Keep the first experiment small enough to learn without a large commitment.', questions: [
        { key: 'experiment', question: 'What is the smallest useful test?', help: 'Describe the participants, action and length of the test.', example: 'Ask existing customers about their reorder process before building automation.' },
        { key: 'metric', question: 'What result would make you continue?', help: 'Choose the measure and threshold before the test.', example: 'Your chosen threshold for customers requesting a reminder.' },
        { key: 'decision', question: 'What have you learned or decided so far?', help: 'Before running the test, write “not tested yet” or leave this blank.', example: 'Not tested yet; customer interest still needs evidence.' },
      ] },
    ],
  },
  seo: {
    title: 'Help the right customers find your page', description: 'Prepare the page facts and search description. This does not publish changes or guarantee rankings.', titleExample: 'Our corporate welcome-kit page',
    steps: [
      { title: 'Which page are you preparing?', description: 'Start with facts about the business and the page.', questions: [
        { key: 'business_name', question: 'What is the business called?', help: 'Use the public business name customers recognise.' },
        { key: 'business_type', question: 'What kind of business is it?', help: 'Describe it in everyday language.', example: 'Corporate gifts supplier.' },
        { key: 'url', question: 'What is the full page address?', help: 'Use an https:// or http:// address without passwords. Leave blank if the page is not ready.', example: 'https://your-business.com/welcome-kits' },
      ] },
      { title: 'What are customers looking for?', description: 'Match the content to a useful customer question.', questions: [
        { key: 'keywords', question: 'What would your customer search for?', help: 'Use phrases relevant to your offer; no search volume is inferred.', example: 'Custom welcome kits for new employees.' },
        { key: 'content_outline', question: 'What should the page explain?', help: 'List the questions the page should answer.', example: 'What is included, customisation choices, ordering steps and delivery information.' },
      ] },
      { title: 'How should the page appear in search?', description: 'Write clear copy. Search engines may choose different text.', questions: [
        { key: 'page_title', question: 'What title describes the page?', help: 'Name the offer and business; avoid unsupported superlatives.', example: 'Employee Welcome Kits | Your Business' },
        { key: 'description', question: 'What short description would help someone choose?', help: 'Summarise the useful content, not a ranking promise.', example: 'Explore kit contents, branding options and how to request a quote.' },
      ] },
    ],
  },
  research: {
    title: 'Find evidence for a business decision', description: 'Keep the source next to the finding. Unknowns stay unknown until you have evidence.', titleExample: 'What corporate buyers need before ordering',
    steps: [
      { title: 'What do you need to learn?', description: 'A specific question is easier to investigate than an entire market.', questions: [
        { key: 'question', question: 'What question will this research answer?', help: 'Choose something that could change a decision.', example: 'What prevents office managers from placing a repeat order?' },
        { key: 'segment', question: 'Which customers or market does this concern?', help: 'Define who and where the findings apply.', example: 'Office managers at small companies in our delivery area.' },
      ] },
      { title: 'Where did the information come from?', description: 'Add a traceable source. If you do not have one, leave it blank rather than inventing it.', questions: [
        { key: 'source_title', question: 'What is the source or publisher?', help: 'Name the publication, interview record or internal report.', example: 'Customer interview notes, with the interview date.' },
        { key: 'source_url', question: 'Where can you check the source?', help: 'Use the full http:// or https:// link without embedded credentials.', example: 'https://publisher.com/original-report' },
        { key: 'published_date', question: 'When was it published or recorded?', help: 'Use the source date, not the date you found it.' },
      ] },
      { title: 'What does it tell you?', description: 'Separate what you observed from what you think it means.', questions: [
        { key: 'evidence', question: 'What did you actually observe?', help: 'Record the claim or finding accurately and include its limits.', example: 'Quote or summarise a specific finding from the source above.' },
        { key: 'assumptions', question: 'What is still unverified?', help: 'Note gaps, possible bias and unanswered questions.', example: 'We do not know whether this finding applies to smaller buyers.' },
        { key: 'conclusion', question: 'How might this affect your decision?', help: 'Explain what you would change, or what to investigate next.', example: 'Test simpler reorder instructions before changing the product range.' },
      ] },
    ],
  },
};
