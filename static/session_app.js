const TRANSLATIONS_KEY = "metaphor-extension:show-translations";

let graphAnimation = null;

const state = {
  session: null,
  index: 0,
  source: null,
  target: null,
  sessions: [],
  showTranslations: JSON.parse(localStorage.getItem(TRANSLATIONS_KEY) || "false"),
};

const els = {
  form: document.querySelector("#search-form"),
  sessions: document.querySelector("#sessions"),
  loadSession: document.querySelector("#load-session"),
  message: document.querySelector("#message"),
  annotation: document.querySelector("#annotation"),
  queueTitle: document.querySelector("#queue-title"),
  queueCount: document.querySelector("#queue-count"),
  queueList: document.querySelector("#queue-list"),
  lemmaTitle: document.querySelector("#lemma-title"),
  progress: document.querySelector("#progress"),
  sourceTitle: document.querySelector("#source-title"),
  translationToggleLabel: document.querySelector("#translation-toggle-label"),
  showTranslations: document.querySelector("#show-translations"),
  translationToggleText: document.querySelector("#translation-toggle-text"),
  graph: document.querySelector("#graph"),
  sourceSenses: document.querySelector("#source-senses"),
  direction: document.querySelector("#direction"),
  selectionState: document.querySelector("#selection-state"),
  linksList: document.querySelector("#links-list"),
  comment: document.querySelector("#comment"),
  prev: document.querySelector("#prev"),
  next: document.querySelector("#next"),
  finished: document.querySelector("#finished"),
  incomplete: document.querySelector("#incomplete"),
  ignore: document.querySelector("#ignore"),
};

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("Loading Wordnet and computing hyponym overlap...");
  const payload = Object.fromEntries(new FormData(els.form).entries());
  try {
    state.session = await api("/api/search", payload);
    state.index = firstOpenIndex(state.session);
    clearSelection();
    await loadSessionSummaries();
    render();
  } catch (error) {
    showMessage(error.message);
  }
});

els.loadSession.addEventListener("click", async () => {
  if (!els.sessions.value) return;
  try {
    state.session = await requestJson(`/api/sessions/${encodeURIComponent(els.sessions.value)}`);
    state.index = firstOpenIndex(state.session);
    clearSelection();
    render();
  } catch (error) {
    showMessage(error.message);
  }
});

document.querySelectorAll("[data-link-type]").forEach((button) => {
  button.addEventListener("click", () => saveLink(button.dataset.linkType));
  button.addEventListener("mouseenter", () => renderSelection(button.dataset.linkType));
  button.addEventListener("focus", () => renderSelection(button.dataset.linkType));
  button.addEventListener("mouseleave", () => renderSelection());
  button.addEventListener("blur", () => renderSelection());
});

els.comment.addEventListener("change", async () => {
  const item = currentItem();
  if (!item) return;
  const updated = await api(itemUrl(item, "comment"), { comment: els.comment.value });
  replaceCurrent(updated);
  renderQueue();
});

els.prev.addEventListener("click", () => move(-1));
els.next.addEventListener("click", () => move(1));
els.finished.addEventListener("click", () => markStatus("done"));
els.incomplete.addEventListener("click", () => markStatus("incomplete"));
els.ignore.addEventListener("click", () => markStatus("ignore"));
els.direction.addEventListener("change", renderSelection);

els.showTranslations.checked = state.showTranslations;
els.showTranslations.addEventListener("change", () => {
  state.showTranslations = els.showTranslations.checked;
  localStorage.setItem(TRANSLATIONS_KEY, JSON.stringify(state.showTranslations));
  const item = currentItem();
  if (item) renderSenses(els.sourceSenses, allSenses(item), item.links);
});

loadSessionSummaries();

