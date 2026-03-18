# Algarve É Um - Autonomous Content System

This is a modular Python system designed to power an autonomous content pipeline for the Portuguese civic movement **Algarve É Um**. The system automatically hunts for news, uses AI to curate and generate highly tailored social media content (using the civic, youth-oriented, and anti-regionalism voice of the movement), scores the quality of the generated text, sends it for human review via email, and pushes approved data to a centralized Supabase database.

## 🏗️ Architecture Overview

The system is split into distinct modules:
- **`core/`**: Houses the singleton Supabase client, the Claude-powered content generator (`content_generator.py`), and the AI auditor (`quality_scorer.py`).
- **`orchestrator/`**: The brain of the daily operation. It runs daily at 08:00 Lisbon time (`scheduler.py`), searches recent news discarding pure tourism articles via Tavily API (`news_search.py`), and orchestrates the generation and scoring workflow logic (`curator.py`).
- **`notifier/`**: Dispatches the AI-proposed outputs to human reviewers via an HTML email formatted with action buttons (`email_sender.py`).
- **`webhook/`**: A lightweight FastAPI application (`approval_server.py`) that catches the reviewer's clicks directly from their email inbox, instantly updating the database.
- **`content_manager/`**: A suite for planned content, generating 30-day schedules (`calendar_generator.py`), holding our core copy definitions (`templates_library.py`), and aggregating engagement (`analytics.py`).
- **`instagram/`**: Logic mapping Facebook Graph API data back to our DB (`graph_api.py`). Inactive by default.
- **`database/`**: Contains the unified `schema.sql` to deploy on your Supabase instance.

## ⚙️ Setup Instructions

### 1. Database Initialization
1. Create a project in [Supabase](https://supabase.com).
2. Navigate to the SQL Editor and run the complete script found in `database/schema.sql`.
3. Enable Row Level Security (RLS) policies as appropriate depending on your frontend setup.

### 2. Environment Configuration
1. Rename `.env.example` to `.env` in the root directory.
2. Fill out **all** required keys:
   - `ANTHROPIC_API_KEY`: Used for Content Generation and Quality Scoring.
   - `TAVILY_API_KEY`: Used for automated News Searching.
   - `SUPABASE_URL` / `SUPABASE_KEY`: Used to interface with the database.
   - `RESEND_API_KEY` / `EDITOR_EMAIL`: Used to send the review emails.
   - `WEBHOOK_BASE_URL`: The production URL pointing to your FastAPI server (e.g., `https://api.algarveeum.pt`).

### 3. Install Dependencies
Make sure you are using Python 3.10+.
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 How to Run

### Daily Pipeline (Automated)
To run the APScheduler loop that triggers every day at 08:00 Lisbon time:
```bash
python orchestrator/scheduler.py
```
> Note: Keep this process running on your server, or wrap it in a systemd service.

### Manual Pipeline Test (One-Off)
To force a run immediately without waiting for the schedule (useful for debugging):
```bash
python run_test.py
```

### Content Manager & Analytics
You can independently trigger calendar creation and analytics lookups:
```bash
python content_manager/calendar_generator.py
python content_manager/analytics.py
```

## 🌐 Deploying the Webhook Server to Production

The FastAPI server (`webhook/approval_server.py`) must be accessible to the public internet so that the links clicked in the reviewer's emails resolve correctly.

1. **Option 1 (Render/Fly.io/Heroku)**:
   - Point your PaaS to start `uvicorn webhook.approval_server:app --host 0.0.0.0 --port $PORT`.
   - Update `WEBHOOK_BASE_URL` in your `.env` to match the generated domain.
   
2. **Option 2 (VPS with Nginx & Systemd)**:
   - Run the uvicorn process bound to localhost.
   - Use Nginx as a reverse proxy bridging port 80/443 to the uvicorn port.
   - Secure the endpoint using Certbot (LetsEncrypt).

*(For local testing, you can use `ngrok http 8000` to temporarily expose your development port and update `WEBHOOK_BASE_URL` in your `.env` to the ngrok URL.)*
