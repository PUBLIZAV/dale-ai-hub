const state = {
  metaPortfolio: {},
  aiEngines: [],
  clients: [],
  posts: [],
  configuredKeys: {},
  activeFilter: "all",
  searchQuery: "",
  activeStudioClientId: null,
  lastGeneratedPost: null,
  queueClientFilter: "all"
};

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function showToast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => t.classList.add("hidden"), 3600);
}

function getAiLabel(aiId) {
  const map = {
    claude: "Claude",
    chatgpt: "ChatGPT",
    kimi: "Kimi",
    manus: "Manus",
    gemini: "Gemini"
  };
  return map[aiId] || aiId;
}

function getFallbackAvatar(name) {
  const initials = String(name || "C")
    .split(/\s+/)
    .slice(0, 2)
    .map(w => w[0] || "")
    .join("")
    .toUpperCase();
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="100%" height="100%" fill="#312e81"/><text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="#e0e7ff" font-family="sans-serif" font-size="28" font-weight="bold">${escapeHtml(initials)}</text></svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

async function fetchState() {
  let data = window.__INITIAL_HUB_STATE__ || {};
  try {
    const res = await fetch("/api/state");
    if (res.ok) {
      data = await res.json();
    }
  } catch (_) {
    // Running directly from file:// — use embedded bundle
  }
  state.metaPortfolio = data.meta_portfolio || {};
  state.aiEngines = data.ai_engines || [];
  state.clients = data.clients || [];
  state.posts = data.posts || [];
  state.configuredKeys = data.configured_keys || {};

  if (!state.activeStudioClientId && state.clients.length > 0) {
    state.activeStudioClientId = state.clients[0].id;
  }
  if (!state.lastGeneratedPost && state.posts.length > 0) {
    state.lastGeneratedPost = state.posts[0];
  }

  renderAll();
}

function buildLocalPost(client, topic, fmt, selectedAi) {
  const ag = client.agent || {};
  const pillars = ag.content_pillars || ["Contenido de Valor", "Servicio Garantizado", "Atención Inmediata"];
  const cta = ag.default_cta || "📲 Envíanos mensaje directo.";
  const cleanTopic = (topic || "").trim() || `Campaña estratégica de ${pillars[0]} para ${client.name}`;
  const leadAi = selectedAi === "council" ? (ag.primary_ai || "claude") : selectedAi;
  const supportAi = ag.secondary_ai || "gemini";
  const hook = `🔥 ¡Atención ${client.location}! Descubre cómo ${client.name} transforma ${cleanTopic.toLowerCase()} con atención de primer nivel.`;
  const copy = `${hook}\n\nEn ${client.name} (${client.category}) cuidamos cada detalle para ti:\n\n✅ ${pillars[0]}\n✅ ${pillars[1] || "Calidad y Confianza"}\n✅ ${pillars[2] || "Atención personalizada"}\n\n${cta}\n\n#${client.name.replace(/[^a-zA-Z0-9]/g, "").slice(0, 20)} #Mexicali #DaleMasIA`;
  return {
    id: `post_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
    client_id: client.id,
    asset_id: client.asset_id,
    client_name: client.name,
    category: client.category,
    platforms: (client.ig_id || client.ig_username) ? ["facebook", "instagram"] : ["facebook"],
    format: fmt,
    status: "review",
    scheduled_for: new Date(Date.now() + 86400000).toISOString().slice(0, 10) + " 13:00",
    ai_lead: leadAi,
    ai_support: supportAi,
    topic: cleanTopic,
    hook,
    copy,
    visual_prompt: `[${fmt} — Dirigido por Gemini]: Toma principal de '${cleanTopic}' en ${client.location}, estética profesional de ${client.name}, texto dinámico en pantalla y cierre con CTA.`,
    council_notes: {
      claude: `Alineó el tono de voz (${(ag.brand_voice || "").slice(0, 60)}...)`,
      chatgpt: `Optimizó el hook de conversión y el CTA`,
      kimi: `Validó contexto local en ${client.location}`,
      manus: `Preparó ruta de publicación para Asset ID ${client.asset_id}`,
      gemini: `Diseñó guion visual para formato ${fmt}`
    }
  };
}

function renderAll() {
  renderKpis();
  renderClientsGrid();
  renderStudioSelectors();
  renderStudioPreview();
  renderKanbanQueue();
  renderAiHub();
}

function renderKpis() {
  const totalClients = state.clients.length;
  const igClients = state.clients.filter(c => c.ig_id || c.ig_username).length;
  const totalMsgs = state.clients.reduce((acc, c) => acc + (c.unseen_messages || 0), 0);

  document.getElementById("nav-count-clients").textContent = totalClients;
  document.getElementById("nav-count-posts").textContent = state.posts.length;
  document.getElementById("kpi-total-clients").textContent = totalClients;
  document.getElementById("kpi-ig-clients").textContent = igClients;
  document.getElementById("kpi-unseen-msgs").textContent = totalMsgs;
}

function getFilteredClients() {
  return state.clients.filter(c => {
    const q = state.searchQuery.trim().toLowerCase();
    if (q) {
      const hay = `${c.name} ${c.category} ${c.location} ${c.asset_id} ${c.ig_name || ""}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    const f = state.activeFilter;
    if (f === "all") return true;
    if (f === "ig") return Boolean(c.ig_id || c.ig_username);
    if (f === "msgs") return (c.unseen_messages || 0) > 0;
    return c.category.toLowerCase().includes(f.toLowerCase());
  });
}

