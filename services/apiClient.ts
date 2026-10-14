const configuredBase =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "";
// Local development uses Vite's same-origin proxy; deployments may set an HTTPS API origin.
const API_BASE_URL =
  import.meta.env.DEV &&
  /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(configuredBase)
    ? ""
    : configuredBase;
const TOKEN_KEY = "sme-toolkit-auth-token";
const DEMO_TOKEN_KEY = 'sme-toolkit-demo-token';
const RETURN_TOKEN_KEY = 'sme-toolkit-return-token';
let sessionVersion = 0;
let pendingLogin: Promise<string> | null = null;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function failure(response: Response): Promise<ApiError> {
  const data = await response.json().catch(() => null);
  const detail = data?.detail;
  const message =
    typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail
            .map(
              (item: { loc?: string[]; msg?: string }) =>
                `${item.loc?.slice(1).join(".") || "Input"}: ${item.msg || "Invalid value"}`,
            )
            .join("; ")
        : `Request failed (${response.status}). Please try again.`;
  return new ApiError(message, response.status);
}

export function signOut(): void {
  sessionVersion += 1;
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(DEMO_TOKEN_KEY);
  sessionStorage.removeItem(RETURN_TOKEN_KEY);
  window.dispatchEvent(new Event("sme-session-changed"));
}

export function authenticate(
  username?: string,
  password?: string,
): Promise<string> {
  if (pendingLogin) return pendingLogin;
  const user =
    username ??
    (import.meta.env.DEV ? import.meta.env.VITE_DEMO_USERNAME : undefined);
  const pass =
    password ??
    (import.meta.env.DEV ? import.meta.env.VITE_DEMO_PASSWORD : undefined);
  if (!user || !pass)
    return Promise.reject(
      new ApiError("Enter your account username and password.", 401),
    );
  const version = sessionVersion;
  pendingLogin = (async () => {
    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: user, password: pass }),
    });
    if (!response.ok) throw await failure(response);
    const data = await response.json();
    if (typeof data.access_token !== "string" || !data.access_token)
      throw new Error(
        "The server returned an invalid session. Please sign in again.",
      );
    if (version !== sessionVersion)
      throw new Error("Sign-in was cancelled. Please try again.");
    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    return data.access_token;
  })().finally(() => {
    pendingLogin = null;
  });
  return pendingLogin;
}

export async function authenticatedFetch(
  endpoint: string,
  method = "GET",
  body?: unknown,
): Promise<Response> {
  const token = sessionStorage.getItem(TOKEN_KEY);
  if (!token)
    throw new ApiError("Sign in to access your business workspace.", 401);
  const version = sessionVersion;
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (version !== sessionVersion)
    throw new ApiError("Your session changed. Please sign in again.", 401);
  if (response.status === 401) {
    signOut();
    throw new ApiError("Your session expired. Sign in again to continue.", 401);
  }
  if (!response.ok) throw await failure(response);
  return response;
}

export async function apiCall<T>(
  endpoint: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await authenticatedFetch(endpoint, method, body);
  return response.status === 204 ? (undefined as T) : response.json();
}

export async function submitPilotEnquiry<T>(body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api/v1/pilot-requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw await failure(response);
  return response.json();
}

export function getCurrentUser(): Promise<{ username: string }> {
  return apiCall("/auth/me");
}

export async function startDemoSession(): Promise<void> {
  const active = sessionStorage.getItem(TOKEN_KEY);
  if (active && active === sessionStorage.getItem(DEMO_TOKEN_KEY)) return;
  const version = sessionVersion;
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/auth/demo`, { method: 'POST' });
  } catch {
    throw new ApiError('Could not reach the demo service. Check your connection, then try again. You can still browse the solutions.', 0);
  }
  if (response.status === 403) throw new ApiError('The interactive demo is not enabled on this deployment. Browse the solutions or ask your workspace administrator for demo access.', 403);
  if (!response.ok) throw await failure(response);
  const data = await response.json();
  if (typeof data.access_token !== 'string' || !data.access_token) throw new Error('The demo session could not be created. Try again.');
  if (version !== sessionVersion) throw new Error('Your session changed. Open the demo again.');
  if (active) sessionStorage.setItem(RETURN_TOKEN_KEY, active);
  sessionStorage.setItem(DEMO_TOKEN_KEY, data.access_token);
  sessionStorage.setItem(TOKEN_KEY, data.access_token);
  sessionVersion += 1;
  window.dispatchEvent(new Event('sme-session-changed'));
}

export function exitDemoSession(): void {
  if (!window.dispatchEvent(new Event('sme-before-navigate', { cancelable: true }))) return;
  const previous = sessionStorage.getItem(RETURN_TOKEN_KEY);
  sessionVersion += 1;
  sessionStorage.removeItem(DEMO_TOKEN_KEY);
  sessionStorage.removeItem(RETURN_TOKEN_KEY);
  if (previous) sessionStorage.setItem(TOKEN_KEY, previous);
  else sessionStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event('sme-session-changed'));
  window.location.hash = previous ? '#/dashboard' : '#/';
}