async function api(url, payload) {
  return requestJson(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function loadSessionSummaries() {
  state.sessions = await requestJson("/api/sessions");
  renderSessionSummaries();
}

function render() {
  if (!state.session) return;
  renderQueue();
  renderSessionSummaries();
  const item = currentItem();
  if (!item) {
    showMessage("No matching words found.");
    els.annotation.classList.add("hidden");
    return;
  }
  els.message.classList.add("hidden");
  els.annotation.classList.remove("hidden");
  els.lemmaTitle.textContent = item.lemma;
  els.progress.textContent = `${state.index + 1} / ${state.session.items.length}`;
  els.sourceTitle.textContent = `All senses of ${item.lemma}`;
  const displayLexicon = state.session.display_lexicon;
  if (displayLexicon) {
    els.translationToggleLabel.classList.remove("hidden");
    els.translationToggleText.textContent = `Show ${displayLexicon}`;
  } else {
    els.translationToggleLabel.classList.add("hidden");
  }
  els.comment.value = item.comment || "";
  renderSenses(els.sourceSenses, allSenses(item), item.links);
  renderGraph(item);
  renderLinks(item);
  renderSelection();
  els.prev.disabled = state.index === 0;
  els.next.disabled = state.index >= state.session.items.length - 1;
}

function renderSessionSummaries() {
  els.sessions.innerHTML = "";
  if (!state.sessions.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No stored sessions";
    els.sessions.append(option);
    els.loadSession.disabled = true;
    return;
  }
  els.loadSession.disabled = false;
  for (const session of state.sessions) {
    const option = document.createElement("option");
    option.value = session.id;
    option.textContent = `${session.name} (${session.counts.done || 0}/${session.total})`;
    if (state.session?.id === session.id) option.selected = true;
    els.sessions.append(option);
  }
}

function renderQueue() {
  const total = state.session.items.length;
  const closed = state.session.items.filter((item) => item.status !== "open").length;
  els.queueTitle.textContent = state.session.name || state.session.lexicon || state.session.wordnet;
  els.queueCount.textContent = `${closed}/${total}`;
  els.queueList.innerHTML = "";
  state.session.items.forEach((item, index) => {
    const button = document.createElement("button");
    button.className = `queue-item ${index === state.index ? "active" : ""}`;
    button.innerHTML = `<span>${escapeHtml(item.lemma)}</span><span class="status">${statusLabel(item.status)}</span>`;
    button.addEventListener("click", () => {
      state.index = index;
      clearSelection();
      render();
    });
    els.queueList.append(button);
  });
}

function renderSenses(container, senses, links) {
  container.innerHTML = "";
  for (const [index, sense] of senses.entries()) {
    const card = document.createElement("article");
    const linkedType = linkedClass(sense.id, links);
    const annotation = senseAnnotation(sense);
    card.className = `sense ${selectedClass(sense.id)} ${linkedType} ${annotation.bad_sense ? "bad-sense" : ""}`;
    const hasAnnotation = annotation.bad_sense || annotation.comment;
    card.innerHTML = `
      <div class="sense-main" role="button" tabindex="0">
        <div class="sense-topline">
          <span class="sense-number">${index + 1}</span>
          <strong>${escapeHtml(sense.synset.lemmas.join(", "))}</strong>
          <span class="sense-topline-right">
            ${senseIliLink(sense)}
            <button class="annotate-toggle${hasAnnotation ? " has-annotation" : ""}" title="Note" aria-label="Toggle sense note">✎</button>
          </span>
        </div>
        <div class="meta">${escapeHtml(sense.id)} · ${escapeHtml(sense.synset.pos || "")}</div>
        <div class="def">${escapeHtml(sense.synset.definition || "")}</div>
        ${state.showTranslations && sense.display_synset ? `<div class="def def-reference">${escapeHtml(sense.display_synset.lemmas.join(", "))} — ${escapeHtml(sense.display_synset.definition)}</div>` : ""}
        ${senseBadges(sense)}
      </div>
      <div class="sense-annotation${hasAnnotation ? "" : " hidden"}">
        <label class="bad-sense-toggle">
          <input type="checkbox" data-sense-bad="${escapeHtml(sense.id)}" ${annotation.bad_sense ? "checked" : ""}>
          bad
        </label>
        <textarea data-sense-comment="${escapeHtml(sense.id)}" rows="2" placeholder="note">${escapeHtml(annotation.comment)}</textarea>
      </div>
    `;
    card.querySelector(".sense-main").addEventListener("click", () => {
      selectSense(sense);
      render();
    });
    card.querySelector(".sense-main").addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      selectSense(sense);
      render();
    });
    const annotateBtn = card.querySelector(".annotate-toggle");
    annotateBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      card.querySelector(".sense-annotation").classList.toggle("hidden");
      annotateBtn.classList.toggle("active");
    });
    annotateBtn.addEventListener("keydown", (event) => event.stopPropagation());
    card.querySelector("[data-sense-bad]").addEventListener("change", (event) => {
      saveSenseAnnotation(sense, { bad_sense: event.target.checked });
    });
    card.querySelector("[data-sense-comment]").addEventListener("change", (event) => {
      saveSenseAnnotation(sense, { comment: event.target.value });
    });
    container.append(card);
  }
}

