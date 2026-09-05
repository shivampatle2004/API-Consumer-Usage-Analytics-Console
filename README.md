# API Consumer Usage & Analytics Console

A production-grade, lightweight demonstration of an **API Provider** (Super Admin) and **API Consumer** (Developer) ecosystem built strictly with **Python, FastAPI, SQLAlchemy, and SQLite**.

---

## Architecture & Port Allocation

The system consists of three completely separated, dedicated services running simultaneously:

| Service | Port | Base URL | Description |
| :--- | :--- | :--- | :--- |
| **Super Admin Portal** | `8100` | `http://localhost:8100` | API Provider dashboard for monitoring consumers, API keys, quota usage, error rates, and global request logs. |
| **Calculator API** | `8101` | `http://localhost:8101` | Core external API providing arithmetic operations secured with `X-API-Key`. Interactive Swagger docs at `/docs`. |
| **Consumer Developer Portal** | `8200` | `http://localhost:8200` | Developer portal for exploring endpoints, copying API keys, live testing, and viewing usage metrics. |
| *External Projects* | `3000` | `http://localhost:3000` | **UNTOUCHED & PRESERVED** — Strictly isolated. |

```text
Super Admin (Port 8100)
       │
       │ monitors & owns
       ▼
Calculator API (Port 8101)  ◄──────  API Consumer Portal (Port 8200)
       │                              (Sends real HTTP requests with X-API-Key)
       │ auto-logs
       ▼
 SQLite Database (data/app.db)
       │
       ▼
 Analytics Engine
 (Volume, Quota Remaining, Error Rate)
```

---

## Features

1. **Calculator API (`http://localhost:8101`)**:
   - `GET /api/calculator/add?a={a}&b={b}`
   - `GET /api/calculator/subtract?a={a}&b={b}`
   - `GET /api/calculator/multiply?a={a}&b={b}`
   - `GET /api/calculator/divide?a={a}&b={b}` (returns `400 Bad Request` if denominator is 0)
   - Secured via required `X-API-Key` header.
   - Built-in Swagger UI at `http://localhost:8101/docs`.

2. **Automatic Request Logging**:
   - Every API request made with a valid API key is automatically persisted in the `api_request_logs` SQLite table.
   - Logs timestamp, consumer ID, API key ID, HTTP method, endpoint, and status code (both `200` success and `4xx`/`5xx` failures).

3. **Analytics Formulas**:
   - **Total Requests**: `total_requests = count(consumer_requests)`
   - **Quota Used**: `used = total_requests`
   - **Remaining Quota**: `remaining = max(0, quota_limit - used)`
   - **Usage %**: `(used / quota_limit) * 100`
   - **Failed Requests**: `count(requests with status_code >= 400)`
   - **Error Rate %**: `(failed_requests / total_requests) * 100` (or `0.0%` if `total_requests == 0`)

4. **Multi-Tenant Security & Isolation**:
   - Consumers can only access their own API keys, analytics, and request logs.
   - Super Admin can view all registered consumers and full global logs.

---

## Demo Credentials

Demo accounts and API keys are automatically seeded into SQLite on startup:

### 1. Super Admin
- **URL**: `http://localhost:8100`
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `SUPER_ADMIN`

### 2. API Consumer (Alice)
- **URL**: `http://localhost:8200`
- **Username**: `alice`
- **Password**: `alice123`
- **API Key**: `ak_alice_1234567890abcdef`
- **Quota Limit**: `1,000` requests

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start All 3 Services
Launch all services simultaneously with a single command:
```bash
python run.py
```
*(On Windows, you can also double-click `run.bat`)*.

### 3. Stop All Services
To cleanly stop background instances:
```bash
stop.bat
```

---

## Free Cloud Deployment (Render.com / Railway / Fly.io)

This repository includes a [`Procfile`](file:///c:/Users/shiva/Desktop/seqa/Procfile) and [`unified_app.py`](file:///c:/Users/shiva/Desktop/seqa/backend/app/unified_app.py) for **100% free hosting**:

### Deploying to Render.com for Free:
1. Push this project to your **GitHub** repository.
2. Sign up at [Render.com](https://render.com) (Free account).
3. Click **New +** &rarr; **Web Service** &rarr; Connect your GitHub repository.
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app.unified_app:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**.

Once deployed, you get a free public URL (e.g. `https://my-api-console.onrender.com`):
- `https://my-api-console.onrender.com/` &rarr; Consumer Developer Portal
- `https://my-api-console.onrender.com/admin` &rarr; Super Admin Portal
- `https://my-api-console.onrender.com/docs` &rarr; Calculator API Swagger UI
- `https://my-api-console.onrender.com/api/calculator/add?a=10&b=20` &rarr; Public Calculator API

---

## Step-by-Step Live Demonstration

1. **Open 3 Browser Windows / Tabs**:
   - Tab 1: `http://localhost:8100` (Super Admin Portal)
   - Tab 2: `http://localhost:8200` (Consumer Developer Portal)
   - Tab 3: `http://localhost:8101/docs` (Calculator API Swagger UI)

2. **Login to Consumer Portal (Tab 2)**:
   - Login with `alice` / `alice123`.
   - Observe initial metrics: **0 Requests**, **1,000 Remaining**, **0% Error Rate**.
   - Notice the active API key `ak_alice_1234567890abcdef` and the **Copy API Key** button.

3. **Make a Successful Request via Live Tester**:
   - In the Calculator API Live Tester, choose `Addition (+)`, set `A = 10`, `B = 20`.
   - Click **Send Request to Calculator API**.
   - The response box immediately shows `200 OK` and `{"operation": "addition", "a": 10, "b": 20, "result": 30}`.
   - Metrics instantly update to **1 Total Request**, **999 Remaining Quota**, **0% Error Rate**.

4. **Trigger an Error Scenario (Division by Zero)**:
   - Select `Division (/)`, set `A = 20`, `B = 0`.
   - Click **Send Request to Calculator API**.
   - The response box shows `400 Bad Request` with `{"detail": "Division by zero is not allowed"}`.
   - Metrics update immediately to reflect the error:
     - Total Requests: **2** (or 3 with additional calls)
     - Error Rate: calculated accurately based on failed vs total requests.

5. **Verify on Super Admin Portal (Tab 1)**:
   - Login with `admin` / `admin123`.
   - View the Calculator API status (`Operational` on `http://localhost:8101`).
   - View Alice's consumer card: exact match of requests used, remaining quota, and error rate.
   - View the **Real-Time Request Activity Logs** table showing the exact timestamps, HTTP methods, endpoints, and status codes (`200` vs `400`).

---

## Automated Tests

Run the complete test suite:
```bash
pytest -v
```

All 15 automated tests verify:
- Authentication and role-based permissions (`SUPER_ADMIN` vs `CONSUMER`).
- Calculator arithmetic endpoints (`add`, `subtract`, `multiply`, `divide`).
- Input validation and division-by-zero error handling (`400`).
- Mandatory `X-API-Key` security validation and rejection of invalid keys.
- Automatic SQLite logging of successful and failed requests.
- Exact analytics calculations for quotas and error rates.
- Multi-tenant data isolation.
