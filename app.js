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
    sadhana: { total: 0, lastDate: null, streak: 0, monthCounts: {} },
    theme: null,
    fontSize: 'normal',
    chantPosition: 0,
    chantShowIast: false,
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
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
    catch (e) { console.warn('Could not save', e); }
  }

  let state = loadState();
  const data = window.DURGA_DATA;

  // ============================================================
  // DOM helpers
  // ============================================================

  function $(s, root) { return (root || document).querySelector(s); }
  function $$(s, root) { return Array.from((root || document).querySelectorAll(s)); }

  function el(tag, attrs, children) {
    const e = document.createElement(tag);
    if (attrs) {
      for (const k in attrs) {
        if (k === 'class') e.className = attrs[k];
        else if (k === 'dataset') for (const dk in attrs[k]) e.dataset[dk] = attrs[k][dk];
        else if (k.startsWith('on')) e.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        else if (k === 'html') e.innerHTML = attrs[k];
        else e.setAttribute(k, attrs[k]);
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

  function todayKey() { return new Date().toISOString().slice(0, 10); }
  function yesterdayKey() { const d = new Date(); d.setDate(d.getDate() - 1); return d.toISOString().slice(0, 10); }
  function monthKey(d) { return (d || todayKey()).slice(0, 7); }
  function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  // ============================================================
  // Routing
  // ============================================================

  const VIEWS = ['home', 'charitas', 'chapters', 'angas', 'hymns', 'navadurga', 'paath', 'chant', 'search', 'about'];

  function currentView() {
    const hash = window.location.hash.replace('#', '') || 'home';
    return VIEWS.includes(hash) ? hash : 'home';
  }

  function showView(name) {
    VIEWS.forEach(v => {
      const view = $(`#view-${v}`);
      if (view) view.hidden = v !== name;
    });
    $$('.nav-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.view === name));
    window.scrollTo({ top: 0, behavior: 'instant' });
    if (name === 'chant') ensureChantInit();
  }

  window.addEventListener('hashchange', () => showView(currentView()));

  // ============================================================
  // Theme & font
  // ============================================================

  function applyTheme() {
    if (state.theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else if (state.theme === 'light') document.documentElement.setAttribute('data-theme', 'light');
    else document.documentElement.removeAttribute('data-theme');
    const btn = $('#theme-toggle');
    if (btn) btn.textContent = state.theme === 'dark' ? 'Dark' : state.theme === 'light' ? 'Light' : 'System';
  }

  function cycleTheme() {
    state.theme = state.theme === null ? 'dark' : state.theme === 'dark' ? 'light' : null;
    applyTheme();
    saveState();
  }

  function applyFontSize() {
    if (state.fontSize === 'normal') document.documentElement.removeAttribute('data-font-size');
    else document.documentElement.setAttribute('data-font-size', state.fontSize);
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
  // Sadhana
  // ============================================================

  function logRecitation() {
    const today = todayKey();
    const yesterday = yesterdayKey();
    state.sadhana.total = (state.sadhana.total || 0) + 1;
    if (state.sadhana.lastDate === today) {} // same-day bump
    else if (state.sadhana.lastDate === yesterday) state.sadhana.streak = (state.sadhana.streak || 0) + 1;
    else state.sadhana.streak = 1;
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
    const setText = (id, t) => { const e = $(id); if (e) e.textContent = t; };
    setText('#sadhana-total', total);
    setText('#sadhana-streak', streak);
    setText('#sadhana-month', month);
    const lastEl = $('#sadhana-last');
    if (lastEl) lastEl.textContent = state.sadhana.lastDate ? `Last: ${state.sadhana.lastDate}` : '';
    setText('#stat-completed', total);
  }

  // ============================================================
  // Navarna
  // ============================================================

  function renderNavarna() {
    const root = $('#navarna-breakdown');
    if (!root || !data.navarnaMantra) return;
    root.innerHTML = '';
    data.navarnaMantra.wordBreakdown.forEach(w => {
      root.appendChild(el('div', { class: 'navarna-syllable' }, [
        el('span', { class: 'navarna-syllable-deva' }, w.word),
        el('span', { class: 'navarna-syllable-iast' }, w.iast),
        el('span', { class: 'navarna-syllable-meaning' }, w.meaning),
      ]));
    });
  }

  // ============================================================
  // Charitas
  // ============================================================

  function renderCharitas() {
    const root = $('#charitas-grid');
    if (!root) return;
    root.innerHTML = '';
    data.charitas.forEach(c => {
      const card = el('div', { class: 'charita-card', dataset: { charita: c.id } });
      card.appendChild(el('div', { class: 'charita-header' }, [
        el('div', { class: 'charita-name-sa' }, c.name_sa),
        el('div', { class: 'charita-name-en' }, c.name_en),
      ]));
      card.appendChild(el('div', { class: 'charita-meta' }, [
        metaItem('Presiding Devi', c.deity_sa, true),
        metaItem('Form', c.deity, false),
        metaItem('Guna', c.guna, false),
        metaItem('Chapters', c.chapters.join(', '), false),
      ]));
      card.appendChild(el('div', { class: 'charita-summary' }, c.summary));

      const chapters = el('div', { class: 'charita-chapters-list' });
      c.chapters.forEach(num => {
        const ch = data.chapters.find(x => x.num === num);
        if (!ch) return;
        const pill = el('a', {
          class: 'charita-chapter-pill', href: `#chapters`,
          onclick: () => setTimeout(() => {
            const e2 = $(`#chapter-card-${num}`);
            if (e2) { e2.classList.add('expanded'); e2.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
          }, 50)
        }, `Ch ${num} - ${ch.titleEn}`);
        chapters.appendChild(pill);
      });
      card.appendChild(chapters);
      root.appendChild(card);
    });
  }

  function metaItem(label, value, isDeitySa) {
    return el('div', { class: 'charita-meta-item' }, [
      el('span', { class: 'charita-meta-label' }, label),
      el('span', { class: 'charita-meta-value' + (isDeitySa ? ' deity-sa' : '') }, value),
    ]);
  }

  // ============================================================
  // Chapters
  // ============================================================

  function renderChapters() {
    const root = $('#chapters-list');
    if (!root) return;
    root.innerHTML = '';
    data.chapters.forEach(ch => root.appendChild(makeChapterCard(ch)));
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
      onclick: () => card.classList.toggle('expanded')
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
    body.appendChild(el('div', { class: 'chapter-meta' }, [
      smallMeta('Presiding Deity', ch.deity),
      smallMeta('Charita', capitalize(ch.charita)),
      smallMeta('Verses (approx)', String(ch.versesApprox)),
      smallMeta('Narrator', ch.narrator),
    ]));
    body.appendChild(el('div', { class: 'chapter-summary' }, ch.summary));

    if (ch.phala) {
      body.appendChild(el('div', { class: 'phala-card' }, [
        el('div', { class: 'phala-label' }, 'Phala (Fruit of recitation)'),
        el('div', { class: 'phala-text' }, ch.phala),
      ]));
    }

    if (ch.keyHymns && ch.keyHymns.length) {
      const hymns = el('div', { class: 'key-hymns' }, [el('div', { class: 'key-hymns-label' }, 'Key Hymns')]);
      ch.keyHymns.forEach(h => hymns.appendChild(el('span', { class: 'key-hymn' }, h)));
      body.appendChild(hymns);
    }

    body.appendChild(el('div', { class: 'text-tabs' }, [
      tabBtn('Devanagari', true, (e) => switchTextTab(e, body, 'devanagari')),
      tabBtn('IAST', false, (e) => switchTextTab(e, body, 'iast')),
    ]));
    body.appendChild(el('div', { class: 'chapter-text devanagari', dataset: { textType: 'devanagari' } }, ch.devanagari));
    body.appendChild(el('div', { class: 'chapter-text iast', dataset: { textType: 'iast' }, hidden: '' }, ch.iast));

    const reciteBtn = el('button', {
      class: 'recite-btn' + (isRecited ? ' recited' : ''),
      onclick: (e) => { e.stopPropagation(); toggleChapterRecited(ch.num); }
    }, isRecited ? '✓ Recited' : 'Mark as Recited');
    body.appendChild(el('div', { class: 'chapter-actions' }, reciteBtn));

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

  function smallMeta(label, value) {
    return el('div', { class: 'chapter-meta-item' }, [
      el('div', { class: 'chapter-meta-label' }, label),
      el('div', { class: 'chapter-meta-value' }, value),
    ]);
  }

  function switchTextTab(e, body, type) {
    e.stopPropagation();
    body.querySelectorAll('.text-tab').forEach(t => t.classList.remove('active'));
    e.target.classList.add('active');
    body.querySelectorAll('.chapter-text, .anga-text, .hymn-text').forEach(t => {
      t.hidden = t.dataset.textType !== type;
    });
  }

  function toggleChapterRecited(num) {
    state.chaptersRecited[num] = !state.chaptersRecited[num];
    saveState();
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
    const ep = $('#chapters-progress');
    if (ep) ep.textContent = `${done} / ${total} recited`;
  }

  // ============================================================
  // Angas
  // ============================================================

  function renderAngas() {
    const preList = $('#angas-pre-list');
    const postList = $('#angas-post-list');
    if (!preList || !postList) return;
    preList.innerHTML = ''; postList.innerHTML = '';
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
      onclick: () => card.classList.toggle('expanded')
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
    body.appendChild(el('div', { class: 'anga-meta' }, [
      smallAnga('Verses', String(a.verseCount)),
      smallAnga('Rishi', a.rishi),
      smallAnga('Devata', a.devata),
      a.chhanda ? smallAnga('Chhanda', a.chhanda) : null,
    ].filter(Boolean)));
    body.appendChild(el('div', { class: 'anga-summary' }, a.summary));
    body.appendChild(el('div', { class: 'text-tabs' }, [
      tabBtn('Devanagari', true, (e) => switchTextTab(e, body, 'devanagari')),
      tabBtn('IAST', false, (e) => switchTextTab(e, body, 'iast')),
    ]));
    body.appendChild(el('div', { class: 'anga-text devanagari', dataset: { textType: 'devanagari' } }, a.devanagari));
    body.appendChild(el('div', { class: 'anga-text iast', dataset: { textType: 'iast' }, hidden: '' }, a.iast));
    const reciteBtn = el('button', {
      class: 'recite-btn' + (isRecited ? ' recited' : ''),
      onclick: (e) => { e.stopPropagation(); toggleAngaRecited(a.id); }
    }, isRecited ? '✓ Recited' : 'Mark as Recited');
    body.appendChild(el('div', { class: 'anga-actions' }, reciteBtn));
    card.appendChild(header); card.appendChild(body);
    return card;
  }

  function smallAnga(label, value) {
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
  // Hymns
  // ============================================================

  function renderHymns() {
    const root = $('#hymns-list');
    if (!root) return;
    root.innerHTML = '';
    (data.hymns || []).forEach(h => root.appendChild(makeHymnCard(h)));
  }

  function makeHymnCard(h) {
    const card = el('div', { class: 'hymn-feature-card' });
    card.appendChild(el('div', { class: 'hymn-header' }, [
      el('div', { class: 'hymn-from' }, `From Chapter ${h.from_chapter} • ${h.verse_range}`),
      el('div', { class: 'hymn-name-sa' }, h.name_sa),
      el('div', { class: 'hymn-name-en' }, h.name_en),
      el('div', { class: 'hymn-subtitle' }, h.subtitle),
    ]));
    card.appendChild(el('div', { class: 'hymn-summary' }, h.summary));

    if (h.key_line) {
      const lineCard = el('div', { class: 'hymn-keyline' });
      lineCard.appendChild(el('div', { class: 'hymn-keyline-label' }, 'Key Verse'));
      lineCard.appendChild(el('div', { class: 'hymn-keyline-deva' }, h.key_line));
      if (h.key_line_iast) lineCard.appendChild(el('div', { class: 'hymn-keyline-iast' }, h.key_line_iast));
      card.appendChild(lineCard);
    }

    if (h.aspects && h.aspects.length) {
      card.appendChild(el('h4', { class: 'aspects-heading' }, '21 Aspects of "Ya Devi Sarva Bhuteshu"'));
      const grid = el('div', { class: 'aspects-grid' });
      h.aspects.forEach(a => {
        grid.appendChild(el('div', { class: 'aspect-card' }, [
          el('div', { class: 'aspect-deva' }, a.sa),
          el('div', { class: 'aspect-iast' }, a.iast),
          el('div', { class: 'aspect-meaning' }, a.en),
        ]));
      });
      card.appendChild(grid);
    }

    card.appendChild(el('a', {
      class: 'hymn-jump-link',
      href: `#chapters`,
      onclick: () => setTimeout(() => {
        const e2 = $(`#chapter-card-${h.from_chapter}`);
        if (e2) { e2.classList.add('expanded'); e2.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
      }, 50)
    }, `→ Read full Chapter ${h.from_chapter}`));
    return card;
  }

  // ============================================================
  // Navadurga
  // ============================================================

  function renderNavadurga() {
    const root = $('#navadurga-grid');
    if (!root) return;
    root.innerHTML = '';
    (data.navadurga || []).forEach(d => root.appendChild(makeNavadurgaCard(d)));
  }

  function makeNavadurgaCard(d) {
    const card = el('div', { class: 'navadurga-card', dataset: { id: d.id } });
    const header = el('div', {
      class: 'navadurga-header',
      onclick: () => card.classList.toggle('expanded')
    }, [
      el('div', { class: 'navadurga-day-badge' }, `Day ${d.day}`),
      el('div', { class: 'navadurga-title-block' }, [
        el('div', { class: 'navadurga-name-sa' }, d.name_sa),
        el('div', { class: 'navadurga-name-en' }, d.name_en),
        el('div', { class: 'navadurga-meaning' }, d.meaning),
      ]),
      el('div', { class: 'navadurga-color', style: `background: ${navadurgaColor(d.color)};`, title: d.color }),
    ]);
    const body = el('div', { class: 'navadurga-body' });
    body.appendChild(el('div', { class: 'navadurga-meta' }, [
      smallNav('Color', d.color),
      smallNav('Vahana', d.vahana),
      smallNav('Weapons', d.weapons),
      smallNav('Boon', d.boon),
    ]));
    body.appendChild(el('div', { class: 'navadurga-story' }, d.story));
    body.appendChild(el('div', { class: 'navadurga-mantra-card' }, [
      el('div', { class: 'navadurga-section-label' }, 'Mantra'),
      el('div', { class: 'navadurga-mantra-deva' }, d.mantra_sa),
      el('div', { class: 'navadurga-mantra-iast' }, d.mantra_iast),
    ]));
    body.appendChild(el('div', { class: 'navadurga-dhyana-card' }, [
      el('div', { class: 'navadurga-section-label' }, 'Dhyana Verse'),
      el('div', { class: 'navadurga-dhyana-deva' }, d.dhyana),
    ]));
    card.appendChild(header);
    card.appendChild(body);
    return card;
  }

  function smallNav(label, value) {
    return el('div', { class: 'navadurga-meta-item' }, [
      el('div', { class: 'navadurga-meta-label' }, label),
      el('div', { class: 'navadurga-meta-value' }, value),
    ]);
  }

  function navadurgaColor(name) {
    const c = (name || '').toLowerCase();
    if (c.includes('red')) return '#a83838';
    if (c.includes('royal blue') || c.includes('dark blue')) return '#2a3a78';
    if (c.includes('blue') && c.includes('black')) return '#1a1a3a';
    if (c.includes('yellow')) return '#d4a843';
    if (c.includes('green')) return '#3d6b48';
    if (c.includes('grey') || c.includes('gray')) return '#7a7a7a';
    if (c.includes('orange')) return '#c4793c';
    if (c.includes('pink')) return '#c47a8a';
    if (c.includes('sky') || c.includes('purple')) return '#6b4d8c';
    return '#c9a84c';
  }

  // ============================================================
  // Saptamatrika
  // ============================================================

  function renderSaptamatrika() {
    const root = $('#saptamatrika-grid');
    if (!root) return;
    root.innerHTML = '';
    (data.saptamatrika || []).forEach(m => {
      const card = el('div', { class: 'matrika-card' });
      card.appendChild(el('div', { class: 'matrika-name-sa' }, m.name_sa));
      card.appendChild(el('div', { class: 'matrika-name-en' }, m.name_en));
      card.appendChild(el('div', { class: 'matrika-shakti' }, `Shakti of ${m.from}`));
      card.appendChild(el('div', { class: 'matrika-desc' }, m.description));
      card.appendChild(el('div', { class: 'matrika-meta' }, [
        smallMatrika('Vahana', m.vahana),
        smallMatrika('Weapon', m.weapon),
      ]));
      root.appendChild(card);
    });
  }

  function smallMatrika(label, value) {
    return el('div', { class: 'matrika-meta-item' }, [
      el('span', { class: 'matrika-meta-label' }, label + ': '),
      el('span', { class: 'matrika-meta-value' }, value),
    ]);
  }

  // ============================================================
  // Beginner Path
  // ============================================================

  function renderBeginnerPath() {
    const root = $('#stages-grid');
    if (!root) return;
    root.innerHTML = '';
    (data.beginnerPath || []).forEach(s => {
      root.appendChild(el('div', { class: 'stage-card' }, [
        el('div', { class: 'stage-label' }, `Stage ${s.stage}`),
        el('div', { class: 'stage-title' }, s.title),
        el('div', { class: 'stage-desc' }, s.desc),
      ]));
    });
  }

  // ============================================================
  // Navratri + Nitya Chandi + Homa + Weapons
  // ============================================================

  function renderNavratri() {
    const root = $('#navratri-content');
    if (!root || !data.navratri) return;
    root.innerHTML = '';
    root.appendChild(el('p', {}, data.navratri.intro));

    root.appendChild(el('h3', {}, 'Four Annual Navratris'));
    const fest = el('div', { class: 'festival-grid' });
    data.navratri.festivals.forEach(f => {
      fest.appendChild(el('div', { class: 'festival-card' }, [
        el('div', { class: 'festival-name' }, f.name),
        el('div', { class: 'festival-month' }, f.month),
        el('div', { class: 'festival-note' }, f.note),
      ]));
    });
    root.appendChild(fest);

    root.appendChild(el('h3', {}, 'The Nine Nights'));
    const nights = el('div', { class: 'navratri-nights-grid' });
    data.navratri.navratri_days.forEach(d => {
      nights.appendChild(el('div', { class: 'night-card' }, [
        el('div', { class: 'night-num' }, `Night ${d.night}`),
        el('div', { class: 'night-form' }, d.form),
        el('div', { class: 'night-color', style: `background: ${navadurgaColor(d.color)};`, title: d.color }),
        el('div', { class: 'night-focus' }, d.focus),
      ]));
    });
    root.appendChild(nights);
  }

  function renderNityaChandi() {
    const root = $('#nitya-chandi');
    if (!root || !data.navratri) return;
    root.innerHTML = '';
    const nc = data.navratri.kerala_nitya_chandi;
    root.appendChild(el('p', {}, nc.description));
    const tbl = el('div', { class: 'nitya-chandi-grid' });
    nc.schedule.forEach(s => {
      tbl.appendChild(el('div', { class: 'nitya-row' }, [
        el('div', { class: 'nitya-day' }, `Day ${s.day}`),
        el('div', { class: 'nitya-chapters' }, s.chapters),
        el('div', { class: 'nitya-charita' }, s.charita),
      ]));
    });
    root.appendChild(tbl);
  }

  function renderChandiHoma() {
    const root = $('#homa-content');
    if (!root || !data.chandiHoma) return;
    root.innerHTML = '';
    root.appendChild(el('p', {}, data.chandiHoma.intro));
    root.appendChild(el('h3', {}, 'Types of Chandi Homa'));
    const types = el('div', { class: 'homa-types-grid' });
    data.chandiHoma.types.forEach(t => {
      types.appendChild(el('div', { class: 'homa-type-card' }, [
        el('div', { class: 'homa-type-name' }, t.name),
        el('div', { class: 'homa-type-desc' }, t.desc),
      ]));
    });
    root.appendChild(types);
    root.appendChild(el('h3', {}, 'Auspicious Occasions'));
    const ul = el('ul');
    data.chandiHoma.occasions.forEach(o => ul.appendChild(el('li', {}, o)));
    root.appendChild(ul);
  }

  function renderWeapons() {
    const root = $('#weapons-content');
    if (!root || !data.eighteenWeapons) return;
    root.innerHTML = '';
    root.appendChild(el('p', {}, data.eighteenWeapons.intro));
    const grid = el('div', { class: 'weapons-grid' });
    data.eighteenWeapons.weapons.forEach((w, i) => {
      grid.appendChild(el('div', { class: 'weapon-card' }, [
        el('div', { class: 'weapon-num' }, String(i + 1)),
        el('div', { class: 'weapon-info' }, [
          el('div', { class: 'weapon-name' }, w.weapon),
          el('div', { class: 'weapon-from' }, `Gifted by ${w.from}`),
          el('div', { class: 'weapon-meaning' }, w.represents),
        ]),
      ]));
    });
    root.appendChild(grid);
  }

  // ============================================================
  // Paath
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
    let n = 1;
    phases.forEach(phase => {
      root.appendChild(el('div', { class: 'paath-phase-heading' }, phase.label));
      data.paathOrder.filter(p => p.phase === phase.id).forEach(p => {
        root.appendChild(makePaathItem(p, n));
        n++;
      });
    });
    updatePaathProgress();
  }

  function makePaathItem(p, num) {
    const isDone = isPaathItemDone(p);
    return el('div', {
      id: `paath-item-${p.id}`,
      class: 'paath-item' + (isDone ? ' done' : ''),
      onclick: () => togglePaathItem(p)
    }, [
      el('div', { class: 'paath-num' }, String(num)),
      el('div', { class: 'paath-checkbox' }),
      el('div', { class: 'paath-label' }, p.label),
    ]);
  }

  function isPaathItemDone(p) {
    if (p.id.startsWith('chapter-')) {
      const num = parseInt(p.id.replace('chapter-', ''), 10);
      return !!state.chaptersRecited[num];
    }
    if (data.angas.find(a => a.id === p.id)) return !!state.angasRecited[p.id];
    return !!state.paathProgress[p.id];
  }

  function togglePaathItem(p) {
    if (p.id.startsWith('chapter-')) {
      const num = parseInt(p.id.replace('chapter-', ''), 10);
      toggleChapterRecited(num);
    } else if (data.angas.find(a => a.id === p.id)) {
      toggleAngaRecited(p.id);
    } else {
      state.paathProgress[p.id] = !state.paathProgress[p.id];
      saveState();
      syncPaathItem(p.id);
    }
    updatePaathProgress();
  }

  function syncPaathItem(id) {
    const item = $(`#paath-item-${id.toString().match(/^\d+$/) ? 'chapter-' + id : id}`);
    if (!item) return;
    const pid = id.toString().match(/^\d+$/) ? `chapter-${id}` : id;
    const p = data.paathOrder.find(x => x.id === pid);
    if (!p) return;
    item.classList.toggle('done', isPaathItemDone(p));
  }

  function updatePaathProgress() {
    const total = data.paathOrder.length;
    const done = data.paathOrder.filter(p => isPaathItemDone(p)).length;
    const pp = $('#paath-progress');
    if (pp) pp.textContent = `${done} / ${total} complete`;
  }

  function resetPaathProgress() {
    if (!confirm('Reset all paath progress? Sadhana log will not be affected.')) return;
    state.chaptersRecited = {};
    state.angasRecited = {};
    state.paathProgress = {};
    saveState();
    renderChapters();
    renderAngas();
    renderPaath();
  }

  // ============================================================
  // Chant Mode
  // ============================================================

  let chantInited = false;
  let chantItems = [];

  function ensureChantInit() {
    if (chantInited) return;
    chantInited = true;

    chantItems = data.paathOrder.map(p => {
      let titleSa = '', titleEn = p.label, devanagari = '', iast = '';
      if (p.id.startsWith('chapter-')) {
        const num = parseInt(p.id.replace('chapter-', ''), 10);
        const ch = data.chapters.find(c => c.num === num);
        if (ch) {
          titleSa = ch.titleSa;
          titleEn = `Chapter ${num}: ${ch.titleEn}`;
          devanagari = ch.devanagari;
          iast = ch.iast;
        }
      } else if (p.id === 'navarna') {
        titleSa = data.navarnaMantra.nameSa;
        titleEn = data.navarnaMantra.nameEn;
        devanagari = data.navarnaMantra.devanagari + '\n\n(Recite 108 times)';
        iast = data.navarnaMantra.iast + '\n\n(Recite 108 times)';
      } else {
        const a = data.angas.find(x => x.id === p.id);
        if (a) {
          titleSa = a.nameSa;
          titleEn = a.nameEn;
          devanagari = a.devanagari;
          iast = a.iast;
        }
      }
      return { id: p.id, titleSa, titleEn, devanagari, iast };
    }).filter(x => x.devanagari);

    // Jump select
    const sel = $('#chant-jump-select');
    if (sel) {
      sel.innerHTML = '';
      chantItems.forEach((it, i) => {
        sel.appendChild(el('option', { value: i }, `${i + 1}. ${it.titleEn}`));
      });
      sel.addEventListener('change', () => {
        state.chantPosition = parseInt(sel.value, 10);
        saveState();
        renderChantStage();
      });
    }

    $('#chant-prev').addEventListener('click', () => {
      state.chantPosition = Math.max(0, (state.chantPosition || 0) - 1);
      saveState(); renderChantStage();
    });
    $('#chant-next').addEventListener('click', () => {
      state.chantPosition = Math.min(chantItems.length - 1, (state.chantPosition || 0) + 1);
      saveState(); renderChantStage();
    });
    $('#chant-fullscreen').addEventListener('click', toggleChantFullscreen);
    $('#chant-toggle-script').addEventListener('click', () => {
      state.chantShowIast = !state.chantShowIast;
      saveState();
      renderChantStage();
    });

    document.addEventListener('keydown', (e) => {
      if ($('#view-chant').hidden) return;
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') $('#chant-prev').click();
      else if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
        e.preventDefault(); $('#chant-next').click();
      }
      else if (e.key === 'f' || e.key === 'F') toggleChantFullscreen();
    });

    renderChantStage();
  }

  function renderChantStage() {
    if (!chantItems.length) return;
    const pos = Math.max(0, Math.min(chantItems.length - 1, state.chantPosition || 0));
    const it = chantItems[pos];
    $('#chant-position-info').textContent = `Position ${pos + 1} of ${chantItems.length}`;
    $('#chant-position-label').innerHTML = `<span class="chant-pos-sa">${it.titleSa || ''}</span> <span class="chant-pos-en">${it.titleEn}</span>`;
    $('#chant-text-deva').textContent = it.devanagari;
    $('#chant-text-iast').textContent = it.iast;
    $('#chant-text-deva').hidden = !!state.chantShowIast;
    $('#chant-text-iast').hidden = !state.chantShowIast;
    $('#chant-toggle-script').textContent = state.chantShowIast ? 'Show Devanagari' : 'Show IAST';
    const sel = $('#chant-jump-select');
    if (sel) sel.value = pos;
  }

  function toggleChantFullscreen() {
    const stage = $('#chant-stage');
    if (!document.fullscreenElement) stage.requestFullscreen();
    else document.exitFullscreen();
  }

  // ============================================================
  // Search
  // ============================================================

  function renderSearch() {
    const input = $('#search-input');
    if (!input) return;
    input.addEventListener('input', () => doSearch(input.value));
  }

  function normalize(s) {
    return (s || '').toString().toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '');
  }

  function doSearch(q) {
    const root = $('#search-results');
    const counter = $('#search-counter');
    if (!root) return;
    root.innerHTML = '';
    const query = normalize(q.trim());
    if (!query || query.length < 2) {
      counter.textContent = '';
      return;
    }
    const results = [];

    // Search chapters
    data.chapters.forEach(ch => {
      const haystack = normalize(`${ch.titleEn} ${ch.titleSa} ${ch.subtitle} ${ch.summary} ${ch.deity}`)
                     + ' ' + ch.devanagari + ' ' + normalize(ch.iast);
      if (haystack.includes(query) || haystack.includes(q)) {
        results.push({ type: 'Chapter', label: `Chapter ${ch.num}: ${ch.titleEn}`, snippet: ch.subtitle, link: `#chapters`, target: `chapter-card-${ch.num}` });
      }
    });

    // Angas
    data.angas.forEach(a => {
      const haystack = normalize(`${a.nameEn} ${a.nameSa} ${a.subtitle} ${a.summary}`)
                     + ' ' + a.devanagari + ' ' + normalize(a.iast);
      if (haystack.includes(query) || haystack.includes(q)) {
        results.push({ type: 'Anga', label: a.nameEn, snippet: a.subtitle, link: `#angas`, target: `anga-card-${a.id}` });
      }
    });

    // Hymns
    (data.hymns || []).forEach(h => {
      const haystack = normalize(`${h.name_en} ${h.name_sa} ${h.summary}`) + ' ' + (h.key_line || '');
      if (haystack.includes(query) || haystack.includes(q)) {
        results.push({ type: 'Hymn', label: h.name_en, snippet: h.subtitle, link: `#hymns` });
      }
    });

    // Navadurga
    (data.navadurga || []).forEach(d => {
      const haystack = normalize(`${d.name_en} ${d.meaning} ${d.story} ${d.boon}`) + ' ' + d.name_sa;
      if (haystack.includes(query) || haystack.includes(q)) {
        results.push({ type: 'Form', label: d.name_en, snippet: d.meaning, link: `#navadurga` });
      }
    });

    // Saptamatrika
    (data.saptamatrika || []).forEach(m => {
      const haystack = normalize(`${m.name_en} ${m.description} ${m.from}`) + ' ' + m.name_sa;
      if (haystack.includes(query) || haystack.includes(q)) {
        results.push({ type: 'Matrika', label: m.name_en, snippet: m.description.slice(0, 80) + '...', link: `#about` });
      }
    });

    counter.textContent = `${results.length} result${results.length === 1 ? '' : 's'}`;
    results.forEach(r => {
      const card = el('a', {
        class: 'search-result-card',
        href: r.link,
        onclick: () => {
          if (r.target) setTimeout(() => {
            const t = $(`#${r.target}`);
            if (t) { t.classList.add('expanded'); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
          }, 50);
        }
      }, [
        el('div', { class: 'search-result-type' }, r.type),
        el('div', { class: 'search-result-label' }, r.label),
        el('div', { class: 'search-result-snippet' }, r.snippet),
      ]);
      root.appendChild(card);
    });
  }

  // ============================================================
  // Export / Import
  // ============================================================

  function exportData() {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `durga-saptashati-progress-${todayKey()}.json`; a.click();
    URL.revokeObjectURL(url);
  }

  function importData(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        state = { ...defaultState, ...parsed, sadhana: { ...defaultState.sadhana, ...(parsed.sadhana || {}) } };
        saveState();
        applyTheme(); applyFontSize(); renderFontControls();
        renderSadhana(); renderChapters(); renderAngas(); renderPaath();
        alert('Progress imported successfully.');
      } catch (err) { alert('Could not parse file.'); }
    };
    reader.readAsText(file);
  }

  // ============================================================
  // Init
  // ============================================================

  function init() {
    if (!data) { console.error('DURGA_DATA not loaded'); return; }
    applyTheme(); applyFontSize(); renderFontControls();
    const tb = $('#theme-toggle');
    if (tb) tb.addEventListener('click', cycleTheme);

    renderSadhana();
    const sb = $('#sadhana-log');
    if (sb) sb.addEventListener('click', logRecitation);

    renderNavarna();
    renderCharitas();
    renderChapters();
    renderAngas();
    renderHymns();
    renderNavadurga();
    renderSaptamatrika();
    renderBeginnerPath();
    renderNavratri();
    renderNityaChandi();
    renderChandiHoma();
    renderWeapons();
    renderPaath();
    renderSearch();

    const pr = $('#paath-reset');
    if (pr) pr.addEventListener('click', resetPaathProgress);

    const exp = $('#export-data');
    if (exp) exp.addEventListener('click', exportData);
    const imp = $('#import-data');
    if (imp) imp.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) importData(e.target.files[0]);
    });

    showView(currentView());
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
