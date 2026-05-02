(function () {
  'use strict';

  // ============================================================
  // State
  // ============================================================

  const STORAGE_KEY = 'durga-saptashati-v1';

  const defaultState = {
    chaptersRecited: {},
    angasRecited: {},
    paathProgress: {},
    sadhana: {
      total: 0,
      lastDate: null,
      streak: 0,
      monthCounts: {},
    },
    theme: null, // null = system, 'dark', 'light'
    fontSize: 'normal', // normal, large, xlarge
  };

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { ...defaultState };
      const parsed = JSON.parse(raw);
      return {
        ...defaultState,
        ...parsed,
        sadhana: { ...defaultState.sadhana, ...(parsed.sadhana || {}) },
      };
    } catch (e) {
      return { ...defaultState };
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn('Could not save state', e);
    }
  }

  let state = loadState();
  const data = window.DURGA_DATA;

  // ============================================================
  // Utilities
  // ============================================================

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $$(sel, root) {
    return Array.from((root || document).querySelectorAll(sel));
  }
  function el(tag, attrs, children) {
    const e = document.createElement(tag);
    if (attrs) {
      for (const k in attrs) {
        if (k === 'class') e.className = attrs[k];
        else if (k === 'dataset') {
          for (const dk in attrs[k]) e.dataset[dk] = attrs[k][dk];
        } else if (k.startsWith('on')) {
          e.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        } else if (k === 'html') {
          e.innerHTML = attrs[k];
        } else {
          e.setAttribute(k, attrs[k]);
        }
      }
    }
    if (children) {
      const arr = Array.isArray(children) ? children : [children];
      arr.forEach(c => {
        if (c == null) return;
        if (typeof c === 'string') e.appendChild(document.createTextNode(c));
        else e.appendChild(c);
      });
    }
    return e;
  }

  function todayKey() {
    return new Date().toISOString().slice(0, 10);
  }

  function yesterdayKey() {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    return d.toISOString().slice(0, 10);
  }

  function monthKey(dateStr) {
    return (dateStr || todayKey()).slice(0, 7);
  }


  // ============================================================
  // Routing
  // ============================================================

  const VIEWS = ['home', 'charitas', 'chapters', 'angas', 'paath', 'about'];

  function currentView() {
    const hash = window.location.hash.replace('#', '') || 'home';
    return VIEWS.includes(hash) ? hash : 'home';
  }

  function showView(name) {
    VIEWS.forEach(v => {
      const view = $(`#view-${v}`);
      if (view) view.hidden = v !== name;
    });
    $$('.nav-tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.view === name);
    });
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  window.addEventListener('hashchange', () => showView(currentView()));


  // ============================================================
  // Theme & font size
  // ============================================================

  function applyTheme() {
    if (state.theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else if (state.theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    const btn = $('#theme-toggle');
    if (btn) {
      btn.textContent = state.theme === 'dark' ? 'Dark'
                      : state.theme === 'light' ? 'Light'
                      : 'System';
    }
  }

  function cycleTheme() {
    state.theme = state.theme === null ? 'dark'
                : state.theme === 'dark' ? 'light'
                : null;
    applyTheme();
    saveState();
  }

  function applyFontSize() {
    if (state.fontSize === 'normal') {
      document.documentElement.removeAttribute('data-font-size');
    } else {
      document.documentElement.setAttribute('data-font-size', state.fontSize);
    }
  }

  function renderFontControls() {
    const root = $('#font-controls');
    if (!root) return;
    root.innerHTML = '';
    [
      { id: 'normal', label: 'A' },
      { id: 'large', label: 'A+' },
      { id: 'xlarge', label: 'A++' },
    ].forEach(opt => {
      const b = el('button', {
        class: 'font-btn' + (state.fontSize === opt.id ? ' active' : ''),
        onclick: () => {
          state.fontSize = opt.id;
          applyFontSize();
          saveState();
          renderFontControls();
        }
      }, opt.label);
      root.appendChild(b);
    });
  }


  // ============================================================
  // Sadhana Tracker
  // ============================================================

  function logRecitation() {
    const today = todayKey();
    const yesterday = yesterdayKey();

    state.sadhana.total = (state.sadhana.total || 0) + 1;

    if (state.sadhana.lastDate === today) {
      // Already logged today - just bump count
    } else if (state.sadhana.lastDate === yesterday) {
      state.sadhana.streak = (state.sadhana.streak || 0) + 1;
    } else {
      state.sadhana.streak = 1;
    }

    state.sadhana.lastDate = today;
    const m = monthKey(today);
    state.sadhana.monthCounts = state.sadhana.monthCounts || {};
    state.sadhana.monthCounts[m] = (state.sadhana.monthCounts[m] || 0) + 1;

    saveState();
    renderSadhana();
  }

  function renderSadhana() {
    const total = state.sadhana.total || 0;
    const streak = state.sadhana.streak || 0;
    const m = monthKey();
    const month = (state.sadhana.monthCounts && state.sadhana.monthCounts[m]) || 0;

    const totalEl = $('#sadhana-total');
    const streakEl = $('#sadhana-streak');
    const monthEl = $('#sadhana-month');
    const lastEl = $('#sadhana-last');

    if (totalEl) totalEl.textContent = total;
    if (streakEl) streakEl.textContent = streak;
    if (monthEl) monthEl.textContent = month;
    if (lastEl) {
      lastEl.textContent = state.sadhana.lastDate
        ? `Last: ${state.sadhana.lastDate}`
        : '';
    }

    // Stat card on home
    const statCount = $('#stat-completed');
    if (statCount) statCount.textContent = total;
  }


  // ============================================================
  // Navarna breakdown render
  // ============================================================

  function renderNavarna() {
    const root = $('#navarna-breakdown');
    if (!root || !data.navarnaMantra) return;
    root.innerHTML = '';
    data.navarnaMantra.wordBreakdown.forEach(w => {
      const card = el('div', { class: 'navarna-syllable' }, [
        el('span', { class: 'navarna-syllable-deva' }, w.word),
        el('span', { class: 'navarna-syllable-iast' }, w.iast),
        el('span', { class: 'navarna-syllable-meaning' }, w.meaning),
      ]);
      root.appendChild(card);
    });
  }


  // ============================================================
  // Charitas view
  // ============================================================

  function renderCharitas() {
    const root = $('#charitas-grid');
    if (!root) return;
    root.innerHTML = '';
    data.charitas.forEach(c => {
      const card = el('div', {
        class: 'charita-card',
        dataset: { charita: c.id }
      });

      const header = el('div', { class: 'charita-header' }, [
        el('div', { class: 'charita-name-sa' }, c.name_sa),
        el('div', { class: 'charita-name-en' }, c.name_en),
      ]);

      const meta = el('div', { class: 'charita-meta' }, [
        metaItem('Presiding Devi', c.deity_sa, true),
        metaItem('Form', c.deity, false),
        metaItem('Guna', c.guna, false),
        metaItem('Chapters', c.chapters.join(', '), false),
      ]);

      const summary = el('div', { class: 'charita-summary' }, c.summary);

      const chapters = el('div', { class: 'charita-chapters-list' });
      c.chapters.forEach(num => {
        const ch = data.chapters.find(x => x.num === num);
        if (!ch) return;
        const pill = el('a', {
          class: 'charita-chapter-pill',
          href: `#chapters`,
          onclick: () => {
            setTimeout(() => {
              const el2 = $(`#chapter-card-${num}`);
              if (el2) {
                el2.classList.add('expanded');
                el2.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }
            }, 50);
          }
        }, `Ch ${num} - ${ch.titleEn}`);
        chapters.appendChild(pill);
      });

      card.appendChild(header);
      card.appendChild(meta);
      card.appendChild(summary);
      card.appendChild(chapters);
      root.appendChild(card);
    });
  }

  function metaItem(label, value, isDeitySa) {
    return el('div', { class: 'charita-meta-item' }, [
      el('span', { class: 'charita-meta-label' }, label),
      el('span', {
        class: 'charita-meta-value' + (isDeitySa ? ' deity-sa' : '')
      }, value),
    ]);
  }


  // ============================================================
  // Chapters view
  // ============================================================

  function renderChapters() {
    const root = $('#chapters-list');
    if (!root) return;
    root.innerHTML = '';
    data.chapters.forEach(ch => {
      root.appendChild(makeChapterCard(ch));
    });
    updateChaptersProgress();
  }

  function makeChapterCard(ch) {
    const isRecited = !!state.chaptersRecited[ch.num];
    const card = el('div', {
      id: `chapter-card-${ch.num}`,
      class: 'chapter-card' + (isRecited ? ' recited' : ''),
      dataset: { charita: ch.charita }
    });

    const header = el('div', {
      class: 'chapter-header',
      onclick: () => toggleExpanded(card)
    }, [
      el('div', { class: 'chapter-title-block' }, [
        el('div', { class: 'chapter-num-row' }, `Chapter ${ch.num} • ${capitalize(ch.charita)} Charita • ${ch.deity}`),
        el('div', { class: 'chapter-name-sa' }, ch.titleSa),
        el('div', { class: 'chapter-name-en' }, ch.titleEn),
        el('div', { class: 'chapter-subtitle' }, ch.subtitle),
      ]),
      el('div', { class: 'chapter-toggle' }, '+'),
    ]);

    const body = el('div', { class: 'chapter-body' });

    const meta = el('div', { class: 'chapter-meta' }, [
      smallMetaItem('Presiding Deity', ch.deity),
      smallMetaItem('Charita', capitalize(ch.charita)),
      smallMetaItem('Verses (approx)', String(ch.versesApprox)),
      smallMetaItem('Narrator', ch.narrator),
    ]);

    body.appendChild(meta);
    body.appendChild(el('div', { class: 'chapter-summary' }, ch.summary));

    if (ch.keyHymns && ch.keyHymns.length) {
      const hymns = el('div', { class: 'key-hymns' }, [
        el('div', { class: 'key-hymns-label' }, 'Key Hymns')
      ]);
      ch.keyHymns.forEach(h => {
        hymns.appendChild(el('span', { class: 'key-hymn' }, h));
      });
      body.appendChild(hymns);
    }

    // Text tabs
    const tabs = el('div', { class: 'text-tabs' }, [
      tabBtn('Devanagari', true, (e) => switchTextTab(e, body, 'devanagari')),
      tabBtn('IAST', false, (e) => switchTextTab(e, body, 'iast')),
    ]);

    const textDeva = el('div', {
      class: 'chapter-text devanagari',
      dataset: { textType: 'devanagari' }
    }, ch.devanagari);

    const textIast = el('div', {
      class: 'chapter-text iast',
      dataset: { textType: 'iast' },
      hidden: ''
    }, ch.iast);

    body.appendChild(tabs);
    body.appendChild(textDeva);
    body.appendChild(textIast);

    // Actions
    const actions = el('div', { class: 'chapter-actions' });
    const reciteBtn = el('button', {
      class: 'recite-btn' + (isRecited ? ' recited' : ''),
      onclick: (e) => {
        e.stopPropagation();
        toggleChapterRecited(ch.num);
      }
    }, isRecited ? '✓ Recited' : 'Mark as Recited');
    actions.appendChild(reciteBtn);
    body.appendChild(actions);

    card.appendChild(header);
    card.appendChild(body);
    return card;
  }

  function tabBtn(label, isActive, onClickFn) {
    return el('button', {
      class: 'text-tab' + (isActive ? ' active' : ''),
      onclick: onClickFn
    }, label);
  }

  function smallMetaItem(label, value) {
    return el('div', { class: 'chapter-meta-item' }, [
      el('div', { class: 'chapter-meta-label' }, label),
      el('div', { class: 'chapter-meta-value' }, value),
    ]);
  }

  function switchTextTab(e, body, type) {
    e.stopPropagation();
    const tabs = body.querySelectorAll('.text-tab');
    tabs.forEach(t => t.classList.remove('active'));
    e.target.classList.add('active');
    body.querySelectorAll('.chapter-text, .anga-text').forEach(t => {
      t.hidden = t.dataset.textType !== type;
    });
  }

  function toggleExpanded(card) {
    card.classList.toggle('expanded');
  }

  function toggleChapterRecited(num) {
    state.chaptersRecited[num] = !state.chaptersRecited[num];
    saveState();
    // Re-render this card
    const card = $(`#chapter-card-${num}`);
    if (card) {
      const wasExpanded = card.classList.contains('expanded');
      const ch = data.chapters.find(c => c.num === num);
      const newCard = makeChapterCard(ch);
      if (wasExpanded) newCard.classList.add('expanded');
      card.replaceWith(newCard);
    }
    updateChaptersProgress();
    updatePaathProgress();
    syncPaathItem(`chapter-${num}`);
  }

  function updateChaptersProgress() {
    const total = data.chapters.length;
    const done = Object.values(state.chaptersRecited).filter(Boolean).length;
    const elProgress = $('#chapters-progress');
    if (elProgress) elProgress.textContent = `${done} / ${total} recited`;
  }

  function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }


  // ============================================================
  // Angas view
  // ============================================================

  function renderAngas() {
    const preList = $('#angas-pre-list');
    const postList = $('#angas-post-list');
    if (!preList || !postList) return;
    preList.innerHTML = '';
    postList.innerHTML = '';
    data.angas.forEach(a => {
      const card = makeAngaCard(a);
      if (a.phase === 'pre') preList.appendChild(card);
      else postList.appendChild(card);
    });
  }

  function makeAngaCard(a) {
    const isRecited = !!state.angasRecited[a.id];
    const card = el('div', {
      id: `anga-card-${a.id}`,
      class: 'anga-card' + (isRecited ? ' recited' : '')
    });

    const header = el('div', {
      class: 'anga-header',
      onclick: () => toggleExpanded(card)
    }, [
      el('div', { class: 'anga-title-block' }, [
        el('div', { class: 'anga-num-row' }, `${a.phase === 'pre' ? 'Purvanga' : 'Uttaranga'} • ${a.verseCount} verses`),
        el('div', { class: 'anga-name-sa' }, a.nameSa),
        el('div', { class: 'anga-name-en' }, a.nameEn),
        el('div', { class: 'anga-subtitle' }, a.subtitle),
      ]),
      el('div', { class: 'anga-toggle' }, '+'),
    ]);

    const body = el('div', { class: 'anga-body' });

    const meta = el('div', { class: 'anga-meta' }, [
      smallAngaMeta('Verses', String(a.verseCount)),
      smallAngaMeta('Rishi', a.rishi),
      smallAngaMeta('Devata', a.devata),
      a.chhanda ? smallAngaMeta('Chhanda', a.chhanda) : null,
    ].filter(Boolean));

    body.appendChild(meta);
    body.appendChild(el('div', { class: 'anga-summary' }, a.summary));

    const tabs = el('div', { class: 'text-tabs' }, [
      tabBtn('Devanagari', true, (e) => switchTextTab(e, body, 'devanagari')),
      tabBtn('IAST', false, (e) => switchTextTab(e, body, 'iast')),
    ]);

    const textDeva = el('div', {
      class: 'anga-text devanagari',
      dataset: { textType: 'devanagari' }
    }, a.devanagari);

    const textIast = el('div', {
      class: 'anga-text iast',
      dataset: { textType: 'iast' },
      hidden: ''
    }, a.iast);

    body.appendChild(tabs);
    body.appendChild(textDeva);
    body.appendChild(textIast);

    const actions = el('div', { class: 'anga-actions' });
    const reciteBtn = el('button', {
      class: 'recite-btn' + (isRecited ? ' recited' : ''),
      onclick: (e) => {
        e.stopPropagation();
        toggleAngaRecited(a.id);
      }
    }, isRecited ? '✓ Recited' : 'Mark as Recited');
    actions.appendChild(reciteBtn);
    body.appendChild(actions);

    card.appendChild(header);
    card.appendChild(body);
    return card;
  }

  function smallAngaMeta(label, value) {
    return el('div', { class: 'anga-meta-item' }, [
      el('div', { class: 'anga-meta-label' }, label),
      el('div', { class: 'anga-meta-value' }, value),
    ]);
  }

  function toggleAngaRecited(id) {
    state.angasRecited[id] = !state.angasRecited[id];
    saveState();
    const card = $(`#anga-card-${id}`);
    if (card) {
      const wasExpanded = card.classList.contains('expanded');
      const a = data.angas.find(x => x.id === id);
      const newCard = makeAngaCard(a);
      if (wasExpanded) newCard.classList.add('expanded');
      card.replaceWith(newCard);
    }
    updatePaathProgress();
    syncPaathItem(id);
  }


  // ============================================================
  // Paath view
  // ============================================================

  function renderPaath() {
    const root = $('#paath-list');
    if (!root) return;
    root.innerHTML = '';

    const phases = [
      { id: 'pre', label: 'Pre-Paath (Purvanga)' },
      { id: 'main', label: '13 Chapters (Mukhyanga)' },
      { id: 'post', label: 'Post-Paath (Uttaranga)' },
    ];

    phases.forEach(phase => {
      root.appendChild(el('div', { class: 'paath-phase-heading' }, phase.label));
      data.paathOrder.filter(p => p.phase === phase.id).forEach((p, i) => {
        root.appendChild(makePaathItem(p, i + 1));
      });
    });

    updatePaathProgress();
  }

  function makePaathItem(p, num) {
    const isDone = isPaathItemDone(p);
    const item = el('div', {
      id: `paath-item-${p.id}`,
      class: 'paath-item' + (isDone ? ' done' : ''),
      onclick: () => togglePaathItem(p)
    }, [
      el('div', { class: 'paath-num' }, String(num)),
      el('div', { class: 'paath-checkbox' }),
      el('div', { class: 'paath-label' }, p.label),
    ]);
    return item;
  }

  function isPaathItemDone(p) {
    if (p.id.startsWith('chapter-')) {
      const num = parseInt(p.id.replace('chapter-', ''), 10);
      return !!state.chaptersRecited[num];
    }
    if (p.id === 'navarna' || p.id === 'chandika-dhyana' || p.id === 'saptashloki') {
      // These are home/anga items - track separately via paathProgress
      return !!(state.paathProgress[p.id] || state.angasRecited[p.id]);
    }
    return !!state.angasRecited[p.id];
  }

  function togglePaathItem(p) {
    if (p.id.startsWith('chapter-')) {
      const num = parseInt(p.id.replace('chapter-', ''), 10);
      toggleChapterRecited(num);
    } else if (data.angas.find(a => a.id === p.id)) {
      toggleAngaRecited(p.id);
    } else {
      // Items like 'navarna' that aren't in angas list
      state.paathProgress[p.id] = !state.paathProgress[p.id];
      saveState();
      syncPaathItem(p.id);
    }
    updatePaathProgress();
  }

  function syncPaathItem(id) {
    // Find paath items that map to this id
    const matchIds = [];
    if (typeof id === 'number' || /^\d+$/.test(String(id))) {
      matchIds.push(`chapter-${id}`);
    } else {
      matchIds.push(id);
      // Also handle: angasRecited id === paath id
    }
    matchIds.forEach(pid => {
      const item = $(`#paath-item-${pid}`);
      if (!item) return;
      const p = data.paathOrder.find(x => x.id === pid);
      if (!p) return;
      const isDone = isPaathItemDone(p);
      item.classList.toggle('done', isDone);
    });
  }

  function updatePaathProgress() {
    const total = data.paathOrder.length;
    const done = data.paathOrder.filter(p => isPaathItemDone(p)).length;
    const pp = $('#paath-progress');
    if (pp) pp.textContent = `${done} / ${total} complete`;
  }

  function resetPaathProgress() {
    if (!confirm('Reset all paath progress (chapters + angas + checkpoints)? Sadhana log will not be affected.')) return;
    state.chaptersRecited = {};
    state.angasRecited = {};
    state.paathProgress = {};
    saveState();
    renderChapters();
    renderAngas();
    renderPaath();
  }


  // ============================================================
  // Export / Import
  // ============================================================

  function exportData() {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `durga-saptashati-progress-${todayKey()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function importData(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        state = { ...defaultState, ...parsed, sadhana: { ...defaultState.sadhana, ...(parsed.sadhana || {}) } };
        saveState();
        applyTheme();
        applyFontSize();
        renderFontControls();
        renderSadhana();
        renderChapters();
        renderAngas();
        renderPaath();
        alert('Progress imported successfully.');
      } catch (err) {
        alert('Could not parse file.');
      }
    };
    reader.readAsText(file);
  }


  // ============================================================
  // Bootstrap
  // ============================================================

  function init() {
    if (!data) {
      console.error('DURGA_DATA not loaded');
      return;
    }

    // Theme + font
    applyTheme();
    applyFontSize();
    renderFontControls();

    // Theme button
    const tb = $('#theme-toggle');
    if (tb) tb.addEventListener('click', cycleTheme);

    // Sadhana
    renderSadhana();
    const sb = $('#sadhana-log');
    if (sb) sb.addEventListener('click', logRecitation);

    // Navarna breakdown
    renderNavarna();

    // Initial views
    renderCharitas();
    renderChapters();
    renderAngas();
    renderPaath();

    // Paath reset
    const pr = $('#paath-reset');
    if (pr) pr.addEventListener('click', resetPaathProgress);

    // Export/import
    const exp = $('#export-data');
    if (exp) exp.addEventListener('click', exportData);
    const imp = $('#import-data');
    if (imp) imp.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) importData(e.target.files[0]);
    });

    // Show initial view
    showView(currentView());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
