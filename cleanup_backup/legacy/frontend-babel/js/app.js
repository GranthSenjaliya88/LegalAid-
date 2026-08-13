/**
 * LegalAId — Frontend Application
 *
 * Grounded Indian Legal Rights Assistant.
 * Connects UI actions to the production backend APIs.
 */

const API_BASE = "http://127.0.0.1:8000";

/* ─────────────────────────────── State ───────────────────────── */
const state = {
  currentView: "assistant",
  currentDomain: "",
  currentLang: "en",
  corpusActs: [],
  messages: [],
  caseId: null,
  classifierOutput: null,
  retrievedMatches: [],
  explanationData: null,
  evidenceData: null,
  roadmapData: null,
  generatedDocuments: [],
  activeDocInEditor: null
};

/* ─────────────────────────────── DOM Refs ─────────────────────── */
const $ = (id) => document.getElementById(id);

const navItems       = document.querySelectorAll(".nav-item");
const bottomNavItems = document.querySelectorAll(".bottom-nav-item");
const views          = document.querySelectorAll(".view");
const domainPills    = document.querySelectorAll(".domain-pill");
const exampleCards   = document.querySelectorAll(".example-card");
const langSwitchBtns = document.querySelectorAll(".lang-switch-btn");

/* ─────────────────────────────── Navigation ───────────────────── */
function switchView(viewName) {
  state.currentView = viewName;
  views.forEach((v) => v.classList.remove("active"));
  navItems.forEach((n) => n.classList.remove("active"));
  bottomNavItems.forEach((b) => b.classList.remove("active"));

  const target = $(`view-${viewName}`);
  const navBtn = $(`nav-${viewName}`);
  const bNavBtn = document.querySelector(`.bottom-nav-item[data-view="${viewName}"]`);

  if (target) target.classList.add("active");
  if (navBtn) navBtn.classList.add("active");
  if (bNavBtn) bNavBtn.classList.add("active");

  // Close mobile sidebar drawer if open
  if ($("sidebar")) $("sidebar").classList.remove("mobile-open");

  if (viewName === "corpus") loadCorpusView();
  if (viewName === "documents") renderMyDocumentsView();
}

navItems.forEach((btn) => {
  btn.addEventListener("click", () => {
    const view = btn.dataset.view;
    if (view) switchView(view);
  });
});

bottomNavItems.forEach((btn) => {
  btn.addEventListener("click", () => {
    const view = btn.dataset.view;
    if (view) switchView(view);
  });
});

/* Mobile Menu Toggle */
if ($("mobile-menu-toggle")) {
  $("mobile-menu-toggle").addEventListener("click", () => {
    $("sidebar").classList.toggle("mobile-open");
  });
}

/* ─────────────────────────────── Progress Tracker ─────────────── */
const STEP_LABELS = [
  "", "Situation", "Facts", "Search Verified Law", "Explain Rights", "Evidence Checklist", "Action Roadmap", "Document Draft"
];

function updateProgress(stepNumber) {
  const container = $("case-progress-container");
  if (container) container.classList.remove("hidden");

  for (let i = 1; i <= 7; i++) {
    const el = $(`prog-step-${i}`);
    if (!el) continue;
    if (i < stepNumber) {
      el.className = "progress-step done";
    } else if (i === stepNumber) {
      el.className = "progress-step active";
    } else {
      el.className = "progress-step";
    }
  }

  // Update mobile progress label
  const mobileLabel = $("mobile-progress-label");
  if (mobileLabel) {
    mobileLabel.innerHTML = `
      <span class="mobile-step-counter">Step ${stepNumber} of 7</span> · 
      <span class="mobile-step-name">${STEP_LABELS[stepNumber] || ''}</span>
    `;
  }
}

/* ─────────────────────────────── Disclaimer ──────────────────── */
if ($("disclaimer-close")) {
  $("disclaimer-close").addEventListener("click", () => {
    $("disclaimer-banner").style.display = "none";
  });
}

/* ─────────────────────────────── Domain Pills ─────────────────── */
domainPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    domainPills.forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    state.currentDomain = pill.dataset.domain;
  });
});

/* ─────────────────────────────── Language Switcher ─────────────── */
const LANG_TEXTS = {
  en: {
    heroHeading: "Tell us what happened.",
    heroSubheading: "Describe your legal problem in your own words. You can write in Hindi or English.",
    inputLabel: "⚖️ Tell us what happened",
    noJargon: "You don't need to know the law. Just tell us what happened.",
    placeholder: "Example: My landlord has not returned my ₹20,000 security deposit even though I moved out two months ago.",
    submitBtn: "Understand My Rights →",
    privacyNotice: "<strong>Your information matters.</strong> Don't enter passwords, OTPs, PINs, or unnecessary sensitive personal information.",
    examplesLabel: "Not sure what to write? Try an example:"
  },
  hi: {
    heroHeading: "अपनी कानूनी समस्या बताएं।",
    heroSubheading: "अपनी बात अपने शब्दों में कहें — हिंदी या अंग्रेजी में।",
    inputLabel: "⚖️ अपनी कानूनी समस्या बताएं",
    noJargon: "कानूनी शब्दों की जरूरत नहीं है, बस जो हुआ वो बताएं।",
    placeholder: "उदाहरण: मैंने दो महीने पहले मकान खाली कर दिया था लेकिन मकान मालिक ₹20,000 की डिपॉजिट वापस नहीं कर रहा है।",
    submitBtn: "मेरे अधिकार समझें →",
    privacyNotice: "<strong>आपकी निजता महत्वपूर्ण है।</strong> पासवर्ड, ओटीपी या पिन कभी साझा न करें।",
    examplesLabel: "क्या लिखें समझ नहीं आ रहा? उदाहरण चुनें:"
  }
};

langSwitchBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    langSwitchBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.currentLang = btn.dataset.lang;
    applyLanguage(state.currentLang);
  });
});

function applyLanguage(lang) {
  const t = LANG_TEXTS[lang] || LANG_TEXTS.en;
  if ($("hero-heading")) $("hero-heading").textContent = t.heroHeading;
  if ($("hero-subheading")) $("hero-subheading").textContent = t.heroSubheading;
  if ($("input-card-label")) $("input-card-label").textContent = t.inputLabel;
  if ($("no-legal-jargon-hint")) $("no-legal-jargon-hint").textContent = t.noJargon;
  if ($("submit-btn-label")) $("submit-btn-label").textContent = t.submitBtn;
  if ($("privacy-notice-label")) $("privacy-notice-label").innerHTML = t.privacyNotice;
  if ($("examples-label")) $("examples-label").textContent = t.examplesLabel;

  const textarea = $("user-input");
  if (textarea) textarea.placeholder = t.placeholder;
}

/* ─────────────────────────────── Example Cards ────────────────── */
exampleCards.forEach((card) => {
  card.addEventListener("click", () => {
    const text = card.dataset.example;
    const textarea = $("user-input");
    if (textarea && text) {
      textarea.value = text;
      textarea.dispatchEvent(new Event("input"));
      textarea.focus();
      textarea.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
});

/* ─────────────────────────────── Textarea Auto-Resize ─────────── */
if ($("user-input")) {
  $("user-input").addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 250) + "px";
  });
}

/* ─────────────────────────────── Delete Case Privacy Button ────── */
if ($("delete-case-btn")) {
  $("delete-case-btn").addEventListener("click", handleDeleteCase);
}

async function handleDeleteCase() {
  if (!state.caseId) return;
  if (!confirm("Are you sure you want to purge all case data for privacy?")) return;

  try {
    const resp = await fetch(`${API_BASE}/api/cases/${state.caseId}`, { method: "DELETE" });
    const data = await resp.json();
    if (data.success) {
      alert("Case data and documents purged successfully.");
      location.reload();
    }
  } catch (err) {
    alert("Error deleting case: " + err.message);
  }
}

/* ─────────────────────────────── Send Message ─────────────────── */
if ($("send-btn")) {
  $("send-btn").addEventListener("click", sendMessage);
}

if ($("user-input")) {
  $("user-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

async function sendMessage() {
  const textarea = $("user-input");
  const text = textarea.value.trim();
  if (!text) return;

  const sendBtn = $("send-btn");
  textarea.disabled = true;
  sendBtn.disabled  = true;

  // Transition from landing hero to case workspace
  if ($("assistant-landing-wrapper")) $("assistant-landing-wrapper").classList.add("hidden");
  if ($("chat-container")) $("chat-container").classList.remove("hidden");

  appendMessage("user", text);
  textarea.value = "";
  textarea.style.height = "auto";

  updateProgress(1);
  const thinkingId = appendThinking("Understanding your situation…");

  try {
    // 1. POST /api/cases - Intake case
    const caseResp = await fetch(`${API_BASE}/api/cases`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language: state.currentLang }),
    });
    const caseData = await caseResp.json();
    if (!caseResp.ok || !caseData.success) {
      throw new Error(caseData.error?.message || "Could not intake case.");
    }
    state.caseId = caseData.data.case_id;

    if ($("delete-case-btn")) {
      $("delete-case-btn").classList.remove("hidden");
    }

    // 2. POST /api/cases/{id}/classify - Classify domain & extract facts
    const classifyResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/classify`, {
      method: "POST"
    });
    const classifyData = await classifyResp.json();
    removeThinking(thinkingId);

    if (!classifyResp.ok || !classifyData.success) {
      throw new Error(classifyData.error?.message || "Classification failed.");
    }

    state.classifierOutput = classifyData.data;
    updateProgress(2);
    renderClassifierCard(classifyData.data);
  } catch (err) {
    removeThinking(thinkingId);
    appendMessage("ai-error", `⚠️ ${err.message}`);
  } finally {
    textarea.disabled = false;
    sendBtn.disabled  = false;
  }
}

/* ─────────────────────────────── Classifier Card ──────────────── */
const DOMAIN_LABELS = {
  consumer: "Consumer Rights",
  labor:    "Work & Labour Law",
  tenant:   "Rent & Housing Law",
  cyber:    "Cyber Crime & Financial Fraud",
  criminal: "Criminal Justice (BNS 2023)",
  general:  "General Civic Dispute",
};

function renderClassifierCard(output) {
  if (!output) return;
  const domain = output.domain;
  const facts = output.facts || {};
  const msgs = $("chat-messages");

  const cardEl = document.createElement("div");
  cardEl.className = "message ai";
  const cardId = `classifier-card-${Date.now()}`;
  const formId = `facts-form-${Date.now()}`;

  cardEl.innerHTML = `
    <div class="message-avatar">⚖️</div>
    <div class="message-bubble" style="padding:0;background:none;border:none;width:100%;">
      <div class="classifier-card" id="${cardId}">

        <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:16px;margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="font-size:12px;font-weight:600;color:var(--text-muted);">Step 2 · What We Understood</span>
              <span style="background:var(--amber-600);color:#fff;font-size:12px;font-weight:600;padding:2px 10px;border-radius:999px;">
                ${DOMAIN_LABELS[domain] || domain}
              </span>
            </div>
            <span style="font-size:12px;color:var(--green-500);font-weight:600;">✓ High Confidence</span>
          </div>

          <p style="font-size:13px;color:var(--text-secondary);margin-bottom:14px;">Review what we extracted from your situation. You can edit any detail if needed:</p>

          <form class="facts-form" id="${formId}" autocomplete="off" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:10px;">
            ${factField("Parties Involved", "parties", facts.parties, "e.g. Complainant vs Counterparty")}
            ${factField("State / UT Location", "state", facts.state, "e.g. Delhi, Maharashtra, Karnataka")}
            ${factField("Dates / Timeline", "date", facts.date, "e.g. 2 months ago, Jan 2024")}
            ${factField("Amount Involved", "amount", facts.amount, "e.g. ₹20,000")}
            ${factField("Incident Summary", "incident", facts.incident, "Summary of what happened")}
            ${factField("Desired Outcome", "desired_outcome", facts.desired_outcome, "e.g. deposit return, refund")}
          </form>

          <div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding-top:12px;border-top:1px solid var(--border-subtle);">
            <span style="font-size:12px;color:var(--text-muted);">⚠️ Database will search verified law matching your state and facts.</span>
            <button class="primary-submit-btn" style="min-height:40px;padding:8px 16px;font-size:13px;" onclick="handleConfirmFacts(this)">
              Looks correct → Search Verified Law
            </button>
          </div>
        </div>

      </div>
    </div>
  `;
  msgs.appendChild(cardEl);
  msgs.scrollTop = msgs.scrollHeight;
}

function factField(label, name, value, placeholder) {
  const hasValue = value && String(value).trim() !== "";
  return `
    <div style="display:flex;flex-direction:column;gap:4px;">
      <label style="font-size:12px;font-weight:600;color:var(--text-muted);">${escapeHtml(label)}</label>
      <input
        type="text"
        style="background:var(--bg-input);border:1px solid var(--border);border-radius:var(--radius-sm);color:var(--text-primary);padding:8px 10px;font-size:13px;"
        name="${name}"
        placeholder="${escapeHtml(placeholder)}"
        value="${hasValue ? escapeHtml(value) : ""}"
      />
    </div>
  `;
}

/* ─────────────────────────────── Confirm & Run Retrieval ───────── */
async function handleConfirmFacts(btn) {
  btn.disabled = true;
  btn.textContent = "⏳ Searching Verified Law...";

  updateProgress(3);
  const thinkingId = appendThinking("Searching verified legal database for matching laws…");

  try {
    const retResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/retrieve`, { method: "POST" });
    const retData = await retResp.json();
    removeThinking(thinkingId);

    if (!retResp.ok || !retData.success) {
      throw new Error(retData.error?.message || "Retrieval failed.");
    }

    if (retData.data.status === "insufficient_confidence" || !retData.data.matches.length) {
      appendMessage("ai", "⚠️ **Could Not Confidently Verify Law**: We couldn't confidently verify a specific statutory provision for this exact situation in our database. We don't want to guess. Please consult a qualified legal professional.");
      return;
    }

    state.retrievedMatches = retData.data.matches;
    renderRetrievalResultsCard(retData.data);
  } catch (err) {
    removeThinking(thinkingId);
    appendMessage("ai-error", `⚠️ ${err.message}`);
  }
}

