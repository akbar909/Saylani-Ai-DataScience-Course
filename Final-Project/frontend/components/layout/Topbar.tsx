"use client";

import { useRouter } from "next/navigation";
import { Bell, Command, FileText, LayoutDashboard, Menu, Search, Upload, X, Zap } from "lucide-react";
import { useState, useEffect, useRef } from "react";

const pages = [
  { label: "Dashboard",       href: "/dashboard",       icon: LayoutDashboard, category: "Pages" },
  { label: "Forecasting",     href: "/forecasting",     icon: Zap,             category: "Pages" },
  { label: "Fraud Detection", href: "/fraud-detection", icon: Zap,             category: "Pages" },
  { label: "AI Agent",        href: "/ai-agent",        icon: Zap,             category: "Pages" },
  { label: "Document Chat",   href: "/document-chat",   icon: FileText,        category: "Pages" },
  { label: "Reports",         href: "/reports",         icon: FileText,        category: "Pages" },
  { label: "Integrations",    href: "/integrations",    icon: Zap,             category: "Pages" },
  { label: "Billing",         href: "/billing",         icon: Zap,             category: "Pages" },
  { label: "Settings",        href: "/settings",        icon: Zap,             category: "Pages" },
];

type NotifTab = "all" | "alerts" | "system";

const BASE_NOTIFICATIONS = [
  {
    id: 1,
    title: "Models loaded",
    body: "creditcard_baseline & paysim_baseline ready",
    time: "2m ago",
    type: "success" as const,
  },
  {
    id: 2,
    title: "Phase 4 complete",
    body: "Fraud prediction endpoints are live",
    time: "1h ago",
    type: "info" as const,
  },
  {
    id: 3,
    title: "Stripe connected",
    body: "Webhook listener is running in demo mode",
    time: "3h ago",
    type: "warning" as const,
  },
];

const STORAGE_KEY = "ledgerly_read_notifs";

function loadReadIds(): Set<number> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? new Set<number>(JSON.parse(raw)) : new Set<number>();
  } catch {
    return new Set<number>();
  }
}

function saveReadIds(ids: Set<number>) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(ids))); } catch { /* noop */ }
}

function buildNotifs(readIds: Set<number>) {
  return BASE_NOTIFICATIONS.map((n) => ({ ...n, unread: !readIds.has(n.id) }));
}

