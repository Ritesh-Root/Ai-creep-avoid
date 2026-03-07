/* SmartShield AI – Frontend Logic */

(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  let currentSessionId = generateSessionId();
  let messageLog = [];
  let selectedFile = null;

  // ---------------------------------------------------------------------------
  // DOM refs
  // ---------------------------------------------------------------------------
  const $ = (id) => document.getElementById(id);
  const sessionIdInput = $('session-id');
  const senderIdInput = $('sender-id');
  const apiBaseInput = $('api-base');
  const textInput = $('text-input');
  const fileInput = $('file-input');
  const uploadZone = $('upload-zone');
  const imagePreviewContainer = $('image-preview-container');
  const imagePreview = $('image-preview');
  const imageBlurOverlay = $('image-blur-overlay');
  const btnAnalyzeText = $('btn-analyze-text');
  const btnAnalyzeImage = $('btn-analyze-image');
  const btnFloodDemo = $('btn-flood-demo');
  const btnNewSession = $('btn-new-session');
  const btnClearSession = $('btn-clear-session');
  const resultsPanel = $('results-panel');
  const messageLogEl = $('message-log');

  // ---------------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------------
  sessionIdInput.placeholder = currentSessionId;

  // Sample buttons
  document.querySelectorAll('.sample-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      textInput.value = btn.dataset.text;
    });
  });

  // File upload
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    selectedFile = file;
    const url = URL.createObjectURL(file);
    imagePreview.src = url;
    imageBlurOverlay.style.display = 'none';
    imagePreviewContainer.style.display = 'block';
    uploadZone.querySelector('p').textContent = `📎 ${file.name}`;
    btnAnalyzeImage.disabled = false;
  });

  uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.style.borderColor = 'var(--primary)'; });
  uploadZone.addEventListener('dragleave', () => { uploadZone.style.borderColor = ''; });
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = '';
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      fileInput.files = e.dataTransfer.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });

  btnAnalyzeText.addEventListener('click', () => analyzeText());
  btnAnalyzeImage.addEventListener('click', () => analyzeImage());
  btnFloodDemo.addEventListener('click', () => runFloodDemo());
  btnNewSession.addEventListener('click', () => {
    currentSessionId = generateSessionId();
    sessionIdInput.placeholder = currentSessionId;
    sessionIdInput.value = '';
    messageLog = [];
    renderLog();
    resultsPanel.style.display = 'none';
  });
  btnClearSession.addEventListener('click', clearSession);

  // ---------------------------------------------------------------------------
  // API helpers
  // ---------------------------------------------------------------------------
  function getApiBase() { return (apiBaseInput.value || 'http://localhost:8000/api/v1').replace(/\/$/, ''); }
  function getSessionId() { return sessionIdInput.value.trim() || currentSessionId; }
  function getSenderId() { return senderIdInput.value.trim() || 'demo_sender'; }

  async function analyzeText(overrideText = null) {
    const content = overrideText !== null ? overrideText : textInput.value.trim();
    if (!content) return showError('Please enter a message to analyze.');
    setLoading(btnAnalyzeText, true);

    try {
      const res = await fetch(`${getApiBase()}/analyze/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          sender_id: getSenderId(),
          session_id: getSessionId(),
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      displayResults(data, 'text', content);
    } catch (err) {
      showError(`Failed to reach API: ${err.message}\n\nMake sure the backend is running:\ncd backend && uvicorn app.main:app --reload`);
    } finally {
      setLoading(btnAnalyzeText, false);
    }
  }

  async function analyzeImage() {
    if (!selectedFile) return showError('Please select an image first.');
    setLoading(btnAnalyzeImage, true);
    imageBlurOverlay.style.display = 'none';

    const form = new FormData();
    form.append('session_id', getSessionId());
    form.append('sender_id', getSenderId());
    form.append('file', selectedFile);

    try {
      const res = await fetch(`${getApiBase()}/analyze/image`, { method: 'POST', body: form });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      displayResults(data, 'image', selectedFile.name);

      // Apply blur/block to image preview
      if (data.disposition === 'BLUR' || data.disposition === 'BLOCK') {
        imageBlurOverlay.style.display = 'flex';
        imagePreview.style.filter = 'blur(20px)';
      } else {
        imagePreview.style.filter = 'none';
      }
    } catch (err) {
      showError(`Failed to reach API: ${err.message}`);
    } finally {
      setLoading(btnAnalyzeImage, false);
    }
  }

  async function runFloodDemo() {
    setLoading(btnFloodDemo, true, '⚡ Flooding…');
    const messages = [
      'Hey', 'Are you there?', 'Hello?', "Why aren't you replying?",
      "I'm waiting", 'Answer me', "Don't ignore me", 'I KNOW YOU ARE THERE',
      "You can't hide", "I'll find you",
    ];
    for (const msg of messages) {
      await analyzeText(msg);
      await sleep(300);
    }
    setLoading(btnFloodDemo, false, '⚡ Flood Demo (10x)');
  }

  async function clearSession() {
    const sid = getSessionId();
    try {
      await fetch(`${getApiBase()}/session/${encodeURIComponent(sid)}`, { method: 'DELETE' });
    } catch (_) { /* ignore */ }
    messageLog = [];
    renderLog();
    resultsPanel.style.display = 'none';
    showToast(`Session '${sid}' data cleared.`);
  }

  // ---------------------------------------------------------------------------
  // Display helpers
  // ---------------------------------------------------------------------------
  function displayResults(data, type, contentPreview) {
    resultsPanel.style.display = 'block';
    resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    const score = data.creep_score;
    const disposition = data.disposition;

    // Score circle
    const circle = $('score-circle');
    $('score-value').textContent = score.toFixed(2);
    circle.className = 'creep-score-circle ' + dispositionClass(disposition) + '-circle';
    circle.style.background = dispositionBg(disposition);

    // Disposition badge
    const badge = $('disposition-badge');
    badge.textContent = disposition;
    badge.className = 'disposition-badge ' + dispositionClass(disposition);

    // Progress bars
    setBar('text-bar', 'text-score-val', data.text_score);
    setBar('image-bar', 'image-score-val', data.image_score);
    setBar('behavior-bar', 'behavior-score-val', data.behavior_score);
    colorBar('text-bar', data.text_score);
    colorBar('image-bar', data.image_score);
    colorBar('behavior-bar', data.behavior_score);

    // Reasons
    const reasonsSection = $('reasons-section');
    const reasonsList = $('reasons-list');
    if (data.reasons && data.reasons.length > 0) {
      reasonsList.innerHTML = data.reasons.map((r) => `<li>${escHtml(r)}</li>`).join('');
      reasonsSection.style.display = 'block';
    } else {
      reasonsSection.style.display = 'none';
    }

    // Categories
    const categoriesSection = $('categories-section');
    const categoriesList = $('categories-list');
    if (data.categories && data.categories.length > 0) {
      categoriesList.innerHTML = data.categories.map((c) => `<span class="tag">${escHtml(c)}</span>`).join('');
      categoriesSection.style.display = 'block';
    } else {
      categoriesSection.style.display = 'none';
    }

    // Meta
    $('session-display').textContent = `Session: ${data.session_id}`;
    $('timing-display').textContent = `${data.processing_time_ms.toFixed(1)} ms`;

    // Log
    addToLog({ disposition, score, contentPreview, type });
  }

  function setBar(barId, valId, score) {
    $(barId).style.width = `${Math.round(score * 100)}%`;
    $(valId).textContent = score.toFixed(2);
  }

  function colorBar(barId, score) {
    const el = $(barId);
    if (score >= 0.8) el.style.background = 'var(--danger)';
    else if (score >= 0.6) el.style.background = 'var(--blur-color)';
    else if (score >= 0.4) el.style.background = 'var(--warn)';
    else el.style.background = 'var(--primary)';
  }

  function dispositionClass(d) {
    return { ALLOW: 'allow', WARN: 'warn', BLUR: 'blur', BLOCK: 'block' }[d] || '';
  }

  function dispositionBg(d) {
    return { ALLOW: '#052e16', WARN: '#1c1205', BLUR: '#150e24', BLOCK: '#1c0505' }[d] || '';
  }

  function addToLog(entry) {
    messageLog.unshift(entry);
    if (messageLog.length > 50) messageLog.pop();
    renderLog();
  }

  function renderLog() {
    if (messageLog.length === 0) {
      messageLogEl.innerHTML = '<p class="log-empty">No messages analyzed yet.</p>';
      return;
    }
    messageLogEl.innerHTML = messageLog.map((e) => `
      <div class="log-entry">
        <span class="log-disposition ${dispositionClass(e.disposition)}" style="background:${dispositionBg(e.disposition)}">${e.disposition}</span>
        <span class="log-text">${e.type === 'image' ? '🖼️ ' : '💬 '}${escHtml(truncate(e.contentPreview, 60))}</span>
        <span class="log-score">${e.score.toFixed(2)}</span>
      </div>
    `).join('');
  }

  function setLoading(btn, loading, loadingText = '⏳ Analyzing…') {
    if (loading) {
      btn.disabled = true;
      btn._originalText = btn.textContent;
      btn.textContent = loadingText;
    } else {
      btn.disabled = false;
      btn.textContent = btn._originalText || btn.textContent;
    }
  }

  function showError(msg) {
    alert(`⚠️ ${msg}`);
  }

  function showToast(msg) {
    const t = document.createElement('div');
    t.textContent = msg;
    Object.assign(t.style, {
      position: 'fixed', bottom: '24px', right: '24px',
      background: '#1e293b', color: '#e2e8f0', padding: '12px 20px',
      borderRadius: '8px', fontSize: '0.875rem', zIndex: 9999,
      border: '1px solid #334155',
    });
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }

  // ---------------------------------------------------------------------------
  // Utils
  // ---------------------------------------------------------------------------
  function generateSessionId() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return 'sess_' + crypto.randomUUID().replace(/-/g, '').slice(0, 8);
    }
    const arr = new Uint8Array(4);
    crypto.getRandomValues(arr);
    return 'sess_' + Array.from(arr, (b) => b.toString(16).padStart(2, '0')).join('');
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function truncate(str, len) {
    return str.length > len ? str.slice(0, len) + '…' : str;
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }
})();
