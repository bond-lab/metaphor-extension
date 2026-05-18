const state = {
  session: null,
  index: 0,
  source: null,
  target: null,
};

const els = {
  form: document.querySelector("#search-form"),
  message: document.querySelector("#message"),
  annotation: document.querySelector("#annotation"),
  queueTitle: document.querySelector("#queue-title"),
  queueCount: document.querySelector("#queue-count"),
  queueList: document.querySelector("#queue-list"),
  lemmaTitle: document.querySelector("#lemma-title"),
  progress: document.querySelector("#progress"),
  sourceTitle: document.querySelector("#source-title"),
  targetTitle: document.querySelector("#target-title"),
  sourceSenses: document.querySelector("#source-senses"),
  targetSenses: document.querySelector("#target-senses"),
  selectionState: document.querySelector("#selection-state"),
  linksList: document.querySelector("#links-list"),
  comment: document.querySelector("#comment"),
  prev: document.querySelector("#prev"),
  next: document.querySelector("#next"),
  finished: document.querySelector("#finished"),
  incomplete: document.querySelector("#incomplete"),
};

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("Loading Wordnet and computing hyponym overlap...");
  const payload = Object.fromEntries(new FormData(els.form).entries());
  try {
    const session = await api("/api/search", payload);
    state.session = session;
    state.index = firstOpenIndex(session);
    clearSelection();
    render();
  } catch (error) {
    showMessage(error.message);
  }
});

document.querySelectorAll("[data-link-type]").forEach((button) => {
  button.addEventListener("click", () => saveLink(button.dataset.linkType));
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

async function api(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

function render() {
  if (!state.session) return;
  renderQueue();
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
  els.sourceTitle.textContent = `Source senses under ${state.session.source_ili}`;
  els.targetTitle.textContent = `Target senses under ${state.session.target_ili}`;
  els.comment.value = item.comment || "";
  renderSenses(els.sourceSenses, item.source_senses, "source", item.links);
  renderSenses(els.targetSenses, item.target_senses, "target", item.links);
  renderLinks(item);
  renderSelection();
  els.prev.disabled = state.index === 0;
  els.next.disabled = state.index >= state.session.items.length - 1;
}

function renderQueue() {
  const total = state.session.items.length;
  const done = state.session.items.filter((item) => item.status !== "open").length;
  els.queueTitle.textContent = state.session.lexicon || state.session.wordnet;
  els.queueCount.textContent = `${done}/${total}`;
  els.queueList.innerHTML = "";
  state.session.items.forEach((item, index) => {
    const button = document.createElement("button");
    button.className = `queue-item ${index === state.index ? "active" : ""}`;
    button.innerHTML = `<span>${escapeHtml(item.lemma)}</span><span class="status">${escapeHtml(item.status)}</span>`;
    button.addEventListener("click", () => {
      state.index = index;
      clearSelection();
      render();
    });
    els.queueList.append(button);
  });
}

function renderSenses(container, senses, side, links) {
  container.innerHTML = "";
  for (const sense of senses) {
    const button = document.createElement("button");
    const linkedType = linkedClass(sense.id, side, links);
    button.className = `sense ${selectedClass(sense.id, side)} ${linkedType}`;
    button.innerHTML = `
      <strong>${escapeHtml(sense.synset.lemmas.join(", "))}</strong>
      <div class="meta">${escapeHtml(sense.id)} · ${escapeHtml(sense.synset.ili || "")} · ${escapeHtml(sense.synset.pos || "")}</div>
      <div class="def">${escapeHtml(sense.synset.definition || "")}</div>
    `;
    button.addEventListener("click", () => {
      state[side] = sense;
      render();
    });
    container.append(button);
  }
}

function renderLinks(item) {
  const sourceById = new Map(item.source_senses.map((sense) => [sense.id, sense]));
  const targetById = new Map(item.target_senses.map((sense) => [sense.id, sense]));
  const links = Object.values(item.links || {});
  if (!links.length) {
    els.linksList.textContent = "No links saved for this word.";
    return;
  }
  els.linksList.innerHTML = "";
  for (const link of links) {
    const row = document.createElement("div");
    row.className = "link";
    row.innerHTML = `
      <span>${escapeHtml(labelFor(sourceById.get(link.source)))}</span>
      <span class="link-type">${escapeHtml(link.type)}</span>
      <span>${escapeHtml(labelFor(targetById.get(link.target)))}</span>
    `;
    els.linksList.append(row);
  }
}

function renderSelection() {
  const source = state.source ? labelFor(state.source) : "no source";
  const target = state.target ? labelFor(state.target) : "no target";
  els.selectionState.textContent = `Selection: ${source} -> ${target}`;
}

async function saveLink(type) {
  const item = currentItem();
  if (!item || !state.source || !state.target) return;
  const updated = await api(itemUrl(item, "link"), {
    source: state.source.id,
    target: state.target.id,
    type,
  });
  replaceCurrent(updated);
  render();
}

async function markStatus(status) {
  const item = currentItem();
  if (!item) return;
  const updated = await api(itemUrl(item, "status"), { status });
  replaceCurrent(updated);
  const next = firstOpenIndex(state.session, state.index + 1);
  state.index = next >= 0 ? next : Math.min(state.index + 1, state.session.items.length - 1);
  clearSelection();
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

function showMessage(text) {
  els.message.textContent = text;
  els.message.classList.remove("hidden");
  els.annotation.classList.add("hidden");
}

function selectedClass(id, side) {
  return state[side]?.id === id ? "selected" : "";
}

function linkedClass(id, side, links) {
  for (const link of Object.values(links || {})) {
    if ((side === "source" && link.source === id) || (side === "target" && link.target === id)) {
      return `linked-${link.type}`;
    }
  }
  return "";
}

function labelFor(sense) {
  if (!sense) return "";
  return `${sense.synset.lemmas.join(", ")} (${sense.synset.ili})`;
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