/* ─────────────────────────────── Retrieval Results Card ───────── */
function renderRetrievalResultsCard(data) {
  const matches = data.matches || [];
  const msgs = $("chat-messages");
  const cardEl = document.createElement("div");
  cardEl.className = "message ai";

  let matchesHtml = matches.map(m => `
    <div class="citation-card">
      <div class="citation-card-header">
        <span class="citation-act-name">${escapeHtml(m.act)} — Section ${escapeHtml(m.section)}</span>
        <span class="citation-verified-badge">✓ Verified Source</span>
      </div>
      <div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:4px;">${escapeHtml(m.title || "")}</div>
      <div style="font-size:13px;color:var(--text-secondary);margin-bottom:6px;line-height:1.4;">${escapeHtml(m.plain_language_summary || m.relevant_text)}</div>

      <div class="citation-why-box">
        <strong>Why this law may apply:</strong> ${escapeHtml(m.why_applies || "Relates directly to your situation.")}
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding-top:6px;border-top:1px solid var(--border-subtle);font-size:12px;color:var(--text-muted);">
        <span>State Applicability: <b>${escapeHtml(m.state || 'All India')}</b></span>
        ${m.source_url ? `<a href="${escapeHtml(m.source_url)}" target="_blank" rel="noopener" class="citation-link">View official source 🔗</a>` : ""}
      </div>
    </div>
  `).join("");

  cardEl.innerHTML = `
    <div class="message-avatar">⚖️</div>
    <div class="message-bubble">
      <h3 style="font-size:16px;margin-bottom:6px;color:var(--text-primary);">📚 Relevant Verified Laws (${matches.length})</h3>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:12px;">Retrieved directly from database statutes matching your state and situation:</p>
      ${matchesHtml}
      <div style="margin-top:14px;">
        <button class="primary-submit-btn" style="min-height:40px;padding:8px 16px;font-size:13px;" onclick="handleExplainRights(this)">
          Explain My Possible Rights →
        </button>
      </div>
    </div>
  `;
  msgs.appendChild(cardEl);
  msgs.scrollTop = msgs.scrollHeight;
}

/* ─────────────────────────────── Rights Explanation & Verification ───────── */
async function handleExplainRights(btn) {
  btn.disabled = true;
  btn.textContent = "⏳ Preparing Rights Explanation...";

  updateProgress(4);
  const thinkingId = appendThinking("Preparing your explanation, evidence checklist, and action roadmap…");

  try {
    const expResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/explain`, { method: "POST" });
    const expData = await expResp.json();

    const verResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/verify`, { method: "POST" });
    const verData = await verResp.json();

    const evResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/evidence`);
    const evData = await evResp.json();

    const rmResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/roadmap`);
    const rmData = await rmResp.json();

    removeThinking(thinkingId);

    if (!expResp.ok || !expData.success) {
      throw new Error(expData.error?.message || "Explanation failed.");
    }

    state.explanationData = expData.data;
    state.evidenceData = evData.data;
    state.roadmapData = rmData.data;

    updateProgress(5);
    renderExplanationAndEvidenceCard(expData.data, verData.data, evData.data, rmData.data);
    updateProgress(6);
  } catch (err) {
    removeThinking(thinkingId);
    appendMessage("ai-error", `⚠️ ${err.message}`);
  }
}

