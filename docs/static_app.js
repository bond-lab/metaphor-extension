const TRANSLATIONS_KEY = "metaphor-extension:show-translations";

const state = {
  session: null,
  index: 0,
  source: null,
  target: null,
  showTranslations: JSON.parse(localStorage.getItem(TRANSLATIONS_KEY) || "false"),
};

const els = {
  form: document.querySelector("#search-form"),
  openSession: document.querySelector("#open-session"),
  exportSession: document.querySelector("#export-session"),
  importAnnotations: document.querySelector("#import-annotations"),
  clearLocal: document.querySelector("#clear-local"),
  localState: document.querySelector("#local-state"),
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

els.form.addEventListener("submit", (event) => event.preventDefault());

els.openSession.addEventListener("change", openSessionFile);
els.exportSession.addEventListener("click", exportSession);
els.importAnnotations.addEventListener("change", importAnnotations);
els.clearLocal.addEventListener("click", clearLocalAnnotations);

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
  item.comment = els.comment.value;
  saveLocalAnnotations();
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

init();

async function init() {
  els.exportSession.disabled = true;
  els.clearLocal.disabled = true;
  const remembered = loadRememberedSession();
  if (remembered) {
    loadSession(remembered);
    return;
  }
  renderLocalState();
}

function render() {
  if (!state.session) return;
  renderQueue();
  renderLocalState();
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
  els.exportSession.disabled = false;
  els.clearLocal.disabled = false;
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

function setLink(item, source, target, type) {
  const key = `${source}::${target}`;
  item.links = item.links || {};
  if (type === "none") {
    delete item.links[key];
    return;
  }
  item.links[key] = { source, target, type };
}

function renderSenses(container, senses, links) {
  container.innerHTML = "";
  for (const [index, sense] of senses.entries()) {
    const card = document.createElement("article");
    const linkedType = linkedClass(sense.id, links);
    const annotation = senseAnnotation(sense);
    card.className = `sense ${selectedClass(sense.id)} ${linkedType} ${annotation.bad_sense ? "bad-sense" : ""}`;
    card.innerHTML = `
      <div class="sense-main" role="button" tabindex="0">
        <div class="sense-topline">
          <span class="sense-number">${index + 1}</span>
          <strong>${escapeHtml(sense.synset.lemmas.join(", "))}</strong>
          ${senseIliLink(sense)}
        </div>
        <div class="meta">${escapeHtml(sense.id)} · ${escapeHtml(sense.synset.pos || "")}</div>
        <div class="def">${escapeHtml(sense.synset.definition || "")}</div>
        ${state.showTranslations && sense.display_synset ? `<div class="def def-reference">${escapeHtml(sense.display_synset.lemmas.join(", "))} — ${escapeHtml(sense.display_synset.definition)}</div>` : ""}
        ${senseBadges(sense)}
      </div>
      <div class="sense-annotation">
        <label class="bad-sense-toggle">
          <input type="checkbox" data-sense-bad="${escapeHtml(sense.id)}" ${annotation.bad_sense ? "checked" : ""}>
          bad-sense
        </label>
        <textarea data-sense-comment="${escapeHtml(sense.id)}" rows="2" placeholder="sense comment">${escapeHtml(annotation.comment)}</textarea>
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
  const width = 680;
  const height = 420;
  const senses = allSenses(item);
  const nodes = senses.map((sense, index) => ({
    id: sense.id,
    role: senseRole(sense),
    sense,
    x: width * (0.22 + (index % 3) * 0.28),
    y: ((Math.floor(index / 3) + 1) * height) / (Math.ceil(senses.length / 3) + 1),
  }));
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const links = Object.values(item.links || {}).map((link) => ({
    ...link,
    sourceNode: byId.get(link.source),
    targetNode: byId.get(link.target),
  })).filter((link) => link.sourceNode && link.targetNode);
  const existingRelations = (item.existing_relations || []).map((relation) => ({
    ...relation,
    sourceNode: byId.get(relation.source),
    targetNode: byId.get(relation.target),
  })).filter((relation) => relation.sourceNode && relation.targetNode);

  runForceLayout(nodes, [...links, ...existingRelations], width, height);
  els.graph.innerHTML = `<defs>${["metaphor", "metonymy", "hypernym", "other"].map((type) => `
    <marker id="arrow-${type}" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,-5L10,0L0,5" fill="${linkColor(type)}"></path>
    </marker>
  `).join("")}
    <marker id="arrow-existing" viewBox="0 -5 10 10" refX="28" refY="0" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0,-5L10,0L0,5" fill="#7a828e"></path>
    </marker>
  </defs>`;

  for (const relation of existingRelations) {
    els.graph.append(svgEl("line", {
      class: "graph-link existing",
      x1: relation.sourceNode.x,
      y1: relation.sourceNode.y,
      x2: relation.targetNode.x,
      y2: relation.targetNode.y,
      stroke: "#7a828e",
      "marker-end": "url(#arrow-existing)",
    }));
    const label = svgEl("text", {
      x: (relation.sourceNode.x + relation.targetNode.x) / 2,
      y: (relation.sourceNode.y + relation.targetNode.y) / 2 + 12,
      fill: "#626a75",
      class: "graph-label existing",
    });
    label.textContent = relation.type;
    els.graph.append(label);
  }

  for (const link of links) {
    els.graph.append(svgEl("line", {
      class: "graph-link",
      x1: link.sourceNode.x,
      y1: link.sourceNode.y,
      x2: link.targetNode.x,
      y2: link.targetNode.y,
      stroke: linkColor(link.type),
      "marker-end": `url(#arrow-${link.type})`,
    }));
    const label = svgEl("text", {
      x: (link.sourceNode.x + link.targetNode.x) / 2,
      y: (link.sourceNode.y + link.targetNode.y) / 2 - 8,
      fill: linkColor(link.type),
      class: "graph-label",
    });
    label.textContent = link.type;
    els.graph.append(label);
  }

  for (const node of nodes) {
    const selected = selectedClass(node.sense.id) ? " selected" : "";
    const group = svgEl("g", {
      class: `graph-node ${node.role}${selected}`,
      transform: `translate(${node.x}, ${node.y})`,
    });
    group.append(svgEl("rect", { class: "graph-box", x: -48, y: -17, width: 96, height: 34, rx: 5 }));
    const label = svgEl("text", { class: "graph-label", y: 4 });
    label.textContent = `${senseNumber(node.sense)} - ${shortLabel(node.sense)}`;
    group.append(label);
    group.addEventListener("click", () => {
      selectSense(node.sense);
      render();
    });
    els.graph.append(group);
  }
}