export function Topbar({ onMenuToggle }: { onMenuToggle?: () => void }) {
  const router = useRouter();
  const [searchOpen, setSearchOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<NotifTab>("all");
  const [notifs, setNotifs] = useState(() => buildNotifs(loadReadIds()));
  const [highlightIdx, setHighlightIdx] = useState(0);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  // Sync read state from localStorage on mount (handles SSR hydration)
  useEffect(() => {
    setNotifs(buildNotifs(loadReadIds()));
  }, []);

  const unreadCount = notifs.filter((n) => n.unread).length;

  const filtered = query.trim()
    ? pages.filter((p) => p.label.toLowerCase().includes(query.toLowerCase()))
    : pages;

  // Ctrl+K shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
        setNotifOpen(false);
      }
      if (e.key === "Escape") {
        setSearchOpen(false);
        setNotifOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  // Focus input when search opens
  useEffect(() => {
    if (searchOpen) {
      setHighlightIdx(0);
      setTimeout(() => searchInputRef.current?.focus(), 50);
    } else {
      setQuery("");
    }
  }, [searchOpen]);

  // Reset highlight on filter change
  useEffect(() => setHighlightIdx(0), [query]);

  // Close notif dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    };
    if (notifOpen) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [notifOpen]);

  const handleKeyNav = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightIdx((i) => Math.min(i + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightIdx((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && filtered[highlightIdx]) {
      router.push(filtered[highlightIdx].href);
      setSearchOpen(false);
    }
  };

  const markAllRead = () => {
    const allIds = new Set<number>(BASE_NOTIFICATIONS.map((n) => n.id));
    saveReadIds(allIds);
    setNotifs(buildNotifs(allIds));
  };

  const filteredNotifs =
    activeTab === "alerts"
      ? notifs.filter((n) => n.type === "warning" || n.type === "success")
      : activeTab === "system"
      ? notifs.filter((n) => n.type === "info")
      : notifs;

  return (
    <>
      <header className="topbar">
        <div className="topbar-left">
          <button
            className="icon-button mobile-menu-btn"
            aria-label="Open menu"
            onClick={onMenuToggle}
            id="mobile-menu-toggle"
          >
            <Menu size={18} />
          </button>
          <div className="crumbs">
            <span>Workspace</span>
            <b>/</b>
            <strong>Finance command center</strong>
          </div>
        </div>

        <div className="topbar-actions">
          {/* Search trigger */}
          <button
            className="topbar-search-btn"
            aria-label="Search"
            id="search-trigger"
            onClick={() => { setSearchOpen(true); setNotifOpen(false); }}
          >
            <Search size={14} />
            <span>Search…</span>
            <kbd className="topbar-kbd"><Command size={10} />K</kbd>
          </button>

          {/* Notification Bell */}
          <div className="notif-wrap" ref={notifRef}>
            <button
              className={`icon-button notif-btn${unreadCount > 0 ? " has-unread" : ""}`}
              aria-label="Notifications"
              id="notif-toggle"
              onClick={() => { setNotifOpen((v) => !v); setSearchOpen(false); }}
            >
              <Bell size={17} />
              {unreadCount > 0 && (
                <span className="notif-badge">
                  {unreadCount}
                  <span className="notif-ping" />
                </span>
              )}
            </button>

            {notifOpen && (
              <div className="notif-dropdown" role="dialog" aria-label="Notifications">
                {/* Header */}
                <div className="notif-header">
                  <strong>Notifications</strong>
                  <div className="notif-header-actions">
                    {unreadCount > 0 && (
                      <button className="notif-mark-read" onClick={markAllRead}>
                        Mark all read
                      </button>
                    )}
                    <button className="icon-button-sm" onClick={() => setNotifOpen(false)}>
                      <X size={13} />
                    </button>
                  </div>
                </div>

                {/* Tabs */}
                <div className="notif-tabs">
                  {(["all", "alerts", "system"] as NotifTab[]).map((tab) => (
                    <button
                      key={tab}
                      className={`notif-tab${activeTab === tab ? " notif-tab-active" : ""}`}
                      onClick={() => setActiveTab(tab)}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Items */}
                <div className="notif-list">
                  {filteredNotifs.length === 0 ? (
                    <div className="notif-empty">No notifications</div>
                  ) : (
                    filteredNotifs.map((n) => (
                      <div
                        key={n.id}
                        className={`notif-item${n.unread ? " notif-unread" : ""}`}
                      >
                        <span className={`notif-type-dot notif-type-${n.type}`} />
                        <div className="notif-body">
                          <strong>{n.title}</strong>
                          <span>{n.body}</span>
                        </div>
                        <span className="notif-time">{n.time}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Upload CTA */}
          <button
            className="topbar-upload"
            onClick={() => router.push("/document-chat")}
            id="upload-docs-btn"
          >
            <Upload size={14} />
            <span>Upload docs</span>
          </button>
        </div>
      </header>

      {/* Command Palette */}
      {searchOpen && (
        <div
          className="cmd-backdrop"
          onClick={() => setSearchOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Command palette"
        >
          <div className="cmd-modal" onClick={(e) => e.stopPropagation()}>
            {/* Search Input */}
            <div className="cmd-input-wrap">
              <Search size={16} className="cmd-search-icon" />
              <input
                ref={searchInputRef}
                className="cmd-input"
                placeholder="Search pages and actions…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyNav}
                autoComplete="off"
              />
              <button className="cmd-esc-badge" onClick={() => setSearchOpen(false)}>
                ESC
              </button>
            </div>

            {/* Results */}
            <div className="cmd-results">
              {filtered.length === 0 ? (
                <div className="cmd-no-results">No results for &ldquo;{query}&rdquo;</div>
              ) : (
                <>
                  <div className="cmd-section-label">Pages</div>
                  {filtered.map((p, i) => {
                    const Icon = p.icon;
                    return (
                      <button
                        key={p.href}
                        className={`cmd-result-item${i === highlightIdx ? " cmd-highlighted" : ""}`}
                        onMouseEnter={() => setHighlightIdx(i)}
                        onClick={() => {
                          router.push(p.href);
                          setSearchOpen(false);
                          setQuery("");
                        }}
                      >
                        <span className="cmd-result-icon">
                          <Icon size={14} />
                        </span>
                        <span>{p.label}</span>
                        {i === highlightIdx && (
                          <kbd className="cmd-enter-hint">↵</kbd>
                        )}
                      </button>
                    );
                  })}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="cmd-footer">
              <span><kbd>↑↓</kbd> navigate</span>
              <span><kbd>↵</kbd> open</span>
              <span><kbd>ESC</kbd> close</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