function renderClientsGrid() {
  const grid = document.getElementById("clients-grid");
  const list = getFilteredClients();

  if (list.length === 0) {
    grid.innerHTML = `<div class="panel"><p>No se encontraron cuentas con ese filtro.</p></div>`;
    return;
  }

  grid.innerHTML = list.map(c => {
    const ag = c.agent || {};
    const pAi = ag.primary_ai || "claude";
    const sAi = ag.secondary_ai || "gemini";
    const fallback = getFallbackAvatar(c.name);
    const avatarSrc = c.fb_avatar || fallback;
    const igBadge = (c.ig_id || c.ig_username)
      ? `<span class="tag ig-linked">📸 IG: ${escapeHtml(c.ig_name || c.ig_username)}</span>`
      : `<span class="tag">FB Page</span>`;
    const msgBadge = (c.unseen_messages || 0) > 0
      ? `<span class="tag msg-alert">💬 ${c.unseen_messages} msgs sin leer</span>`
      : "";
    const updBadge = (c.unseen_updates || 0) > 0
      ? `<span class="tag">🔔 ${c.unseen_updates} notif</span>`
      : "";

    return `
      <article class="client-card">
        <div class="client-top">
          <div class="avatar-wrap">
            <img class="client-avatar" src="${escapeHtml(avatarSrc)}" alt="${escapeHtml(c.name)}" loading="lazy" onerror="this.onerror=null;this.src='${fallback}';" />
            ${(c.ig_id || c.ig_username) ? `<span class="ig-sub-avatar" title="Instagram Vinculado">IG</span>` : ""}
          </div>
          <div class="client-meta">
            <div class="client-name" title="${escapeHtml(c.name)}">${escapeHtml(c.name)}</div>
            <div class="client-cat">${escapeHtml(c.category)} · ${escapeHtml(c.location)}</div>
            <div class="badge-row">
              ${igBadge}
              ${msgBadge}
              ${updBadge}
            </div>
          </div>
        </div>

        <div class="agent-strip">
          <div class="agent-strip-header">
            <span>🤖 ${escapeHtml(ag.agent_name || "Agente Especializado")}</span>
            <div style="display:flex; gap:4px;">
              <span class="ai-badge ai-${escapeHtml(pAi)}">${escapeHtml(getAiLabel(pAi))}</span>
              <span class="ai-badge ai-${escapeHtml(sAi)}">+${escapeHtml(getAiLabel(sAi))}</span>
            </div>
          </div>
          <div class="agent-voice-preview">
            <strong>Voz:</strong> ${escapeHtml(ag.brand_voice || "")}
          </div>
          <div style="font-size:11px; color:var(--text-muted);">
            <strong>Pilares:</strong> ${escapeHtml((ag.content_pillars || []).slice(0, 3).join(" · "))}
          </div>
        </div>

        <div class="card-actions">
          <button class="btn btn-primary btn-sm" onclick="openStudioForClient('${escapeHtml(c.id)}')">
            ✨ Crear Contenido
          </button>
          <button class="btn btn-sm" onclick="openAgentModal('${escapeHtml(c.id)}')">
            ⚙️ ADN Agente
          </button>
          <a class="btn btn-sm" href="${escapeHtml(c.business_suite_url)}" target="_blank" rel="noopener" title="Asset ID: ${escapeHtml(c.asset_id)}">
            📊 Suite
          </a>
          <a class="btn btn-sm" href="${escapeHtml(c.reels_composer_url)}" target="_blank" rel="noopener">
            🎬 Reels
          </a>
        </div>
      </article>
    `;
  }).join("");
}

