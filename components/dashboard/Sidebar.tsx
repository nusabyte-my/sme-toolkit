import React from "react";
import {
  Bot,
  Building2,
  ChartNoAxesCombined,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Megaphone,
  ShoppingBag,
  Users,
  Compass,
} from "lucide-react";
import { AppView } from "../../types";
import { workspaceNavigation } from "./navigation";
import { useStrategyMode } from '../../contexts/StrategyModeContext';
import { strategyMenu } from './strategyGuidance';

interface SidebarProps {
  collapsed: boolean;
  onCollapse: (value: boolean) => void;
  currentView: AppView;
  onNavigate: (view: AppView) => void;
  companyName?: string;
}
const icons: Partial<Record<AppView, React.ElementType>> = {
  [AppView.DASHBOARD]: LayoutDashboard,
  [AppView.PROFILES]: Building2,
  [AppView.AGENT_FORGE]: Bot,
  [AppView.SALES]: ChartNoAxesCombined,
  [AppView.ECOMMERCE]: ShoppingBag,
  [AppView.ADS]: Megaphone,
  [AppView.SOCIAL_STUDIO]: Megaphone,
  [AppView.LEADS]: Users,
};
export default function Sidebar({
  collapsed,
  onCollapse,
  currentView,
  onNavigate,
  companyName,
}: SidebarProps) {
  const { mode } = useStrategyMode();
  const items = mode === 'guided' ? [...workspaceNavigation.filter(item => item.group !== 'Strategy'), ...strategyMenu.map(step => ({ ...workspaceNavigation.find(item => item.view === step.view)!, label: step.label }))] : workspaceNavigation;
  return (
    <aside
      className={`${collapsed ? "w-20" : "w-64"} h-full flex flex-col bg-primary-900 text-primary-50 border-r border-primary-800`}
      aria-label="Workspace sidebar"
    >
      <a
        href="#/dashboard"
        className="flex items-center gap-3 p-5 border-b border-primary-800"
      >
        <LayoutDashboard className="w-7 h-7 shrink-0 text-primary-200" />
        <span className={collapsed ? "sr-only" : "min-w-0"}>
          <span className="font-display font-bold text-lg block">SME OS</span>
          <span className="text-xs text-primary-200">Owner workspace</span>
        </span>
      </a>
      {!collapsed && (
        <div className="p-5 border-b border-primary-800">
          <p className="font-semibold text-sm truncate">
            {companyName || "Set up your business"}
          </p>
          <button
            className="text-xs text-primary-200 mt-2 underline underline-offset-4"
            onClick={() => onNavigate(AppView.PROFILES)}
          >
            Edit business context
          </button>
        </div>
      )}
      <nav
        className="flex-1 overflow-y-auto p-3 space-y-5"
        aria-label="Workspace navigation"
      >
        {[...new Set(workspaceNavigation.map(item => item.group))].map((group) => (
          <div key={group}>
            {!collapsed && (
              <p className="px-3 mb-2 text-xs font-semibold text-primary-200">
                {group}
              </p>
            )}
            <div className="space-y-1">
              {items
                .filter((item) => item.group === group)
                .map((item) => {
                  const Icon = icons[item.view] || Compass;
                  return (
                    <button
                      key={item.view}
                      title={collapsed ? item.label : undefined}
                      aria-label={collapsed ? item.label : undefined}
                      aria-current={
                        currentView === item.view ? "page" : undefined
                      }
                      onClick={() => onNavigate(item.view)}
                      className={`w-full min-h-11 rounded-lg flex items-center gap-3 px-3 text-left text-sm ${currentView === item.view ? "bg-primary-100 text-primary-900 font-semibold" : "hover:bg-primary-800 text-primary-100"} ${collapsed ? "justify-center" : ""}`}
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      {!collapsed && <span className="py-2">{item.label}{mode === 'guided' && item.group === 'Strategy' && <span className="block text-xs opacity-80 font-normal mt-1">{strategyMenu.find(step => step.view === item.view)?.hint}</span>}</span>}
                    </button>
                  );
                })}
            </div>
          </div>
        ))}
      </nav>
      <div className="p-3 border-t border-primary-800">
        <button
          className="w-full min-h-11 flex justify-center gap-2 items-center text-sm rounded-lg hover:bg-primary-800"
          onClick={() => onCollapse(!collapsed)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              Collapse sidebar
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
