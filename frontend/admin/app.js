let adminToken = localStorage.getItem("admin_token");
let pollInterval = null;

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    if (adminToken) {
        showDashboard();
    } else {
        showAuth();
    }
});

function fillDemoCredentials(user, pass) {
    document.getElementById("username").value = user;
    document.getElementById("password").value = pass;
}

async function handleLogin(e) {
    e.preventDefault();
    const usernameInput = document.getElementById("username").value.trim();
    const passwordInput = document.getElementById("password").value;
    const errorEl = document.getElementById("login-error");
    const btnLogin = document.getElementById("btn-login");

    errorEl.style.display = "none";
    btnLogin.disabled = true;
    btnLogin.textContent = "Signing In...";

    try {
        const response = await fetch("/api/admin/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed");
        }

        adminToken = data.access_token;
        localStorage.setItem("admin_token", adminToken);
        localStorage.setItem("admin_username", data.username);
        showDashboard();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
    } finally {
        btnLogin.disabled = false;
        btnLogin.textContent = "Sign In to Admin Portal";
    }
}

function showAuth() {
    if (pollInterval) clearInterval(pollInterval);
    document.getElementById("auth-view").style.display = "flex";
    document.getElementById("dashboard-view").style.display = "none";
}

function showDashboard() {
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("dashboard-view").style.display = "block";
    const username = localStorage.getItem("admin_username") || "admin";
    const userTag = document.getElementById("current-admin-name");
    if (userTag) userTag.textContent = username;

    loadDashboardData();
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(loadDashboardData, 3000);
}

function logout() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");
    adminToken = null;
    showAuth();
}

async function loadDashboardData() {
    if (!adminToken) return;

    try {
        await Promise.all([
            fetchApis(),
            fetchConsumers(),
            fetchLogs()
        ]);
    } catch (err) {
        if (err.message.includes("401") || err.message.includes("credentials")) {
            logout();
        }
    }
}

async function fetchApis() {
    const res = await fetch("/api/admin/apis", {
        headers: { "Authorization": `Bearer ${adminToken}` }
    });
    if (res.status === 401) throw new Error("401 Unauthorized");
    const apis = await res.json();
    if (apis && apis.length > 0) {
        const api = apis[0];
        document.getElementById("api-name").textContent = api.name;
        document.getElementById("api-desc").textContent = api.description;
        document.getElementById("api-base-url").textContent = api.base_url;
    }
}

async function fetchConsumers() {
    const res = await fetch("/api/admin/consumers", {
        headers: { "Authorization": `Bearer ${adminToken}` }
    });
    if (res.status === 401) throw new Error("401 Unauthorized");
    const consumers = await res.json();
    renderConsumers(consumers);
}

function maskApiKey(key) {
    if (!key || key.length < 10) return key;
    return key.substring(0, 9) + "•".repeat(key.length - 9);
}

let keyVisibility = {};

function toggleKeyVisibility(consumerId, rawKey) {
    keyVisibility[consumerId] = !keyVisibility[consumerId];
    const keyEl = document.getElementById(`key-display-${consumerId}`);
    const btnEl = document.getElementById(`btn-toggle-${consumerId}`);
    if (keyVisibility[consumerId]) {
        keyEl.textContent = rawKey;
        btnEl.textContent = "Hide";
    } else {
        keyEl.textContent = maskApiKey(rawKey);
        btnEl.textContent = "Show";
    }
}

function renderConsumers(consumers) {
    const container = document.getElementById("consumers-container");
    const badge = document.getElementById("consumer-count-badge");
    if (badge) badge.textContent = `${consumers.length} Registered Consumer${consumers.length === 1 ? '' : 's'}`;

    if (!consumers || consumers.length === 0) {
        container.innerHTML = `<div class="empty-state">No registered API consumers found.</div>`;
        return;
    }

    container.innerHTML = consumers.map(c => {
        const isVisible = !!keyVisibility[c.id];
        const displayKey = isVisible ? c.api_key : maskApiKey(c.api_key);
        const errorClass = c.error_rate > 0 ? "highlight-red" : "highlight-green";

        return `
            <div class="consumer-card">
                <div class="consumer-header">
                    <div>
                        <div class="consumer-name">${c.username}</div>
                        <div style="font-size: 12px; color: var(--text-muted);">${c.email}</div>
                    </div>
                    <span class="badge-online">Active</span>
                </div>

                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">
                    Consumer API Key
                </div>
                <div class="consumer-key-box">
                    <span id="key-display-${c.id}">${displayKey}</span>
                    <button id="btn-toggle-${c.id}" onclick="toggleKeyVisibility(${c.id}, '${c.api_key}')" class="btn-secondary" style="padding: 2px 8px; font-size: 11px;">
                        ${isVisible ? 'Hide' : 'Show'}
                    </button>
                </div>

                <div class="metrics-row">
                    <div class="metric-box">
                        <div class="metric-label">Quota Limit</div>
                        <div class="metric-value">${c.quota_limit.toLocaleString()}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Requests Used</div>
                        <div class="metric-value">${c.requests_used.toLocaleString()}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Remaining</div>
                        <div class="metric-value highlight-green">${c.remaining.toLocaleString()}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Error Rate</div>
                        <div class="metric-value ${errorClass}">${c.error_rate}%</div>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

async function fetchLogs() {
    const res = await fetch("/api/admin/logs?limit=50", {
        headers: { "Authorization": `Bearer ${adminToken}` }
    });
    if (res.status === 401) throw new Error("401 Unauthorized");
    const logs = await res.json();
    renderLogs(logs);
}

function renderLogs(logs) {
    const tbody = document.getElementById("logs-tbody");
    if (!logs || logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No API requests recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const time = new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const isSuccess = log.status_code < 400;
        const statusClass = isSuccess ? "status-200" : "status-400";

        return `
            <tr>
                <td style="font-family: var(--font-mono); color: var(--text-muted);">${time}</td>
                <td><strong>${log.username || 'Consumer'}</strong></td>
                <td><span class="method-tag">${log.method}</span></td>
                <td><span class="endpoint-tag">${log.endpoint}</span></td>
                <td><span class="status-badge ${statusClass}">${log.status_code}</span></td>
            </tr>
        `;
    }).join("");
}
