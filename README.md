# PersonalAiChatBot

A **production‑ready**, privacy‑focused Telegram bot that forwards user prompts to an **Ollama** LLM (e.g., `llama3.2:latest`).  
The bot is fully configurable via environment variables, supports both **polling** and **webhook** modes, emits **structured JSON logs**, and includes a whitelist‑based authorization system.

---  

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Configuration](#configuration)
- [Running in Production](#running-in-production)
- [Testing](#testing)
- [Logging & Monitoring](#logging--monitoring)
- [Security & Hardening](#security--hardening)
- [License](#license)

---  

## Features
- **Async Telegram API** (`python‑telegram-bot` 21+)
- **Ollama client** using `httpx` (non‑blocking)
- **Environment‑driven configuration** – no secrets in source
- **JSON‑structured logging** (easy to ship to ELK, Loki, Splunk, etc.)
- **Graceful shutdown** on SIGINT/SIGTERM
- **Polling** (default) **or webhook** mode
- **Whitelist authorization** (`ALLOWED_USER_IDS`)
- **Dockerised** for reproducible builds
- **Unit‑test skeleton** with `pytest‑asyncio`

---  

## Architecture Overview
```
┌─────────────────────┐
│  Telegram API (Bot) │
└───────▲───────▲─────┘
        │       │
   (poll)   (webhook)
        │       │
┌───────▼───────▼─────┐
│   Application      │
│  - Handlers        │
│  - Config loader   │
│  - Logger          │
│  - Ollama client   │
└───────▲───────▲─────┘
        │       │
   HTTP │   HTTP│
        │       │
┌───────▼───────▼─────┐
│   Ollama Service   │
│ (local or remote) │
└─────────────────────┘
```

---  

## Quick Start (Docker Compose)

```bash
# 1. Clone the repository
git clone https://github.com/yourorg/PersonalAiChatBot.git
cd PersonalAiChatBot

# 2. Copy the example env file and fill in your values
cp .env.example .env
# edit .env → set TELEGRAM_TOKEN, ALLOWED_USER_IDS, etc.

# 3. Start the stack
docker compose up -d
```

The bot will start **polling** Telegram for updates.  
Send `/start` from an allowed Telegram account to verify it works.

---  

## Configuration  

All settings are read from environment variables (see `.env.example`).  
Key variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_TOKEN` | Bot token from BotFather | `123456:ABCDEF...` |
| `BOT_USERNAME` | Bot’s `@username` (used for group mentions) | `@edoAlabot` |
| `ALLOWED_USER_IDS` | Comma‑separated list of Telegram user IDs allowed to use the bot | `111111111,222222222` |
| `OLLAMA_URL` | HTTP endpoint of Ollama’s `/api/generate` | `http://localhost:11434/api/generate` |
| `OLLAMA_MODEL` | Model name to query | `llama3.2:latest` |
| `MAX_CHARS` | Max characters returned to the user | `500` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, …) | `INFO` |
| `USE_WEBHOOK` | `true` to run in webhook mode, otherwise polling | `false` |
| `WEBHOOK_URL` | Public HTTPS URL for Telegram webhook (required if `USE_WEBHOOK=true`) | `https://mydomain.com/bot/webhook` |
| `MESSAGE_RATE_LIMIT` | Optional per‑user messages per minute (0 = disabled) | `10` |

The configuration module (`app/config.py`) validates and converts these values at start‑up.

---  

## Running in Production  

### Polling (simple)

```bash
docker run -d \
  -e TELEGRAM_TOKEN=... \
  -e ALLOWED_USER_IDS=... \
  -e OLLAMA_URL=http://ollama:11434/api/generate \
  yourorg/personal-aichatbot:latest
```

### Webhook (cloud‑native)

1. Deploy the container behind a TLS‑terminating reverse proxy (NGINX, Traefik, Cloud Run, etc.).  
2. Set `USE_WEBHOOK=true` and `WEBHOOK_URL=https://yourdomain.com/bot/webhook`.  
3. Ensure the public URL is reachable by Telegram (port 443).  

The bot will automatically register the webhook on start‑up.

---  

## Testing  

```bash
# Install dev dependencies
poetry install --with dev

# Run the test suite
pytest
```

A minimal test suite (`tests/test_bot.py`) demonstrates how to mock Telegram updates and verify authorization logic. Extend it to cover group‑mention handling, Ollama error paths, and rate‑limit enforcement.

---  

## Logging & Monitoring  

- Logs are emitted as **JSON lines** to `stdout`, compatible with ELK, Loki, Splunk, etc.  
- Adjust `LOG_LEVEL` to control verbosity.  
- In production, pipe logs to a side‑car or use Docker logging drivers (`json-file`, `fluentd`, …).  

Optional: add a health‑check endpoint (e.g., `GET /health`) behind your reverse proxy to allow orchestration platforms to monitor liveness.

---  

## Security & Hardening  

| Concern | Mitigation |
|---------|------------|
| **Secret leakage** | All secrets are supplied via environment variables; never committed to source. |
| **User enumeration** | Bot replies with a generic “Access restricted” message; no details about allowed IDs are exposed. |
| **Denial‑of‑service** | Placeholder `MESSAGE_RATE_LIMIT` can be wired to Redis or a token‑bucket library. |
| **Network exposure** | Ollama service should be bound to an internal network only; Docker Compose isolates it. |
| **Webhook TLS** | Telegram requires HTTPS; terminate TLS at a trusted proxy (e.g., Nginx with Let’s Encrypt). |
| **Data privacy** | No user data is persisted; chats are only forwarded anonymously to the Ollama endpoint. |

---  

