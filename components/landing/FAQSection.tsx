import React from 'react';

interface FAQItemData {
  question: string;
  answer: string;
}

const faqItems: FAQItemData[] = [
  { question: 'What is SME OS?', answer: 'SME OS is a working space for small-business owners to manage sales, customer follow-ups, quotations, invoices and daily tasks. Marketing tools and reviewable agents sit alongside those records. Start with the fictional Meranti business to see the product in use, then decide which workflow fits your business.' },
  { question: 'Can I try it without signing up?', answer: 'Yes, when the interactive demo is enabled. No signup or card is required. You get separate sample records to edit; your own business data stays untouched. If this deployment has no demo access, you can still browse the product examples or send a pilot enquiry.' },
  { question: 'Will the demo send messages or spend money?', answer: 'No. Demo messaging, paid AI and external actions are blocked. Recording a payment only changes the sample records; it does not charge a customer. In a real workspace, Telegram and WhatsApp require verified connections and an explicitly chosen reply policy.' },
  { question: 'What needs setup for my real business?', answer: 'Your business details and starting records come first. AI generation needs valid provider credentials; marketplace syncing needs a live connector. MP4 exports need FFmpeg. Hosting, backups, access and commercial terms are agreed separately. Enterprise SSO, an SLA and certification are not included claims.' },
  { question: 'What happens when I request a pilot?', answer: 'Tell us the workflow you want to improve. Your details are saved for administrator review, with a receipt reference. No meeting, subscription or payment is created automatically. The optional planning brief is a local download, not another enquiry.' },
];

const FAQSection: React.FC = () => {
  return (
    <section id="faq" className="py-12 sm:py-16 bg-background scroll-mt-24" aria-labelledby="faq-heading">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 id="faq-heading" className="font-display text-3xl sm:text-4xl font-semibold text-foreground mb-6">A few things worth knowing.</h2>

        <div className="space-y-4">
          {faqItems.map((item) => (
            <FAQItem key={item.question} question={item.question} answer={item.answer} />
          ))}
        </div>

      </div>
    </section>
  );
};

const FAQItem: React.FC<FAQItemData> = ({ question, answer }) => {
  return (
    <details className="border-b border-border py-2">
      <summary className="font-display font-semibold text-base sm:text-lg cursor-pointer min-h-11 py-2">{question}</summary>
      <p className="text-sm sm:text-base text-muted-foreground leading-relaxed mt-3">{answer}</p>
    </details>
  );
};

export default FAQSection;