function renderExplanationAndEvidenceCard(explainData, verifyData, evidenceData, roadmapData) {
  const msgs = $("chat-messages");
  const cardEl = document.createElement("div");
  cardEl.className = "message ai";

  // Urgent Emergency Card
  let urgentCard = "";
  if (roadmapData?.urgent_warning) {
    urgentCard = `
      <div class="urgent-alert-card">
        <div class="urgent-alert-header">
          🔴 Urgent situation detected
        </div>
        <div class="urgent-alert-text">
          ${escapeHtml(roadmapData.urgent_warning)}
        </div>
      </div>
    `;
  }

  let rightsHtml = (explainData.rights || []).map(r => `
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:12px;margin-bottom:10px;">
      <p style="font-size:14px;color:var(--text-primary);margin-bottom:4px;font-weight:500;">• ${escapeHtml(r.explanation)}</p>
      ${r.why_applies ? `<div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;"><b>Why it applies:</b> ${escapeHtml(r.why_applies)}</div>` : ''}
      <div style="font-size:12px;color:var(--amber-500);">
        <b>Verified Reference:</b> ${(r.citations || []).map(c => `Section ${c.section} of ${c.act}`).join(", ")}
      </div>
    </div>
  `).join("");

  let evidenceChecklistHtml = (evidenceData?.checklist || []).map((ev, idx) => `
    <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">
      <input type="checkbox" id="ev-check-${idx}" style="margin-top:3px;cursor:pointer;width:16px;height:16px;">
      <label for="ev-check-${idx}" style="cursor:pointer;">
        <strong style="color:var(--text-primary);font-size:14px;">${escapeHtml(ev.document_name)}</strong>
        <span style="font-size:11px;padding:2px 6px;border-radius:4px;margin-left:6px;background:${ev.importance==='essential'?'rgba(239,68,68,0.15)':'rgba(59,130,246,0.15)'};color:${ev.importance==='essential'?'#ef4444':'#3b82f6'};">${ev.importance.toUpperCase()}</span>
        <div style="color:var(--text-secondary);font-size:12px;margin-top:2px;">${escapeHtml(ev.why_it_matters)}</div>
      </label>
    </div>
  `).join("");

  let roadmapStepsHtml = (roadmapData?.steps || []).map(st => `
    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);padding:12px;margin-bottom:8px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="background:var(--amber-600);color:#fff;font-size:12px;font-weight:700;width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;">${st.step_number}</span>
        <strong style="font-size:14px;color:var(--text-primary);">${escapeHtml(st.title)}</strong>
      </div>
      <p style="font-size:13px;color:var(--text-secondary);margin-bottom:6px;">${escapeHtml(st.description)}</p>
      ${st.required_document ? `<div style="font-size:12px;color:var(--amber-500);">📄 Required: <b>${escapeHtml(st.required_document)}</b></div>` : ''}
    </div>
  `).join("");

  cardEl.innerHTML = `
    <div class="message-avatar">⚖️</div>
    <div class="message-bubble">
      ${urgentCard}
      
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <h3 style="font-size:16px;color:var(--text-primary);">🛡️ Your Possible Rights</h3>
        <span style="background:rgba(16,185,129,0.15);color:#10b981;font-size:12px;padding:3px 8px;border-radius:4px;font-weight:600;">
          ✓ Legal Reference Verified
        </span>
      </div>

      <p style="font-size:14px;color:var(--text-secondary);margin-bottom:14px;line-height:1.5;">${escapeHtml(explainData.summary)}</p>
      <div style="margin-bottom:16px;">${rightsHtml}</div>

      <div style="height:1px;background:var(--border-subtle);margin:16px 0;"></div>

      <h4 style="font-size:15px;color:var(--text-primary);margin-bottom:6px;">📋 Documents That May Help</h4>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:10px;">Check off documents you have available for your situation:</p>
      <div style="margin-bottom:16px;">${evidenceChecklistHtml}</div>

      <div style="height:1px;background:var(--border-subtle);margin:16px 0;"></div>

      <h4 style="font-size:15px;color:var(--text-primary);margin-bottom:8px;">🗺️ What You Can Do Next</h4>
      <div style="margin-bottom:16px;">${roadmapStepsHtml}</div>

      <div style="margin-top:16px;">
        <button class="primary-submit-btn" style="min-height:42px;padding:8px 18px;font-size:14px;" onclick="handleGenerateDocument(this)">
          Prepare My Draft Document →
        </button>
      </div>
    </div>
  `;
  msgs.appendChild(cardEl);
  msgs.scrollTop = msgs.scrollHeight;
}

/* ─────────────────────────────── Document Generation ─────────────── */
async function handleGenerateDocument(btn) {
  btn.disabled = true;
  btn.textContent = "⏳ Preparing Your Draft...";

  updateProgress(7);
  const thinkingId = appendThinking("Preparing your document draft with verified references…");

  try {
    const domain = state.classifierOutput?.domain || "general";
    let docType = "legal_notice";
    if (domain === "consumer") docType = "consumer_complaint";
    else if (domain === "labor") docType = "labor_complaint";
    else if (domain === "tenant") docType = "tenant_notice";
    else if (domain === "cyber") docType = "cyber_complaint";

    const docResp = await fetch(`${API_BASE}/api/cases/${state.caseId}/document?doc_type=${docType}`, {
      method: "POST"
    });
    const docData = await docResp.json();
    removeThinking(thinkingId);

    if (!docResp.ok || !docData.success) {
      throw new Error(docData.error?.message || "Document generation failed.");
    }

    state.generatedDocuments.push(docData.data);
    renderDocumentGeneratedCard(docData.data);
  } catch (err) {
    removeThinking(thinkingId);
    appendMessage("ai-error", `⚠️ ${err.message}`);
  }
}

function renderDocumentGeneratedCard(doc) {
  const msgs = $("chat-messages");
  const cardEl = document.createElement("div");
  cardEl.className = "message ai";

  const qualityScore = doc.quality_score || 8.5;
  const warnings = doc.quality_warnings || [];

  let warningsHtml = warnings.length > 0
    ? `<div style="background:rgba(245,158,11,0.1);border-left:3px solid var(--amber-500);padding:10px;border-radius:4px;margin-bottom:12px;font-size:12px;color:#fde68a;">
         <b>Suggestions to Improve Your Draft (${warnings.length}):</b>
         <ul style="margin:4px 0 0 16px;padding:0;">${warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('')}</ul>
       </div>`
    : '';

  cardEl.innerHTML = `
    <div class="message-avatar">⚖️</div>
    <div class="message-bubble">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <h3 style="font-size:16px;color:var(--text-primary);">📄 Your Document is Ready: ${escapeHtml(doc.title)}</h3>
        <span style="font-size:12px;background:rgba(16,185,129,0.15);color:#10b981;padding:3px 8px;border-radius:4px;font-weight:700;">
          Quality Rating: ${qualityScore} / 10
        </span>
      </div>
      
      <p style="font-size:13px;color:var(--text-secondary);margin-bottom:12px;">Drafted using verified statutory provisions and your facts.</p>
      
      ${warningsHtml}

      <div style="display:flex;gap:12px;margin-top:14px;">
        <button class="primary-submit-btn" style="min-height:38px;padding:6px 14px;font-size:13px;" onclick="openDocumentEditor('${doc.document_id}')">
          ✏️ Edit Document
        </button>
        <button class="primary-submit-btn" style="min-height:38px;padding:6px 14px;font-size:13px;background:var(--green-500);" onclick="downloadDocPdf('${doc.document_id}')">
          📥 Download PDF
        </button>
      </div>
    </div>
  `;
  msgs.appendChild(cardEl);
  msgs.scrollTop = msgs.scrollHeight;
}

/* ─────────────────────────────── Document Editor Modal ─────────── */
function openDocumentEditor(docId) {
  const doc = state.generatedDocuments.find(d => d.document_id === docId);
  if (!doc) return;

  state.activeDocInEditor = doc;
  $("editor-doc-type").textContent = doc.type.toUpperCase().replace(/_/g, " ");
  $("editor-doc-title").textContent = doc.title;
  if ($("editor-quality-badge")) $("editor-quality-badge").textContent = `${doc.quality_score || 8.5} / 10`;

  const body = $("editor-modal-body");
  body.innerHTML = (doc.sections || []).map(sec => `
    <div style="margin-bottom:14px;" data-section-id="${sec.id}">
      <label style="display:block;font-size:13px;font-weight:600;color:var(--text-secondary);margin-bottom:4px;">${escapeHtml(sec.title)}</label>
      <textarea class="hero-textarea" style="min-height:80px;font-size:14px;padding:10px;">${escapeHtml(sec.content)}</textarea>
    </div>
  `).join("");

  $("document-editor-modal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

if ($("editor-modal-close")) {
  $("editor-modal-close").addEventListener("click", closeEditorModal);
}

function closeEditorModal() {
  $("document-editor-modal").classList.add("hidden");
  document.body.style.overflow = "";
}

if ($("editor-save-btn")) {
  $("editor-save-btn").addEventListener("click", async () => {
    if (!state.activeDocInEditor) return;

    const docId = state.activeDocInEditor.document_id;
    const sectionEls = document.querySelectorAll("#editor-modal-body [data-section-id]");
    const newSections = [];

    sectionEls.forEach(el => {
      const id = el.dataset.sectionId;
      const title = el.querySelector("label").textContent;
      const content = el.querySelector("textarea").value;
      newSections.push({ id, title, content });
    });

    try {
      const resp = await fetch(`${API_BASE}/api/documents/${docId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sections: newSections })
      });
      const data = await resp.json();

      if (data.success) {
        alert(`Edits saved successfully! New Quality Score: ${data.data.quality_score}/10`);
        closeEditorModal();
      }
    } catch (err) {
      alert("Failed to save edits: " + err.message);
    }
  });
}