function renderStudioSelectors() {
  const sel = document.getElementById("studio-client-select");
  const qSel = document.getElementById("queue-client-filter");

  sel.innerHTML = state.clients.map(c => `
    <option value="${escapeHtml(c.id)}" ${c.id === state.activeStudioClientId ? "selected" : ""}>
      ${escapeHtml(c.name)} (${escapeHtml(c.category)}) ${(c.ig_id || c.ig_username) ? "· [FB+IG]" : "· [FB]"}
    </option>
  `).join("");

  qSel.innerHTML = `<option value="all">Todos los Clientes (${state.clients.length})</option>` +
    state.clients.map(c => `
      <option value="${escapeHtml(c.id)}" ${c.id === state.queueClientFilter ? "selected" : ""}>
        ${escapeHtml(c.name)}
      </option>
    `).join("");

  renderStudioAgentDna();
}

function renderStudioAgentDna() {
  const box = document.getElementById("studio-agent-dna");
  const client = state.clients.find(c => c.id === state.activeStudioClientId);
  if (!client) return;
  const ag = client.agent || {};
  box.innerHTML = `
    <div class="agent-strip-header">
      <span>🎯 Especialización Activa: <strong>${escapeHtml(client.name)}</strong> (Asset ID: <code>${escapeHtml(client.asset_id)}</code>)</span>
      <div style="display:flex; gap:6px;">
        <span class="ai-badge ai-${escapeHtml(ag.primary_ai)}">Líder: ${escapeHtml(getAiLabel(ag.primary_ai))}</span>
        <span class="ai-badge ai-${escapeHtml(ag.secondary_ai)}">Apoyo: ${escapeHtml(getAiLabel(ag.secondary_ai))}</span>
      </div>
    </div>
    <div style="font-size:12.5px; color:var(--text-secondary);">
      <strong>Tono de Voz:</strong> ${escapeHtml(ag.brand_voice)}<br/>
      <strong>Audiencia:</strong> ${escapeHtml(ag.target_audience)}<br/>
      <strong>Pilares:</strong> ${escapeHtml((ag.content_pillars || []).join(" | "))}
    </div>
  `;
}

