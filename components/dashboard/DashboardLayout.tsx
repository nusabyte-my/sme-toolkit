import React, { Suspense, useEffect, useRef, useState } from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";
import { AppView } from "../../types";
import { useOwner } from "../../contexts/OwnerContext";
import WorkspaceGuide from './WorkspaceGuide';
import WorkspaceLoading from '../common/WorkspaceLoading';
import { workspaceNavigation } from './navigation';

interface DashboardLayoutProps {
  currentView: AppView;
  setCurrentView: (view: AppView) => void;
  username: string;
  children: React.ReactNode;
}
export default function DashboardLayout({
  currentView,
  setCurrentView,
  username,
  children,
}: DashboardLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const drawer = useRef<HTMLDialogElement>(null);
  const main = useRef<HTMLElement>(null);
  const { overview, loading, error, refresh } = useOwner();
  useEffect(() => {
    main.current?.scrollTo({ top: 0, behavior: 'instant' });
    main.current?.focus();
    drawer.current?.close();
  }, [currentView]);
  const navigate = (view: AppView) => {
    setCurrentView(view);
    drawer.current?.close();
  };
  return (
    <div className="flex h-dvh bg-background text-foreground overflow-hidden">
      <a
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          main.current?.focus();
        }}
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:bg-card focus:p-3"
      >
        Skip to main content
      </a>
      <div className="hidden lg:block h-full shrink-0">
        <Sidebar
          collapsed={collapsed}
          onCollapse={setCollapsed}
          currentView={currentView}
          onNavigate={navigate}
          companyName={overview?.context?.company_name}
        />
      </div>
      <dialog
        ref={drawer}
        className="m-0 h-dvh max-h-none w-64 max-w-[90vw] p-0 bg-primary-900 backdrop:bg-black/60"
        onClick={(event) => {
          if (event.target === drawer.current) drawer.current.close();
        }}
        aria-label="Workspace navigation"
      >
        <div className="h-full">
          <button
            className="absolute top-4 right-3 text-primary-100 p-2 z-10"
            aria-label="Close navigation"
            onClick={() => drawer.current?.close()}
          >
            Close
          </button>
          <Sidebar
            collapsed={false}
            onCollapse={() => drawer.current?.close()}
            currentView={currentView}
            onNavigate={navigate}
            companyName={overview?.context?.company_name}
          />
        </div>
      </dialog>
      <div className="min-w-0 flex-1 flex flex-col">
        <Header
          onNavigate={navigate}
          username={username}
          onMenuToggle={() => drawer.current?.showModal()}
        />
        <main
          id="main-content"
          ref={main}
          tabIndex={-1}
          className="flex-1 overflow-y-auto min-w-0 px-4 py-6 sm:px-6 lg:px-8"
        >
          <div className="max-w-[1440px] mx-auto min-w-0">
            {!overview ? loading ? <WorkspaceLoading label="your business" /> : <section className="owner-panel"><p className="owner-error" role="alert">{error || 'Your business workspace could not be loaded.'}</p><button className="owner-button mt-4" onClick={()=>void refresh()}>Retry workspace</button></section> :
              <Suspense key={currentView} fallback={<WorkspaceLoading label={workspaceNavigation.find(item=>item.view===currentView)?.label.toLowerCase() || 'workspace'} />}>
                <WorkspaceGuide view={currentView} onNavigate={navigate}/>
                <div id="workspace-tools" tabIndex={-1} className="outline-none scroll-mt-4">{children}</div>
              </Suspense>}
          </div>
        </main>
      </div>
    </div>
  );
}
