import React, {
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { AppView } from "./types";
import DashboardLayout from "./components/dashboard/DashboardLayout";
import ProfilesPage from "./components/dashboard/ProfilesPage";
import { workspaceNavigation } from "./components/dashboard/navigation";
import AuthGate from "./components/common/AuthGate";
import { OwnerProvider } from "./contexts/OwnerContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { StrategyModeProvider } from './contexts/StrategyModeContext';
import { ErrorBoundary } from "./components/common";
import WorkspaceLoading from './components/common/WorkspaceLoading';
import {
  getPageMetadata,
  getPageOpenGraphData,
  getPageTwitterCardData,
  getBreadcrumbs,
  generateBreadcrumbSchema,
  generateSoftwareApplicationSchema,
} from "./src/utils/seo";

const LandingPage = React.lazy(() => import("./components/LandingPage"));
const LegalPage = React.lazy(() => import("./components/LegalPage"));
const OwnerDashboard = React.lazy(
  () => import("./components/dashboard/StrategyHubDashboard"),
);
const AgentForgeChat = React.lazy(
  () => import("./components/dashboard/AgentForgeChat"),
);
const ECommerceHub = React.lazy(() =>
  import("./components/dashboard/ECommerceHub").then((m) => ({
    default: m.ECommerceHub,
  })),
);
const SocialMediaStudio = React.lazy(() =>
  import("./components/dashboard/SocialMediaStudio").then((m) => ({
    default: m.SocialMediaStudio,
  })),
);
const SalesTracker = React.lazy(() => import("./components/SalesTracker"));
const AdsStudio = React.lazy(() => import("./components/dashboard/AdsStudio"));
const BusinessWorkbench = React.lazy(
  () => import("./components/dashboard/BusinessWorkbench"),
);
const AdOptimization = React.lazy(
  () => import("./components/dashboard/AdOptimization"),
);
const LeadManager = React.lazy(() => import("./components/LeadManager"));
const AdminDashboard = React.lazy(() => import("./components/AdminDashboard"));
const AutomationCenter = React.lazy(() => import('./components/dashboard/AutomationCenter'));
const Bookkeeping = React.lazy(() => import('./components/dashboard/Bookkeeping'));
const HRWorkspace = React.lazy(() => import('./components/dashboard/HRWorkspace'));
const BillingWorkspace = React.lazy(() => import('./components/dashboard/BillingWorkspace'));
const AgentChannels = React.lazy(() => import('./components/dashboard/AgentChannels'));

const slugs = Object.fromEntries(
  workspaceNavigation.map((item) => [item.view, item.slug]),
) as Record<AppView, string>;
slugs[AppView.LANDING] = "";
slugs[AppView.PRIVACY] = "privacy";
slugs[AppView.TERMS] = "terms";
slugs[AppView.ADMIN] = "admin";
const views = Object.fromEntries(
  Object.entries(slugs).map(([view, slug]) => [slug, view]),
) as Record<string, AppView>;

function App() {
  const [view, setView] = useState<AppView>(
    () => views[window.location.hash.replace(/^#\/?/, "")] || AppView.LANDING,
  );
  const currentHash = useRef(window.location.hash);
  const navigate = useCallback((next: AppView) => {
    window.location.hash = `#/${slugs[next]}`;
  }, []);
  useEffect(() => {
    const changed = () => {
      if (
        !window.dispatchEvent(
          new Event("sme-before-navigate", { cancelable: true }),
        )
      ) {
        window.history.replaceState(null, "", currentHash.current || "#/");
        return;
      }
      currentHash.current = window.location.hash;
      setView(
        views[window.location.hash.replace(/^#\/?/, "")] || AppView.LANDING,
      );
    };
    window.addEventListener("hashchange", changed);
    return () => window.removeEventListener("hashchange", changed);
  }, []);
  useEffect(() => {
    const names: Partial<Record<AppView, string>> = {
      [AppView.LANDING]: "landing",
      [AppView.DASHBOARD]: "dashboard",
      [AppView.BMC_HUB]: "bmc",
      [AppView.LEADS]: "leads",
      [AppView.SALES]: "sales",
      [AppView.MARKETING_COPY]: "copywriter",
      [AppView.MARKETING_VISUAL]: "visual",
      [AppView.MARKETING_VIDEO]: "video",
      [AppView.STRATEGY]: "strategy",
      [AppView.PROFILES]: "profiles",
    };
    const page = names[view] || "dashboard";
    const metadata = getPageMetadata(page);
    document.title =
      view === AppView.LANDING
        ? metadata.title
        : `${workspaceNavigation.find((item) => item.view === view)?.label || slugs[view]} · SME OS`;
    const tags = {
      description: metadata.description,
      ...getPageOpenGraphData(page),
      ...getPageTwitterCardData(page),
    };
    Object.entries(tags).forEach(([name, value]) => {
      const attr = name.startsWith("og:") ? "property" : "name";
      let tag = document.querySelector<HTMLMetaElement>(
        `meta[${attr}="${name}"]`,
      );
      if (!tag) {
        tag = document.createElement("meta");
        tag.setAttribute(attr, name);
        document.head.appendChild(tag);
      }
      tag.content = String(value);
    });
    let breadcrumb = document.getElementById("breadcrumb-schema");
    if (!breadcrumb) {
      breadcrumb = document.createElement("script");
      breadcrumb.id = "breadcrumb-schema";
      breadcrumb.setAttribute("type", "application/ld+json");
      document.head.appendChild(breadcrumb);
    }
    breadcrumb.textContent = generateBreadcrumbSchema(getBreadcrumbs(page));
    document.getElementById("software-schema")?.remove();
    if (view === AppView.LANDING) {
      const schema = document.createElement("script");
      schema.id = "software-schema";
      schema.type = "application/ld+json";
      schema.textContent = generateSoftwareApplicationSchema({
        name: "SME Toolkit",
        description:
          "Business owner workspace for context, sales, agents and marketing",
        applicationCategory: "BusinessApplication",
        operatingSystem: "Web",
      });
      document.head.appendChild(schema);
    }
  }, [view]);
  const content = (username: string) => {
    switch (view) {
      case AppView.PROFILES:
        return <ProfilesPage />;
      case AppView.DASHBOARD:
        return <OwnerDashboard onNavigate={navigate} />;
      case AppView.AGENT_FORGE:
        return <AgentForgeChat />;
      case AppView.AUTOMATIONS:
        return <AutomationCenter />;
      case AppView.BOOKKEEPING:
        return <Bookkeeping />;
      case AppView.HR:
        return <HRWorkspace />;
      case AppView.BILLING:
        return <BillingWorkspace onNavigate={navigate} />;
      case AppView.CHANNELS:
        return <AgentChannels />;
      case AppView.ECOMMERCE:
        return <ECommerceHub />;
      case AppView.SOCIAL_STUDIO:
        return <SocialMediaStudio />;
      case AppView.SALES:
        return <SalesTracker />;
      case AppView.ADS:
        return <AdsStudio />;
      case AppView.AD_OPTIMIZATION:
        return <AdOptimization />;
      case AppView.BMC_HUB:
        return <BusinessWorkbench key="canvas" kind="canvas" />;
      case AppView.LEADS:
        return <LeadManager />;
      case AppView.STRATEGY:
        return <BusinessWorkbench key="strategy" kind="strategy" />;
      case AppView.MARKETING_COPY:
        return <AdsStudio key="copy" initialTab="copy" />;
      case AppView.MARKETING_VISUAL:
        return <AdsStudio key="image" initialTab="image" />;
      case AppView.MARKETING_VIDEO:
        return <AdsStudio key="video" initialTab="video" />;
      case AppView.IDEATION:
        return <BusinessWorkbench key="ideation" kind="ideation" />;
      case AppView.SEO_STUDIO:
        return <BusinessWorkbench key="seo" kind="seo" />;
      case AppView.MARKET_RESEARCH:
        return <BusinessWorkbench key="research" kind="research" />;
      case AppView.QUICKWINS:
        return <BusinessWorkbench key="quickwins" kind="quickwins" />;
      case AppView.ADMIN:
        return username === "admin" ? (
          <AdminDashboard />
        ) : (
          <p role="alert">Administrator access required.</p>
        );
      default:
        return <OwnerDashboard onNavigate={navigate} />;
    }
  };
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <Suspense
          fallback={<WorkspaceLoading label="SME OS" />}
        >
          {view === AppView.LANDING ? (
            <LandingPage
              onGetStarted={() => navigate(AppView.DASHBOARD)}
              onNavigateLegal={navigate}
            />
          ) : view === AppView.PRIVACY || view === AppView.TERMS ? (
            <LegalPage
              kind={view === AppView.PRIVACY ? "privacy" : "terms"}
              onNavigate={navigate}
            />
          ) : (
            <AuthGate>
              {(username) => (
                <OwnerProvider>
                  <StrategyModeProvider key={username} username={username}>
                  <DashboardLayout
                    currentView={view}
                    setCurrentView={navigate}
                    username={username}
                  >
                    {content(username)}
                  </DashboardLayout>
                  </StrategyModeProvider>
                </OwnerProvider>
              )}
            </AuthGate>
          )}
        </Suspense>
      </ErrorBoundary>
    </ThemeProvider>
  );
}
export default App;
