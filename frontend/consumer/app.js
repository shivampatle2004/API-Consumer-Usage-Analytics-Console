let consumerToken = localStorage.getItem("consumer_token");
let rawApiKey = "";
const CALCULATOR_API_BASE = (window.location.port === "8200" || window.location.port === "8080" || window.location.port === "8100")
    ? "http://localhost:8101"
    : window.location.origin;

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    const testerForm = document.getElementById("tester-form");
    if (testerForm) {
        testerForm.addEventListener("submit", handleTesterSubmit);
    }

    if (consumerToken) {
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
        const response = await fetch("/api/consumer/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed");
        }

        consumerToken = data.access_token;
        localStorage.setItem("consumer_token", consumerToken);
        localStorage.setItem("consumer_username", data.username);
        showDashboard();
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
    } finally {
        btnLogin.disabled = false;
        btnLogin.textContent = "Sign In to Developer Portal";
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
    const username = localStorage.getItem("consumer_username") || "alice";
    const userTag = document.getElementById("current-user-name");
    if (userTag) userTag.textContent = username;

    loadDashboardData();
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(loadDashboardData, 3000);
}

function logout() {
    localStorage.removeItem("consumer_token");
    localStorage.removeItem("consumer_username");
    consumerToken = null;
    rawApiKey = "";
    showAuth();
}

async function loadDashboardData() {
    if (!consumerToken) return;

    try {
        await Promise.all([
            fetchApiKey(),
            fetchApis(),
            fetchAnalytics()
        ]);
    } catch (err) {
        if (err.message.includes("401") || err.message.includes("credentials")) {
            logout();
        }
    }
}

async function fetchApiKey() {
    const res = await fetch("/api/consumer/api-key", {
        headers: { "Authorization": `Bearer ${consumerToken}` }
    });
    if (res.status === 401) throw new Error("401 Unauthorized");
    const data = await res.json();
    if (data && data.api_key) {
        rawApiKey = data.api_key;
        document.getElementById("display-api-key").textContent = rawApiKey;
    }
}

function copyApiKey() {
    if (!rawApiKey) return;
    navigator.clipboard.writeText(rawApiKey).then(() => {
        const btn = document.getElementById("btn-copy-key");
        const originalText = btn.textContent;
        btn.textContent = "Copied!";
        btn.style.background = "#10b981";
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = "";
        }, 1500);
    });
}

async function fetchApis() {
    const res = await fetch("/api/consumer/apis", {
        headers: { "Authorization": `Bearer ${consumerToken}` }
    });
    if (res.status === 401) throw new Error("401 Unauthorized");
    const apis = await res.json();
    if (apis && apis.length > 0) {
        const api = apis[0];
        document.getElementById("api-title").textContent = api.name;
        document.getElementById("api-description").textContent = api.description;
        document.getElementById("api-base-url-display").textContent = api.base_url;
    }
}

async function fetchAnalytics() {
    const res = await fetch("/api/consumer/analytics", {
        headers: { "Authorization": `Bearer ${consumerToken}` }
    });
    if (res.status === 401) throw new Error("401 Unauthorized");
    const analytics = await res.json();
    renderAnalytics(analytics);
}

function renderAnalytics(analytics) {
    document.getElementById("val-total-requests").textContent = analytics.total_requests.toLocaleString();
    document.getElementById("val-quota-limit").textContent = analytics.quota_limit.toLocaleString();
    document.getElementById("val-remaining").textContent = analytics.remaining.toLocaleString();
    document.getElementById("val-used").textContent = analytics.used.toLocaleString();
    
    document.getElementById("quota-progress-bar").style.width = `${Math.min(100, analytics.usage_percentage)}%`;
    document.getElementById("val-usage-pct").textContent = `${analytics.usage_percentage}% used`;

    const errorRateEl = document.getElementById("val-error-rate");
    errorRateEl.textContent = `${analytics.error_rate}%`;
    if (analytics.error_rate > 0) {
        errorRateEl.style.color = "var(--danger)";
    } else {
        errorRateEl.style.color = "var(--success)";
    }

    document.getElementById("val-success-count").textContent = analytics.successful_requests.toLocaleString();
    document.getElementById("val-fail-count").textContent = analytics.failed_requests.toLocaleString();

    renderRecentLogs(analytics.recent_logs);
}

function renderRecentLogs(logs) {
    const tbody = document.getElementById("consumer-logs-tbody");
    if (!logs || logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-state">No requests recorded yet. Make a request above!</td></tr>`;
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const time = new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const isSuccess = log.status_code < 400;
        const statusClass = isSuccess ? "status-200" : "status-400";

        return `
            <tr>
                <td><span class="method-tag">${log.method}</span></td>
                <td><span class="endpoint-tag">${log.endpoint}</span></td>
                <td><span class="status-badge ${statusClass}">${log.status_code}</span></td>
                <td style="font-family: var(--font-mono); color: var(--text-muted);">${time}</td>
            </tr>
        `;
    }).join("");
}

async function handleTesterSubmit(e) {
    e.preventDefault();
    const op = document.getElementById("test-op").value;
    const a = document.getElementById("test-a").value;
    const b = document.getElementById("test-b").value;
    const btnSend = document.getElementById("btn-send-test");
    const outputEl = document.getElementById("response-output");
    const statusBadge = document.getElementById("response-status-badge");

    if (!rawApiKey) {
        outputEl.textContent = "Error: API Key not loaded yet. Please wait or refresh.";
        return;
    }

    btnSend.disabled = true;
    btnSend.textContent = "Sending Request...";
    statusBadge.style.display = "none";
    outputEl.textContent = "Contacting Calculator API on Port 8101...";

    const url = `${CALCULATOR_API_BASE}/api/calculator/${op}?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "X-API-Key": rawApiKey
            }
        });

        const status = response.status;
        const data = await response.json().catch(() => ({ status_text: response.statusText }));

        statusBadge.style.display = "inline-block";
        statusBadge.textContent = `${status} ${response.statusText || (status < 400 ? 'OK' : 'Error')}`;
        statusBadge.className = `status-badge ${status < 400 ? 'status-200' : 'status-400'}`;

        outputEl.textContent = JSON.stringify(data, null, 2);

        // Immediate reload of analytics after the real request
        setTimeout(fetchAnalytics, 200);
    } catch (err) {
        statusBadge.style.display = "inline-block";
        statusBadge.textContent = "Network Error";
        statusBadge.className = "status-badge status-400";
        outputEl.textContent = `Error reaching Calculator API at ${url}:\n${err.message}\nMake sure Calculator API is running on Port 8101.`;
    } finally {
        btnSend.disabled = false;
        btnSend.textContent = "Send Request to Calculator API";
    }
}
