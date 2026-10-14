// Run: node scripts/check_demo_session.mjs. No live API or business database is used.
import assert from 'node:assert/strict';
import { createServer } from 'vite';

const store = new Map();
globalThis.sessionStorage = {
  getItem: key => store.get(key) ?? null,
  setItem: (key, value) => store.set(key, String(value)),
  removeItem: key => store.delete(key),
};
globalThis.window = Object.assign(new EventTarget(), { location: { hash: '#/profiles' } });
const server = await createServer({ configFile: false, server: { middlewareMode: true, hmr: false }, appType: 'custom' });
try {
  const { exitDemoSession, authenticatedFetch } = await server.ssrLoadModule('/services/apiClient.ts');
  store.set('sme-toolkit-auth-token', 'demo-session');
  store.set('sme-toolkit-demo-token', 'demo-session');
  store.set('sme-toolkit-return-token', 'owner-session');
  let complete;
  globalThis.fetch = () => new Promise(resolve => { complete = resolve; });
  let changes = 0;
  window.addEventListener('sme-session-changed', () => changes++);
  const preventExit = event => event.preventDefault();
  window.addEventListener('sme-before-navigate', preventExit);
  const pending = authenticatedFetch('/api/v1/owner/context');
  exitDemoSession();
  assert.equal(store.get('sme-toolkit-auth-token'), 'demo-session');
  assert.equal(store.get('sme-toolkit-return-token'), 'owner-session');
  assert.equal(window.location.hash, '#/profiles');
  assert.equal(changes, 0);
  complete(new Response('{}', { status: 200 }));
  assert.equal((await pending).status, 200, 'A cancelled exit must not invalidate the current session');

  window.removeEventListener('sme-before-navigate', preventExit);
  const oldRequest = authenticatedFetch('/api/v1/owner/context');
  exitDemoSession();
  assert.equal(store.get('sme-toolkit-auth-token'), 'owner-session');
  assert.equal(store.has('sme-toolkit-demo-token'), false);
  assert.equal(store.has('sme-toolkit-return-token'), false);
  assert.equal(window.location.hash, '#/dashboard');
  assert.equal(changes, 1);
  complete(new Response('{}', { status: 200 }));
  await assert.rejects(oldRequest, error => error.status === 401, 'A response from the exited demo must not enter the owner session');

  store.set('sme-toolkit-auth-token', 'another-demo');
  store.set('sme-toolkit-demo-token', 'another-demo');
  exitDemoSession();
  assert.equal(store.has('sme-toolkit-auth-token'), false);
  assert.equal(window.location.hash, '#/');
  console.log('PASS: cancelled exit preserves edits/session; accepted exit restores owner; stale responses rejected; anonymous exit returns home');
} finally {
  await server.close();
}
