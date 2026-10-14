import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FileText,
  Plus,
  Printer,
  RefreshCw,
  Save,
  ArrowRight,
  Eye,
  ChevronDown,
  Sparkles,
} from 'lucide-react';
import { apiCall, authenticatedFetch } from '../../services/apiClient';
import { useOwner } from '../../contexts/OwnerContext';
import { useUnsavedChanges } from '../../hooks/useUnsavedChanges';
import WorkspaceLoading from '../common/WorkspaceLoading';
import DocumentPreview, {
  DocumentFormValues,
  DocumentLineItem,
} from './DocumentPreview';
import { AppView } from '../../types';

type Customer = {
  id: string;
  name: string;
  email: string;
  address: string;
  registration_number: string;
};

type Document = {
  id: string;
  kind: 'quotation' | 'invoice';
  number: string;
  status: string;
  day: string;
  due_date: string;
  currency: string;
  customer_id: string;
  customer: Customer;
  seller: { name: string; website: string };
  lines: {
    description: string;
    quantity: string;
    unit_price_cents: number;
    discount_cents: number;
    tax_percent: string;
    tax_cents: number;
    total_cents: number;
  }[];
  subtotal_cents: number;
  discount_cents: number;
  tax_cents: number;
  total_cents: number;
  paid_cents: number;
  balance_cents: number;
  notes: string;
  terms: string;
  decision_note: string;
  version: number;
  source_quote_id: string | null;
};

type Payment = {
  id: string;
  document_id: string;
  day: string;
  reference: string;
  amount_cents: number;
  reversal_id: string | null;
};

type Data = {
  customers: Customer[];
  documents: Document[];
  payments: Payment[];
  cash_accounts: { id: string; name: string; currency: string }[];
  notice: string;
};

interface QuickWin {
  id: string;
  urgency: number; // 1 (most urgent) to 5
  title: string;
  description: string;
  actionLabel: string;
  badge: string;
  badgeClass: string;
  action: () => void;
}

interface BillingWorkspaceProps {
  onNavigate?: (view: AppView) => void;
}

function getTodayIso(): string {
  return new Date().toLocaleDateString('en-CA');
}

function createDefaultLineItem(): DocumentLineItem {
  return {
    description: '',
    quantity: '1',
    unit_price: '',
    discount: '0',
    tax_percent: '0',
  };
}

