import React, { useEffect, useRef, useState } from "react";
import { Search, Bell, Menu, Moon, Sun, LogOut, Building2 } from "lucide-react";
import { AppView } from "../../types";
import { useOwner } from "../../contexts/OwnerContext";
import { useTheme } from "../../contexts/ThemeContext";
import { signOut, exitDemoSession } from "../../services/apiClient";
import { workspaceNavigation } from "./navigation";
import { workspaceGuide } from './workspaceContent';
import { useStrategyMode } from '../../contexts/StrategyModeContext';
import { strategyMenu } from './strategyGuidance';

interface HeaderProps {
  onNavigate: (view: AppView) => void;
  onMenuToggle: () => void;
  username: string;
}
export default function Header({
  onNavigate,
  onMenuToggle,
  username,
}: HeaderProps) {
  const { overview } = useOwner();
  const { mode } = useStrategyMode();
  const { resolvedTheme, toggleTheme } = useTheme();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState<"search" | "attention" | "account" | null>(
    null,
  );
  const root = useRef<HTMLElement>(null);
  const search = useRef<HTMLInputElement>(null);
  const results = workspaceNavigation
    .filter((item) =>
      `${item.label} ${item.group} ${strategyMenu.find(step=>step.view===item.view)?.label || ''} ${workspaceGuide[item.view]?.capabilities.join(' ') || ''}`.toLowerCase().includes(query.toLowerCase()),
    )
    .slice(0, 7);
  useEffect(() => {
    const click = (event: MouseEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(null);
    };
    const keys = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(null);
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        search.current?.focus();
        setOpen("search");
      }
    };
    document.addEventListener("mousedown", click);
    document.addEventListener("keydown", keys);
    return () => {
      document.removeEventListener("mousedown", click);
      document.removeEventListener("keydown", keys);
    };
  }, []);
  const navigate = (view: AppView) => {
    setOpen(null);
    setQuery("");
    onNavigate(view);
  };
  const attention = overview?.attention || [];
  const views = {
    profiles: AppView.PROFILES,
    sales: AppView.SALES,
    agent_forge: AppView.AGENT_FORGE,
    social_studio: AppView.SOCIAL_STUDIO,
    ecommerce: AppView.ECOMMERCE,
    quickwins: AppView.QUICKWINS,
    hr: AppView.HR,
    bookkeeping: AppView.BOOKKEEPING,
  };
  return (
    <header
      ref={root}
      className="relative z-30 border-b border-border bg-card px-3 sm:px-6 py-3 flex items-center gap-2 sm:gap-4"
    >
      <button
        className="lg:hidden p-3 rounded-lg hover:bg-muted"
        aria-label="Toggle navigation"
        onClick={onMenuToggle}
      >
        <Menu className="w-5 h-5" />
      </button>
      <div className="relative flex-1 min-w-0 max-w-xl">
        <label htmlFor="workspace-search" className="sr-only">
          Search workspace tools
        </label>
        <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
        <input
          id="workspace-search"
          ref={search}
          className="owner-input pl-9 pr-3"
          placeholder="Find a tool…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen("search");
          }}
          onFocus={() => setOpen("search")}
          onKeyDown={(e) => {
            if (e.key === "Enter" && results[0]) navigate(results[0].view);
          }}
          aria-expanded={open === "search"}
          aria-controls="workspace-search-results"
          autoComplete="off"
        />
        {open === "search" && (
          <div
            id="workspace-search-results"
            className="absolute top-full mt-2 left-0 right-0 bg-popover border border-border rounded-xl shadow-lg p-2"
          >
            <p className="px-3 py-2 text-xs text-muted-foreground">
              Workspace tools · Ctrl K
            </p>
            {results.map((item) => (
              <button
                key={item.view}
                className="w-full rounded-lg px-3 py-3 text-left text-sm hover:bg-muted flex justify-between gap-3"
                onClick={() => navigate(item.view)}
              >
                <span>{mode === 'guided' ? strategyMenu.find(step=>step.view===item.view)?.label || item.label : item.label}</span>
                <span className="text-xs text-muted-foreground">
                  {item.group}
                </span>
              </button>
            ))}
            {!results.length && (
              <p className="p-3 text-sm text-muted-foreground" role="status">
                No tools match “{query}”.
              </p>
            )}
          </div>
        )}
      </div>
      {overview?.context?.is_demo && <span className="shrink-0 rounded-md bg-primary/10 px-2 py-1 text-xs font-semibold text-primary" title="Demo enterprise · fictional sample data">DEMO</span>}
      <div className="flex items-center gap-1 sm:gap-2 ml-auto">
        <button
          className="p-3 rounded-lg hover:bg-muted"
          onClick={toggleTheme}
          aria-label={
            resolvedTheme === "dark"
              ? "Switch to light theme"
              : "Switch to dark theme"
          }
        >
          {resolvedTheme === "dark" ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </button>
        <button
          className="p-3 relative rounded-lg hover:bg-muted"
          aria-label={`Needs attention: ${attention.length} items`}
          aria-expanded={open === "attention"}
          onClick={() => setOpen(open === "attention" ? null : "attention")}
        >
          <Bell className="w-5 h-5" />
          {attention.length > 0 && (
            <span className="absolute top-1 right-1 bg-primary text-primary-foreground text-[10px] px-1 rounded-full">
              {attention.length}
            </span>
          )}
        </button>
        <button
          className="p-3 rounded-lg hover:bg-muted"
          aria-label="Account menu"
          aria-expanded={open === "account"}
          onClick={() => setOpen(open === "account" ? null : "account")}
        >
          <Building2 className="w-5 h-5" />
        </button>
      </div>
      {open === "attention" && (
        <div className="absolute top-full right-3 sm:right-6 mt-2 w-80 max-w-[calc(100vw-24px)] bg-popover border border-border rounded-xl shadow-lg p-4">
          <h2 className="font-semibold">Needs your attention</h2>
          <div className="mt-2 divide-y divide-border">
            {attention.map((item) => (
              <button
                key={item.id}
                onClick={() => navigate(views[item.view])}
                className="w-full py-3 text-left hover:text-primary"
              >
                <span className="block text-sm font-medium">{item.title}</span>
                <span className="block text-xs text-muted-foreground mt-1">
                  {item.detail}
                </span>
              </button>
            ))}
            {!attention.length && (
              <p className="py-4 text-sm text-muted-foreground">
                No recorded items need attention.
              </p>
            )}
          </div>
        </div>
      )}
      {open === "account" && (
        <div className="absolute top-full right-3 sm:right-6 mt-2 w-64 bg-popover border border-border rounded-xl shadow-lg p-3">
          <p className="px-3 py-2 text-sm font-semibold truncate">
            {overview?.context?.is_demo ? 'Meranti demo workspace' : `Signed in as ${username}`}
          </p>
          <button
            className="w-full text-left rounded-lg px-3 py-3 hover:bg-muted text-sm"
            onClick={() => navigate(AppView.PROFILES)}
          >
            Edit business context
          </button>
          {username === 'admin' && <button className="w-full text-left rounded-lg px-3 py-3 hover:bg-muted text-sm" onClick={() => navigate(AppView.ADMIN)}>Pilot enquiries</button>}
          <button
            className="w-full flex gap-2 items-center rounded-lg px-3 py-3 hover:bg-muted text-sm"
            onClick={() => { if (overview?.context?.is_demo) exitDemoSession(); else if (window.dispatchEvent(new Event('sme-before-navigate', { cancelable: true }))) signOut(); }}
          >
            <LogOut className="w-4 h-4" />
            {overview?.context?.is_demo ? 'Exit demo' : 'Sign out'}
          </button>
        </div>
      )}
    </header>
  );
}
