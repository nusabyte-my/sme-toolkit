/**
 * LegalPage — Privacy Policy & Terms of Service (shared shell).
 * Content is deliberately honest for a pre-launch product: it describes what
 * the app actually does today (local demo data, backend calls to the API base
 * URL, Gemini-powered generation) and flags the tier-gating rules. Legal
 * review is still required before charging money — this is a real foundation,
 * not lorem-ipsum filler.
 */

import React from 'react';
import { Layers, ArrowLeft, ShieldCheck, FileText } from 'lucide-react';
import { AppView } from '../types';

type LegalKind = 'privacy' | 'terms';

interface LegalPageProps {
  kind: LegalKind;
  onNavigate: (view: AppView) => void;
}

const SECTION_HEAD = 'font-display text-lg font-semibold text-slate-900 mt-8 mb-3';
const BODY = 'text-slate-600 leading-relaxed text-sm';

const PrivacyContent: React.FC = () => (
  <>
    <p className={BODY}>
      This policy explains what information SME Toolkit handles when you use the
      app. It is written for Malaysian SMEs and follows the general principles of
      the Personal Data Protection Act 2010 (PDPA). Plain language, no dark
      patterns: we collect the minimum needed to run your workspace.
    </p>

    <h2 className={SECTION_HEAD}>What we handle</h2>
    <ul className="list-disc pl-5 space-y-2 text-slate-600 text-sm leading-relaxed">
      <li><strong className="text-slate-800">Workspace content</strong> — your business profiles, canvas answers, leads, sales records, and generated copy/visuals. This is stored so the app works when you return.</li>
      <li><strong className="text-slate-800">Account basics</strong> — your name, email, and subscription tier.</li>
      <li><strong className="text-slate-800">Usage counters</strong> — token consumption and request counts, used only to enforce plan limits and show your usage dashboard.</li>
      <li><strong className="text-slate-800">Pilot enquiries</strong> — your name, business, email, selected workflow and goal, plus consent to contact you about that enquiry. Requests are stored in an administrator-only inbox until deleted by the administrator. No automatic booking, email or marketing subscription is created. Short-lived keyed hashes of the connecting address and email enforce submission limits; raw network addresses are not stored in enquiry records.</li>
    </ul>

    <h2 className={SECTION_HEAD}>AI processing</h2>
    <p className={BODY}>
      When you request provider-backed generation, the relevant business context and prompt are sent to the configured provider. Its retention, processing and training terms depend on your provider agreement. Confirm those terms before submitting confidential or personal data. Paid generation is disabled in the local sample demo.
    </p>

    <h2 className={SECTION_HEAD}>What we never do</h2>
    <ul className="list-disc pl-5 space-y-2 text-slate-600 text-sm leading-relaxed">
      <li>Sell your data or share it with advertisers.</li>
      <li>Send you marketing email unless you explicitly subscribed (and every email includes an unsubscribe link).</li>
      <li>Store payment card numbers — checkout is handled by Stripe; we only keep the payment status and plan it unlocked.</li>
    </ul>

    <h2 className={SECTION_HEAD}>Your control</h2>
    <p className={BODY}>
      Use the available editors and exports to manage workspace records. The local demo stores its sample records in the application database; exiting does not erase them. Ask your workspace administrator about full export, retention and deletion procedures before storing production data.
    </p>

    <h2 className={SECTION_HEAD}>Contact</h2>
    <p className={BODY}>
      Questions about this policy: <a className="text-primary underline underline-offset-2 hover:text-primary/80" href="mailto:hello@sme-toolkit.com">hello@sme-toolkit.com</a>.
      Material changes will be announced in-app before they take effect.
    </p>
  </>
);

