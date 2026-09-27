# 🌦️ WeatherGPT — AI-Powered Weather Intelligence Platform

> **METEOR.OPS** — National Meteorological Telemetry System

## 🎯 Problem Statement

Weather information is scattered across multiple portals, bulletins, satellite products, and forecast systems — making it difficult for farmers, disaster managers, researchers, and citizens to get actionable insights quickly.

**WeatherGPT** bridges this gap with a conversational AI platform that delivers real-time weather intelligence, forecasts, extreme-event warnings, and climate analytics — in natural language, across 10 Indian languages.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🌡️ **Real-time Weather** | Live conditions via OpenWeatherMap (temp, humidity, wind, AQI, visibility) |
| 💬 **Telemetry Copilot** | Gemini AI — natural language weather Q&A with streaming |
| 🌐 **Multilingual** | 10 Indian languages: Hindi, Tamil, Telugu, Bengali, Kannada, Marathi, Gujarati, Punjabi, Malayalam |
| ⚠️ **Extreme Alerts** | IMD-style color-coded warnings (Red / Orange / Yellow / Green) |
| 🎯 **7 Advisory Domains** | Agriculture, Aviation, Flood & Cyclone, Smart City, Marine, Climate Research, General |
| 📅 **5-Day Forecast** | Daily summaries with condition, temperature, humidity |
| 📊 **Climate Analytics** | Historical data via Open-Meteo API (1940–present, free) |
| 🎤 **Voice Input** | HTML5 Speech API for hands-free rural accessibility |
| 🔊 **Audio Readout** | Optional TTS with stop control — off by default |
| 🗄️ **Live Database** | SQLite / PostgreSQL — all queries, weather snapshots & alerts persisted |
| 🚀 **Scalable Backend** | FastAPI + Redis cache + PostgreSQL + Docker |

---

## 🏗️ Architecture

```
WeatherGPT/
├── frontend/                         # METEOR.OPS — HTML/JS/CSS dashboard
│   ├── index.html                    # Main entry point (served at localhost:8000)
│   ├── js/
│   │   ├── app.js                    # Core app bootstrap & routing
│   │   ├── chat.js                   # Telemetry Copilot AI chatbot
│   │   ├── weather.js                # Live weather & forecast panels
│   │   ├── api.js                    # Backend API calls & SSE streaming
│   │   ├── charts.js                 # Chart.js visualizations
│   │   └── i18n.js                   # 10-language localization engine
│   └── css/                          # Premium dark glassmorphism styles
├── backend/
│   ├── main.py                       # FastAPI app — serves frontend + API
│   ├── config.py                     # Environment & constants
│   ├── models.py                     # Pydantic schemas
│   ├── routes/
│   │   ├── chat.py                   # POST /chat   — AI conversational endpoint
│   │   ├── weather.py                # GET  /weather — Real-time data
│   │   ├── alerts.py                 # GET  /alerts  — Early warning system
│   │   └── climate.py                # POST /climate — Historical analytics
│   ├── services/
│   │   ├── llm_service.py            # Gemini API — domain + multilingual prompts
│   │   ├── weather_service.py        # OpenWeatherMap + AQI + derived alerts
│   │   ├── alert_service.py          # OWM One Call + severity classification
│   │   ├── climate_service.py        # Open-Meteo historical API
│   │   └── db_service.py             # Database queries
│   ├── utils/
│   │   ├── location_parser.py        # City extractor (Indian city fast-path)
│   │   └── cache.py                  # Redis w/ graceful degradation
│   └── db/
│       ├── models.py                 # SQLAlchemy ORM (ChatLog, WeatherSnapshot, AlertLog)
│       └── init_db.py                # Table bootstrapper
├── database/
│   └── weather_gpt.db                # SQLite database (auto-created)
├── docker/
│   └── Dockerfile
├── docker-compose.yml                # PostgreSQL + Redis containers
├── run.bat                           # One-click Windows startup
└── tests/
    ├── test_chat.py
    ├── test_weather.py
    └── test_llm.py
```

---

## 🧠 AI / LLM Design

- **Model:** Google Gemini 3.6 Flash (latest, fast, cost-effective)
- **Fallback chain:** `gemini-3.6-flash` → `gemini-3.5-flash` → `gemini-3.5-flash-lite` → `gemini-2.5-flash`
- **Domain-aware prompting:** 7 system personas (Farmer, Aviation Officer, Disaster Manager, Urban Planner, Marine Advisor, Climate Scientist, General Assistant)
- **Multilingual responses:** Native-script responses in 10 Indian languages
- **Streaming:** Server-Sent Events (SSE) for real-time token-by-token display
- **Climate summarization:** Dedicated Gemini call for historical trend narratives

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- OpenWeatherMap API key (free tier works)
- Google Gemini API key (free tier: 1500 req/day)

### 1. Clone & set up environment
```bash
git clone <repo>
cd WeatherGPT
cp .env.example .env   # edit and fill in your keys
```

### 2. One-click start (Windows)
```bat
./run.bat
```
This activates the virtual environment, installs dependencies, and starts the server.

### 3. Open the app
```
http://localhost:8000
```

### 4. API Documentation
```
http://localhost:8000/docs
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat/` | AI weather Q&A with language + domain context |
| `POST` | `/chat/stream` | Streaming SSE AI response |
| `GET`  | `/chat/history` | Recent chat logs from database |
| `GET`  | `/weather/?city=Delhi` | Real-time weather + 5-day forecast + AQI |
| `GET`  | `/alerts/?city=Mumbai` | Active extreme weather alerts |
| `POST` | `/climate/` | Historical climate trend + AI summary |
| `GET`  | `/db/stats` | Live database record counts |
| `GET`  | `/health` | Service health check |

### Example `/chat/` request
```json
{
  "user_question": "Should I irrigate my wheat crop today?",
  "location": "Ludhiana",
  "language_code": "hi",
  "domain": "Agriculture / Farming"
}
```

---

## 🌾 Use Cases

| Domain | Example Query |
|---|---|
| **Agriculture** | "Should I spray pesticide tomorrow in Nashik?" |
| **Aviation** | "Give aviation weather briefing for Delhi IGI airport." |
| **Flood Warning** | "What is the flood risk in Patna this week?" |
| **Smart City** | "AQI and heat island warning for Bangalore today." |
| **Marine** | "Wave height and fishing window for Kochi tomorrow." |
| **Research** | "How has July rainfall in Mumbai changed over 30 years?" |

---

## 🔑 Environment Variables

```env
OPENWEATHERMAP_API_KEY=...   # Required — openweathermap.org (free)
GEMINI_API_KEY=...           # Required — aistudio.google.com (free)
GEMINI_MODEL=gemini-3.6-flash  # Optional — defaults to gemini-3.6-flash
DATABASE_URL=...             # Optional — defaults to SQLite (database/weather_gpt.db)
REDIS_URL=redis://localhost:6379  # Optional — cache degrades gracefully if offline
```

---

## 📊 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Vanilla JS, CSS3 (glassmorphism dark theme) |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI** | Google Gemini 3.6 Flash (google-genai SDK) |
| **Database** | SQLite (default) / PostgreSQL (production) via SQLAlchemy |
| **Cache** | Redis (optional, graceful degradation) |
| **Weather API** | OpenWeatherMap + Open-Meteo (historical) |
| **Deployment** | Docker + docker-compose |

---

## 📜 License
MIT — Built for the WeatherGPT Hackathon 2026
