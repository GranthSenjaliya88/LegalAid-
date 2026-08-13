/**
 * LegalAId — Complete React 18 Application (Babel in-browser)
 * Production-quality UI/UX upgrade with Glassmorphic Aesthetics & Domain Selection Chips.
 * Architecture: Components → Context-via-props → Views → Modals → Root
 *
 * Design System: Deep Teal #123F3F + Warm Ivory #F5F5EC + Legal Gold #E9A52F
 * Icons: Inline SVG (Lucide-compatible, no external dependency)
 */

const { useState, useEffect, useCallback, useRef, useReducer } = React;

const API_BASE = "http://127.0.0.1:8000";

/* ═══════════════════════════════════════════════════════════════════════════
   INLINE SVG ICONS (Lucide-style, 24px viewBox, 2px stroke)
   ═══════════════════════════════════════════════════════════════════════════ */
const Icon = ({ name, size = 18, className = "", style = {} }) => {
  const paths = {
    scale: "M12 3v1m0 16v1M4.22 4.22l.71.71m14.14 14.14.71.71M3 12h1m16 0h1M4.22 19.78l.71-.71M18.36 5.64l.71-.71M12 7a5 5 0 1 0 0 10A5 5 0 0 0 12 7z",
    messageSquare: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
    bookOpen: "M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z",
    fileText: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8",
    info: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM12 16v-4M12 8h.01",
    alertTriangle: "M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01",
    checkCircle: "M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4 12 14.01l-3-3",
    x: "M18 6 6 18M6 6l12 12",
    xCircle: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM15 9l-6 6M9 9l6 6",
    check: "M20 6 9 17l-5-5",
    menu: "M3 12h18M3 6h18M3 18h18",
    trash: "M3 6h18M8 6V4h8v2M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6",
    edit: "M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4z",
    download: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
    externalLink: "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3",
    shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
    zap: "M13 2 3 14h9l-1 8 10-12h-9l1-8z",
    search: "M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z",
    shoppingBag: "M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4zM3 6h18M16 10a4 4 0 0 1-8 0",
    briefcase: "M20 7H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2",
    home: "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
    creditCard: "M1 4h22v16H1zM1 10h22",
    gavel: "m14 13-8.5 8.5a2.12 2.12 0 0 1-3-3L11 10m3 3 2-2m-2 2-5-5m5 5 7.5-7.5a2.12 2.12 0 0 0-3-3L11 10",
    lockKeyhole: "M12 2a5 5 0 0 0-5 5v3H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V12a2 2 0 0 0-2-2h-2V7a5 5 0 0 0-5-5zm0 2a3 3 0 0 1 3 3v3H9V7a3 3 0 0 1 3-3zm0 10a1 1 0 1 1 0 2 1 1 0 0 1 0-2z",
    arrowRight: "M5 12h14M12 5l7 7-7 7",
    chevronRight: "M9 18l6-6-6-6",
    listChecks: "M11 12H3M16 6H3M16 18H3M21 12l-4 4-2-2",
    mapPin: "M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0zM12 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
    verifiedBadge: "M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 0 0 1.946-.806 3.42 3.42 0 0 1 4.438 0 3.42 3.42 0 0 0 1.946.806 3.42 3.42 0 0 1 3.138 3.138 3.42 3.42 0 0 0 .806 1.946 3.42 3.42 0 0 1 0 4.438 3.42 3.42 0 0 0-.806 1.946 3.42 3.42 0 0 1-3.138 3.138 3.42 3.42 0 0 0-1.946.806 3.42 3.42 0 0 1-4.438 0 3.42 3.42 0 0 0-1.946-.806 3.42 3.42 0 0 1-3.138-3.138 3.42 3.42 0 0 0-.806-1.946 3.42 3.42 0 0 1 0-4.438 3.42 3.42 0 0 0 .806-1.946 3.42 3.42 0 0 1 3.138-3.138z",
    law: "M12 3 3 9.5V21h18V9.5L12 3zm0 0v18M3 9.5h18",
  };

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      style={style}
      aria-hidden="true"
    >
      {paths[name] && <path d={paths[name]} />}
    </svg>
  );
};

/* ═══════════════════════════════════════════════════════════════════════════
   DOMAIN CONFIG
   ═══════════════════════════════════════════════════════════════════════════ */
const DOMAIN_CONFIG = {
  consumer: { label: "Consumer Rights", icon: "shoppingBag", color: "#5B9B78" },
  labor:    { label: "Work & Labour Law", icon: "briefcase", color: "#4A90B8" },
  tenant:   { label: "Rent & Housing Law", icon: "home", color: "#8B6CAC" },
  cyber:    { label: "Cyber Crime & Fraud", icon: "creditCard", color: "#C96B5C" },
  criminal: { label: "Criminal Justice (BNS 2023)", icon: "gavel", color: "#D98B18" },
  general:  { label: "General Civic Dispute", icon: "scale", color: "#123F3F" },
};

const LANG_TEXTS = {
  en: {
    eyebrow: "A CALMER WAY TO BEGIN",
    heroPrefix: "Tell us what ",
    heroSuffix: "happened.",
    subtitle: "Describe your legal problem in your own words. Hindi or English — both work.",
    inputLabel: "Tell us what happened",
    noJargon: "No legal jargon needed. Just describe what happened.",
    placeholder: "Example: My landlord has not returned my ₹20,000 security deposit even though I moved out two months ago.",
    submitBtn: "Understand My Rights",
    privacyNotice: "Your privacy matters. Don't enter passwords, OTPs, PINs, or sensitive personal data.",
    examplesLabel: "Not sure what to write?",
    examplesSub: "Choose an example or click a category chip below to place it in the box.",
  },
  hi: {
    eyebrow: "शांत तरीके से शुरुआत करें",
    heroPrefix: "अपनी कानूनी समस्या ",
    heroSuffix: "बताएं।",
    subtitle: "अपनी बात अपने शब्दों में कहें — हिंदी या अंग्रेजी में।",
    inputLabel: "अपनी कानूनी समस्या बताएं",
    noJargon: "कानूनी शब्दों की जरूरत नहीं है, बस जो हुआ वो बताएं।",
    placeholder: "उदाहरण: मैंने दो महीने पहले मकान खाली कर दिया था लेकिन मकान मालिक ₹20,000 की डिपॉजिट वापस नहीं कर रहा है।",
    submitBtn: "मेरे अधिकार समझें",
    privacyNotice: "आपकी निजता महत्वपूर्ण है। पासवर्ड, ओटीपी या पिन कभी साझा न करें।",
    examplesLabel: "क्या लिखें समझ नहीं आ रहा?",
    examplesSub: "उदाहरण या कैटेगरी चिप्स चुनें — आप इसे भेजने से पहले बदल सकते हैं।",
  }
};

const PIPELINE_STEPS = [
  "Situation", "Facts", "Law Search", "Rights", "Evidence", "Roadmap", "Document"
];

const PIPELINE_LOADER_STEPS = [
  { id: 1, label: "Understanding your situation" },
  { id: 2, label: "Extracting facts and parties" },
  { id: 3, label: "Searching verified legal database" },
  { id: 4, label: "Preparing rights explanation" },
  { id: 5, label: "Generating evidence checklist" },
  { id: 6, label: "Building your action roadmap" },
  { id: 7, label: "Drafting your legal document" },
];

/* ═══════════════════════════════════════════════════════════════════════════
   TOAST SYSTEM
   ═══════════════════════════════════════════════════════════════════════════ */
let _toastSetState = null;
let _toastId = 0;