function renderGraph(item) {
  if (graphAnimation !== null) {
    cancelAnimationFrame(graphAnimation);
    graphAnimation = null;
  }

  const width = 680;
  const height = 420;
  const margin = 58;
  const senses = allSenses(item);
  if (!senses.length) { els.graph.innerHTML = ""; return; }

  const nodes = senses.map((sense, index) => {
    const angle = (2 * Math.PI * index) / senses.length - Math.PI / 2;
    const r = Math.min(width, height) * 0.28;
    return {
      id: sense.id,
      role: senseRole(sense),
      sense,
      x: width / 2 + r * Math.cos(angle),
      y: height / 2 + r * Math.sin(angle),
      vx: 0,
      vy: 0,
      pinned: false,
    };
  });
  const byId = new Map(nodes.map((n) => [n.id, n]));

  const linkEdges = Object.values(item.links || {})
    .map((l) => ({ ...l, sourceNode: byId.get(l.source), targetNode: byId.get(l.target) }))
    .filter((l) => l.sourceNode && l.targetNode);
  const existingEdges = (item.existing_relations || [])
    .map((r) => ({ ...r, sourceNode: byId.get(r.source), targetNode: byId.get(r.target) }))
    .filter((r) => r.sourceNode && r.targetNode);
  const allEdges = [...linkEdges, ...existingEdges];

  els.graph.innerHTML = `<defs>
    <filter id="node-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="2.5" flood-opacity="0.15"/>
    </filter>
    ${["metaphor", "metonymy", "hypernym", "other"].map((type) => `
    <marker id="arrow-${type}" viewBox="0 -5 10 10" refX="30" refY="0" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,-5L10,0L0,5" fill="${linkColor(type)}"></path>
    </marker>`).join("")}
    <marker id="arrow-existing" viewBox="0 -5 10 10" refX="30" refY="0" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,-5L10,0L0,5" fill="#7a828e"></path>
    </marker>
  </defs>`;

  const edgeEls = [
    ...existingEdges.map((r) => {
      const line = svgEl("line", { class: "graph-link existing", stroke: "#7a828e", "marker-end": "url(#arrow-existing)" });
      const lbl = svgEl("text", { class: "graph-label existing", fill: "#626a75" });
      lbl.textContent = r.type;
      els.graph.append(line, lbl);
      return { line, lbl, edge: r };
    }),
    ...linkEdges.map((l) => {
      const line = svgEl("line", { class: "graph-link", stroke: linkColor(l.type), "marker-end": `url(#arrow-${l.type})` });
      const lbl = svgEl("text", { class: "graph-label", fill: linkColor(l.type) });
      lbl.textContent = l.type;
      els.graph.append(line, lbl);
      return { line, lbl, edge: l };
    }),
  ];

  const nodeEls = nodes.map((node) => {
    const selected = selectedClass(node.sense.id) ? " selected" : "";
    const g = svgEl("g", { class: `graph-node ${node.role}${selected}` });
    g.append(svgEl("rect", { class: "graph-box", x: -52, y: -18, width: 104, height: 36, rx: 6, filter: "url(#node-shadow)" }));
    const lbl = svgEl("text", { class: "graph-label", y: 5 });
    lbl.textContent = `${senseNumber(node.sense)} - ${shortLabel(node.sense)}`;
    g.append(lbl);
    g.addEventListener("click", () => { selectSense(node.sense); render(); });
    g.addEventListener("mousedown", (e) => {
      e.stopPropagation();
      node.pinned = true;
      node.vx = node.vy = 0;
      const svgRect = els.graph.getBoundingClientRect();
      const sx = width / svgRect.width;
      const sy = height / svgRect.height;
      const onMove = (ev) => {
        node.x = clamp((ev.clientX - svgRect.left) * sx, margin, width - margin);
        node.y = clamp((ev.clientY - svgRect.top) * sy, margin, height - margin);
        if (!graphAnimation) graphAnimation = requestAnimationFrame(tick);
      };
      const onUp = () => {
        node.pinned = false;
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };
      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    });
    els.graph.append(g);
    return { g, node };
  });

  function updatePositions() {
    for (const { line, lbl, edge } of edgeEls) {
      const s = edge.sourceNode;
      const t = edge.targetNode;
      line.setAttribute("x1", s.x); line.setAttribute("y1", s.y);
      line.setAttribute("x2", t.x); line.setAttribute("y2", t.y);
      lbl.setAttribute("x", (s.x + t.x) / 2);
      lbl.setAttribute("y", (s.y + t.y) / 2 - 8);
    }
    for (const { g, node } of nodeEls) {
      g.setAttribute("transform", `translate(${node.x},${node.y})`);
    }
  }

  function tick() {
    graphAnimation = null;
    for (let i = 0; i < 4; i++) physicsStep(nodes, allEdges, width, height, margin);
    updatePositions();
    const energy = nodes.reduce((s, n) => s + n.vx * n.vx + n.vy * n.vy, 0);
    if (energy > 0.08) graphAnimation = requestAnimationFrame(tick);
  }

  updatePositions();
  graphAnimation = requestAnimationFrame(tick);
}