function renderStudioPreview() {
  const container = document.getElementById("studio-preview-content");
  const p = state.lastGeneratedPost;
  if (!p) return;

  const client = state.clients.find(c => c.id === p.client_id || c.asset_id === p.asset_id) || {};
  const suiteUrl = client.business_suite_url || `https://business.facebook.com/latest/home?asset_id=${p.asset_id}`;
  const reelsUrl = client.reels_composer_url || `https://business.facebook.com/latest/reels_composer?asset_id=${p.asset_id}`;
  const notes = p.council_notes || {};

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <span class="tag">${escapeHtml(p.format)}</span>
        <span class="ai-badge ai-${escapeHtml(p.ai_lead)}">Líder: ${escapeHtml(getAiLabel(p.ai_lead))}</span>
        <span class="ai-badge ai-${escapeHtml(p.ai_support)}">Apoyo: ${escapeHtml(getAiLabel(p.ai_support))}</span>
      </div>
      <span style="font-size:12px; color:var(--text-secondary);">Programado: ${escapeHtml(p.scheduled_for)}</span>
    </div>

    <div class="post-card">
      <div style="font-weight:700; font-size:14px;">📌 ${escapeHtml(p.client_name)} — ${escapeHtml(p.topic)}</div>
      <div class="post-copy-preview" id="preview-copy-text">${escapeHtml(p.copy)}</div>
      <div style="font-size:12px; color:#93c5fd; background:rgba(59,130,246,0.1); padding:10px; border-radius:8px; border:1px solid rgba(59,130,246,0.25);">
        <strong>🎥 Dirección Visual / Guion (Gemini):</strong><br/>
        ${escapeHtml(p.visual_prompt)}
      </div>
    </div>

    <div class="council-box">
      <div style="font-size:12px; font-weight:700; text-transform:uppercase; color:var(--text-secondary);">
        🤝 Intervención del Consejo de las 5 IAs para este Cliente
      </div>
      ${["claude", "chatgpt", "kimi", "manus", "gemini"].map(ai => `
        <div class="council-item">
          <span class="ai-badge ai-${ai}" style="min-width:74px; justify-content:center;">${getAiLabel(ai)}</span>
          <span>${escapeHtml(notes[ai] || "Validado por el agente.")}</span>
        </div>
      `).join("")}
    </div>

    <div style="display:flex; flex-wrap:wrap; gap:8px;">
      <button class="btn btn-primary" onclick="copyAndLaunch('${escapeHtml(p.id)}', '${escapeHtml(suiteUrl)}')">
        📋 Copiar Copy + Abrir Business Suite (${escapeHtml(p.client_name.slice(0, 18))})
      </button>
      <button class="btn btn-emerald" onclick="updatePostStatus('${escapeHtml(p.id)}', 'approved')">
        ✅ Aprobar en Cola
      </button>
      <a class="btn" href="${escapeHtml(reelsUrl)}" target="_blank" rel="noopener">
        🎬 Subir Reel Directo
      </a>
    </div>
  `;
}

function renderKanbanQueue() {
  const board = document.getElementById("kanban-board");
  const columns = [
    { key: "draft", title: "📝 Borradores de Agentes" },
    { key: "review", title: "👀 En Revisión (Por Aprobar)" },
    { key: "approved", title: "✅ Aprobados / Programados" },
    { key: "published", title: "🚀 Publicados en Meta" }
  ];

  const filteredPosts = state.posts.filter(p =>
    state.queueClientFilter === "all" || p.client_id === state.queueClientFilter
  );

  board.innerHTML = columns.map(col => {
    const items = filteredPosts.filter(p => p.status === col.key);
    return `
      <div class="kanban-col">
        <div class="kanban-col-header">
          <span>${col.title}</span>
          <span class="nav-badge">${items.length}</span>
        </div>
        ${items.length === 0 ? `<p style="font-size:12px; color:var(--text-muted);">Sin publicaciones en esta etapa.</p>` : ""}
        ${items.map(p => {
          const suiteUrl = `https://business.facebook.com/latest/home?asset_id=${encodeURIComponent(p.asset_id)}`;
          return `
            <div class="post-card">
              <div style="display:flex; justify-content:space-between; align-items:center; gap:6px;">
                <strong style="font-size:13px;">${escapeHtml(p.client_name)}</strong>
                <span class="ai-badge ai-${escapeHtml(p.ai_lead)}">${escapeHtml(getAiLabel(p.ai_lead))}</span>
              </div>
              <div style="font-size:11.5px; color:var(--text-secondary);">
                ${escapeHtml(p.format)} · 🕒 ${escapeHtml(p.scheduled_for)}
              </div>
              <div class="post-copy-preview">${escapeHtml(p.copy)}</div>
              <div style="display:flex; flex-wrap:wrap; gap:6px;">
                ${col.key !== "approved" && col.key !== "published" ? `
                  <button class="btn btn-emerald btn-sm" onclick="updatePostStatus('${escapeHtml(p.id)}', 'approved')">
                    ✅ Aprobar
                  </button>
                ` : ""}
                <button class="btn btn-primary btn-sm" onclick="copyAndLaunch('${escapeHtml(p.id)}', '${escapeHtml(suiteUrl)}')">
                  🚀 Copiar y Publicar en Suite
                </button>
                ${col.key !== "published" ? `
                  <button class="btn btn-sm" onclick="updatePostStatus('${escapeHtml(p.id)}', 'published')">
                    ✔️ Marcar Publicado
                  </button>
                ` : ""}
              </div>
            </div>
          `;
        }).join("")}
      </div>
    `;
  }).join("");
}

function renderAiHub() {
  const aiList = document.getElementById("ai-engines-list");
  aiList.innerHTML = state.aiEngines.map(ai => {
    const assignedCount = state.clients.filter(c => c.agent?.primary_ai === ai.id).length;
    const supportCount = state.clients.filter(c => c.agent?.secondary_ai === ai.id).length;
    return `
      <div class="post-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="ai-badge ai-${escapeHtml(ai.id)}">${escapeHtml(ai.name)}</span>
            <code style="font-size:11.5px; color:var(--text-secondary);">${escapeHtml(ai.model)}</code>
          </div>
          <span class="tag">${assignedCount} Agentes Líder · ${supportCount} Co-Piloto</span>
        </div>
        <div style="font-size:13px; font-weight:600;">${escapeHtml(ai.role)}</div>
        <div style="font-size:12px; color:var(--text-secondary);">${escapeHtml(ai.specialty)}</div>
      </div>
    `;
  }).join("");

  const metaList = document.getElementById("meta-apps-list");
  const apps = state.metaPortfolio.meta_apps || [];
  metaList.innerHTML = apps.map(app => `
    <div class="post-card" style="flex-direction:row; justify-content:space-between; align-items:center;">
      <div>
        <div style="font-weight:700; font-size:13.5px;">${escapeHtml(app.name)}</div>
        <div style="font-size:12px; color:var(--text-secondary);">App ID: <code>${escapeHtml(app.app_id)}</code> · ${escapeHtml(app.role)}</div>
      </div>
      <a class="btn btn-sm" href="https://developers.facebook.com/apps/${encodeURIComponent(app.app_id)}/dashboard/" target="_blank" rel="noopener">
        Abrir en Meta Dev ↗
      </a>
    </div>
  `).join("");
}

function switchTab(tabName) {
  const updateDom = () => {
    document.querySelectorAll(".nav-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.tab === tabName);
    });
    document.querySelectorAll(".tab-view").forEach(sec => {
      sec.classList.toggle("hidden", sec.id !== `tab-${tabName}`);
    });
  };

  if (document.startViewTransition) {
    document.startViewTransition(updateDom);
  } else {
    updateDom();
  }
}

window.openStudioForClient = function(clientId) {
  state.activeStudioClientId = clientId;
  renderStudioSelectors();
  switchTab("studio");
};

window.openAgentModal = function(clientId) {
  const client = state.clients.find(c => c.id === clientId);
  if (!client) return;
  const ag = client.agent || {};
  document.getElementById("modal-agent-title").textContent = `Agente Especializado: ${client.name}`;
  document.getElementById("edit-agent-client-id").value = client.id;
  document.getElementById("edit-agent-primary-ai").value = ag.primary_ai || "claude";
  document.getElementById("edit-agent-secondary-ai").value = ag.secondary_ai || "gemini";
  document.getElementById("edit-agent-voice").value = ag.brand_voice || "";
  document.getElementById("edit-agent-audience").value = ag.target_audience || "";
  document.getElementById("edit-agent-pillars").value = (ag.content_pillars || []).join(", ");
  document.getElementById("edit-agent-cta").value = ag.default_cta || "";
  document.getElementById("edit-agent-prompt").value = ag.system_prompt || "";

  document.getElementById("modal-agent").showModal();
};

window.copyAndLaunch = async function(postId, url) {
  const post = state.posts.find(p => p.id === postId);
  if (post && navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(post.copy);
      showToast("📋 Copy copiado al portapapeles. Abriendo Meta Business Suite...");
    } catch (_) {
      showToast("Abriendo Meta Business Suite...");
    }
  }
  window.open(url, "_blank", "noopener");
};

window.updatePostStatus = async function(postId, status) {
  try {
    const res = await fetch("/api/posts/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ post_id: postId, status })
    });
    const data = await res.json();
    if (data.ok) {
      const idx = state.posts.findIndex(p => p.id === postId);
      if (idx !== -1) state.posts[idx] = data.post;
      if (state.lastGeneratedPost?.id === postId) state.lastGeneratedPost = data.post;
      renderAll();
      showToast(`Estado actualizado a: ${status.toUpperCase()}`);
      return;
    }
  } catch (_) {}
  const idx = state.posts.findIndex(p => p.id === postId);
  if (idx !== -1) {
    state.posts[idx].status = status;
    if (state.lastGeneratedPost?.id === postId) state.lastGeneratedPost = state.posts[idx];
    renderAll();
    showToast(`Estado actualizado a: ${status.toUpperCase()}`);
  }
};

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  fetchState();

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  document.getElementById("btn-quick-create").addEventListener("click", () => switchTab("studio"));

  document.getElementById("category-filters").addEventListener("click", e => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    document.querySelectorAll("#category-filters .chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    state.activeFilter = chip.dataset.filter;
    renderClientsGrid();
  });

  document.getElementById("client-search").addEventListener("input", e => {
    state.searchQuery = e.target.value;
    renderClientsGrid();
  });

  document.getElementById("studio-client-select").addEventListener("change", e => {
    state.activeStudioClientId = e.target.value;
    renderStudioAgentDna();
  });

  document.getElementById("queue-client-filter").addEventListener("change", e => {
    state.queueClientFilter = e.target.value;
    renderKanbanQueue();
  });

  document.getElementById("btn-edit-current-agent").addEventListener("click", () => {
    if (state.activeStudioClientId) openAgentModal(state.activeStudioClientId);
  });

  document.getElementById("btn-generate-post").addEventListener("click", async () => {
    const btn = document.getElementById("btn-generate-post");
    btn.disabled = true;
    btn.textContent = "⏳ Orquestando las 5 IAs...";
    const aiEngine = document.getElementById("studio-ai-select").value;
    const fmt = document.getElementById("studio-format-select").value;
    const topic = document.getElementById("studio-topic-input").value;
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: state.activeStudioClientId,
          ai_engine: aiEngine,
          format: fmt,
          topic
        })
      });
      const data = await res.json();
      if (data.ok) {
        state.posts.unshift(data.post);
        state.lastGeneratedPost = data.post;
        renderAll();
        showToast(`✨ Contenido creado para ${data.post.client_name}`);
        return;
      }
    } catch (_) {
      const client = state.clients.find(c => c.id === state.activeStudioClientId);
      if (client) {
        const post = buildLocalPost(client, topic, fmt, aiEngine);
        state.posts.unshift(post);
        state.lastGeneratedPost = post;
        renderAll();
        showToast(`✨ Contenido creado para ${post.client_name}`);
      }
    } finally {
      btn.disabled = false;
      btn.textContent = "✨ Generar Publicación con Agente";
    }
  });

  document.getElementById("btn-generate-week").addEventListener("click", async () => {
    const btn = document.getElementById("btn-generate-week");
    btn.disabled = true;
    btn.textContent = "⏳ Generando 5 días...";
    try {
      const res = await fetch("/api/generate-week", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client_id: state.activeStudioClientId })
      });
      const data = await res.json();
      if (data.ok && data.posts?.length) {
        state.posts = [...data.posts, ...state.posts];
        state.lastGeneratedPost = data.posts[0];
        renderAll();
        showToast(`📅 Parrilla semanal de 5 publicaciones generada y enviada a la Cola`);
        return;
      }
    } catch (_) {
      const client = state.clients.find(c => c.id === state.activeStudioClientId);
      if (client) {
        const ais = ["claude", "chatgpt", "kimi", "gemini", "manus"];
        const fmts = ["Reel + Post", "Carrusel Educativo", "Post de Venta Directa", "Historia Interactiva", "Campaña Meta Ads"];
        const created = ais.map((ai, i) => buildLocalPost(client, `Día ${i + 1}: Estrategia de marca`, fmts[i], ai));
        state.posts = [...created, ...state.posts];
        state.lastGeneratedPost = created[0];
        renderAll();
        showToast(`📅 Parrilla semanal de 5 publicaciones generada y enviada a la Cola`);
      }
    } finally {
      btn.disabled = false;
      btn.textContent = "📅 Generar Parrilla Semanal (5 Posts)";
    }
  });

  // Modals
  const modalAgent = document.getElementById("modal-agent");
  document.getElementById("btn-close-agent-modal").addEventListener("click", () => modalAgent.close());
  document.getElementById("btn-cancel-agent").addEventListener("click", () => modalAgent.close());

  document.getElementById("form-agent").addEventListener("submit", async e => {
    e.preventDefault();
    const clientId = document.getElementById("edit-agent-client-id").value;
    const pillars = document.getElementById("edit-agent-pillars").value
      .split(",")
      .map(s => s.trim())
      .filter(Boolean);

    const res = await fetch("/api/agent/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: clientId,
        primary_ai: document.getElementById("edit-agent-primary-ai").value,
        secondary_ai: document.getElementById("edit-agent-secondary-ai").value,
        brand_voice: document.getElementById("edit-agent-voice").value,
        target_audience: document.getElementById("edit-agent-audience").value,
        content_pillars: pillars,
        default_cta: document.getElementById("edit-agent-cta").value,
        system_prompt: document.getElementById("edit-agent-prompt").value
      })
    });
    const data = await res.json();
    if (data.ok) {
      const idx = state.clients.findIndex(c => c.id === clientId);
      if (idx !== -1) state.clients[idx] = data.client;
      renderAll();
      modalAgent.close();
      showToast("💾 ADN del Agente actualizado");
    }
  });

  const modalKeys = document.getElementById("modal-keys");
  document.getElementById("btn-open-keys").addEventListener("click", () => modalKeys.showModal());
  document.getElementById("btn-close-keys-modal").addEventListener("click", () => modalKeys.close());
  document.getElementById("btn-cancel-keys").addEventListener("click", () => modalKeys.close());

  document.getElementById("form-keys").addEventListener("submit", async e => {
    e.preventDefault();
    const payload = {
      ANTHROPIC_API_KEY: document.getElementById("key-claude").value,
      OPENAI_API_KEY: document.getElementById("key-openai").value,
      MOONSHOT_API_KEY: document.getElementById("key-kimi").value,
      GEMINI_API_KEY: document.getElementById("key-gemini").value,
      MANUS_API_KEY: document.getElementById("key-manus").value,
      META_ACCESS_TOKEN: document.getElementById("key-meta").value
    };
    const res = await fetch("/api/config/keys", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.ok) {
      state.configuredKeys = data.configured_keys;
      modalKeys.close();
      showToast("🔑 API Keys guardadas en el servidor local");
    }
  });
});
