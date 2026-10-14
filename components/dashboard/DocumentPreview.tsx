import { useMemo } from 'react';
import type { BusinessContext } from '../../types/owner';

export interface DocumentLineItem {
  description: string;
  quantity: string;
  unit_price: string;
  discount: string;
  tax_percent: string;
}

export interface DocumentFormValues {
  kind: 'quotation' | 'invoice';
  customer_id: string;
  day: string;
  due_date: string;
  notes: string;
  terms: string;
  lines: DocumentLineItem[];
  version?: number;
}

export interface CustomerPreviewInfo {
  id?: string;
  name: string;
  email?: string;
  address?: string;
  registration_number?: string;
}

export interface DocumentPreviewProps {
  form: DocumentFormValues;
  customer?: CustomerPreviewInfo | null;
  context?: BusinessContext | null;
  currency?: string;
  documentNumber?: string;
  status?: string;
  paidCents?: number;
}

export function formatCurrency(cents: number, currency: string = 'MYR'): string {
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currency || 'MYR',
    }).format(cents / 100);
  } catch {
    return `${currency || 'MYR'} ${(cents / 100).toFixed(2)}`;
  }
}

export default function DocumentPreview({
  form,
  customer,
  context,
  currency: currencyProp,
  documentNumber,
  status,
  paidCents = 0,
}: DocumentPreviewProps) {
  const currency = currencyProp || context?.currency || 'MYR';

  // Client-side calculations matching backend rounding exactly
  const calculations = useMemo(() => {
    let subtotalCents = 0;
    let discountCents = 0;
    let taxCents = 0;

    const computedLines = form.lines.map((line) => {
      const qty = parseFloat(line.quantity) || 0;
      const price = parseFloat(line.unit_price) || 0;
      const disc = parseFloat(line.discount) || 0;
      const taxRate = parseFloat(line.tax_percent) || 0;

      const gross = Math.round(qty * price * 100);
      const lineDisc = Math.round(disc * 100);
      const cappedDisc = Math.min(gross, Math.max(0, lineDisc));
      const net = gross - cappedDisc;
      const lineTax = Math.round((net * taxRate) / 100);
      const total = net + lineTax;

      subtotalCents += gross;
      discountCents += cappedDisc;
      taxCents += lineTax;

      return {
        description: line.description || 'Item description',
        quantity: line.quantity || '0',
        unitPriceCents: Math.round(price * 100),
        grossCents: gross,
        discountCents: cappedDisc,
        taxPercent: line.tax_percent || '0',
        taxCents: lineTax,
        totalCents: total,
      };
    });

    const totalCents = Math.max(0, subtotalCents - discountCents + taxCents);
    const balanceCents = Math.max(0, totalCents - paidCents);

    return {
      lines: computedLines,
      subtotalCents,
      discountCents,
      taxCents,
      totalCents,
      balanceCents,
    };
  }, [form.lines, paidCents]);

  const docTypeLabel = form.kind === 'quotation' ? 'QUOTATION' : 'INVOICE';
  const displayDocNumber = documentNumber || 'DRAFT';
  const displayStatus = status || 'draft';

  return (
    <div className="bg-white text-zinc-900 border border-zinc-200 rounded-lg p-6 sm:p-8 shadow-sm font-sans text-xs sm:text-sm selection:bg-zinc-200">
      {/* Header: Logo & Seller info on Left, Document Meta on Right */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-6 border-b border-zinc-200 pb-6">
        <div className="space-y-2 max-w-[280px]">
          {context?.logo_data_url ? (
            <img
              src={context.logo_data_url}
              alt={context.company_name || 'Company logo'}
              className="max-w-[120px] max-h-16 object-contain mb-2"
            />
          ) : null}
          <h2 className="text-base sm:text-lg font-bold tracking-tight text-zinc-900">
            {context?.company_name || 'Your Company Name'}
          </h2>
          {context?.industry ? (
            <p className="text-xs text-zinc-500">{context.industry}</p>
          ) : null}
          {context?.website ? (
            <p className="text-xs text-zinc-500 break-all">{context.website}</p>
          ) : null}
        </div>

        <div className="sm:text-right space-y-1">
          <div className="flex sm:justify-end items-center gap-2">
            <span className="text-xl sm:text-2xl font-extrabold tracking-wider text-zinc-800">
              {docTypeLabel}
            </span>
            <span
              className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded tracking-wide ${
                displayStatus === 'paid'
                  ? 'bg-emerald-100 text-emerald-800'
                  : displayStatus === 'issued'
                  ? 'bg-blue-100 text-blue-800'
                  : displayStatus === 'accepted'
                  ? 'bg-teal-100 text-teal-800'
                  : 'bg-zinc-100 text-zinc-600'
              }`}
            >
              {displayStatus}
            </span>
          </div>
          <p className="text-sm font-mono font-medium text-zinc-700">{displayDocNumber}</p>
          <div className="text-xs text-zinc-500 pt-1 space-y-0.5">
            <div>
              <span className="text-zinc-400">Date: </span>
              <span className="font-medium text-zinc-700">{form.day || '—'}</span>
            </div>
            <div>
              <span className="text-zinc-400">
                {form.kind === 'invoice' ? 'Due Date: ' : 'Valid Until: '}
              </span>
              <span className="font-medium text-zinc-700">{form.due_date || '—'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bill To / Recipient block */}
      <div className="grid sm:grid-cols-2 gap-6 py-6 border-b border-zinc-200">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 block mb-1">
            {form.kind === 'quotation' ? 'Quotation For' : 'Billed To'}
          </span>
          {customer ? (
            <div className="space-y-0.5">
              <p className="font-bold text-zinc-900">{customer.name || 'Untitled Customer'}</p>
              {customer.registration_number ? (
                <p className="text-xs text-zinc-500">Reg: {customer.registration_number}</p>
              ) : null}
              {customer.email ? (
                <p className="text-xs text-zinc-600">{customer.email}</p>
              ) : null}
              {customer.address ? (
                <p className="text-xs text-zinc-600 whitespace-pre-line mt-1">
                  {customer.address}
                </p>
              ) : null}
            </div>
          ) : (
            <p className="text-xs italic text-zinc-400">No customer selected</p>
          )}
        </div>
      </div>

      {/* Line Items Table */}
      <div className="py-6 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-zinc-200 text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
              <th className="py-2 pr-3 text-left">Description</th>
              <th className="py-2 px-2 text-right">Qty</th>
              <th className="py-2 px-2 text-right">Unit Price</th>
              {calculations.discountCents > 0 && (
                <th className="py-2 px-2 text-right">Discount</th>
              )}
              <th className="py-2 px-2 text-right">Tax</th>
              <th className="py-2 pl-3 text-right">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100">
            {calculations.lines.length === 0 ? (
              <tr>
                <td
                  colSpan={calculations.discountCents > 0 ? 6 : 5}
                  className="py-4 text-center text-xs text-zinc-400 italic"
                >
                  No items added yet
                </td>
              </tr>
            ) : (
              calculations.lines.map((line, idx) => (
                <tr key={idx} className="text-xs text-zinc-700">
                  <td className="py-2.5 pr-3 text-left font-medium text-zinc-900 break-words">
                    {line.description}
                  </td>
                  <td className="py-2.5 px-2 text-right">{line.quantity}</td>
                  <td className="py-2.5 px-2 text-right">
                    {formatCurrency(line.unitPriceCents, currency)}
                  </td>
                  {calculations.discountCents > 0 && (
                    <td className="py-2.5 px-2 text-right text-zinc-500">
                      {line.discountCents > 0
                        ? `-${formatCurrency(line.discountCents, currency)}`
                        : '—'}
                    </td>
                  )}
                  <td className="py-2.5 px-2 text-right text-zinc-500">
                    {parseFloat(line.taxPercent) > 0 ? `${line.taxPercent}%` : '—'}
                  </td>
                  <td className="py-2.5 pl-3 text-right font-semibold text-zinc-900">
                    {formatCurrency(line.totalCents, currency)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Totals Summary */}
      <div className="flex justify-end pt-2 pb-6 border-b border-zinc-200">
        <div className="w-full sm:w-64 space-y-1.5 text-xs text-zinc-600">
          <div className="flex justify-between py-0.5">
            <span>Subtotal</span>
            <span className="font-medium text-zinc-800">
              {formatCurrency(calculations.subtotalCents, currency)}
            </span>
          </div>

          {calculations.discountCents > 0 && (
            <div className="flex justify-between py-0.5 text-zinc-600">
              <span>Discount</span>
              <span className="font-medium text-zinc-800">
                -{formatCurrency(calculations.discountCents, currency)}
              </span>
            </div>
          )}

          {calculations.taxCents > 0 && (
            <div className="flex justify-between py-0.5 text-zinc-600">
              <span>Tax</span>
              <span className="font-medium text-zinc-800">
                +{formatCurrency(calculations.taxCents, currency)}
              </span>
            </div>
          )}

          <div className="flex justify-between pt-2 border-t border-zinc-200 text-sm font-bold text-zinc-900">
            <span>Total</span>
            <span>{formatCurrency(calculations.totalCents, currency)}</span>
          </div>

          {form.kind === 'invoice' && paidCents > 0 && (
            <>
              <div className="flex justify-between py-0.5 text-emerald-700">
                <span>Paid to date</span>
                <span className="font-medium">
                  {formatCurrency(paidCents, currency)}
                </span>
              </div>
              <div className="flex justify-between pt-1 border-t border-zinc-100 font-semibold text-zinc-900">
                <span>Balance Due</span>
                <span>{formatCurrency(calculations.balanceCents, currency)}</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Notes & Terms */}
      {(form.notes || form.terms) && (
        <div className="pt-6 grid sm:grid-cols-2 gap-6 text-xs text-zinc-500">
          {form.notes ? (
            <div>
              <span className="font-semibold text-zinc-700 uppercase tracking-wider text-[11px] block mb-1">
                Notes
              </span>
              <p className="whitespace-pre-line leading-relaxed text-zinc-600">
                {form.notes}
              </p>
            </div>
          ) : null}

          {form.terms ? (
            <div>
              <span className="font-semibold text-zinc-700 uppercase tracking-wider text-[11px] block mb-1">
                Terms & Conditions
              </span>
              <p className="whitespace-pre-line leading-relaxed text-zinc-600">
                {form.terms}
              </p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