function physicsStep(nodes, edges, width, height, margin) {
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i];
      const b = nodes[j];
      if (a.pinned && b.pinned) continue;
      const dx = a.x - b.x || 0.01;
      const dy = a.y - b.y || 0.01;
      const dist2 = Math.max(dx * dx + dy * dy, 100);
      const f = 2200 / dist2;
      if (!a.pinned) { a.vx += dx * f; a.vy += dy * f; }
      if (!b.pinned) { b.vx -= dx * f; b.vy -= dy * f; }
    }
  }
  for (const { sourceNode: s, targetNode: t } of edges) {
    const dx = t.x - s.x;
    const dy = t.y - s.y;
    const dist = Math.max(Math.hypot(dx, dy), 1);
    const f = (dist - 160) * 0.04;
    const fx = (dx / dist) * f;
    const fy = (dy / dist) * f;
    if (!s.pinned) { s.vx += fx; s.vy += fy; }
    if (!t.pinned) { t.vx -= fx; t.vy -= fy; }
  }
  const cx = width / 2;
  const cy = height / 2;
  for (const node of nodes) {
    if (node.pinned) continue;
    node.vx += (cx - node.x) * 0.004;
    node.vy += (cy - node.y) * 0.004;
    if (node.x < margin) node.vx += (margin - node.x) * 0.3;
    else if (node.x > width - margin) node.vx -= (node.x - (width - margin)) * 0.3;
    if (node.y < margin) node.vy += (margin - node.y) * 0.3;
    else if (node.y > height - margin) node.vy -= (node.y - (height - margin)) * 0.3;
    node.vx *= 0.82;
    node.vy *= 0.82;
    node.x = clamp(node.x + node.vx, margin, width - margin);
    node.y = clamp(node.y + node.vy, margin, height - margin);
  }
}

