document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("gateway-login-form");
    if (form) {
        form.addEventListener("submit", handleGatewayLogin);
    }
});

function selectAccount(username, password) {
    document.getElementById("username").value = username;
    document.getElementById("password").value = password;
    document.getElementById("login-error").style.display = "none";
}

async function handleGatewayLogin(e) {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const errorEl = document.getElementById("login-error");
    const btn = document.getElementById("btn-login");

    errorEl.style.display = "none";
    btn.disabled = true;
    btn.textContent = "Authenticating...";

    try {
        const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Invalid username or password");
        }

        btn.textContent = `Routing to ${data.role === 'SUPER_ADMIN' ? 'Super Admin Portal' : 'Developer Console'}...`;

        // Direct redirection based on role
        if (data.role === "SUPER_ADMIN") {
            window.location.href = data.redirect_url || "http://localhost:8100";
        } else {
            window.location.href = data.redirect_url || "http://localhost:8200";
        }
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.style.display = "block";
        btn.disabled = false;
        btn.textContent = "Sign In & Launch Portal";
    }
}