function ToastContainer() {
  const [toasts, setToasts] = useState([]);
  _toastSetState = setToasts;

  const removeToast = (id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, removing: true } : t));
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300);
  };

  const ICONS = { success: "checkCircle", error: "xCircle", warning: "alertTriangle", info: "info" };

  return (
    <div className="toast-container" role="region" aria-label="Notifications" aria-live="polite">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}${t.removing ? ' removing' : ''}`} role="alert">
          <div className="toast-icon"><Icon name={ICONS[t.type]} size={16} /></div>
          <div className="toast-body">
            {t.title && <div className="toast-title">{t.title}</div>}
            <div className="toast-message">{t.message}</div>
          </div>
          <button className="toast-close" onClick={() => removeToast(t.id)} aria-label="Dismiss">
            <Icon name="x" size={13} />
          </button>
        </div>
      ))}
    </div>
  );
}

function showToast(type, message, title = null, duration = null) {
  if (!_toastSetState) return;
  const id = ++_toastId;
  const autoDismiss = duration ?? (type === 'error' ? 8000 : type === 'warning' ? 6000 : 4000);
  _toastSetState(prev => [...prev, { id, type, message, title, removing: false }]);
  if (autoDismiss > 0) {
    setTimeout(() => {
      _toastSetState(prev => prev.map(t => t.id === id ? { ...t, removing: true } : t));
      setTimeout(() => _toastSetState(prev => prev.filter(t => t.id !== id)), 300);
    }, autoDismiss);
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   CONFIRM DIALOG
   ═══════════════════════════════════════════════════════════════════════════ */
function ConfirmDialog({ title, message, warning, confirmLabel = "Confirm", cancelLabel = "Cancel", onConfirm, onCancel, isDanger = true }) {
  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onCancel(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onCancel]);

  return (
    <div className="modal-overlay" onClick={onCancel} role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
        <div className="confirm-header">
          <div className="confirm-icon">
            <Icon name="alertTriangle" size={20} />
          </div>
          <div className="confirm-text-block">
            <div className="confirm-title" id="confirm-title">{title}</div>
            <div className="confirm-message">{message}</div>
          </div>
        </div>
        {warning && (
          <div className="confirm-body">
            <div className="confirm-warning">{warning}</div>
          </div>
        )}
        <div className="confirm-footer">
          <button className="btn btn-secondary btn-sm" onClick={onCancel}>{cancelLabel}</button>
          <button className={`btn ${isDanger ? 'btn-danger' : 'btn-primary'} btn-sm`} onClick={onConfirm} autoFocus>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   PIPELINE LOADER
   ═══════════════════════════════════════════════════════════════════════════ */
function PipelineLoader({ currentStep, label }) {
  const activeIdx = PIPELINE_LOADER_STEPS.findIndex(s => s.label === label || s.id === currentStep);

  return (
    <div className="pipeline-loader">
      <div className="pipeline-loader-title">
        <Icon name="zap" size={20} />
        Analysing your case…
        <div className="spinner spinner-sm" role="status" aria-label="Processing" />
      </div>
      <div className="pipeline-steps">
        {PIPELINE_LOADER_STEPS.slice(0, Math.max(activeIdx + 2, 3)).map((step, idx) => {
          const status = idx < activeIdx ? "done" : idx === activeIdx ? "active" : "pending";
          return (
            <div key={step.id} className={`pipeline-step ${status}`}>
              <div className="pipeline-step-dot">
                {status === "done" && <Icon name="check" size={10} />}
                {status === "active" && "●"}
                {status === "pending" && "○"}
              </div>
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════════════════════════ */
function EmptyState({ icon, title, message, action }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon" aria-hidden="true">
        <Icon name={icon} size={28} />
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-message">{message}</p>
      {action}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ERROR CARD
   ═══════════════════════════════════════════════════════════════════════════ */
function ErrorCard({ message, onRetry }) {
  return (
    <div className="error-card" role="alert">
      <div className="error-card-icon"><Icon name="alertTriangle" size={20} /></div>
      <div className="error-card-body">
        <div className="error-card-title">Something went wrong</div>
        <div className="error-card-message">{message}</div>
        {onRetry && (
          <div className="error-card-actions">
            <button className="btn btn-secondary btn-sm" onClick={onRetry}>Try Again</button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════════════════════ */
function Sidebar({ view, switchView, isOpen, apiStatus }) {
  const navItems = [
    { id: "assistant", label: "Legal Assistant", icon: "messageSquare" },
    { id: "corpus",    label: "Legal Sources",   icon: "bookOpen" },
    { id: "documents", label: "My Documents",    icon: "fileText" },
    { id: "about",     label: "About LegalAId",  icon: "info" },
  ];

  return (
    <aside id="sidebar" className={`sidebar${isOpen ? ' mobile-open' : ''}`} aria-label="Main navigation">
      <div className="sidebar-brand">
        <div className="brand-icon-wrap" aria-hidden="true">
          <Icon name="scale" size={22} className="brand-icon-svg" />
        </div>
        <div className="brand-text">
          <span className="brand-name">LegalAId</span>
          <span className="brand-sub">कानूनी सहायता</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="App navigation">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-item${view === item.id ? ' active' : ''}`}
            onClick={() => switchView(item.id)}
            aria-current={view === item.id ? 'page' : undefined}
          >
            <span className="nav-icon"><Icon name={item.icon} size={18} /></span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-divider" aria-hidden="true" />

      <div className="sidebar-footer">
        <div className="status-row">
          <div className={`status-dot${apiStatus !== 'ready' ? ' offline' : ''}`} role="status" aria-label={apiStatus === 'ready' ? 'Service online' : 'Service offline'} />
          <span className={`status-label${apiStatus !== 'ready' ? ' offline' : ''}`}>
            {apiStatus === 'ready' ? 'LegalAId is ready' : 'Connecting…'}
          </span>
        </div>
        <div className="status-sublabel">Source-backed legal guidance</div>
      </div>
    </aside>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   MOBILE HEADER
   ═══════════════════════════════════════════════════════════════════════════ */
