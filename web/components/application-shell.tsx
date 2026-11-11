"use client";

import { useEffect, useState, type ReactNode } from "react";
import { Code2, Menu, X } from "lucide-react";
import { SidebarNavigation } from "@/components/sidebar-navigation";

export function ProductMark() {
  return (
    <div className="product-lockup" aria-label="Olist Evidence Lab">
      <span className="product-mark" aria-hidden="true"><i /><i /><i /><i /></span>
      <span><strong>Olist</strong><small>Evidence Lab</small></span>
    </div>
  );
}

export function ApplicationShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!open) return;
    const close = (event: KeyboardEvent) => event.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [open]);

  return (
    <div className="app-frame">
      <a className="skip-link" href="#main-content">Skip to evidence</a>
      <aside className="desktop-sidebar">
        <ProductMark />
        <div className="workspace-scope"><span>Historical marketplace</span><strong>Brazil · 2016–2018</strong></div>
        <SidebarNavigation />
        <a className="repo-link" href="https://github.com/Jlawnat/ecommerce-sql-business-analytics" target="_blank" rel="noreferrer">
          <Code2 aria-hidden="true" size={16} /> View repository
        </a>
      </aside>

      <header className="top-rail">
        <div className="mobile-brand"><ProductMark /></div>
        <p className="top-scope">Verified aggregate research <span>·</span> Static historical snapshot</p>
        <a href="https://github.com/Jlawnat/ecommerce-sql-business-analytics" target="_blank" rel="noreferrer" className="top-repo"><Code2 aria-hidden="true" size={16} /> Source</a>
        <button className="mobile-menu-button" type="button" onClick={() => setOpen(true)} aria-label="Open navigation" aria-expanded={open}>
          <Menu aria-hidden="true" size={20} />
        </button>
      </header>

      {open && (
        <div className="nav-overlay" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && setOpen(false)}>
          <aside className="mobile-nav-sheet" role="dialog" aria-modal="true" aria-label="Navigation">
            <div className="mobile-nav-head"><ProductMark /><button type="button" onClick={() => setOpen(false)} aria-label="Close navigation"><X size={20} /></button></div>
            <div className="workspace-scope"><span>Historical marketplace</span><strong>Brazil · 2016–2018</strong></div>
            <SidebarNavigation onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      )}

      <main id="main-content" className="content-sheet">{children}</main>
    </div>
  );
}
