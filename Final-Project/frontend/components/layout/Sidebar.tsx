"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCurrentUser } from "../../hooks/useCurrentUser";
import {
  Activity,
  Bot,
  ChevronRight,
  CreditCard,
  FileText,
  Gauge,
  LayoutDashboard,
  LogOut,
  Plug,
  ScrollText,
  Settings,
  Sparkles,
  X,
  Zap,
} from "lucide-react";

const navigation = [
  { href: "/dashboard",       label: "Overview",        icon: LayoutDashboard, desc: "Finance summary" },
  { href: "/forecasting",     label: "Forecasting",     icon: Activity,        desc: "Revenue trends" },
  { href: "/fraud-detection", label: "Fraud Detection", icon: Gauge,           desc: "Risk scoring" },
  { href: "/ai-agent",        label: "AI Agent",        icon: Bot,             desc: "Smart assistant", pro: true },
  { href: "/document-chat",   label: "Document Chat",   icon: FileText,        desc: "Chat with docs",  pro: true },
];

const workspace = [
  { href: "/reports",      label: "Reports",      icon: ScrollText },
  { href: "/integrations", label: "Integrations", icon: Plug },
  { href: "/billing",      label: "Billing",      icon: CreditCard },
  { href: "/settings",     label: "Settings",     icon: Settings },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, loading } = useCurrentUser();

  const initials = user?.email?.[0]?.toUpperCase() ?? "U";
  const emailLabel = loading ? "Loading…" : (user?.email ?? "Workspace user");

  return (
    <>
      {/* Overlay — mobile only */}
      <div
        className={`sb-overlay${isOpen ? " sb-overlay-visible" : ""}`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside className={`sidebar${isOpen ? " sidebar-open" : ""}`}>
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-mark">
            <Sparkles size={16} />
          </div>
          <div className="brand-text">
            <strong>ledgerly</strong>
            <span>finance intelligence</span>
          </div>
          <button
            className="sidebar-close-btn"
            aria-label="Close menu"
            onClick={onClose}
          >
            <X size={15} />
          </button>
        </div>

        {/* Workspace Pill */}
        <div className="sb-workspace-pill">
          <Zap size={11} />
          <span>AI Finance Workspace</span>
          <span className="sb-ws-dot" />
        </div>

        {/* Primary Navigation */}
        <div className="sidebar-group">
          <span className="sidebar-label">Navigation</span>
          <nav aria-label="Primary navigation">
            {navigation.map(({ href, label, icon: Icon, desc, pro }) => {
              const active = pathname === href || (href !== "/dashboard" && pathname?.startsWith(href));
              return (
                <Link
                  className={`sidebar-link${active ? " is-active" : ""}`}
                  href={href}
                  key={href}
                  onClick={onClose}
                >
                  <span className={`sb-icon-wrap${active ? " sb-icon-active" : ""}`}>
                    <Icon size={16} strokeWidth={active ? 2.2 : 1.8} />
                  </span>
                  <span className="sb-link-body">
                    <span className="sb-link-label">{label}</span>
                    <span className="sb-link-desc">{desc}</span>
                  </span>
                  {pro && <span className="pro-pill">PRO</span>}
                  {active && <ChevronRight size={13} className="sb-chevron" />}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Manage Section */}
        <div className="sidebar-group sidebar-lower">
          <span className="sidebar-label">Manage</span>
          <nav aria-label="Management navigation">
            {workspace.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  className={`sidebar-link sidebar-link-sm${active ? " is-active" : ""}`}
                  href={href}
                  key={href}
                  onClick={onClose}
                >
                  <span className={`sb-icon-wrap${active ? " sb-icon-active" : ""}`}>
                    <Icon size={15} strokeWidth={1.8} />
                  </span>
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Footer */}
        <div className="sidebar-user">
          <div className="sb-avatar">
            {initials}
            <span className="sb-avatar-ring" />
          </div>
          <div className="user-copy">
            <strong title={emailLabel}>{emailLabel}</strong>
            <span className="sb-plan-badge">
              <Zap size={8} />
              Starter plan
            </span>
          </div>
          <button className="sb-logout-btn" aria-label="Sign out" title="Sign out">
            <LogOut size={14} />
          </button>
        </div>
      </aside>
    </>
  );
}