function runForceLayout(nodes, links, width, height) {
  for (const node of nodes) {
    node.vx = 0;
    node.vy = 0;
  }
  for (let step = 0; step < 140; step++) {
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = a.x - b.x || 0.01;
        const dy = a.y - b.y || 0.01;
        const dist2 = Math.max(dx * dx + dy * dy, 100);
        const force = 700 / dist2;
        a.vx += dx * force;
        a.vy += dy * force;
        b.vx -= dx * force;
        b.vy -= dy * force;
      }
    }
    for (const link of links) {
      const dx = link.targetNode.x - link.sourceNode.x;
      const dy = link.targetNode.y - link.sourceNode.y;
      const dist = Math.max(Math.hypot(dx, dy), 1);
      const force = (dist - 230) * 0.01;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      link.sourceNode.vx += fx;
      link.sourceNode.vy += fy;
      link.targetNode.vx -= fx;
      link.targetNode.vy -= fy;
    }
    for (const node of nodes) {
      const anchorX = node.role === "source" ? width * 0.22 : node.role === "target" ? width * 0.78 : width * 0.5;
      node.vx += (anchorX - node.x) * 0.015;
      node.x = clamp(node.x + node.vx, 40, width - 40);
      node.y = clamp(node.y + node.vy, 40, height - 40);
      node.vx *= 0.72;
      node.vy *= 0.72;
    }
  }
}

function renderLinks(item) {
  const senseById = new Map(allSenses(item).map((sense) => [sense.id, sense]));
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
  setLink(item, source.id, target.id, type);
  saveLocalAnnotations();
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
  item.status = status;
  saveLocalAnnotations();
  const next = firstOpenIndex(state.session, state.index + 1);
  state.index = next >= 0 ? next : Math.min(state.index + 1, state.session.items.length - 1);
  clearSelection();
  render();
}

function saveSenseAnnotation(sense, patch) {
  const item = currentItem();
  if (!item) return;
  const existing = senseAnnotation(sense);
  const annotation = {
    comment: patch.comment ?? existing.comment,
    bad_sense: patch.bad_sense ?? existing.bad_sense,
  };
  item.sense_annotations = item.sense_annotations || {};
  if (annotation.comment || annotation.bad_sense) {
    item.sense_annotations[sense.id] = annotation;
  } else {
    delete item.sense_annotations[sense.id];
  }
  saveLocalAnnotations();
  render();
}

