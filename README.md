# 🎬 VidGen Studio — Full Stack Autonomous AI Video Platform

An enterprise-grade, event-driven AI video creation platform that transforms text prompts, research papers, and URLs into scene-level structured scripts, multi-voice character acting, synchronized multimodal assets, and cinematic videos at **$0/month baseline idle cost**.

![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white)
![Angular](https://img.shields.io/badge/Angular-17-dd0031?logo=angular&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas_M0-47A248?logo=mongodb&logoColor=white)
![Cloudflare R2](https://img.shields.io/badge/Storage-Cloudflare_R2-F38020?logo=cloudflare&logoColor=white)
![AWS SQS](https://img.shields.io/badge/Queue-AWS_SQS-FF4F8B?logo=amazonsqs&logoColor=white)
![Meta Muse](https://img.shields.io/badge/Model-Meta_Muse_Spark-0668E1?logo=meta&logoColor=white)

---

## 🏛️ Event-Driven Zero-Cost Cloud Architecture

```mermaid
flowchart TD
    subgraph Client ["1. Client (Vercel - $0/mo Free Tier)"]
        UI["Angular 17 Glassmorphic Client\n(Edge Global CDN)"]
        SSE["WebSocket / Live Stream"]
    end

    subgraph API ["2. Ingestion & Security (AWS Lambda / Serverless FastAPI)"]
        FastAPI["FastAPI Handler (1M free requests/mo)"]
        Security["OWASP Security Middleware & Rate Limiting"]
        DB[("MongoDB Atlas M0 Free Tier (512MB)")]
    end

    subgraph Queue ["3. Resilient Messaging (AWS SQS FIFO + DLQ)"]
        SQS["AWS SQS FIFO Queue (1M free calls/mo)\nvideo-generation-jobs.fifo"]
        DLQ["Dead Letter Queue (DLQ)\nAuto-retry 3x on transient failure"]
    end

    subgraph Compute ["4. Ephemeral Compute ($0/mo Idle Cost!)"]
        Orchestrator["Lambda Spawner / SQS Trigger"]
        ECS["AWS ECS Fargate Task / Spot Container\n(Runs Docker + FFmpeg + TTS)\nSpins up -> Renders -> Shuts Down!"]
    end

    subgraph Storage ["5. Zero-Egress Storage (Cloudflare R2 / AWS S3)"]
        R2["Cloudflare R2 Storage\n(10GB Permanent Free Storage, $0 Egress Fees)"]
    end

    subgraph Notification ["6. Event Fan-out (AWS SNS Topic)"]
        SNS["AWS SNS Topic (1M free calls/mo)\nvideo-generation-events"]
        Webhook["Lambda / API Status Updater"]
    end

    UI -->|"1. POST /api/v1/videos/generate"| FastAPI
    FastAPI --> Security
    Security -->|"2. Insert PENDING record"| DB
    FastAPI -->|"3. Enqueue job payload"| SQS
    SQS -->|"If 3 retries fail"| DLQ
    SQS -->|"4. Trigger batch"| Orchestrator
    Orchestrator -->|"5. ecs:RunTask"| ECS
    ECS -->|"6. Download media assets"| R2
    ECS -->|"7. Render video & upload .mp4"| R2
    ECS -->|"8. Publish JobCompleted event"| SNS
    ECS -->|"9. Auto-terminates container"| ECS
    SNS -->|"10. Fan-out webhook"| Webhook
    Webhook -->|"11. Update MongoDB status to COMPLETED"| DB
    Webhook -->|"12. Broadcast status update"| SSE
    SSE -->|"13. Instant preview & player update"| UI
```

---

## 💰 Zero-Cost Free-Tier Financial Breakdown

| Component | Cloud Provider | Free Tier Allowance | Idle / Monthly Cost |
| :--- | :--- | :--- | :--- |
| **Frontend Client** | **Vercel** | 100GB bandwidth, automatic SSL, preview deploys | **$0.00 / month** |
| **API & Auth** | **AWS Lambda** | 1,000,000 requests/mo forever + 3.2M seconds compute | **$0.00 / month** |
| **Database** | **MongoDB Atlas** | M0 Shared Cluster: 512MB RAM/Storage, TLS 1.3 encrypted | **$0.00 / month** |
| **Job Queue** | **AWS SQS** | 1,000,000 requests/mo forever + FIFO delivery | **$0.00 / month** |
| **Notifications** | **AWS SNS** | 1,000,000 publish/delivery calls/month free forever | **$0.00 / month** |
| **Media Storage** | **Cloudflare R2** | 10 GB storage free, **$0.00 egress bandwidth fees** | **$0.00 / month** |
| **FFmpeg Rendering** | **AWS ECS Fargate Spot / GCP Cloud Run** | On-demand compute (~$0.0006 per 60s video) / GCP 180k vCPU-s free | **$0.00 idle (cents per render)** |

---

## 🛡️ Complete Enterprise Security Stack (OWASP Top 10)

- **Security Headers Middleware**: Enforces HSTS (1 year), Content Security Policy (CSP), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and restricted `Permissions-Policy`.
- **SSRF Defense (`validate_safe_url`)**: Disallows requests to localhost (`127.0.0.1`), cloud instance metadata endpoints (`169.254.169.254`), and private RFC1918 subnets.
- **Rate Limiting**: In-memory IP rate limiter on sensitive endpoints (`/auth/login`, `/auth/register`) preventing credential stuffing and brute-force attacks.
- **Strict Access Control**: Eliminated arbitrary development bypasses in production environments; all ObjectId strings strictly validated.
- **Safe CORS Policy**: Dynamically restricts origins to `ALLOWED_ORIGINS` in production while allowing seamless local and preview testing.
- **Input Sanitization**: Control character and null-byte stripping with bounded topic and prompt lengths.

---

## 🤖 OpenCode & Meta Muse Agent Delegation

To delegate coding and maintenance tasks without consuming primary conversational tokens, use the pre-configured local CLI tools:

### 1. OpenCode Autonomous Agent
```powershell
# Run OpenCode with free models (no payment required)
opencode run --model opencode/muse-spark-1.3-contributor-free "Refactor component styles"

# Or start interactive TUI
opencode
```

### 2. Meta Muse Code Agent
```powershell
# Run task using Meta Muse CLI
$env:Path = "C:\Users\vaibh\AppData\Local\Programs\muse;$env:Path"
muse exec --trust-workspace "Review and audit test coverage"
```

---

## 🚀 Local Development Setup

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Angular 17)
```bash
cd frontend
npm install
npm run start
```
Frontend will be running at `http://localhost:4200` with the glassmorphism Studio UI.