function renderLinks(item) {
  const senses = allSenses(item);
  const senseById = new Map(senses.map((sense) => [sense.id, sense]));
  const links = Object.values(item.links || {});
  const existingRelations = item.existing_relations || [];
  if (!links.length && !existingRelations.length) {
    els.linksList.textContent = "No links saved or already present in the Wordnet.";
    return;
  }
  els.linksList.innerHTML = "";
  if (links.length) {
    const heading = document.createElement("div");
    heading.className = "link-heading";
    heading.textContent = "Saved annotation links";
    els.linksList.append(heading);
  }
  for (const link of links) {
    const row = document.createElement("div");
    row.className = "link";
    row.innerHTML = `
      <span>${escapeHtml(labelFor(senseById.get(link.source)))}</span>
      <span class="link-type">${escapeHtml(link.type)}</span>
      <span>${escapeHtml(labelFor(senseById.get(link.target)))}</span>
    `;
    els.linksList.append(row);
  }
  if (existingRelations.length) {
    const heading = document.createElement("div");
    heading.className = "link-heading";
    heading.textContent = "Existing WordNet relations";
    els.linksList.append(heading);
  }
  for (const relation of existingRelations) {
    const row = document.createElement("div");
    row.className = "link existing";
    row.innerHTML = `
      <span>${escapeHtml(labelFor(senseById.get(relation.source)))}</span>
      <span class="link-type">${escapeHtml(relation.type)} · ${escapeHtml(relation.level)}</span>
      <span>${escapeHtml(labelFor(senseById.get(relation.target)))}</span>
    `;
    els.linksList.append(row);
  }
}

function renderSelection(previewType = null) {
  const first = state.source ? labelFor(state.source) : "no first sense";
  const second = state.target ? labelFor(state.target) : "no second sense";
  const [a, b] = directedSelection();
  updateLinkButtonTitles(a, b);
  if (previewType && a && b) {
    els.selectionState.textContent = relationHint(previewType, a, b);
    return;
  }
  if (a && b) {
    els.selectionState.textContent = `Selection: A = ${labelFor(a)}; B = ${labelFor(b)}. Direction: A → B.`;
    return;
  }
  els.selectionState.textContent = `Selection: A = ${first}; B = ${second}.`;
}

async function saveLink(type) {
  const item = currentItem();
  if (!item || !state.source || !state.target) return;
  const [source, target] = directedSelection();
  const updated = await api(itemUrl(item, "link"), {
    source: source.id,
    target: target.id,
    type,
  });
  replaceCurrent(updated);
  render();
}

function directedSelection() {
  if (!state.source || !state.target) return [null, null];
  return els.direction.value === "reverse" ? [state.target, state.source] : [state.source, state.target];
}

function relationHint(type, a, b) {
  if (type === "hypernym") {
    return `Hypernym: A is hypernym, B is hyponym. A → B: ${labelFor(a)} → ${labelFor(b)}`;
  }
  if (type === "none") {
    return `None: remove the A → B link. A → B: ${labelFor(a)} → ${labelFor(b)}`;
  }
  return `${type}: A is source, B is target. A → B: ${labelFor(a)} → ${labelFor(b)}`;
}

function updateLinkButtonTitles(a, b) {
  document.querySelectorAll("[data-link-type]").forEach((button) => {
    const type = button.dataset.linkType;
    button.title = a && b ? relationHint(type, a, b) : staticRelationHint(type);
  });
}

function staticRelationHint(type) {
  if (type === "hypernym") return "Hypernym: A is hypernym, B is hyponym. Direction is A → B.";
  if (type === "none") return "None: remove the A → B link.";
  return `${type}: A is source, B is target. Direction is A → B.`;
}

async function markStatus(status) {
  const item = currentItem();
  if (!item) return;
  const updated = await api(itemUrl(item, "status"), { status });
  replaceCurrent(updated);
  await loadSessionSummaries();
  const next = firstOpenIndex(state.session, state.index + 1);
  state.index = next >= 0 ? next : Math.min(state.index + 1, state.session.items.length - 1);
  clearSelection();
  render();
}

async function saveSenseAnnotation(sense, patch) {
  const item = currentItem();
  if (!item) return;
  const existing = senseAnnotation(sense);
  const payload = {
    sense_id: sense.id,
    comment: patch.comment ?? existing.comment,
    bad_sense: patch.bad_sense ?? existing.bad_sense,
  };
  const updated = await api(itemUrl(item, "sense"), payload);
  replaceCurrent(updated);
  render();
}

