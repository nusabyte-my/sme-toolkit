// Run: node scripts/check_strategy_modes.mjs. Isolated DOM and API fixtures; no live data or AI.
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
import { createServer } from 'vite';

const dom = new JSDOM('<div id="root"></div>', { url: 'http://localhost/' });
for (const name of ['window', 'document', 'HTMLElement', 'HTMLInputElement', 'HTMLTextAreaElement', 'Event', 'MouseEvent', 'localStorage', 'sessionStorage']) {
  Object.defineProperty(globalThis, name, { configurable: true, value: dom.window[name] });
}
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
globalThis.requestAnimationFrame = callback => setTimeout(callback, 0);
window.confirm = () => true;
sessionStorage.setItem('sme-toolkit-auth-token', 'isolated-check');
const { createElement: h, act } = await import('react');
const { createRoot } = await import('react-dom/client');
const server = await createServer({ configFile: false, esbuild: { jsx: 'automatic' }, optimizeDeps: { noDiscovery: true, include: [] }, server: { middlewareMode: true, hmr: false }, appType: 'custom' });
let root;
const documents = [], tasks = [];
let failSave = false;
globalThis.fetch = async (url, options = {}) => {
  const path = String(url);
  const method = options.method || 'GET';
  if (path.startsWith('/api/v1/owner/overview')) return Response.json({ context: { id: 'isolated-business', company_name: 'Local check', products_services: 'Office kits', target_market: 'Office managers' }, capabilities: { ai_available: false }, attention: [{ id: 'pending', title: 'Check a pending order', detail: 'Verify payment before fulfilment.', view: 'sales' }] });
  if (path.startsWith('/api/v1/workspace/documents')) {
    if (method === 'GET') return Response.json(documents.filter(row => row.kind === new URL(path, 'http://localhost').searchParams.get('kind')));
    if (failSave) { failSave = false; return Response.json({ detail: 'Temporary save failure' }, { status: 503 }); }
    const row = { ...JSON.parse(options.body), id: 'saved-plan', updated_at: '2026-01-01T00:00:00Z' };
    documents.push(row);
    return Response.json(row, { status: 201 });
  }
  if (path === '/api/v1/workspace/tasks') {
    if (method === 'GET') return Response.json(tasks);
    const row = { ...JSON.parse(options.body), id: 'saved-task', status: 'open', created_at: '2026-01-01T00:00:00Z' };
    tasks.push(row);
    return Response.json(row, { status: 201 });
  }
  throw Error(`Unexpected request: ${method} ${path}`);
};
try {
  const { OwnerProvider } = await server.ssrLoadModule('/contexts/OwnerContext.tsx');
  const { StrategyModeProvider } = await server.ssrLoadModule('/contexts/StrategyModeContext.tsx');
  const { default: Workbench } = await server.ssrLoadModule('/components/dashboard/BusinessWorkbench.tsx');
  async function mount(kind, username = 'check-owner') {
    if (root) await act(async () => root.unmount());
    root = createRoot(document.getElementById('root'));
    await act(async () => {
      root.render(h(OwnerProvider, null, h(StrategyModeProvider, { key: username, username }, h(Workbench, { kind }))));
      await new Promise(resolve => setTimeout(resolve, 0));
    });
  }
  async function click(selector) {
    const element = typeof selector === 'string' ? document.querySelector(selector) : selector;
    assert.ok(element, `Missing control: ${selector}`);
    await act(async () => { element.click(); await new Promise(resolve => setTimeout(resolve, 0)); });
  }
  async function fill(selector, value) {
    const element = document.querySelector(selector);
    assert.ok(element, `Missing field: ${selector}`);
    await act(async () => {
      const prototype = element.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(prototype, 'value').set.call(element, value);
      element.dispatchEvent(new Event(element.type === 'date' ? 'change' : 'input', { bubbles: true }));
    });
  }
  async function submit() {
    const form = [...document.querySelectorAll('form')].find(element => !element.classList.contains('hidden'));
    assert.ok(form, 'No visible editor');
    await act(async () => { form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); await new Promise(resolve => setTimeout(resolve, 0)); });
  }
  await mount('canvas');
  await fill('form input:not([name])', 'Office kits plan');
  await fill('[name="customers"]', 'Office managers');
  await fill('[name="value"]', 'Ready-to-deliver kits');
  await submit();
  await fill('[name="channels"]', 'Referrals');
  await click('fieldset input:not(:checked)');
  assert.equal(document.querySelector('[name="customers"]').value, 'Office managers');
  assert.equal(document.querySelector('[name="channels"]').value, 'Referrals');
  await fill('[name="partners"]', 'Local printer');
  await click('fieldset input:not(:checked)');
  assert.ok(document.querySelector('[name="channels"]'), 'Guided step was reset by mode switch');
  await click(document.querySelector('nav[aria-label="Plan steps"]').lastElementChild);
  assert.ok(document.querySelector('form').textContent.includes('Local printer'), 'Review lost experienced-mode edit');
  failSave = true;
  await submit();
  assert.ok(document.querySelector('[role="alert"]').textContent.includes('Temporary save failure'));
  assert.ok(document.querySelector('form').textContent.includes('Ready-to-deliver kits'), 'Failed save lost draft');
  await submit();
  assert.deepEqual(documents[0].fields, { customers: 'Office managers', value: 'Ready-to-deliver kits', channels: 'Referrals', partners: 'Local printer' });
  await click('fieldset input:not(:checked)');
  await mount('research');
  assert.ok(document.querySelector('[name="conclusion"]'), 'Preference did not persist across strategy tools');
  await mount('research', 'different-owner');
  assert.equal(document.querySelector('[name="conclusion"]'), null, 'One account inherited another account preference');
  await mount('seo', 'url-owner');
  await fill('form input:not([name])', 'Page plan');
  await fill('[name="url"]', 'ftp://example.test/page');
  await submit();
  assert.ok(document.querySelector('[name="url"]'), 'Invalid URL advanced to another step');
  assert.ok(document.querySelector('[role="alert"]').textContent.includes('http://'));
  await fill('[name="url"]', 'https://example.test/page');
  await submit();
  assert.ok(document.querySelector('[name="keywords"]'), 'Valid URL did not advance');
  await mount('quickwins', 'actions-owner');
  await click([...document.querySelectorAll('button')].find(button => button.textContent === 'Choose this priority'));
  assert.equal(tasks.length, 0, 'Choosing a priority created a task before review');
  await fill('form input[type="text"], form input:not([type])', 'Review the pending order');
  await submit();
  assert.equal(tasks.length, 0, 'Review created a task before approval');
  await click('fieldset input:not(:checked)');
  assert.equal(document.querySelector('form input:not([type])').value, 'Review the pending order');
  await click('fieldset input:not(:checked)');
  await submit();
  assert.equal(tasks.length, 1);
  assert.equal(tasks[0].notes, 'Verify payment before fulfilment.');
  assert.ok(document.body.textContent.includes('Track the work'));
  console.log('PASS: draft retention across modes/steps, save-error recovery, account-scoped preference, HTTP-only step validation and reviewed quick-win creation.');
} finally {
  if (root) await act(async () => root.unmount());
  await server.close();
  dom.window.close();
}