function createDefaultForm(): DocumentFormValues {
  const currentDay = getTodayIso();
  return {
    kind: 'quotation',
    customer_id: '',
    day: currentDay,
    due_date: currentDay,
    notes: '',
    terms: '',
    lines: [createDefaultLineItem()],
    version: undefined,
  };
}
export default function BillingWorkspace({ onNavigate }: BillingWorkspaceProps = {}) {
  const { overview, refresh } = useOwner();
  const context = overview?.context;

  const [data, setData] = useState<Data | null>(null);
  const [selected, setSelected] = useState('');
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [form, setForm] = useState<DocumentFormValues>(createDefaultForm);
  const [editing, setEditing] = useState<string | null>(null);
  const [dirty, setDirty] = useState(false);
  const [customer, setCustomer] = useState({
    name: '',
    email: '',
    address: '',
    registration_number: '',
  });
  const [showCustomer, setShowCustomer] = useState(false);
  const [payment, setPayment] = useState({
    day: getTodayIso(),
    reference: '',
    amount: '',
    account_id: '',
  });
  const [action, setAction] = useState('');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [quickWinsOpen, setQuickWinsOpen] = useState(true);

  useUnsavedChanges(
    dirty ||
      !!busy ||
      !!customer.name ||
      !!payment.reference ||
      !!payment.amount ||
      !!payment.account_id ||
      !!note
  );

  const load = useCallback(async () => {
    const next = await apiCall<Data>('/api/v1/billing/');
    setData(next);
    return next;
  }, []);

  useEffect(() => {
    let active = true;
    if (context) {
      apiCall<Data>('/api/v1/billing/')
        .then((next) => {
          if (active) setData(next);
        })
        .catch((e) => {
          if (active) setError(e.message);
        });
    }
    return () => {
      active = false;
    };
  }, [context?.id]);

  const act = async (key: string, work: () => Promise<void>) => {
    if (busy) return;
    setBusy(key);
    setError('');
    setMessage('');
    try {
      await work();
      await load();
      await refresh();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : 'The document could not be saved. Your edits remain here.'
      );
    } finally {
      setBusy('');
    }
  };

  const money = (value: number, currency = context?.currency || 'MYR') =>
    new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(
      value / 100
    );

  const choose = (id: string) => {
    if (
      (dirty || payment.reference || payment.amount || payment.account_id || note) &&
      !confirm('Discard unsaved document, payment or decision changes?')
    )
      return;
    setSelected(id);
    setEditing(null);
    setDirty(false);
    setAction('');
    setNote('');
    setPayment({ day: getTodayIso(), reference: '', amount: '', account_id: '' });
  };

  const edit = (doc: Document) => {
    if (dirty && !confirm('Discard unsaved document changes?')) return;
    setForm({
      kind: doc.kind,
      customer_id: doc.customer_id,
      day: doc.day,
      due_date: doc.due_date,
      notes: doc.notes,
      terms: doc.terms,
      version: doc.version,
      lines: doc.lines.map((l) => ({
        description: l.description,
        quantity: l.quantity,
        unit_price: (l.unit_price_cents / 100).toFixed(2),
        discount: (l.discount_cents / 100).toFixed(2),
        tax_percent: l.tax_percent,
      })),
    });
    setEditing(doc.id);
    setDirty(false);
  };

  const change = (patch: Partial<DocumentFormValues>) => {
    setForm((prev) => ({ ...prev, ...patch }));
    setDirty(true);
  };

  // Derive Quick Win Suggestions from data
  // Conditions: draft quotes >14d, issued quotes >7d, overdue invoices, missing terms, no logo
  // Max 5, most urgent first. Each with action button.
  const quickWins = useMemo(() => {
    if (!data) return [];
    const wins: QuickWin[] = [];
    const now = Date.now();
    const currentDay = getTodayIso();

    // 1. Overdue invoices (Urgency 1 - Highest)
    for (const doc of data.documents) {
      if (
        doc.kind === 'invoice' &&
        doc.status === 'issued' &&
        doc.due_date < currentDay &&
        doc.balance_cents > 0
      ) {
        const daysOverdue = Math.max(
          1,
          Math.floor((now - new Date(doc.due_date).getTime()) / 86400000)
        );
        wins.push({
          id: `overdue-${doc.id}`,
          urgency: 1,
          title: `Overdue invoice: ${doc.number}`,
          description: `${doc.customer.name} owes ${money(
            doc.balance_cents,
            doc.currency
          )} (${daysOverdue}d overdue since ${doc.due_date}).`,
          actionLabel: 'Record payment',
          badge: 'Overdue',
          badgeClass:
            'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20',
          action: () => choose(doc.id),
        });
      }
    }

    // 2. Issued quotes > 7 days (Urgency 2)
    for (const doc of data.documents) {
      if (doc.kind === 'quotation' && doc.status === 'issued') {
        const daysSince = Math.floor(
          (now - new Date(doc.day).getTime()) / 86400000
        );
        if (daysSince > 7) {
          wins.push({
            id: `quote-followup-${doc.id}`,
            urgency: 2,
            title: `Follow up on quote: ${doc.number}`,
            description: `Issued ${daysSince} days ago to ${
              doc.customer.name
            } (${money(doc.total_cents, doc.currency)}). Check in to close deal.`,
            actionLabel: 'Review quote',
            badge: 'Follow-up',
            badgeClass:
              'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
            action: () => choose(doc.id),
          });
        }
      }
    }

    // 3. Draft quotes > 14 days (Urgency 3)
    for (const doc of data.documents) {
      if (doc.kind === 'quotation' && doc.status === 'draft') {
        const daysSince = Math.floor(
          (now - new Date(doc.day).getTime()) / 86400000
        );
        if (daysSince > 14) {
          wins.push({
            id: `draft-quote-${doc.id}`,
            urgency: 3,
            title: `Stale draft quote: ${doc.number}`,
            description: `Draft started ${daysSince} days ago for ${
              doc.customer.name
            } (${money(doc.total_cents, doc.currency)}). Finalize or clear.`,
            actionLabel: 'Edit draft',
            badge: 'Stale draft',
            badgeClass:
              'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20',
            action: () => edit(doc),
          });
        }
      }
    }

    // 4. Missing terms (Urgency 4)
    for (const doc of data.documents) {
      if (doc.status !== 'void' && (!doc.terms || !doc.terms.trim())) {
        wins.push({
          id: `missing-terms-${doc.id}`,
          urgency: 4,
          title: `Missing terms on ${doc.number}`,
          description: `Add payment terms or validity period to ${doc.customer.name}'s ${doc.kind} to protect your business.`,
          actionLabel: doc.status === 'draft' ? 'Add terms' : 'View document',
          badge: 'Missing terms',
          badgeClass:
            'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
          action: () => (doc.status === 'draft' ? edit(doc) : choose(doc.id)),
        });
      }
    }

    // 5. No logo (Urgency 5)
    if (!context?.logo_data_url || !context.logo_data_url.trim()) {
      wins.push({
        id: 'no-logo',
        urgency: 5,
        title: 'Add company logo',
        description:
          'Upload your business logo in Business Profile to brand your printed and PDF invoices.',
        actionLabel: 'Upload logo',
        badge: 'Branding',
        badgeClass:
          'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
        action: () => {
          if (dirty && !confirm('Discard unsaved document changes?')) return;
          if (onNavigate) {
            onNavigate(AppView.PROFILES);
          } else {
            window.location.hash = '#/profiles';
          }
        },
      });
    }

    // Sort by urgency ascending (1 is highest urgency) and cap at 5
    return wins.sort((a, b) => a.urgency - b.urgency).slice(0, 5);
  }, [data, context, onNavigate, dirty]);

  if (!context) {
    return (
      <section className="owner-panel">
        <p>Save business context before creating customer documents.</p>
        <a href="#/profiles" className="owner-button mt-4">
          Set up business context
        </a>
      </section>
    );
  }

  if (!data && !error) return <WorkspaceLoading label="quotations and invoices" />;

  const active = data?.documents.find((d) => d.id === selected);
  const documents =
    data?.documents.filter(
      (d) =>
        (filter === 'all' || d.kind === filter) &&
        `${d.number} ${d.customer.name} ${d.status}`
          .toLowerCase()
          .includes(search.toLowerCase())
    ) || [];

  const editingDoc =
    editing && editing !== 'new'
      ? data?.documents.find((d) => d.id === editing)
      : null;

  const decision = async (name: string) => {
    if (!active) return;
    if (['accept', 'decline', 'void'].includes(name)) {
      setAction(name);
      setNote('');
      return;
    }
    if (
      name === 'issue' &&
      !confirm(
        active.kind === 'invoice'
          ? 'Issue this invoice? Its values become immutable and receivable/income/tax post to bookkeeping.'
          : 'Issue this quotation and lock its values?'
      )
    )
      return;
    await act(name, async () => {
      const result = await apiCall<Document>(
        `/api/v1/billing/documents/${active.id}/action`,
        'POST',
        { action: name }
      );
      setSelected(result.id);
      setMessage(
        name === 'convert'
          ? 'Invoice draft created from the accepted quote. Review before issuing.'
          : 'Document issued. No message or payment was sent.'
      );
    });
  };

  return (
    <div className="space-y-5">
      {/* Workspace Header */}
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold flex gap-2 items-center">
            <FileText className="w-6 h-6 text-primary" />
            Quotations & invoices
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Agree the work. Issue the invoice. Record the payment once.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="owner-button-secondary"
            disabled={!!busy}
            onClick={() =>
              void act('refresh', async () => {
                setMessage('Documents refreshed.');
              })
            }
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            className="owner-button-secondary"
            onClick={() => setShowCustomer(!showCustomer)}
          >
            Add customer
          </button>
          <button
            className="owner-button"
            disabled={!data?.customers.length}
            onClick={() => {
              if (dirty && !confirm('Discard unsaved draft?')) return;
              setEditing('new');
              setForm({
                ...createDefaultForm(),
                customer_id: data?.customers[0]?.id || '',
              });
              setDirty(false);
            }}
          >
            <Plus className="w-4 h-4" />
            New document
          </button>
        </div>
      </div>

      {/* Quick Win Suggestions (Collapsible) */}
      {quickWins.length > 0 && (
        <section className="owner-panel !p-4 bg-muted/20 border border-border">
          <button
            type="button"
            className="w-full flex items-center justify-between text-left focus-visible:outline-none"
            onClick={() => setQuickWinsOpen(!quickWinsOpen)}
            aria-expanded={quickWinsOpen}
          >
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-5 h-5 text-primary" />
              <div>
                <span className="font-semibold text-sm">Quick Win Suggestions</span>
                <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                  {quickWins.length} action{quickWins.length === 1 ? '' : 's'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span>{quickWinsOpen ? 'Hide' : 'Show'}</span>
              <ChevronDown
                className={`w-4 h-4 transition-transform duration-200 ${
                  quickWinsOpen ? 'rotate-180' : ''
                }`}
              />
            </div>
          </button>

          {quickWinsOpen && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {quickWins.map((win) => (
                <div
                  key={win.id}
                  className="flex flex-col justify-between p-3.5 rounded-lg border border-border bg-card hover:border-primary/40 transition-colors space-y-3"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${win.badgeClass}`}
                      >
                        {win.badge}
                      </span>
                    </div>
                    <h4 className="font-semibold text-sm leading-tight text-foreground">
                      {win.title}
                    </h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {win.description}
                    </p>
                  </div>
                  <button
                    type="button"
                    className="owner-button-secondary !py-1.5 !px-3 text-xs w-full justify-center font-medium self-end"
                    onClick={win.action}
                  >
                    {win.actionLabel}
                    <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Notifications */}
      {error && (
        <p role="alert" className="owner-error">
          {error}
        </p>
      )}
      {(busy || message) && (
        <p role="status" className="text-sm">
          {busy ? 'Working on your document…' : message}
        </p>
      )}

      {/* Add Customer Inline Form */}
      {showCustomer && (
        <form
          className="owner-panel space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            void act('customer', async () => {
              const saved = await apiCall<Customer>(
                '/api/v1/billing/customers',
                'POST',
                customer
              );
              setCustomer({
                name: '',
                email: '',
                address: '',
                registration_number: '',
              });
              setShowCustomer(false);
              setForm({ ...form, customer_id: saved.id });
              setMessage('Customer saved. Create a quotation or invoice.');
            });
          }}
        >
          <h3 className="font-semibold">Customer details</h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {(
              [
                ['name', 'Customer / company name'],
                ['email', 'Customer email'],
                ['registration_number', 'Registration number'],
                ['address', 'Billing address'],
              ] as const
            ).map(([key, label]) => (
              <label key={key} className="owner-label">
                {label}
                <input
                  className="owner-input"
                  type={key === 'email' ? 'email' : 'text'}
                  value={customer[key]}
                  maxLength={
                    key === 'address'
                      ? 1000
                      : key === 'name'
                      ? 160
                      : key === 'email'
                      ? 254
                      : 80
                  }
                  required={key === 'name'}
                  onChange={(e) =>
                    setCustomer({ ...customer, [key]: e.target.value })
                  }
                />
              </label>
            ))}
          </div>
          <button
            className="owner-button"
            disabled={!!busy || !customer.name.trim()}
          >
            Save customer
          </button>
        </form>
      )}

      {/* Zero customers state */}
      {data && !data.customers.length && !showCustomer && (
        <section className="owner-panel">
          <h3 className="font-semibold">Start with a customer</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Customer details are snapshotted when the document is created. Later
            changes cannot rewrite an issued invoice.
          </p>
          <button
            className="owner-button mt-4"
            onClick={() => setShowCustomer(true)}
          >
            Add first customer
          </button>
        </section>
      )}

      {/* EDITING STATE: Split layout on xl, collapsible preview below on smaller screens */}
      {editing && (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-6 items-start">
          {/* Left: Editor form */}
          <form
            className="owner-panel space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              void act('save', async () => {
                const saved = await apiCall<Document>(
                  editing === 'new'
                    ? '/api/v1/billing/documents'
                    : `/api/v1/billing/documents/${editing}`,
                  editing === 'new' ? 'POST' : 'PUT',
                  form
                );
                setSelected(saved.id);
                setEditing(null);
                setDirty(false);
                setMessage('Draft saved. Review totals before issuing.');
              });
            }}
          >
            <div className="flex justify-between items-center gap-3">
              <h3 className="font-semibold text-lg">
                {editing === 'new' ? 'New document' : 'Edit draft'}
              </h3>
              <button
                type="button"
                className="owner-button-secondary"
                onClick={() => {
                  if (!dirty || confirm('Discard unsaved document changes?')) {
                    setEditing(null);
                    setDirty(false);
                  }
                }}
              >
                Cancel
              </button>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <label className="owner-label">
                Document type
                <select
                  className="owner-input"
                  value={form.kind}
                  disabled={editing !== 'new'}
                  onChange={(e) =>
                    change({ kind: e.target.value as 'quotation' | 'invoice' })
                  }
                >
                  <option value="quotation">Quotation</option>
                  <option value="invoice">Invoice</option>
                </select>
              </label>
              <label className="owner-label">
                Customer
                <select
                  className="owner-input"
                  value={form.customer_id}
                  required
                  onChange={(e) => change({ customer_id: e.target.value })}
                >
                  <option value="">Choose customer</option>
                  {data?.customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="owner-label">
                Document date
                <input
                  className="owner-input"
                  type="date"
                  value={form.day}
                  required
                  onChange={(e) => change({ day: e.target.value })}
                />
              </label>
              <label className="owner-label">
                {form.kind === 'quotation' ? 'Valid until' : 'Payment due'}
                <input
                  className="owner-input"
                  type="date"
                  min={form.day}
                  value={form.due_date}
                  required
                  onChange={(e) => change({ due_date: e.target.value })}
                />
              </label>
            </div>

            <p className="text-xs text-muted-foreground">
              Currency: {context.currency}. Tax is supplied by you; no tax rate is
              inferred. Server calculates line rounding and totals.
            </p>

            <div className="space-y-3">
              {form.lines.map((l, index) => (
                <fieldset
                  key={index}
                  className="grid grid-cols-2 lg:grid-cols-[minmax(180px,2fr)_repeat(4,minmax(70px,1fr))_auto] gap-2 border-t border-border pt-3"
                >
                  <legend className="sr-only">Line {index + 1}</legend>
                  {(
                    [
                      ['description', 'Description'],
                      ['quantity', 'Quantity'],
                      ['unit_price', 'Unit price'],
                      ['discount', 'Line discount'],
                      ['tax_percent', 'Tax %'],
                    ] as const
                  ).map(([key, label]) => (
                    <label
                      key={key}
                      className={`owner-label ${
                        key === 'description' ? 'col-span-2 lg:col-span-1' : ''
                      }`}
                    >
                      {label}
                      <input
                        className="owner-input"
                        type={key === 'description' ? 'text' : 'number'}
                        min={key === 'quantity' ? '0.001' : '0'}
                        max={key === 'tax_percent' ? '100' : undefined}
                        step={key === 'quantity' ? '0.001' : '0.01'}
                        maxLength={key === 'description' ? 500 : undefined}
                        value={l[key]}
                        required
                        onChange={(e) =>
                          change({
                            lines: form.lines.map((row, i) =>
                              i === index
                                ? { ...row, [key]: e.target.value }
                                : row
                            ),
                          })
                        }
                      />
                    </label>
                  ))}
                  <button
                    type="button"
                    className="owner-button-secondary self-end"
                    disabled={form.lines.length === 1}
                    onClick={() =>
                      change({
                        lines: form.lines.filter((_, i) => i !== index),
                      })
                    }
                  >
                    Remove
                  </button>
                </fieldset>
              ))}
            </div>

            <button
              type="button"
              className="owner-button-secondary"
              disabled={form.lines.length >= 100}
              onClick={() => change({ lines: [...form.lines, createDefaultLineItem()] })}
            >
              <Plus className="w-4 h-4" />
              Add line item
            </button>

            <div className="grid sm:grid-cols-2 gap-3">
              <label className="owner-label">
                Notes
                <textarea
                  className="owner-input"
                  rows={3}
                  value={form.notes}
                  maxLength={4000}
                  placeholder="Special instructions, delivery terms, or client note…"
                  onChange={(e) => change({ notes: e.target.value })}
                />
              </label>
              <label className="owner-label">
                Terms / payment instructions
                <textarea
                  className="owner-input"
                  rows={3}
                  value={form.terms}
                  maxLength={4000}
                  placeholder="Bank account details, due on receipt, validity conditions…"
                  onChange={(e) => change({ terms: e.target.value })}
                />
              </label>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                className="owner-button"
                disabled={!!busy || !form.customer_id}
              >
                <Save className="w-4 h-4" />
                Save draft
              </button>
              <button
                type="button"
                className="owner-button-secondary"
                onClick={() => {
                  if (!dirty || confirm('Discard unsaved document changes?')) {
                    setEditing(null);
                    setDirty(false);
                  }
                }}
              >
                Cancel
              </button>
            </div>

            {/* Below xl: Collapsible preview underneath form */}
            <details
              className="xl:hidden border-t border-border pt-4 group"
              open
            >
              <summary className="cursor-pointer font-semibold flex items-center justify-between text-sm select-none list-none text-foreground py-2">
                <span className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-primary" />
                  Live Document Preview
                </span>
                <span className="text-xs text-primary underline group-open:hidden">
                  Show preview
                </span>
                <span className="text-xs text-muted-foreground hidden group-open:inline">
                  Hide preview
                </span>
              </summary>
              <div className="mt-3 overflow-hidden">
                <DocumentPreview
                  form={form}
                  customer={data?.customers.find(
                    (c) => c.id === form.customer_id
                  )}
                  context={context}
                  currency={context?.currency}
                  documentNumber={editingDoc?.number}
                  status={editingDoc?.status || 'draft'}
                />
              </div>
            </details>
          </form>

          {/* Right: Live Document Preview on xl+ screens */}
          <div className="hidden xl:block sticky top-6 space-y-2">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5 text-primary" />
                Live Document Preview
              </span>
              <span className="text-[11px] text-muted-foreground">
                Updates live as you type
              </span>
            </div>
            <DocumentPreview
              form={form}
              customer={data?.customers.find((c) => c.id === form.customer_id)}
              context={context}
              currency={context?.currency}
              documentNumber={editingDoc?.number}
              status={editingDoc?.status || 'draft'}
            />
          </div>
        </div>
      )}

      {/* VIEWING STATE: Document List and Active Details */}
      {!editing && (
        <div className="grid grid-cols-1 xl:grid-cols-[300px_minmax(0,1fr)] gap-5 items-start">
          <section className="owner-panel !p-4">
            <h3 className="font-semibold">Documents</h3>
            <label className="owner-label mt-3">
              Find a document
              <input
                className="owner-input"
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Number, customer, status…"
              />
            </label>
            <label className="owner-label mt-3">
              Type
              <select
                className="owner-input"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="all">All documents</option>
                <option value="quotation">Quotations</option>
                <option value="invoice">Invoices</option>
              </select>
            </label>
            <div className="divide-y divide-border mt-3">
              {documents.map((d) => (
                <button
                  key={d.id}
                  className={`w-full text-left py-3 text-sm ${
                    selected === d.id ? 'text-primary font-semibold' : ''
                  }`}
                  onClick={() => choose(d.id)}
                >
                  <span className="block">
                    {d.number} · {d.status}
                  </span>
                  <span className="block text-xs text-muted-foreground mt-1">
                    {d.customer.name} · {money(d.total_cents, d.currency)}
                  </span>
                </button>
              ))}
              {!documents.length && (
                <p className="text-sm text-muted-foreground py-4">
                  No matching documents. Create a customer and draft to begin.
                </p>
              )}
            </div>
          </section>

          <section className="owner-panel min-w-0">
            {active ? (
              <>
                <div className="flex flex-wrap justify-between gap-3">
                  <div>
                    <h3 className="font-display text-xl font-semibold">
                      {active.number}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1 capitalize">
                      {active.kind} · {active.status} · {active.currency}
                    </p>
                  </div>
                  <button
                    className="owner-button-secondary"
                    disabled={!!busy}
                    onClick={() =>
                      void act('print', async () => {
                        const response = await authenticatedFetch(
                          `/api/v1/billing/documents/${active.id}/print`
                        );
                        const url = URL.createObjectURL(
                          new Blob([await response.text()], {
                            type: 'text/html',
                          })
                        );
                        window.open(url, '_blank', 'noopener,noreferrer');
                        setTimeout(() => URL.revokeObjectURL(url), 60000);
                        setMessage(
                          'Printable document opened. Use browser Print / Save as PDF.'
                        );
                      })
                    }
                  >
                    <Printer className="w-4 h-4" />
                    Print / PDF
                  </button>
                </div>

                <div className="grid sm:grid-cols-2 gap-4 my-5 text-sm">
                  <div>
                    <strong>{active.customer.name}</strong>
                    <p className="whitespace-pre-wrap text-muted-foreground">
                      {active.customer.address}
                    </p>
                    <p className="text-muted-foreground">
                      {active.customer.email}
                    </p>
                  </div>
                  <div>
                    <p>Date: {active.day}</p>
                    <p>
                      {active.kind === 'quotation' ? 'Valid until' : 'Due'}:{' '}
                      {active.due_date}
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr>
                        <th className="text-left">Description</th>
                        <th className="text-right">Qty</th>
                        <th className="text-right">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {active.lines.map((l, index) => (
                        <tr key={index} className="border-t border-border">
                          <td className="py-3 min-w-32">
                            {l.description}
                            <p className="text-xs text-muted-foreground">
                              Unit {money(l.unit_price_cents, active.currency)}{' '}
                              · discount{' '}
                              {money(l.discount_cents, active.currency)} · tax{' '}
                              {l.tax_percent}%
                            </p>
                          </td>
                          <td className="text-right">{l.quantity}</td>
                          <td className="text-right whitespace-nowrap">
                            {money(l.total_cents, active.currency)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <dl className="ml-auto max-w-xs space-y-2 text-sm mt-5">
                  {[
                    ['Subtotal', active.subtotal_cents],
                    ['Discount', active.discount_cents],
                    ['Tax', active.tax_cents],
                    ['Total', active.total_cents],
                    ...(active.kind === 'invoice'
                      ? [
                          ['Paid', active.paid_cents],
                          ['Balance', active.balance_cents],
                        ]
                      : []),
                  ].map(([label, value]) => (
                    <div key={label} className="flex justify-between gap-4">
                      <dt>{label}</dt>
                      <dd className="font-semibold tabular-nums">
                        {money(Number(value), active.currency)}
                      </dd>
                    </div>
                  ))}
                </dl>

                <p className="whitespace-pre-wrap text-sm mt-5">{active.notes}</p>
                <p className="whitespace-pre-wrap text-xs text-muted-foreground mt-3">
                  {active.terms}
                </p>

                <div className="flex flex-wrap gap-2 mt-5">
                  {active.status === 'draft' && (
                    <>
                      <button
                        className="owner-button-secondary"
                        onClick={() => edit(active)}
                      >
                        Edit draft
                      </button>
                      <button
                        className="owner-button"
                        disabled={!!busy}
                        onClick={() => void decision('issue')}
                      >
                        Issue {active.kind}
                      </button>
                    </>
                  )}
                  {active.kind === 'quotation' && active.status === 'issued' && (
                    <>
                      <button
                        className="owner-button"
                        onClick={() => void decision('accept')}
                      >
                        Record acceptance
                      </button>
                      <button
                        className="owner-button-secondary"
                        onClick={() => void decision('decline')}
                      >
                        Record decline
                      </button>
                    </>
                  )}
                  {active.kind === 'quotation' &&
                    active.status === 'accepted' && (
                      <button
                        className="owner-button"
                        disabled={!!busy}
                        onClick={() => void decision('convert')}
                      >
                        Create invoice
                        <ArrowRight className="w-4 h-4 ml-1" />
                      </button>
                    )}
                  {['draft', 'issued'].includes(active.status) && (
                    <button
                      className="owner-button-secondary"
                      onClick={() => void decision('void')}
                    >
                      Void document
                    </button>
                  )}
                </div>

                {action && (
                  <form
                    className="mt-4 border-t border-border pt-4 space-y-3"
                    onSubmit={(e) => {
                      e.preventDefault();
                      void act(action, async () => {
                        await apiCall(
                          `/api/v1/billing/documents/${active.id}/action`,
                          'POST',
                          { action, note }
                        );
                        setAction('');
                        setNote('');
                        setMessage('Document decision recorded.');
                      });
                    }}
                  >
                    <label className="owner-label">
                      {action === 'void'
                        ? 'Void reason'
                        : 'Customer decision evidence / reference'}
                      <textarea
                        className="owner-input"
                        rows={2}
                        required
                        maxLength={1000}
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                      />
                    </label>
                    <p className="text-xs text-muted-foreground">
                      This records your review. It does not independently verify
                      customer acceptance or send a message.
                    </p>
                    <button
                      className="owner-button"
                      disabled={!!busy || !note.trim()}
                    >
                      Confirm {action}
                    </button>
                    <button
                      type="button"
                      className="owner-button-secondary ml-2"
                      onClick={() => {
                        setAction('');
                        setNote('');
                      }}
                    >
                      Cancel
                    </button>
                  </form>
                )}

                {active.kind === 'invoice' && active.status === 'issued' && (
                  <form
                    className="mt-6 border-t border-border pt-4 space-y-3"
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (
                        !confirm(
                          'Record this received payment and post it to bookkeeping? This does not charge the customer.'
                        )
                      )
                        return;
                      void act('payment', async () => {
                        await apiCall(
                          `/api/v1/billing/documents/${active.id}/payments`,
                          'POST',
                          payment
                        );
                        setPayment({
                          day: getTodayIso(),
                          reference: '',
                          amount: '',
                          account_id: '',
                        });
                        setMessage(
                          'Payment recorded and posted once to bookkeeping.'
                        );
                      });
                    }}
                  >
                    <h4 className="font-semibold">Record a received payment</h4>
                    <div className="grid sm:grid-cols-2 gap-3">
                      <label className="owner-label">
                        Payment date
                        <input
                          className="owner-input"
                          type="date"
                          min={active.day}
                          max={getTodayIso()}
                          value={payment.day}
                          onChange={(e) =>
                            setPayment({ ...payment, day: e.target.value })
                          }
                          required
                        />
                      </label>
                      <label className="owner-label">
                        Unique payment reference
                        <input
                          className="owner-input"
                          value={payment.reference}
                          maxLength={100}
                          onChange={(e) =>
                            setPayment({
                              ...payment,
                              reference: e.target.value,
                            })
                          }
                          required
                        />
                      </label>
                      <label className="owner-label">
                        Received amount
                        <input
                          className="owner-input"
                          type="number"
                          min="0.01"
                          max={active.balance_cents / 100}
                          step="0.01"
                          value={payment.amount}
                          onChange={(e) =>
                            setPayment({ ...payment, amount: e.target.value })
                          }
                          required
                        />
                      </label>
                      <label className="owner-label">
                        Receiving account
                        <select
                          className="owner-input"
                          value={payment.account_id}
                          onChange={(e) =>
                            setPayment({
                              ...payment,
                              account_id: e.target.value,
                            })
                          }
                          required
                        >
                          <option value="">Choose cash / bank</option>
                          {data?.cash_accounts
                            .filter((a) => a.currency === active.currency)
                            .map((a) => (
                              <option key={a.id} value={a.id}>
                                {a.name}
                              </option>
                            ))}
                        </select>
                      </label>
                    </div>
                    <button className="owner-button" disabled={!!busy}>
                      Record payment
                    </button>
                  </form>
                )}

                {active.kind === 'invoice' && (
                  <div className="mt-5 divide-y divide-border">
                    {data?.payments
                      .filter((p) => p.document_id === active.id)
                      .map((p) => (
                        <div
                          key={p.id}
                          className="py-3 flex flex-wrap justify-between gap-2 text-sm"
                        >
                          <span className="min-w-0 break-all">
                            {p.day} · {p.reference} ·{' '}
                            {money(p.amount_cents, active.currency)}
                            {p.reversal_id ? ' · reversed' : ''}
                          </span>
                          {!p.reversal_id && (
                            <button
                              className="text-primary underline min-h-9"
                              disabled={!!busy}
                              onClick={() => {
                                const reason = prompt(
                                  'Reason for reversing this recorded payment?'
                                );
                                if (reason)
                                  void act('reverse-payment', async () => {
                                    await apiCall(
                                      `/api/v1/billing/payments/${p.id}/reverse`,
                                      'POST',
                                      { day: getTodayIso(), reason }
                                    );
                                    setMessage(
                                      'Payment reversed; invoice balance restored.'
                                    );
                                  });
                              }}
                            >
                              Reverse payment
                            </button>
                          )}
                        </div>
                      ))}
                  </div>
                )}
              </>
            ) : (
              <div className="py-12 text-center">
                <FileText className="w-10 h-10 text-primary mx-auto" />
                <h3 className="font-semibold mt-4">Choose a document</h3>
                <p className="text-sm text-muted-foreground mt-2">
                  Review its snapshot, totals, decisions and payments here.
                </p>
              </div>
            )}
          </section>
        </div>
      )}

      <p className="text-xs text-muted-foreground leading-relaxed">
        {data?.notice}
      </p>
    </div>
  );
}