async function openSessionFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const session = JSON.parse(await file.text());
  loadSession(session);
  event.target.value = "";
}

function loadSession(session) {
  rememberSession(session);
  state.session = applyLocalAnnotations(session, loadLocalAnnotation(session.id));
  state.index = firstOpenIndex(state.session);
  clearSelection();
  render();
}

function storageKey(sessionId) {
  return `metaphor-extension:${sessionId}:annotations`;
}

function sessionStorageKey() {
  return "metaphor-extension:current-session";
}

function rememberSession(session) {
  localStorage.setItem(sessionStorageKey(), JSON.stringify(session));
}

function loadRememberedSession() {
  const raw = localStorage.getItem(sessionStorageKey());
  return raw ? JSON.parse(raw) : null;
}

function loadLocalAnnotation(sessionId) {
  const raw = localStorage.getItem(storageKey(sessionId));
  return raw ? JSON.parse(raw) : null;
}

function saveLocalAnnotations() {
  if (!state.session) return;
  rememberSession(state.session);
  const annotation = {
    id: state.session.id,
    name: state.session.name,
    saved_at: new Date().toISOString(),
    items: {},
  };
  for (const item of state.session.items) {
    if (hasItemAnnotations(item)) {
      annotation.items[item.lemma] = {
        status: item.status,
        comment: item.comment || "",
        links: item.links || {},
        sense_annotations: item.sense_annotations || {},
      };
    }
  }
  localStorage.setItem(storageKey(state.session.id), JSON.stringify(annotation));
}

function applyLocalAnnotations(session, annotation) {
  if (!annotation?.items) return session;
  const byLemma = annotation.items;
  for (const item of session.items) {
    const saved = byLemma[item.lemma];
    if (!saved) continue;
    item.status = saved.status || "open";
    item.comment = saved.comment || "";
    item.links = saved.links || {};
    item.sense_annotations = saved.sense_annotations || {};
  }
  return session;
}

function exportSession() {
  if (!state.session) return;
  const payload = {
    ...state.session,
    exported_at: new Date().toISOString(),
  };
  const blob = new Blob([JSON.stringify(payload, null, 2) + "\n"], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${safeFilename(state.session.name || state.session.id)}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

async function importAnnotations(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const payload = JSON.parse(await file.text());
  const annotation = annotationFromSession(payload);
  if (annotation?.id) localStorage.setItem(storageKey(annotation.id), JSON.stringify(annotation));
  event.target.value = "";
  if (state.session?.id === annotation?.id) loadSession(state.session);
}

async function clearLocalAnnotations() {
  if (!state.session) return;
  localStorage.removeItem(storageKey(state.session.id));
  localStorage.removeItem(sessionStorageKey());
  for (const item of state.session.items) {
    item.status = "open";
    item.comment = "";
    item.links = {};
    item.sense_annotations = {};
  }
  render();
}

function annotationFromSession(session) {
  if (session.sessions) return null;
  return {
    id: session.id,
    name: session.name,
    saved_at: session.exported_at || new Date().toISOString(),
    items: Object.fromEntries(
      (session.items || [])
        .filter(hasItemAnnotations)
        .map((item) => [
          item.lemma,
          {
            status: item.status || "open",
            comment: item.comment || "",
            links: item.links || {},
            sense_annotations: item.sense_annotations || {},
          },
        ])
    ),
  };
}

function hasItemAnnotations(item) {
  return (
    item.status !== "open" ||
    item.comment ||
    Object.keys(item.links || {}).length ||
    Object.keys(item.sense_annotations || {}).length
  );
}

function renderLocalState() {
  if (!state.session) {
    els.localState.textContent = "--";
    return;
  }
  const annotation = loadLocalAnnotation(state.session.id);
  els.localState.textContent = annotation ? "saved locally" : "no local edits";
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
  const role = senseRole(sense);
  const badges = [];
  if (role === "source" || role === "both") badges.push('<span class="badge source">SOURCE ILI</span>');
  if (role === "target" || role === "both") badges.push('<span class="badge target">TARGET ILI</span>');
  if (sense.projected) badges.push('<span class="badge projected">EXTENDED</span>');
  if (senseAnnotation(sense).bad_sense) badges.push('<span class="badge bad">BAD-SENSE</span>');
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

function safeFilename(value) {
  return String(value).replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "") || "session";
}