const TermsContent: React.FC = () => (
  <>
    <p className={BODY}>
      These terms govern your use of SME Toolkit. By launching the app you agree
      to them. If you use the app on behalf of a business, you confirm you have
      authority to bind that business.
    </p>

    <h2 className={SECTION_HEAD}>Evaluation and commercial access</h2>
    <ul className="list-disc pl-5 space-y-2 text-slate-600 text-sm leading-relaxed">
      <li>The local sample enterprise is an evaluation environment with fictional data, not an activated paid subscription.</li>
      <li>Downloading an evaluation brief does not submit a sales request, activate a plan or charge a payment method.</li>
      <li>Submitting the pilot enquiry form records a request for administrator review. A receipt confirms storage, not a booked meeting, accepted project, response deadline or email delivery.</li>
      <li>Pricing, hosting, support, integrations and any payment terms must be agreed separately for your deployment.</li>
      <li>Provider-backed AI generation can incur provider charges. Confirm credentials, quotas and billing before enabling it.</li>
    </ul>

    <h2 className={SECTION_HEAD}>Acceptable use</h2>
    <ul className="list-disc pl-5 space-y-2 text-slate-600 text-sm leading-relaxed">
      <li>Do not upload content you have no right to use, or use the app to generate unlawful, misleading, or spam content.</li>
      <li>Do not resell API access or scrape the service.</li>
      <li>We may suspend accounts that break these rules, with notice where practical.</li>
    </ul>

    <h2 className={SECTION_HEAD}>AI-generated output</h2>
    <p className={BODY}>
      Output from the strategy advisor, copywriter, and other AI features is
      draft material to support your judgment — not professional financial,
      legal, or tax advice, and not a guarantee of business results. You are
      responsible for reviewing anything you publish or act on.
    </p>

    <h2 className={SECTION_HEAD}>Service availability and liability</h2>
    <p className={BODY}>
      We aim for high availability but the service is provided as-is during this
      launch phase. To the maximum extent permitted by law, our liability for any
      claim connected to the service is limited to the amount you paid us in the
      three months before the claim.
    </p>

    <h2 className={SECTION_HEAD}>Contact</h2>
    <p className={BODY}>
      Questions about these terms: <a className="text-primary underline underline-offset-2 hover:text-primary/80" href="mailto:hello@sme-toolkit.com">hello@sme-toolkit.com</a>.
      If we change the terms materially, we will notify you in-app before the
      change applies.
    </p>
  </>
);

const LegalPage: React.FC<LegalPageProps> = ({ kind, onNavigate }) => {
  const isPrivacy = kind === 'privacy';

  return (
    <div className="commercial-page min-h-screen font-sans text-foreground">
      <a href="#main-content" onClick={event=>{event.preventDefault();document.getElementById('main-content')?.focus();}} className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded-lg focus:shadow-lg">
        Skip to main content
      </a>

      <header className="commercial-header sticky top-0 z-40">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <button
            onClick={() => onNavigate(AppView.LANDING)}
            className="flex items-center gap-2 font-display font-bold text-lg text-slate-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary rounded-lg"
          >
            <span className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center text-white shadow-md shadow-primary/20">
              <Layers className="w-4 h-4" />
            </span>
            SME Toolkit
          </button>
          <button
            onClick={() => onNavigate(AppView.LANDING)}
            className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground px-3 py-2 rounded-lg hover:bg-muted transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            Back to site
          </button>
        </div>
      </header>

      <main id="main-content" tabIndex={-1} className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            {isPrivacy
              ? <ShieldCheck className="w-5 h-5 text-primary" aria-hidden="true" />
              : <FileText className="w-5 h-5 text-primary" aria-hidden="true" />}
          </div>
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Legal · Evaluation terms · Updated 7 October 2026
          </p>
        </div>

        <h1 className="font-display text-3xl md:text-4xl font-bold text-slate-900 mb-8">
          {isPrivacy ? 'Privacy Policy' : 'Terms of Service'}
        </h1>

        {isPrivacy ? <PrivacyContent /> : <TermsContent />}

        <div className="mt-12 pt-6 border-t border-border/60 flex flex-col sm:flex-row justify-between gap-4 text-sm">
          {isPrivacy ? (
            <button
              onClick={() => onNavigate(AppView.TERMS)}
              className="text-primary font-medium hover:underline text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary rounded"
            >
              Read the Terms of Service →
            </button>
          ) : (
            <button
              onClick={() => onNavigate(AppView.PRIVACY)}
              className="text-primary font-medium hover:underline text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary rounded"
            >
              Read the Privacy Policy →
            </button>
          )}
          <span className="text-muted-foreground">Questions? <a className="text-primary hover:underline underline-offset-2" href="mailto:hello@sme-toolkit.com">hello@sme-toolkit.com</a></span>
        </div>
      </main>
    </div>
  );
};

export default LegalPage;