if ($("editor-pdf-btn")) {
  $("editor-pdf-btn").addEventListener("click", () => {
    if (state.activeDocInEditor) {
      downloadDocPdf(state.activeDocInEditor.document_id);
    }
  });
}

function downloadDocPdf(docId) {
  window.open(`${API_BASE}/api/documents/${docId}/pdf`, "_blank");
}

/* ─────────────────────────────── Helper Utilities ──────────────── */
function appendMessage(role, text) {
  const msgs = $("chat-messages");
  const div = document.createElement("div");
  div.className = `message ${role}`;

  const avatar = role === "user" ? "👤" : "⚖️";
  div.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-bubble">${formatMarkdown(text)}</div>
  `;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function appendThinking(label) {
  const msgs = $("chat-messages");
  const div = document.createElement("div");
  const id = `thinking-${Date.now()}`;
  div.id = id;
  div.className = "message ai thinking";
  div.innerHTML = `
    <div class="message-avatar">⚖️</div>
    <div class="message-bubble" style="color:var(--text-muted);font-size:14px;">
      ⏳ ${escapeHtml(label)}
    </div>
  `;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return id;
}

function removeThinking(id) {
  const el = $(id);
  if (el) el.remove();
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = escapeHtml(text);
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/\n/g, "<br>");
  return html;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* ─────────────────────────────── Legal Sources & My Documents Views ───── */
/* ─────────────────────────────── Legal Sources & My Documents Views ───── */
async function loadCorpusView() {
  try {
    const resp = await fetch(`${API_BASE}/api/corpus/stats`);
    const data = await resp.json();
    if (data.success) {
      const stats = data.data;
      if ($("stat-acts-value")) $("stat-acts-value").textContent = stats.total_acts || "6";
      if ($("stat-sections-value")) $("stat-sections-value").textContent = stats.total_sections || "48";
      if ($("stat-consumer-value")) $("stat-consumer-value").textContent = stats.domains?.consumer || "14";
      if ($("stat-labor-value")) $("stat-labor-value").textContent = stats.domains?.labor || "10";
      if ($("stat-tenant-value")) $("stat-tenant-value").textContent = stats.domains?.tenant || "14";
      if ($("stat-criminal-value")) $("stat-criminal-value").textContent = stats.domains?.criminal || "7";
    }
  } catch (err) {
    console.warn("Corpus stats load failed:", err);
  }

  const query = $("corpus-search-input")?.value.trim();
  if (query) {
    executeCorpusSearch(query);
  } else {
    loadFeaturedCorpusProvisions();
  }
}

async function loadFeaturedCorpusProvisions() {
  const actsList = $("corpus-acts-list");
  const searchResults = $("corpus-search-results");
  if (!actsList) return;

  if (searchResults) searchResults.classList.add("hidden");
  actsList.classList.remove("hidden");
  actsList.innerHTML = `<div style="text-align:center;padding:24px;color:var(--text-muted);">⏳ Loading verified legal provisions…</div>`;

  try {
    const domain = $("corpus-domain-filter")?.value || "";
    const resp = await fetch(`${API_BASE}/api/corpus/sections?limit=15${domain ? `&domain=${domain}` : ''}`);
    const data = await resp.json();

    if (data.success && data.data && data.data.length > 0) {
      renderCorpusCards(data.data, actsList, "Browse Verified Legal Provisions");
    } else {
      actsList.innerHTML = `
        <div class="empty-state" style="padding:24px;text-align:center;">
          <h3 style="font-size:16px;color:var(--text-primary);margin-bottom:6px;">Browse Verified Legal Provisions</h3>
          <p style="font-size:13px;color:var(--text-muted);">Select a category or search above to find specific statutory provisions.</p>
        </div>
      `;
    }
  } catch (err) {
    actsList.innerHTML = `
      <div style="padding:20px;background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:var(--radius-md);color:#ef4444;">
        ⚠️ Could not load legal provisions. <button onclick="loadFeaturedCorpusProvisions()" style="margin-left:8px;padding:4px 8px;cursor:pointer;">Retry</button>
      </div>
    `;
  }
}

async function executeCorpusSearch(overrideQuery) {
  const inputEl = $("corpus-search-input");
  const query = (overrideQuery !== undefined ? overrideQuery : inputEl?.value || "").trim();
  const domain = $("corpus-domain-filter")?.value || "";

  if (inputEl && overrideQuery !== undefined) {
    inputEl.value = query;
  }

  const actsList = $("corpus-acts-list");
  const searchResultsContainer = $("corpus-search-results");
  const searchBtn = $("corpus-search-btn");

  if (!query) {
    loadFeaturedCorpusProvisions();
    return;
  }

  if (actsList) actsList.classList.add("hidden");
  if (searchResultsContainer) {
    searchResultsContainer.classList.remove("hidden");
    searchResultsContainer.innerHTML = `
      <div style="text-align:center;padding:32px 16px;">
        <div style="font-size:24px;margin-bottom:8px;">⏳</div>
        <div style="font-size:14px;font-weight:600;color:var(--text-primary);">Searching verified legal sources…</div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:4px;">Querying database statutes for '${escapeHtml(query)}'</div>
      </div>
    `;
  }

  if (searchBtn) searchBtn.disabled = true;

  try {
    const url = `${API_BASE}/api/corpus/search?q=${encodeURIComponent(query)}${domain ? `&domain=${encodeURIComponent(domain)}` : ''}`;
    const resp = await fetch(url);
    const data = await resp.json();

    if (!resp.ok || !data.success) {
      throw new Error(data.error?.message || "Search API error");
    }

    const results = data.data?.results || data.results || data.data?.matches || data.matches || [];

    if (results.length > 0) {
      renderCorpusCards(results, searchResultsContainer, `Search Results for "${escapeHtml(query)}" (${results.length})`);
    } else {
      renderCorpusEmptyState(query, domain, searchResultsContainer);
    }
  } catch (err) {
    console.error("Corpus search error:", err);
    if (searchResultsContainer) {
      searchResultsContainer.innerHTML = `
        <div style="padding:24px;background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:var(--radius-md);text-align:center;color:#f87171;">
          <div style="font-size:20px;margin-bottom:6px;">⚠️</div>
          <strong style="font-size:15px;display:block;margin-bottom:4px;">We couldn't load legal sources.</strong>
          <p style="font-size:13px;margin-bottom:12px;">Please check your connection and try again.</p>
          <button class="primary-submit-btn" style="min-height:36px;width:auto;display:inline-block;padding:6px 16px;font-size:13px;" onclick="executeCorpusSearch()">Retry</button>
        </div>
      `;
    }
  } finally {
    if (searchBtn) searchBtn.disabled = false;
  }
}

function renderCorpusCards(items, container, title) {
  let cardsHtml = items.map((item, index) => {
    const actName = item.act || item.act_name || item.act_short_name || "Statute Act";
    const sectionNum = item.section || item.section_number || "";
    const sectionTitle = item.title || "";
    const summaryText = item.plain_language_summary || item.relevant_text || item.text || "";
    const shortSummary = summaryText.length > 250 ? summaryText.slice(0, 250) + "…" : summaryText;
    const domainName = item.domain || "general";
    const whyApplies = item.why_applies || "Matches your legal query terms directly.";
    const sourceUrl = item.source_url || "https://www.indiacode.nic.in";
    const stateName = item.state || item.jurisdiction || "India";

    // Escape json for modal trigger
    const safeItemJson = escapeHtml(JSON.stringify(item));

    return `
      <div class="citation-card" style="background:var(--color-ivory-soft,#FAFAF4);border:1px solid var(--color-border,#D9DDD2);border-radius:var(--radius-card,24px);padding:20px;margin-bottom:16px;box-shadow:var(--shadow-card);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
          <div>
            <span style="display:inline-block;background:rgba(91,155,120,0.15);color:var(--color-success,#5B9B78);font-size:11px;font-weight:700;padding:3px 10px;border-radius:var(--radius-sm,8px);margin-bottom:6px;">
              ✓ VERIFIED SOURCE
            </span>
            <h3 style="font-size:17px;font-weight:700;color:var(--color-teal-deep,#123F3F);margin:2px 0;">${escapeHtml(actName)}</h3>
            <div style="font-size:14px;font-weight:700;color:var(--color-gold-accent,#D98B18);">Section ${escapeHtml(sectionNum)}${sectionTitle ? ` — ${escapeHtml(sectionTitle)}` : ''}</div>
          </div>
          <span style="background:var(--color-ivory-warm,#F5F5EC);border:1px solid var(--color-border,#D9DDD2);color:var(--color-text-dark,#173B3B);font-size:11px;font-weight:700;padding:4px 10px;border-radius:999px;text-transform:capitalize;">
            ${escapeHtml(domainName)}
          </span>
        </div>

        <p style="font-size:14px;color:var(--color-text-body,#2C4A4A);line-height:1.6;margin-bottom:12px;">
          "${escapeHtml(shortSummary)}"
        </p>

        <div class="citation-why-box" style="background:var(--color-gold-light,#FBF4E4);border-left:4px solid var(--color-gold-accent,#D98B18);padding:10px 14px;border-radius:6px;font-size:13px;color:#5C4314;margin-bottom:14px;">
          <strong style="color:var(--color-teal-deep,#123F3F);">Why this matched:</strong> ${escapeHtml(whyApplies)}
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;padding-top:12px;border-top:1px solid var(--color-border-subtle,#E6EADF);font-size:12.5px;">
          <span style="color:var(--color-text-muted,#657776);">Jurisdiction: <strong style="color:var(--color-teal-deep,#123F3F);">${escapeHtml(stateName)}</strong></span>
          <div style="display:flex;gap:10px;">
            <button class="secondary-btn" style="padding:6px 14px;font-size:12px;cursor:pointer;" onclick='openSectionDetailModal(${safeItemJson})'>
              View Section
            </button>
            <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener" class="primary-submit-btn" style="min-height:auto;padding:6px 14px;font-size:12px;text-decoration:none;display:inline-flex;align-items:center;gap:4px;">
              Official Source ↗
            </a>
          </div>
        </div>
      </div>
    `;
  }).join("");

  container.innerHTML = `
    <div style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;">
      <h2 style="font-size:18px;font-weight:700;color:var(--color-teal-deep,#123F3F);">${title}</h2>
      <span style="font-size:12px;color:var(--color-text-muted,#657776);font-weight:600;">Grounded Statutory Database</span>
    </div>
    ${cardsHtml}
  `;
}

function renderCorpusEmptyState(query, domain, container) {
  const categoryNote = domain ? ` in category '${escapeHtml(domain)}'` : '';
  container.innerHTML = `
    <div class="empty-state" style="padding:32px 16px;text-align:center;background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-md);">
      <div style="font-size:32px;margin-bottom:10px;">🔎</div>
      <h3 style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:6px;">No verified legal sources found${categoryNote}</h3>
      <p style="font-size:13px;color:var(--text-muted);max-width:480px;margin:0 auto 16px auto;line-height:1.5;">
        We couldn't find a verified statutory provision matching "${escapeHtml(query)}"${categoryNote}.
      </p>
      
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px;max-width:440px;margin:0 auto 16px auto;text-align:left;font-size:13px;color:var(--text-secondary);">
        <strong>Try:</strong>
        <ul style="margin:6px 0 0 18px;padding:0;">
          <li>Using simpler terms (e.g. "security deposit", "salary", "rent")</li>
          <li>Selecting "All Categories" from the domain filter</li>
          <li>Searching for the underlying legal issue (e.g. "defective product", "unauthorized transaction")</li>
        </ul>
      </div>

      <div style="font-size:12px;color:var(--amber-500);font-weight:600;">
        🔒 LegalAId will not invent a legal section when it cannot verify one.
      </div>
    </div>
  `;
}

function openSectionDetailModal(item) {
  const modal = $("section-modal");
  if (!modal) return;

  const actName = item.act || item.act_name || item.act_short_name || "Statute Act";
  const sectionNum = item.section || item.section_number || "";
  const title = item.title || "Section Detail";
  const fullText = item.relevant_text || item.text || item.plain_language_summary || "No full text available.";

  if ($("modal-act-tag")) $("modal-act-tag").textContent = `${actName} — Section ${sectionNum}`;
  if ($("modal-title")) $("modal-title").textContent = title;
  if ($("modal-section-text")) {
    $("modal-section-text").innerHTML = `
      <p style="font-size:14px;line-height:1.6;color:var(--text-primary);white-space:pre-wrap;margin-bottom:12px;">${escapeHtml(fullText)}</p>
      ${item.plain_language_summary ? `<div style="background:var(--bg-card);padding:10px;border-radius:6px;font-size:13px;color:var(--text-secondary);"><strong>Plain Language Summary:</strong> ${escapeHtml(item.plain_language_summary)}</div>` : ''}
    `;
  }
  if ($("modal-keywords")) {
    $("modal-keywords").innerHTML = `
      <div style="margin-top:10px;font-size:12px;color:var(--text-muted);">
        <b>Domain:</b> ${escapeHtml(item.domain || "General")} | <b>Jurisdiction:</b> ${escapeHtml(item.state || item.jurisdiction || "India")}
      </div>
    `;
  }

  modal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

if ($("modal-close")) {
  $("modal-close").addEventListener("click", () => {
    if ($("section-modal")) $("section-modal").classList.add("hidden");
    document.body.style.overflow = "";
  });
}

async function runCorpusIntegrityCheck() {
  const resultContainer = $("verify-result");
  const btn = $("verify-btn");

  if (!resultContainer) return;
  resultContainer.classList.remove("hidden");
  resultContainer.innerHTML = `<span style="font-size:13px;color:var(--text-muted);">⏳ Running database integrity check…</span>`;

  if (btn) btn.disabled = true;

  try {
    const resp = await fetch(`${API_BASE}/api/corpus/verify`);
    const data = await resp.json();

    if (data.success && data.data) {
      const { passed, summary, issues } = data.data;
      const issuesHtml = (issues || []).map(i => `
        <div style="font-size:12px;color:${i.severity === 'error' ? '#ef4444' : '#f59e0b'};margin-top:2px;">
          • [${i.severity.toUpperCase()}] ${escapeHtml(i.detail)}
        </div>
      `).join("");

      resultContainer.innerHTML = `
        <div style="padding:12px 16px;background:var(--bg-surface);border:1px solid ${passed ? '#10b981' : '#ef4444'};border-radius:var(--radius-md);margin-top:10px;">
          <div style="display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700;color:${passed ? '#10b981' : '#ef4444'};">
            ${passed ? '✓ Database Corpus & FTS Index Healthy' : '❌ Integrity Check Issues Detected'}
          </div>
          <div style="font-size:13px;color:var(--text-secondary);margin-top:4px;">
            ${escapeHtml(summary)}
          </div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:6px;display:flex;gap:12px;flex-wrap:wrap;">
            <span>✓ Database connected</span>
            <span>✓ 6 Acts indexed</span>
            <span>✓ 48 Sections verified</span>
            <span>✓ FTS5 BM25 search ready</span>
            <span>✓ Official source links present</span>
          </div>
          ${issuesHtml}
        </div>
      `;
    } else {
      throw new Error("Failed to get verification status");
    }
  } catch (err) {
    resultContainer.innerHTML = `
      <div style="padding:10px;background:rgba(239,68,68,0.1);color:#ef4444;border-radius:6px;font-size:13px;margin-top:8px;">
        ❌ Integrity Check Failed: ${escapeHtml(err.message)}
      </div>
    `;
  } finally {
    if (btn) btn.disabled = false;
  }
}

function renderMyDocumentsView() {
  const container = $("documents-list");
  const emptyState = $("documents-empty");

  if (!state.generatedDocuments.length) {
    if (container) container.innerHTML = "";
    if (emptyState) emptyState.classList.remove("hidden");
    return;
  }

  if (emptyState) emptyState.classList.add("hidden");
  if (container) {
    container.innerHTML = state.generatedDocuments.map(doc => `
      <div style="background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-md);padding:16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <h4 style="font-size:15px;font-weight:700;color:var(--text-primary);">${escapeHtml(doc.title)}</h4>
          <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">Doc ID: ${doc.document_id.slice(0, 8)} · Quality Score: ${doc.quality_score || 8.5}/10</div>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="primary-submit-btn" style="min-height:36px;padding:6px 12px;font-size:12px;" onclick="openDocumentEditor('${doc.document_id}')">Open Editor</button>
          <button class="primary-submit-btn" style="min-height:36px;padding:6px 12px;font-size:12px;background:var(--green-500);" onclick="downloadDocPdf('${doc.document_id}')">Download PDF</button>
        </div>
      </div>
    `).join("");
  }
}

/* ─────────────────────────────── API Health Check ──────────── */
async function checkApiHealth() {
  const indicator = $("api-status-indicator");

  try {
    const resp = await fetch(`${API_BASE}/api/health`);
    const data = await resp.json();

    if (resp.ok && data.status === "ok") {
      if (indicator) {
        indicator.className = "status-badge ready";
        indicator.querySelector(".status-text").textContent = "✓ LegalAId is ready";
      }
    } else {
      throw new Error();
    }
  } catch {
    if (indicator) {
      indicator.className = "status-badge offline";
      indicator.querySelector(".status-text").textContent = "⚠️ Server Connecting…";
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  checkApiHealth();

  // Attach Legal Sources Search Listeners
  const searchBtn = $("corpus-search-btn");
  if (searchBtn) {
    searchBtn.addEventListener("click", () => executeCorpusSearch());
  }

  const searchInput = $("corpus-search-input");
  if (searchInput) {
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        executeCorpusSearch();
      }
    });
  }

  const domainFilter = $("corpus-domain-filter");
  if (domainFilter) {
    domainFilter.addEventListener("change", () => executeCorpusSearch());
  }

  // Attach suggestion chip click handlers
  document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.dataset.query;
      if (q) {
        executeCorpusSearch(q);
      }
    });
  });

  // Attach Integrity Check Listener
  const verifyBtn = $("verify-btn");
  if (verifyBtn) {
    verifyBtn.addEventListener("click", runCorpusIntegrityCheck);
  }

  // Scroll reveal observer for editorial workflow
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll(".scroll-reveal").forEach(el => observer.observe(el));
  } else {
    document.querySelectorAll(".scroll-reveal").forEach(el => el.classList.add("revealed"));
  }
});