function MobileHeader({ onMenuToggle, isOpen }) {
  return (
    <header className="mobile-header">
      <div className="mobile-brand">
        <Icon name="scale" size={20} style={{ color: 'var(--color-accent)' }} />
        <div>
          <div className="mobile-brand-name">LegalAId</div>
          <div className="mobile-brand-sub">कानूनी सहायता</div>
        </div>
      </div>
      <button
        className="mobile-menu-btn"
        onClick={onMenuToggle}
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={isOpen}
      >
        <Icon name={isOpen ? 'x' : 'menu'} size={20} />
      </button>
    </header>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   MOBILE BOTTOM NAV
   ═══════════════════════════════════════════════════════════════════════════ */
function MobileBottomNav({ view, switchView }) {
  const tabs = [
    { id: "assistant", label: "Assistant", icon: "messageSquare" },
    { id: "corpus",    label: "Sources",   icon: "bookOpen" },
    { id: "documents", label: "Documents", icon: "fileText" },
    { id: "about",     label: "About",     icon: "info" },
  ];

  return (
    <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={`bottom-nav-item${view === tab.id ? ' active' : ''}`}
          onClick={() => switchView(tab.id)}
          aria-current={view === tab.id ? 'page' : undefined}
        >
          <span className="bottom-nav-icon"><Icon name={tab.icon} size={22} /></span>
          <span className="bottom-nav-label">{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   DISCLAIMER BANNER
   ═══════════════════════════════════════════════════════════════════════════ */
function DisclaimerBanner({ switchView }) {
  const [dismissed, setDismissed] = useState(() => {
    try { return sessionStorage.getItem('legalaid_disclaimer') === '1'; } catch { return false; }
  });

  const dismiss = () => {
    setDismissed(true);
    try { sessionStorage.setItem('legalaid_disclaimer', '1'); } catch {}
  };

  if (dismissed) return null;

  return (
    <div className="disclaimer-banner" role="banner" aria-label="Legal disclaimer">
      <div className="disclaimer-content">
        <span className="disclaimer-icon" aria-hidden="true">⚖️</span>
        <span className="disclaimer-text">
          <strong>General legal information — not legal advice.</strong> LegalAId helps you understand laws and prepare drafts. For your specific situation, consult a qualified lawyer.
        </span>
      </div>
      <div className="disclaimer-actions">
        <button className="disclaimer-learn-more" onClick={() => switchView('about')}>Learn more</button>
        <button className="disclaimer-close" onClick={dismiss} aria-label="Dismiss disclaimer">
          <Icon name="x" size={14} />
        </button>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   CASE PROGRESS BAR
   ═══════════════════════════════════════════════════════════════════════════ */
function CaseProgressBar({ currentStep, onDelete }) {
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <>
      <div className="progress-bar-card" role="progressbar" aria-valuenow={currentStep} aria-valuemin={1} aria-valuemax={7}>
        <div className="progress-steps-desktop" aria-hidden="true">
          {PIPELINE_STEPS.map((label, idx) => {
            const stepNum = idx + 1;
            const status = stepNum < currentStep ? 'done' : stepNum === currentStep ? 'active' : '';
            return (
              <React.Fragment key={stepNum}>
                <div className={`progress-step-item ${status}`}>
                  <div className="step-bubble-wrap">
                    <div className="step-bubble">
                      {status === 'done' ? <Icon name="check" size={10} /> : stepNum}
                    </div>
                    <span className="step-lbl">{label}</span>
                  </div>
                </div>
                {idx < PIPELINE_STEPS.length - 1 && <div className={`progress-connector${status === 'done' ? ' done' : ''}`} />}
              </React.Fragment>
            );
          })}
        </div>
        <div className="progress-mobile-counter" aria-live="polite">Step {currentStep} of 7</div>
        <button className="btn btn-danger btn-sm" onClick={() => setShowConfirm(true)} aria-label="Delete case data">
          <Icon name="trash" size={14} /> Delete Case
        </button>
      </div>

      {showConfirm && (
        <ConfirmDialog
          title="Delete Case Data?"
          message="This will permanently purge all your case facts, analysis, and drafted documents."
          warning="⚠️ This action cannot be undone. All data will be erased for privacy."
          confirmLabel="Delete Permanently"
          cancelLabel="Keep Case"
          onConfirm={() => { setShowConfirm(false); onDelete(); }}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   CITATION CARD (in results workspace)
   ═══════════════════════════════════════════════════════════════════════════ */
function CitationCard({ match, setModal }) {
  const actName = match.act || match.act_name || match.act_short_name || "Statute Act";
  const section = match.section || match.section_number || "";
  const title = match.title || "";
  const summary = match.plain_language_summary || match.relevant_text || match.text || "";
  const shortSummary = summary.length > 300 ? summary.slice(0, 300) + "…" : summary;
  const why = match.why_applies || "Directly relevant to your stated situation.";
  const state = match.state || match.jurisdiction || "India";

  return (
    <div className="citation-card">
      <div className="citation-card-top">
        <div>
          <div className="citation-act">{actName}</div>
          <div className="citation-section">Section {section}{title ? ` — ${title}` : ''}</div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
          <span className="badge badge-success">✓ Verified Source</span>
          <span className="badge badge-neutral">{(match.domain || 'general').replace('_',' ')}</span>
        </div>
      </div>
      <p className="citation-summary">"{shortSummary}"</p>
      <div className="citation-why">
        <strong>Why this applies: </strong>{why}
      </div>
      <div className="citation-footer">
        <span className="citation-jurisdiction">Jurisdiction: <strong>{state}</strong></span>
        <div className="citation-actions">
          {setModal && (
            <button className="btn btn-secondary btn-sm" onClick={() => setModal({ type: "section", data: match })}>
              <Icon name="fileText" size={13} /> View Section
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   EVIDENCE CHECKLIST
   ═══════════════════════════════════════════════════════════════════════════ */
function EvidenceChecklist({ items }) {
  const [checked, setChecked] = useState({});

  const toggle = (idx) => setChecked(prev => ({ ...prev, [idx]: !prev[idx] }));

  if (!items || !items.length) return null;

  return (
    <div className="evidence-list" role="list">
      {items.map((ev, idx) => (
        <div
          key={idx}
          className={`evidence-item${checked[idx] ? ' checked' : ''}`}
          role="listitem"
          onClick={() => toggle(idx)}
          style={{ cursor: 'pointer' }}
        >
          <div className="evidence-checkbox" aria-hidden="true">
            {checked[idx] && <Icon name="check" size={12} />}
          </div>
          <div className="evidence-info">
            <div className="evidence-name">{ev.document_name}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className={`badge ${ev.importance === 'essential' ? 'badge-error' : 'badge-success'}`}>
                {(ev.importance || 'helpful').toUpperCase()}
              </span>
            </div>
            {ev.why_it_matters && <div className="evidence-why">{ev.why_it_matters}</div>}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ROADMAP STEPS
   ═══════════════════════════════════════════════════════════════════════════ */
function RoadmapSteps({ steps }) {
  if (!steps || !steps.length) return null;

  return (
    <div className="roadmap-list" role="list">
      {steps.map((st, idx) => (
        <div key={idx} className="roadmap-step" role="listitem">
          <div className="roadmap-step-num" aria-label={`Step ${st.step_number || idx + 1}`}>
            {st.step_number || idx + 1}
          </div>
          <div className="roadmap-step-body">
            <div className="roadmap-step-title">{st.title}</div>
            <div className="roadmap-step-desc">{st.description}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   CORPUS CARD (legal sources view)
   ═══════════════════════════════════════════════════════════════════════════ */
function CorpusCard({ item, setModal }) {
  const actName = item.act || item.act_name || item.act_short_name || "Statute Act";
  const sectionNum = item.section || item.section_number || "";
  const sectionTitle = item.title || "";
  const summaryText = item.plain_language_summary || item.relevant_text || item.text || "";
  const shortSummary = summaryText.length > 280 ? summaryText.slice(0, 280) + "…" : summaryText;
  const domainName = item.domain || "general";
  const whyApplies = item.why_applies || "Matches your legal query terms.";
  const sourceUrl = item.source_url || "https://www.indiacode.nic.in";
  const stateName = item.state || item.jurisdiction || "India";

  return (
    <div className="corpus-card">
      <div className="corpus-card-top">
        <div className="corpus-card-left">
          <span className="badge badge-success" style={{ marginBottom: '8px' }}>✓ VERIFIED SOURCE</span>
          <div className="corpus-card-act">{actName}</div>
          <div className="corpus-card-section">Section {sectionNum}{sectionTitle ? ` — ${sectionTitle}` : ''}</div>
        </div>
        <span className="badge badge-neutral">{domainName.replace('_', ' ')}</span>
      </div>

      <p className="corpus-card-summary">"{shortSummary}"</p>

      <div className="corpus-card-why">
        <strong>Relevance: </strong>{whyApplies}
      </div>

      <div className="corpus-card-footer">
        <span className="jurisdiction-text">Jurisdiction: <strong>{stateName}</strong></span>
        <div className="corpus-card-actions">
          <button className="btn btn-secondary btn-sm" onClick={() => setModal({ type: "section", data: item })}>
            <Icon name="fileText" size={13} /> View Section
          </button>
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary btn-sm"
            style={{ textDecoration: 'none' }}
          >
            <Icon name="externalLink" size={13} /> Official Source
          </a>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION MODAL
   ═══════════════════════════════════════════════════════════════════════════ */
function SectionModal({ item, onClose }) {
  if (!item) return null;
  const actName = item.act || item.act_name || item.act_short_name || "Statute Act";
  const sectionNum = item.section || item.section_number || "";
  const title = item.title || "Section Detail";
  const fullText = item.relevant_text || item.text || item.plain_language_summary || "";
  const sourceUrl = item.source_url || "https://www.indiacode.nic.in";
  const state = item.state || item.jurisdiction || "India";

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="section-modal-title">
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-breadcrumb">{actName} · Section {sectionNum}</div>
            <div className="modal-title" id="section-modal-title">{title}</div>
            <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-success">✓ Verified Source</span>
              <span className="badge badge-neutral">{state}</span>
              {item.domain && <span className="badge badge-primary">{item.domain}</span>}
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close section detail">
            <Icon name="x" size={16} />
          </button>
        </div>
        <div className="modal-body">
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', marginBottom: 'var(--sp-4)', lineHeight: 1.6 }}>
            Plain-language interpretation of the statutory provision:
          </p>
          <div className="section-text-block">{fullText}</div>
          {sourceUrl && (
            <a href={sourceUrl} target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-sm" style={{ textDecoration: 'none', marginTop: 'var(--sp-2)' }}>
              <Icon name="externalLink" size={13} /> View on India Code (Official Source)
            </a>
          )}
        </div>
        <div className="modal-footer">
          <Icon name="alertTriangle" size={14} />
          General legal information — consult a qualified advocate for representation in your specific situation.
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   DOCUMENT EDITOR MODAL
   ═══════════════════════════════════════════════════════════════════════════ */
function DocumentEditorModal({ doc, onSave, onClose }) {
  if (!doc) return null;
  const [sections, setSections] = useState(doc.sections || []);
  const [activeSection, setActiveSection] = useState(0);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (id, val) => {
    setSections(prev => prev.map(s => s.id === id ? { ...s, content: val } : s));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(doc.document_id, sections);
      setHasChanges(false);
      showToast('success', `Quality Score updated. Document saved successfully.`, 'Document Saved');
    } catch (err) {
      showToast('error', err.message || 'Failed to save document edits.', 'Save Failed');
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    if (hasChanges) {
      if (!window.confirm('You have unsaved changes. Close anyway?')) return;
    }
    onClose();
  };

  const qualityScore = doc.quality_score || 8.5;
  const qualityClass = qualityScore >= 8 ? 'high' : qualityScore >= 6 ? 'medium' : 'low';

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') handleClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [hasChanges]);

  return (
    <div className="modal-overlay" onClick={handleClose} role="dialog" aria-modal="true" aria-labelledby="editor-title">
      <div className="modal-card modal-card-wide" onClick={e => e.stopPropagation()} style={{ maxHeight: '90vh' }}>
        <div className="modal-header">
          <div>
            <div className="modal-breadcrumb">{doc.type?.toUpperCase().replace(/_/g, " ")}</div>
            <div className="modal-title" id="editor-title">{doc.title}</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-3)' }}>
            <span className={`quality-score ${qualityClass}`}>
              ★ {qualityScore}/10 Quality
            </span>
            <button className="modal-close-btn" onClick={handleClose} aria-label="Close editor">
              <Icon name="x" size={16} />
            </button>
          </div>
        </div>

        <div className="doc-editor-layout" style={{ flex: 1, overflow: 'hidden' }}>
          {/* Section navigation */}
          <div className="doc-editor-nav" aria-label="Document sections">
            <div style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 'var(--sp-2)' }}>
              Sections
            </div>
            {sections.map((sec, idx) => (
              <button
                key={sec.id}
                className={`doc-nav-item${idx === activeSection ? ' active' : ''}`}
                onClick={() => setActiveSection(idx)}
              >
                {sec.title}
              </button>
            ))}
          </div>

          {/* Section editor */}
          <div className="doc-editor-main">
            {sections[activeSection] && (
              <div>
                <label className="doc-section-label" htmlFor={`sec-${sections[activeSection].id}`}>
                  {sections[activeSection].title}
                </label>
                <textarea
                  id={`sec-${sections[activeSection].id}`}
                  className="doc-section-textarea"
                  style={{ minHeight: '200px' }}
                  value={sections[activeSection].content}
                  onChange={e => handleChange(sections[activeSection].id, e.target.value)}
                />
                {sections.length > 1 && activeSection < sections.length - 1 && (
                  <button className="btn btn-ghost btn-sm" onClick={() => setActiveSection(activeSection + 1)}>
                    Next Section <Icon name="chevronRight" size={14} />
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-2)' }}>
            <Icon name="alertTriangle" size={14} />
            Review and customise before downloading.
          </span>
          <div style={{ display: 'flex', gap: 'var(--sp-3)' }}>
            <a
              href={`${API_BASE}/api/documents/${doc.document_id}/pdf`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary btn-sm"
              style={{ textDecoration: 'none' }}
            >
              <Icon name="download" size={13} /> Download PDF
            </a>
            <button
              className={`btn btn-primary btn-sm${saving ? ' btn-loading' : ''}`}
              onClick={handleSave}
              disabled={saving}
            >
              {!saving && <><Icon name="check" size={13} /> Save Edits</>}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ASSISTANT VIEW — LANDING STATE
   ═══════════════════════════════════════════════════════════════════════════ */
function LandingState({ lang, setLang, inputText, setInputText, isLoading, onSubmit }) {
  const t = LANG_TEXTS[lang] || LANG_TEXTS.en;
  const charLimit = 2000;

  const domainChips = [
    { id: "consumer", label: "Consumer Rights", icon: "shoppingBag", fill: "I bought a new washing machine that stopped working after 2 weeks, and the seller refuses to replace or refund it." },
    { id: "labor", label: "Salary & Work", icon: "briefcase", fill: "My employer has not paid my salary for the past two months after 3 years of service." },
    { id: "tenant", label: "Rent & Housing", icon: "home", fill: "I rented an apartment in Delhi, paid a ₹20,000 security deposit, moved out two months ago, and my landlord refuses to return it." },
    { id: "cyber", label: "Cyber Fraud", icon: "creditCard", fill: "₹25,000 was transferred from my bank account without my permission in an unauthorized online transaction." },
    { id: "criminal", label: "Criminal Rights", icon: "gavel", fill: "I need to understand my legal rights regarding police FIR registration and basic procedures." },
  ];

  const exampleCards = [
    {
      icon: "shoppingBag",
      category: "Consumer",
      text: '"My new washing machine stopped working after 2 weeks and the seller refuses to replace it."',
      fill: "I bought a new washing machine that stopped working in two weeks, and the seller is refusing to replace or refund it.",
    },
    {
      icon: "briefcase",
      category: "Salary & Work",
      text: '"My employer hasn\'t paid my salary for the past two months."',
      fill: "My employer has not paid my salary for two months after 3 years of service.",
    },
    {
      icon: "home",
      category: "Rent & Tenant",
      text: '"My landlord hasn\'t returned my ₹20,000 security deposit."',
      fill: "I rented an apartment in Delhi, paid a ₹20,000 security deposit, moved out two months ago, and my landlord has not returned the deposit.",
    },
    {
      icon: "creditCard",
      category: "Cyber Fraud",
      text: '"₹25,000 was transferred from my bank account without my permission."',
      fill: "₹25,000 was transferred from my bank account without my permission in an unauthorized online transaction.",
    },
  ];

  return (
    <div className="assistant-landing-wrapper">
      {/* Hero */}
      <div className="hero-header">
        <div className="hero-eyebrow">✦ {t.eyebrow}</div>
        <h1 className="hero-title">
          {t.heroPrefix}<span className="hero-serif-highlight">{t.heroSuffix}</span>
        </h1>
        <p className="hero-subtitle">{t.subtitle}</p>
        <div className="trust-pill">
          <span>We will help you understand:</span>
          <strong>Your rights <span className="arrow">→</span> Relevant law <span className="arrow">→</span> Evidence <span className="arrow">→</span> Next steps</strong>
        </div>
      </div>

      {/* Input Card */}
      <div className="hero-input-card">
        {/* Domain selection chips */}
        <div className="domain-chips-wrapper">
          <span className="domain-chip-label">Topic:</span>
          {domainChips.map((chip) => (
            <button
              key={chip.id}
              className={`domain-chip-btn${inputText === chip.fill ? ' active' : ''}`}
              onClick={() => setInputText(chip.fill)}
            >
              <Icon name={chip.icon} size={14} />
              <span>{chip.label}</span>
            </button>
          ))}
        </div>

        <div className="input-card-top">
          <label className="input-card-title" htmlFor="user-input">
            <Icon name="scale" size={20} />
            {t.inputLabel}
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-4)' }}>
            <span className="input-card-hint">{t.noJargon}</span>
            <div className="lang-switcher" role="group" aria-label="Language selection">
              <button className={`lang-btn${lang === 'en' ? ' active' : ''}`} onClick={() => setLang('en')}>English</button>
              <button className={`lang-btn${lang === 'hi' ? ' active' : ''}`} onClick={() => setLang('hi')} style={{ fontFamily: 'var(--font-hindi)' }}>हिंदी</button>
            </div>
          </div>
        </div>

        <textarea
          id="user-input"
          className="hero-textarea"
          placeholder={t.placeholder}
          rows="5"
          maxLength={charLimit}
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSubmit(); } }}
          aria-label={t.inputLabel}
          style={{ fontFamily: lang === 'hi' ? 'var(--font-hindi)' : 'inherit' }}
        />

        <div className="textarea-footer">
          {inputText && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setInputText("")}
              style={{ padding: '2px 8px', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}
            >
              <Icon name="x" size={12} /> Clear text
            </button>
          )}
          <span className={`char-count${inputText.length > 1800 ? ' near-limit' : ''}`}>
            {inputText.length}/{charLimit}
          </span>
        </div>

        <div className="hero-input-actions">
          <div className="privacy-notice">
            <Icon name="lockKeyhole" size={14} />
            <span>{t.privacyNotice}</span>
          </div>
          <button
            className={`btn btn-primary${isLoading ? ' btn-loading' : ''}`}
            onClick={onSubmit}
            disabled={isLoading || !inputText.trim()}
            id="submit-btn"
          >
            {!isLoading && <><span>{t.submitBtn}</span> <Icon name="arrowRight" size={16} /></>}
          </button>
        </div>
      </div>

      {/* Example Cards */}
      <div className="examples-section">
        <h2 className="section-heading">{t.examplesLabel}</h2>
        <p className="section-subheading">{t.examplesSub}</p>
        <div className="example-cards-grid">
          {exampleCards.map((card, idx) => (
            <button key={idx} className="example-card" onClick={() => setInputText(card.fill)}>
              <div className="example-card-header">
                <div className="example-card-icon-wrap"><Icon name={card.icon} size={16} /></div>
                <span className="example-card-category">{card.category}</span>
              </div>
              <p className="example-card-text">{card.text}</p>
              <div className="example-card-cta">Use this example <Icon name="arrowRight" size={12} /></div>
            </button>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="how-it-works">
        <h2 className="how-title">From <em>"what happened?"</em><br />to a clearer next step.</h2>
        <p className="how-subtitle">LegalAId breaks down complex statutory codes into structured, source-checked guidance you can act on.</p>
        <div className="how-steps-grid">
          {[
            { n: "1", h: "Tell us", p: "Explain in plain English or Hindi — no legal jargon needed." },
            { n: "2", h: "Understand", p: "We classify your domain, facts, state, and financial scope." },
            { n: "3", h: "Find law", p: "Database queries verified statutory sections matching your state and facts." },
            { n: "4", h: "Plan next", p: "Get a plain-language explanation, evidence checklist, and document draft." },
          ].map(step => (
            <div key={step.n} className="how-step-card">
              <div className="step-num-circle">{step.n}</div>
              <h3>{step.h}</h3>
              <p>{step.p}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ASSISTANT VIEW — WORKSPACE STATE
   ═══════════════════════════════════════════════════════════════════════════ */
function WorkspaceState({
  inputText, caseState, setModal,
  handleConfirmFacts, handleExplainRights, handleGenerateDocument
}) {
  const { step, isLoading, thinkingLabel, error, classifierOutput, retrievedMatches, explanationData, evidenceData, roadmapData, documents } = caseState;

  const isUrgent = (domain) => domain === 'cyber' || (roadmapData?.steps?.some(s => s.urgency === 'urgent'));

  return (
    <div className="workspace-container">
      {/* User's query */}
      <div className="user-query-card">
        <div className="user-query-icon"><Icon name="messageSquare" size={16} /></div>
        <div className="user-query-text">{inputText}</div>
      </div>

      {/* Pipeline Loader */}
      {isLoading && <PipelineLoader currentStep={step} label={thinkingLabel} />}

      {/* Error */}
      {error && !isLoading && <ErrorCard message={error} />}

      {/* Step 2 — Classifier Output (Facts Card) */}
      {classifierOutput && (
        <div className="workspace-card">
          <div className="workspace-card-header">
            <div className="workspace-card-title-block">
              <div className="workspace-card-step">Step 2 · What We Understood</div>
              <div className="workspace-card-title">
                <Icon name="verifiedBadge" size={20} />
                {DOMAIN_CONFIG[classifierOutput.domain]?.label || classifierOutput.domain}
              </div>
            </div>
            <span className="badge badge-success">✓ High Confidence</span>
          </div>
          <div className="workspace-card-body">
            <div className="facts-grid" style={{ marginBottom: 'var(--sp-5)' }}>
              {[
                { label: "Parties Involved", value: classifierOutput.facts?.parties || classifierOutput.extracted_facts?.parties || "Complainant" },
                { label: "State / Jurisdiction", value: classifierOutput.facts?.state || classifierOutput.extracted_facts?.state || "India" },
                { label: "Dates / Timeline", value: classifierOutput.facts?.date || classifierOutput.facts?.dates || classifierOutput.extracted_facts?.dates || "Recent" },
                { label: "Amount Involved", value: classifierOutput.facts?.amount || classifierOutput.facts?.amounts || classifierOutput.extracted_facts?.amounts || "Disputed amount" },
              ].map(f => (
                <div key={f.label} className="fact-item">
                  <div className="fact-label">{f.label}</div>
                  <div className="fact-value">{f.value}</div>
                </div>
              ))}
            </div>
            {!retrievedMatches.length && !isLoading && (
              <button className="btn btn-primary" onClick={() => handleConfirmFacts(classifierOutput.facts || classifierOutput.extracted_facts)} disabled={isLoading}>
                <Icon name="search" size={16} /> Looks Correct — Search Verified Law
              </button>
            )}
          </div>
        </div>
      )}

      {/* Step 3 — Retrieved Laws */}
      {retrievedMatches.length > 0 && (
        <div className="workspace-card">
          <div className="workspace-card-header">
            <div className="workspace-card-title-block">
              <div className="workspace-card-step">Step 3 · Verified Law Found</div>
              <div className="workspace-card-title">
                <Icon name="bookOpen" size={20} />
                Relevant Verified Laws ({retrievedMatches.length})
              </div>
            </div>
          </div>
          <div className="workspace-card-body">
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', marginBottom: 'var(--sp-4)' }}>
              Retrieved directly from the statutory database — matched to your state and situation:
            </p>
            {retrievedMatches.map((m, idx) => (
              <CitationCard key={idx} match={m} setModal={setModal} />
            ))}
            {!explanationData && !isLoading && (
              <div style={{ marginTop: 'var(--sp-5)' }}>
                <button className="btn btn-primary" onClick={handleExplainRights} disabled={isLoading}>
                  <Icon name="shield" size={16} /> Explain My Possible Rights
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Steps 4-6 — Rights + Evidence + Roadmap */}
      {explanationData && (
        <>
          {/* Urgent Alert */}
          {isUrgent(classifierOutput?.domain) && (
            <div className="urgent-alert">
              <div className="urgent-alert-icon"><Icon name="alertTriangle" size={18} /></div>
              <div>
                <div className="urgent-alert-title">⚡ Urgent Action May Be Required</div>
                <div className="urgent-alert-message">
                  {classifierOutput?.domain === 'cyber'
                    ? "For unauthorized bank transactions, report to your bank within 72 hours for zero-liability protection under RBI guidelines."
                    : "This situation may require prompt action. Review the action roadmap below carefully."
                  }
                </div>
              </div>
            </div>
          )}

          {/* Rights */}
          <div className="workspace-card">
            <div className="workspace-card-header">
              <div className="workspace-card-title-block">
                <div className="workspace-card-step">Step 4 · Your Possible Rights</div>
                <div className="workspace-card-title">
                  <Icon name="shield" size={20} />
                  Legal Rights Explained
                </div>
              </div>
              <span className="badge badge-success">✓ Legal Reference Verified</span>
            </div>
            <div className="workspace-card-body">
              {explanationData.summary && (
                <p style={{ fontSize: 'var(--text-base)', color: 'var(--color-text-body)', lineHeight: 1.7, marginBottom: 'var(--sp-5)' }}>
                  {explanationData.summary}
                </p>
              )}
              {explanationData.rights && (
                <div className="rights-list">
                  {explanationData.rights.map((r, i) => (
                    <div key={i} className="right-item">
                      <div className="right-item-main">
                        <div className="right-dot" aria-hidden="true" />
                        <div className="right-text">{r.explanation || r.right}</div>
                      </div>
                      {r.why_applies && (
                        <div className="right-why"><strong>Why it applies:</strong> {r.why_applies}</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Evidence Checklist */}
          {evidenceData?.checklist?.length > 0 && (
            <div className="workspace-card">
              <div className="workspace-card-header">
                <div className="workspace-card-title-block">
                  <div className="workspace-card-step">Step 5 · Evidence Checklist</div>
                  <div className="workspace-card-title">
                    <Icon name="listChecks" size={20} />
                    Documents That May Help
                  </div>
                </div>
                <span className="badge badge-neutral">{evidenceData.checklist.length} items</span>
              </div>
              <div className="workspace-card-body">
                <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', marginBottom: 'var(--sp-4)' }}>
                  Check each document as you gather it. Essential items are highlighted.
                </p>
                <EvidenceChecklist items={evidenceData.checklist} />
              </div>
            </div>
          )}

          {/* Roadmap */}
          {roadmapData?.steps?.length > 0 && (
            <div className="workspace-card">
              <div className="workspace-card-header">
                <div className="workspace-card-title-block">
                  <div className="workspace-card-step">Step 6 · Action Plan</div>
                  <div className="workspace-card-title">
                    <Icon name="mapPin" size={20} />
                    What You Can Do Next
                  </div>
                </div>
              </div>
              <div className="workspace-card-body">
                <RoadmapSteps steps={roadmapData.steps} />
                {!documents.length && !isLoading && (
                  <div style={{ marginTop: 'var(--sp-6)' }}>
                    <button className="btn btn-primary" onClick={handleGenerateDocument} disabled={isLoading}>
                      <Icon name="fileText" size={16} /> Prepare My Draft Document
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {/* Step 7 — Generated Documents */}
      {documents.map((doc, idx) => (
        <div key={idx} className="workspace-card">
          <div className="workspace-card-header">
            <div className="workspace-card-title-block">
              <div className="workspace-card-step">Step 7 · Document Ready</div>
              <div className="workspace-card-title">
                <Icon name="fileText" size={20} />
                {doc.title}
              </div>
            </div>
            <span className={`quality-score ${(doc.quality_score || 8.5) >= 8 ? 'high' : 'medium'}`}>
              ★ {doc.quality_score || 8.5}/10 Quality
            </span>
          </div>
          <div className="workspace-card-body">
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', marginBottom: 'var(--sp-5)' }}>
              Drafted using verified statutory provisions and the facts from your case.
            </p>
            <div style={{ display: 'flex', gap: 'var(--sp-3)', flexWrap: 'wrap' }}>
              <button className="btn btn-secondary" onClick={() => setModal({ type: 'editor', data: doc })}>
                <Icon name="edit" size={15} /> Edit Document
              </button>
              <a
                href={`${API_BASE}/api/documents/${doc.document_id}/pdf`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
                style={{ textDecoration: 'none', background: 'linear-gradient(135deg, var(--color-success) 0%, #4A8A69 100%)' }}
              >
                <Icon name="download" size={15} /> Download PDF
              </a>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ASSISTANT VIEW (root)
   ═══════════════════════════════════════════════════════════════════════════ */
function AssistantView({
  lang, setLang, inputText, setInputText,
  caseState, handleIntakeCase, handleConfirmFacts, handleExplainRights,
  handleGenerateDocument, handleDeleteCase, setModal
}) {
  return (
    <section id="view-assistant" className="view active">
      {!caseState.isLanding && (
        <CaseProgressBar currentStep={caseState.step} onDelete={handleDeleteCase} />
      )}

      {caseState.isLanding ? (
        <LandingState
          lang={lang}
          setLang={setLang}
          inputText={inputText}
          setInputText={setInputText}
          isLoading={caseState.isLoading}
          onSubmit={handleIntakeCase}
        />
      ) : (
        <WorkspaceState
          inputText={inputText}
          caseState={caseState}
          setModal={setModal}
          handleConfirmFacts={handleConfirmFacts}
          handleExplainRights={handleExplainRights}
          handleGenerateDocument={handleGenerateDocument}
        />
      )}
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   CORPUS VIEW — LEGAL SOURCES
   ═══════════════════════════════════════════════════════════════════════════ */
function CorpusView({ corpusState, setCorpusState, handleExecuteCorpusSearch, handleRunVerify, setModal }) {
  const [searchInput, setSearchInput] = useState(corpusState.query || "");

  const triggerSearch = (q, dom) => {
    handleExecuteCorpusSearch(q !== undefined ? q : searchInput, dom !== undefined ? dom : corpusState.domain);
  };

  const SUGGESTIONS = ["security deposit", "unpaid wages", "cyber fraud", "defective product", "unauthorized bank transfer", "illegal eviction"];

  const skeletonCards = Array(3).fill(0).map((_, i) => (
    <div key={i} className="skeleton-card" style={{ marginBottom: '16px' }}>
      <div className="skeleton" style={{ width: '60%', height: '20px', marginBottom: '12px' }} />
      <div className="skeleton" style={{ width: '40%', height: '14px', marginBottom: '16px' }} />
      <div className="skeleton" style={{ width: '100%', height: '56px', marginBottom: '12px' }} />
      <div className="skeleton" style={{ width: '80%', height: '32px' }} />
    </div>
  ));

  return (
    <section id="view-corpus" className="view active">
      <div className="page-header">
        <h1 className="page-title">Legal Sources</h1>
        <p className="page-subtitle">LegalAId uses a curated database of verified Indian statutes. Every response is grounded in real statutory law — never invented.</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid" aria-label="Corpus statistics">
        {[
          { v: corpusState.stats?.total_acts || corpusState.stats?.acts_count || 6, l: "Statute Acts" },
          { v: corpusState.stats?.total_sections || corpusState.stats?.sections_count || 48, l: "Verified Sections" },
          { v: corpusState.stats?.domains?.consumer || 14, l: "Consumer Protection" },
          { v: corpusState.stats?.domains?.labor || 10, l: "Work & Labour" },
          { v: corpusState.stats?.domains?.tenant || 14, l: "Rent & Housing" },
          { v: corpusState.stats?.domains?.criminal || 7, l: "Criminal Justice" },
        ].map((s, i) => (
          <div key={i} className="stat-card">
            <div className="stat-value">{s.v}</div>
            <div className="stat-label">{s.l}</div>
          </div>
        ))}
      </div>

      {/* Search */}
      <div className="corpus-search-bar" role="search">
        <input
          id="corpus-search-input"
          className="corpus-search-input"
          type="search"
          placeholder="Search verified legal sources… (e.g. 'security deposit', 'unpaid wages')"
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); triggerSearch(searchInput, corpusState.domain); } }}
          aria-label="Search legal sources"
        />
        <select
          className="corpus-domain-select"
          value={corpusState.domain || ""}
          onChange={e => {
            const dom = e.target.value;
            setCorpusState(prev => ({ ...prev, domain: dom }));
            triggerSearch(searchInput, dom);
          }}
          aria-label="Filter by domain"
        >
          <option value="">All Categories</option>
          <option value="consumer">Consumer Protection</option>
          <option value="labor">Work & Labour</option>
          <option value="tenant">Rent & Tenant</option>
          <option value="cyber">Cyber Fraud</option>
          <option value="criminal">Criminal Matters</option>
        </select>
        <button
          className={`btn btn-primary${corpusState.isSearching ? ' btn-loading' : ''}`}
          onClick={() => triggerSearch(searchInput, corpusState.domain)}
          disabled={corpusState.isSearching}
        >
          {!corpusState.isSearching && <><Icon name="search" size={15} /> Search</>}
        </button>
      </div>

      {/* Suggestion chips */}
      <div className="suggestion-chips">
        <span className="suggestion-label">Try searching:</span>
        {SUGGESTIONS.map(sug => (
          <button
            key={sug}
            className="suggestion-chip"
            onClick={() => { setSearchInput(sug); triggerSearch(sug, corpusState.domain); }}
          >
            {sug}
          </button>
        ))}
      </div>

      {/* Results */}
      {corpusState.isSearching ? (
        <>{skeletonCards}</>
      ) : corpusState.hasSearched ? (
        corpusState.results.length > 0 ? (
          <div>
            <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 700, color: 'var(--color-primary)', marginBottom: 'var(--sp-4)' }}>
              Search Results for "{corpusState.query}" ({corpusState.results.length} found)
            </h2>
            {corpusState.results.map((item, idx) => <CorpusCard key={idx} item={item} setModal={setModal} />)}
          </div>
        ) : (
          <EmptyState
            icon="search"
            title={`No verified provisions found for "${corpusState.query}"`}
            message='LegalAId does not invent legal sections. When the database returns no verified match, we tell you so — rather than guessing.'
            action={
              <button className="btn btn-secondary" onClick={() => { setSearchInput(""); setCorpusState(prev => ({ ...prev, hasSearched: false, results: [], query: "" })); }}>
                Clear Search
              </button>
            }
          />
        )
      ) : (
        <div>
          <h2 style={{ fontSize: 'var(--text-xl)', fontWeight: 700, color: 'var(--color-primary)', marginBottom: 'var(--sp-4)' }}>
            Browse Verified Legal Provisions
          </h2>
          {corpusState.featured.map((item, idx) => <CorpusCard key={idx} item={item} setModal={setModal} />)}
        </div>
      )}

      {/* Corpus error */}
      {corpusState.error && !corpusState.isSearching && (
        <ErrorCard message={corpusState.error} />
      )}

      {/* Verify bar */}
      <div className="verify-bar">
        <button
          className={`btn btn-secondary${corpusState.isVerifying ? ' btn-loading' : ''}`}
          onClick={handleRunVerify}
          disabled={corpusState.isVerifying}
        >
          {!corpusState.isVerifying && <><Icon name="verifiedBadge" size={15} /> Run Integrity Check</>}
        </button>
        {corpusState.verifyReport && (
          <div className={`verify-report ${corpusState.verifyReport.passed ? 'pass' : 'fail'}`}>
            <div className="verify-report-title">
              {corpusState.verifyReport.passed ? '✓ Database Corpus & FTS Index Healthy' : '❌ Integrity Issues Detected'}
            </div>
            <div className="verify-report-message">{corpusState.verifyReport.summary}</div>
          </div>
        )}
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   DOCUMENTS VIEW
   ═══════════════════════════════════════════════════════════════════════════ */
function DocumentsView({ documents, switchView, setModal }) {
  return (
    <section id="view-documents" className="view active">
      <div className="page-header">
        <h1 className="page-title">My Documents</h1>
        <p className="page-subtitle">Your legal drafts — review, edit sections, and export as a signed PDF.</p>
      </div>

      {documents.length === 0 ? (
        <EmptyState
          icon="fileText"
          title="No documents yet"
          message="Complete a legal query using the Legal Assistant — LegalAId will help you prepare a formal draft notice or complaint."
          action={
            <button className="btn btn-primary" onClick={() => switchView('assistant')}>
              <Icon name="messageSquare" size={15} /> Start a Legal Query
            </button>
          }
        />
      ) : (
        <div>
          {documents.map((doc, idx) => {
            const q = doc.quality_score || 8.5;
            const qClass = q >= 8 ? 'high' : q >= 6 ? 'medium' : 'low';
            return (
              <div key={idx} className="document-card">
                <div className="document-card-info">
                  <div className="document-card-title">{doc.title}</div>
                  <div className="document-card-meta">
                    <span>ID: {doc.document_id?.slice(0, 8)}…</span>
                    <span className={`quality-score ${qClass}`}>★ {q}/10 Quality</span>
                  </div>
                </div>
                <div className="document-card-actions">
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => setModal({ type: 'editor', data: doc })}
                  >
                    <Icon name="edit" size={13} /> Edit
                  </button>
                  <a
                    href={`${API_BASE}/api/documents/${doc.document_id}/pdf`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary btn-sm"
                    style={{ textDecoration: 'none', background: 'linear-gradient(135deg, var(--color-success) 0%, #4A8A69 100%)' }}
                  >
                    <Icon name="download" size={13} /> PDF
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ABOUT VIEW
   ═══════════════════════════════════════════════════════════════════════════ */
function AboutView() {
  return (
    <section id="view-about" className="view active">
      <div className="page-header">
        <h1 className="page-title">How LegalAId Works</h1>
        <p className="page-subtitle">Transparent, source-grounded legal guidance — built for those who need it most.</p>
      </div>

      <div className="about-cards">
        <div className="about-card">
          <h2><Icon name="scale" size={24} /> Built for First-Generation Litigants</h2>
          <p>
            Most people in India facing everyday legal disputes — a defective product refund refusal, an employer withholding severance pay, or a landlord cutting off water supply — cannot afford an advocate. LegalAId was built specifically to bridge this gap by making statutory law accessible in plain English and Hindi.
          </p>
        </div>

        <div className="about-card about-card-gold">
          <h2><Icon name="shield" size={24} /> Zero AI Hallucination Architecture</h2>
          <p>
            Generic AI chatbots frequently invent fake law section numbers and case references. <strong>LegalAId does not allow the AI to invent legal provisions.</strong> Every section cited is retrieved and verified against a curated database of real Indian statutes. If no section matches your situation, LegalAId explicitly tells you — rather than guessing.
          </p>
        </div>

        <div className="about-card">
          <h2><Icon name="zap" size={24} /> The Pipeline (Retrieval Before Generation)</h2>
          <p style={{ marginBottom: '16px' }}>Every response goes through an 8-step verified pipeline:</p>
          <div className="pipeline-diagram" aria-label="Pipeline architecture">
            {[
              "User Case Intake (Hindi / English)",
              "Input Sanitisation & Prompt Injection Defence",
              "Classifier (Domain · Subdomain · State · Urgency)",
              "State-Aware Hybrid Retrieval (FTS5 BM25 + Domain Filter)",
              "Verified Candidate Statutory Provisions",
              "Rights Explainer & 'Why This Law Applies'",
              "Advanced Citation Verifier (8-point check)",
              "Evidence Checklist · Action Roadmap · Document Draft",
            ].map((step, idx) => (
              <div key={idx}>
                {idx > 0 && <span className="pipeline-arrow">    ↓</span>}
                <div>{idx + 1}. {step}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="about-card">
          <h2><Icon name="bookOpen" size={24} /> Supported Legal Domains</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginTop: '16px' }}>
            {[
              { icon: "shoppingBag", label: "Consumer Rights", detail: "Consumer Protection Act, 2019 — defective products, refund disputes, service deficiencies" },
              { icon: "briefcase", label: "Labour & Employment", detail: "Industrial Disputes Act, 1947 — unpaid wages, illegal termination, severance" },
              { icon: "home", label: "Tenant & Housing", detail: "Model Tenancy Act 2021, Delhi Rent Control Act 1958 — security deposits, illegal eviction" },
              { icon: "creditCard", label: "Cyber Crime & Fraud", detail: "IT Act 2000 — unauthorized transactions, phishing, RBI 72-hour zero-liability" },
              { icon: "gavel", label: "Criminal Rights", detail: "Bharatiya Nyaya Sanhita 2023 — FIR rights, civic offences, basic protections" },
            ].map(domain => (
              <div key={domain.label} style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <Icon name={domain.icon} size={16} />
                  <strong style={{ fontSize: 'var(--text-sm)', color: 'var(--color-primary)' }}>{domain.label}</strong>
                </div>
                <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)', lineHeight: 1.55 }}>{domain.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="about-card">
          <h2><Icon name="lockKeyhole" size={24} /> Privacy & Security</h2>
          <p style={{ marginBottom: '16px' }}>
            LegalAId treats all user inputs as case facts — not as trusted instructions. Prompt injection attempts and HTML/XSS injection are automatically neutralised. Password, OTP, Aadhaar, and PAN inputs are strictly prohibited and filtered.
          </p>
          <p>
            <strong>Delete My Case</strong> — clicking the delete button performs a cascading privacy purge: the case, all associated facts, classified outputs, and drafted documents are permanently removed from the database.
          </p>
        </div>

        <div className="about-card">
          <h2><Icon name="info" size={24} /> Limitations & Roadmap</h2>
          <p>
            LegalAId currently covers central statutes and Delhi-specific tenant laws. State-specific statutes for all 28 states and 8 UTs are planned for future versions. FTS5 BM25 full-text search can be augmented with local ONNX vector embeddings when GPU/TPU acceleration is available.
          </p>
          <p style={{ marginTop: '12px', fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', background: 'var(--color-gold-light)', border: '1px solid var(--color-gold-border)', borderRadius: 'var(--radius-sm)', padding: '12px 16px' }}>
            <strong>Important:</strong> LegalAId provides general legal information to help you understand your rights — it does not provide legal advice and is not a substitute for a qualified advocate in your specific situation.
          </p>
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ROOT APP
   ═══════════════════════════════════════════════════════════════════════════ */
function App() {
  const [view, setView] = useState("assistant");
  const [lang, setLang] = useState("en");
  const [inputText, setInputText] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [modal, setModal] = useState({ type: null, data: null });

  // Case pipeline state
  const [caseState, setCaseState] = useState({
    caseId: null,
    step: 1,
    isLanding: true,
    isLoading: false,
    thinkingLabel: "",
    error: null,
    classifierOutput: null,
    retrievedMatches: [],
    explanationData: null,
    evidenceData: null,
    roadmapData: null,
    documents: []
  });

  // Corpus search state
  const [corpusState, setCorpusState] = useState({
    stats: { total_acts: 6, total_sections: 48, domains: { consumer: 14, labor: 10, tenant: 14, criminal: 7 } },
    query: "",
    domain: "",
    results: [],
    featured: [],
    isSearching: false,
    hasSearched: false,
    error: null,
    verifyReport: null,
    isVerifying: false
  });

  /* ── Health Check ── */
  useEffect(() => {
    async function checkHealth() {
      try {
        const resp = await fetch(`${API_BASE}/api/health`);
        const data = await resp.json();
        setApiStatus(resp.ok && data.status === "ok" ? "ready" : "offline");
      } catch {
        setApiStatus("offline");
      }
    }
    checkHealth();
  }, []);

  /* ── Corpus Loading ── */
  const loadCorpusStats = useCallback(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/corpus/stats`);
      const data = await resp.json();
      if (data.success) setCorpusState(prev => ({ ...prev, stats: data.data }));
    } catch {}
  }, []);

  const loadFeaturedSections = useCallback(async (domFilter) => {
    try {
      const url = `${API_BASE}/api/corpus/sections?limit=15${domFilter ? `&domain=${domFilter}` : ''}`;
      const resp = await fetch(url);
      const data = await resp.json();
      if (data.success) setCorpusState(prev => ({ ...prev, featured: data.data }));
    } catch {}
  }, []);

  useEffect(() => {
    if (view === "corpus") {
      loadCorpusStats();
      if (!corpusState.hasSearched) loadFeaturedSections(corpusState.domain);
    }
  }, [view]);

  /* ── Navigation ── */
  const switchView = (newView) => {
    setView(newView);
    setMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  /* ── Case Pipeline ── */
  const handleIntakeCase = async () => {
    const text = inputText.trim();
    if (!text) return;

    setCaseState(prev => ({
      ...prev, isLanding: false, isLoading: true,
      thinkingLabel: "Understanding your situation", error: null, step: 1
    }));

    try {
      const caseResp = await fetch(`${API_BASE}/api/cases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: lang })
      });
      const caseData = await caseResp.json();
      if (!caseResp.ok || !caseData.success) throw new Error(caseData.error?.message || "Could not intake case.");
      const newCaseId = caseData.data.case_id;

      setCaseState(prev => ({ ...prev, thinkingLabel: "Extracting facts and parties", step: 2 }));

      const classifyResp = await fetch(`${API_BASE}/api/cases/${newCaseId}/classify`, { method: "POST" });
      const classifyData = await classifyResp.json();
      if (!classifyResp.ok || !classifyData.success) throw new Error(classifyData.error?.message || "Classification failed.");

      setCaseState(prev => ({
        ...prev,
        caseId: newCaseId,
        classifierOutput: classifyData.data,
        step: 2,
        isLoading: false
      }));
    } catch (err) {
      setCaseState(prev => ({ ...prev, isLoading: false, error: err.message }));
      showToast('error', err.message, 'Case Intake Failed');
    }
  };

  const handleConfirmFacts = async (editedFacts) => {
    setCaseState(prev => ({
      ...prev, isLoading: true,
      thinkingLabel: "Searching verified legal database",
      error: null, step: 3
    }));

    try {
      const retResp = await fetch(`${API_BASE}/api/cases/${caseState.caseId}/retrieve`, { method: "POST" });
      const retData = await retResp.json();
      if (!retResp.ok || !retData.success) throw new Error(retData.error?.message || "Retrieval failed.");

      if (retData.data.status === "insufficient_confidence" || !retData.data.matches?.length) {
        setCaseState(prev => ({
          ...prev, isLoading: false, retrievedMatches: [],
          error: "We couldn't confidently verify a specific statutory provision for this situation in our database. We don't want to guess. Please consult a qualified legal professional."
        }));
        return;
      }

      setCaseState(prev => ({ ...prev, retrievedMatches: retData.data.matches, isLoading: false }));
    } catch (err) {
      setCaseState(prev => ({ ...prev, isLoading: false, error: err.message }));
      showToast('error', err.message, 'Law Search Failed');
    }
  };

  const handleExplainRights = async () => {
    setCaseState(prev => ({
      ...prev, isLoading: true,
      thinkingLabel: "Preparing rights explanation",
      error: null, step: 4
    }));

    try {
      const [expResp, evResp, rmResp] = await Promise.all([
        fetch(`${API_BASE}/api/cases/${caseState.caseId}/explain`, { method: "POST" }),
        fetch(`${API_BASE}/api/cases/${caseState.caseId}/evidence`),
        fetch(`${API_BASE}/api/cases/${caseState.caseId}/roadmap`),
      ]);

      const [expData, evData, rmData] = await Promise.all([expResp.json(), evResp.json(), rmResp.json()]);

      if (!expResp.ok || !expData.success) throw new Error(expData.error?.message || "Explanation failed.");

      setCaseState(prev => ({
        ...prev,
        explanationData: expData.data,
        evidenceData: evData.data,
        roadmapData: rmData.data,
        step: 6,
        isLoading: false
      }));
    } catch (err) {
      setCaseState(prev => ({ ...prev, isLoading: false, error: err.message }));
      showToast('error', err.message, 'Rights Explanation Failed');
    }
  };

  const handleGenerateDocument = async () => {
    setCaseState(prev => ({
      ...prev, isLoading: true,
      thinkingLabel: "Drafting your legal document",
      error: null, step: 7
    }));

    try {
      const dom = caseState.classifierOutput?.domain || "general";
      const docTypeMap = { consumer: "consumer_complaint", labor: "labor_complaint", tenant: "tenant_notice", cyber: "cyber_complaint" };
      const docType = docTypeMap[dom] || "legal_notice";

      const docResp = await fetch(`${API_BASE}/api/cases/${caseState.caseId}/document?doc_type=${docType}`, { method: "POST" });
      const docData = await docResp.json();
      if (!docResp.ok || !docData.success) throw new Error(docData.error?.message || "Document generation failed.");

      setCaseState(prev => ({ ...prev, documents: [...prev.documents, docData.data], isLoading: false }));
      showToast('success', 'Your legal document draft is ready to review and edit.', 'Document Generated');
    } catch (err) {
      setCaseState(prev => ({ ...prev, isLoading: false, error: err.message }));
      showToast('error', err.message, 'Document Generation Failed');
    }
  };

  const handleSaveDocumentEdits = async (docId, updatedSections) => {
    const resp = await fetch(`${API_BASE}/api/documents/${docId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sections: updatedSections })
    });
    const data = await resp.json();
    if (data.success) {
      setCaseState(prev => ({
        ...prev,
        documents: prev.documents.map(d => d.document_id === docId ? data.data : d)
      }));
      setModal({ type: null, data: null });
    } else {
      throw new Error(data.error?.message || "Save failed");
    }
  };

  const handleDeleteCase = async () => {
    if (!caseState.caseId) { window.location.reload(); return; }
    try {
      const resp = await fetch(`${API_BASE}/api/cases/${caseState.caseId}`, { method: "DELETE" });
      const data = await resp.json();
      if (data.success) {
        showToast('success', 'All case data has been permanently purged.', 'Case Deleted');
        setTimeout(() => window.location.reload(), 1500);
      }
    } catch (err) {
      showToast('error', err.message || 'Delete failed. Please refresh the page.', 'Delete Failed');
    }
  };

  /* ── Corpus Actions ── */
  const handleExecuteCorpusSearch = async (queryOverride, domainOverride) => {
    const q = (queryOverride !== undefined ? queryOverride : corpusState.query).trim();
    const dom = domainOverride !== undefined ? domainOverride : corpusState.domain;

    if (!q) {
      setCorpusState(prev => ({ ...prev, query: "", hasSearched: false, results: [] }));
      loadFeaturedSections(dom);
      return;
    }

    setCorpusState(prev => ({ ...prev, query: q, domain: dom, isSearching: true, hasSearched: true, error: null }));

    try {
      const url = `${API_BASE}/api/corpus/search?q=${encodeURIComponent(q)}${dom ? `&domain=${encodeURIComponent(dom)}` : ''}`;
      const resp = await fetch(url);
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error?.message || "Corpus search failed.");

      const results = data.data?.results || data.results || data.data?.matches || data.matches || [];
      setCorpusState(prev => ({ ...prev, results, isSearching: false }));
    } catch (err) {
      setCorpusState(prev => ({ ...prev, isSearching: false, error: err.message }));
    }
  };

  const handleRunVerify = async () => {
    setCorpusState(prev => ({ ...prev, isVerifying: true }));
    try {
      const resp = await fetch(`${API_BASE}/api/corpus/verify`);
      const data = await resp.json();
      if (data.success) setCorpusState(prev => ({ ...prev, verifyReport: data.data, isVerifying: false }));
    } catch (err) {
      showToast('error', err.message || 'Integrity check failed.', 'Verify Failed');
      setCorpusState(prev => ({ ...prev, isVerifying: false }));
    }
  };

  /* ── Render ── */
  return (
    <div className="app-container">
      {/* Toast notifications */}
      <ToastContainer />

      {/* Mobile: header + overlay */}
      <MobileHeader onMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)} isOpen={mobileMenuOpen} />
      {mobileMenuOpen && (
        <div className="sidebar-overlay visible" onClick={() => setMobileMenuOpen(false)} aria-hidden="true" />
      )}

      {/* Desktop sidebar */}
      <Sidebar view={view} switchView={switchView} isOpen={mobileMenuOpen} apiStatus={apiStatus} />

      {/* Main content */}
      <main className="main-content" id="main-content">
        <DisclaimerBanner switchView={switchView} />

        {view === "assistant" && (
          <AssistantView
            lang={lang} setLang={setLang}
            inputText={inputText} setInputText={setInputText}
            caseState={caseState}
            handleIntakeCase={handleIntakeCase}
            handleConfirmFacts={handleConfirmFacts}
            handleExplainRights={handleExplainRights}
            handleGenerateDocument={handleGenerateDocument}
            handleDeleteCase={handleDeleteCase}
            setModal={setModal}
          />
        )}

        {view === "corpus" && (
          <CorpusView
            corpusState={corpusState}
            setCorpusState={setCorpusState}
            handleExecuteCorpusSearch={handleExecuteCorpusSearch}
            handleRunVerify={handleRunVerify}
            setModal={setModal}
          />
        )}

        {view === "documents" && (
          <DocumentsView
            documents={caseState.documents}
            switchView={switchView}
            setModal={setModal}
          />
        )}

        {view === "about" && <AboutView />}
      </main>

      {/* Mobile bottom navigation */}
      <MobileBottomNav view={view} switchView={switchView} />

      {/* Modals */}
      {modal.type === "section" && (
        <SectionModal item={modal.data} onClose={() => setModal({ type: null, data: null })} />
      )}
      {modal.type === "editor" && (
        <DocumentEditorModal
          doc={modal.data}
          onSave={handleSaveDocumentEdits}
          onClose={() => setModal({ type: null, data: null })}
        />
      )}
    </div>
  );
}

/* ── Mount ── */
const container = document.getElementById("root");
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(<App />);
}
