import React, { useEffect, useState } from "react";
import { LockKeyhole, ArrowRight, LoaderCircle } from "lucide-react";
import {
  authenticate,
  getCurrentUser,
  ApiError,
  startDemoSession,
} from "../../services/apiClient";

export default function AuthGate({
  children,
}: {
  children: (username: string) => React.ReactNode;
}) {
  const [account, setAccount] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState<'' | 'login' | 'demo'>('');
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    let request = 0;
    const changed = () => {
      const sequence = ++request;
      setAccount(null);
      setChecking(true);
      setPassword('');
      setError('');
      getCurrentUser().then(user => {
        if (active && sequence === request) setAccount(user.username);
      }).catch(err => {
        if (active && sequence === request && !(err instanceof ApiError && err.status === 401))
          setError('Cannot reach the API. Start the backend, then sign in again.');
      }).finally(() => {
        if (active && sequence === request) setChecking(false);
      });
    };
    changed();
    window.addEventListener('sme-session-changed', changed);
    return () => {
      active = false;
      window.removeEventListener("sme-session-changed", changed);
    };
  }, []);
  if (checking)
    return (
      <main className="min-h-screen grid place-items-center" aria-busy="true">
        <p role="status">Checking your session…</p>
      </main>
    );
  if (account)
    return <React.Fragment key={account}>{children(account)}</React.Fragment>;
  return (
    <main className="min-h-screen grid place-items-center bg-background p-6 text-foreground">
      <form
        className="w-full max-w-md rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-5"
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy('login');
          setError("");
          try {
            await authenticate(username.trim(), password);
            const user = await getCurrentUser();
            setPassword("");
            setAccount(user.username);
          } catch (err) {
            setError(
              err instanceof Error
                ? err.message
                : "Sign-in failed. Check your credentials and try again.",
            );
          } finally {
            setBusy('');
          }
        }}
      >
        <LockKeyhole className="h-8 w-8 text-primary" aria-hidden="true" />
        <div>
          <h1 className="font-display text-2xl font-bold">
            Open your business workspace
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Your context, sales and creative drafts belong to your account.
          </p>
        </div>
        <label className="block text-sm font-medium">
          Username
          <input
            className="owner-input mt-2"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            maxLength={120}
          />
        </label>
        <label className="block text-sm font-medium">
          Password
          <input
            className="owner-input mt-2"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            maxLength={256}
          />
        </label>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <button
          className="owner-button w-full"
          disabled={!!busy || !username.trim() || !password}
        >
          {busy === 'login' ? 'Signing in…' : 'Open my workspace'}
          <ArrowRight className="h-4 w-4" />
        </button>
        <p className="text-xs text-muted-foreground">
          Use the account configured by your workspace administrator. API
          credentials stay on the server.
        </p>
        <button type="button" className="owner-button-secondary w-full" disabled={!!busy} aria-busy={busy === 'demo'} onClick={async()=>{setBusy('demo');setError('');try{await startDemoSession();}catch(err){setError(err instanceof Error?err.message:'Demo could not be opened. Try again.');}finally{setBusy('');}}}>{busy === 'demo' && <LoaderCircle className="w-4 h-4 animate-spin" aria-hidden="true"/>}{busy === 'demo' ? 'Opening demo…' : 'Explore demo'}</button>
        <a
          className="block text-sm text-primary underline underline-offset-4"
          href="#/"
        >
          Return to product overview
        </a>
      </form>
    </main>
  );
}