function itemUrl(item, action) {
  return `/api/sessions/${encodeURIComponent(state.session.id)}/items/${encodeURIComponent(item.lemma)}/${action}`;
}

function currentItem() {
  return state.session?.items[state.index] || null;
}

function replaceCurrent(item) {
  state.session.items[state.index] = item;
}

function move(delta) {
  state.index = Math.max(0, Math.min(state.session.items.length - 1, state.index + delta));
  clearSelection();
  render();
}

function firstOpenIndex(session, start = 0) {
  const index = session.items.findIndex((item, i) => i >= start && item.status === "open");
  return index >= 0 ? index : 0;
}

function clearSelection() {
  state.source = null;
  state.target = null;
}

function selectSense(sense) {
  if (!state.source || (state.source && state.target)) {
    state.source = sense;
    state.target = null;
    return;
  }
  if (state.source.id === sense.id) {
    state.source = null;
    return;
  }
  state.target = sense;
}

function showMessage(text) {
  els.message.textContent = text;
  els.message.classList.remove("hidden");
  els.annotation.classList.add("hidden");
}

function selectedClass(id) {
  return state.source?.id === id || state.target?.id === id ? "selected" : "";
}

function linkedClass(id, links) {
  for (const link of Object.values(links || {})) {
    if (link.source === id || link.target === id) {
      return `linked-${link.type}`;
    }
  }
  return "";
}

function allSenses(item) {
  if (item.all_senses?.length) return item.all_senses;
  const byId = new Map();
  for (const sense of [...(item.source_senses || []), ...(item.target_senses || [])]) {
    byId.set(sense.id, sense);
  }
  return [...byId.values()].sort((a, b) => a.id.localeCompare(b.id));
}

function senseRole(sense) {
  const item = currentItem();
  const inSource = item.source_senses.some((candidate) => candidate.id === sense.id);
  const inTarget = item.target_senses.some((candidate) => candidate.id === sense.id);
  if (inSource && inTarget) return "both";
  if (inSource) return "source";
  if (inTarget) return "target";
  return "other";
}

function senseBadges(sense) {
  const badges = [];
  if (sense.projected) badges.push('<span class="badge projected">EXTENDED</span>');
  if (senseAnnotation(sense).bad_sense) badges.push('<span class="badge bad">BAD</span>');
  return badges.length ? `<div class="badges">${badges.join("")}</div>` : "";
}

function senseAnnotation(sense) {
  const item = currentItem();
  return item?.sense_annotations?.[sense.id] || { comment: "", bad_sense: false };
}

function senseIliLink(sense) {
  const ili = sense.synset.ili;
  if (!ili) return '<span class="sense-ili"></span>';
  const url = cygnetUrl(ili);
  return `<a class="sense-ili" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" title="Open ${escapeHtml(ili)} in Cygnet">${escapeHtml(ili)} <span aria-hidden="true">🦢</span></a>`;
}

function cygnetUrl(ili) {
  return `https://cygnet.maudslay.eu/#/search?q=${encodeURIComponent(ili)}`;
}

function labelFor(sense) {
  if (!sense) return "";
  return `#${senseNumber(sense)} ${sense.synset.lemmas.join(", ")} (${sense.synset.ili})`;
}

function shortLabel(sense) {
  const lemma = sense.synset.lemmas[0] || sense.lemma || sense.id;
  return lemma.length > 14 ? `${lemma.slice(0, 12)}...` : lemma;
}

function senseNumber(sense) {
  const item = currentItem();
  if (!item) return "?";
  const index = allSenses(item).findIndex((candidate) => candidate.id === sense.id);
  return index >= 0 ? String(index + 1) : "?";
}

function statusLabel(status) {
  return {
    done: "DONE",
    incomplete: "PART",
    ignore: "IGNORE",
    open: "--",
  }[status || "open"] || "--";
}

function linkColor(type) {
  return {
    metaphor: "#8b31d6",
    metonymy: "#d64b3c",
    hypernym: "#18794e",
    other: "#6a5d00",
  }[type] || "#4d5663";
}

function svgEl(name, attrs) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs || {})) {
    element.setAttribute(key, value);
  }
  return element;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}
