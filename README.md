# 🌦️ WeatherGPT — AI-Powered Weather Intelligence Platform

> **Hackathon Topic:** WeatherGPT: Conversational AI for Weather Forecasting, Alerts, and Climate Information

## 🎯 Problem Statement

Weather information is scattered across multiple portals, bulletins, satellite products, and forecast systems — making it difficult for farmers, disaster managers, researchers, and citizens to get actionable insights quickly.

**WeatherGPT** bridges this gap with a conversational AI platform that delivers real-time weather intelligence, forecasts, extreme-event warnings, and climate analytics — in natural language, across 10 Indian languages.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🌡️ **Real-time Weather** | Live conditions via OpenWeatherMap (temp, humidity, wind, AQI, visibility) |
| 💬 **Conversational AI** | Gemini 1.5 Flash — natural language weather Q&A |
| 🌐 **Multilingual** | 10 Indian languages: Hindi, Tamil, Telugu, Bengali, Kannada, Marathi, Gujarati, Punjabi, Malayalam |
| ⚠️ **Extreme Alerts** | IMD-style color-coded warnings (Red / Orange / Yellow / Green) |
| 🎯 **7 Advisory Domains** | Agriculture, Aviation, Flood & Cyclone, Smart City, Marine, Climate Research, General |
| 📅 **5-Day Forecast** | Daily summaries with condition, temperature, humidity |
| 📊 **Climate Analytics** | Historical data via Open-Meteo API (1940–present, free) |
| 🎤 **Voice Input** | HTML5 Speech API for hands-free rural accessibility |
| 🚀 **Scalable Backend** | FastAPI + Redis cache + PostgreSQL + Docker |

---

## 🏗️ Architecture

```
weather-gpt/
├── frontend/
│   ├── weather_gpt_frontend.py   # Streamlit UI (premium dark theme)
│   └── requirements.txt
├── backend/
│   ├── main.py                   # FastAPI app
│   ├── config.py                 # Environment & constants
│   ├── models.py                 # Pydantic schemas
│   ├── routes/
│   │   ├── chat.py               # POST /chat   — AI conversational endpoint
│   │   ├── weather.py            # GET  /weather — Real-time data
│   │   ├── alerts.py             # GET  /alerts  — Early warning system
│   │   └── climate.py            # POST /climate — Historical analytics
│   ├── services/
│   │   ├── llm_service.py        # Gemini API — domain + multilingual prompts
│   │   ├── weather_service.py    # OpenWeatherMap + AQI + derived alerts
│   │   ├── alert_service.py      # OWM One Call + severity classification
│   │   ├── climate_service.py    # Open-Meteo historical API
│   │   └── db_service.py         # PostgreSQL queries
│   ├── utils/
│   │   ├── location_parser.py    # City extractor (Indian city fast-path)
│   │   └── cache.py              # Redis w/ graceful degradation
│   └── db/
│       ├── models.py             # SQLAlchemy ORM (ChatLog, WeatherSnapshot, AlertLog)
│       └── init_db.py            # Table bootstrapper
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml        # FastAPI + Streamlit + PostgreSQL + Redis
└── tests/
    ├── test_chat.py
    ├── test_weather.py
    └── test_llm.py
```

---

## 🧠 AI / LLM Design

- **Model:** Google Gemini 1.5 Flash (fast, multimodal, cost-effective)
- **Domain-aware prompting:** 7 system personas (Farmer, Aviation Officer, Disaster Manager, Urban Planner, Marine Advisor, Climate Scientist, General Assistant)
- **Multilingual responses:** Native-script responses in 10 Indian languages via language-tagged instructions
- **Climate summarization:** Dedicated Gemini call for historical trend narratives
- **Translation fallback:** Gemini-powered translation when Google Translate API is unavailable

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- OpenWeatherMap API key (free tier works)
- Google Gemini API key (free tier: 1500 req/day)

### 1. Clone & set up environment
```bash
git clone <repo>
cd weather-gpt
cp .env .env.local   # edit and fill in your keys
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Run frontend (new terminal)
```bash
cd frontend
streamlit run weather_gpt_frontend.py
```

### 5. Or use Docker (one command)
```bash
cd docker
docker-compose up --build
```

Access: **Frontend** → http://localhost:8501 · **API Docs** → http://localhost:8000/docs

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat/` | AI weather Q&A with language + domain context |
| `GET`  | `/weather/?city=Delhi` | Real-time weather + 5-day forecast + AQI |
| `GET`  | `/alerts/?city=Mumbai` | Active extreme weather alerts |
| `POST` | `/climate/` | Historical climate trend + AI summary |
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

## 📊 Evaluation Metrics

| Parameter | Implementation |
|---|---|
| **Accuracy** | Live OWM data + Gemini grounded prompts (no hallucination guard) |
| **Latency** | Redis cache (TTL 5–10 min) keeps p95 < 2s for cached queries |
| **Multilingual** | 10 Indian languages via native Gemini instruction |
| **UI/UX** | Premium dark glassmorphism Streamlit app |
| **Scalability** | FastAPI + Redis + Docker-compose (Kubernetes-ready) |
| **Real-time** | OWM API + Open-Meteo + optional MQTT/WIS2.0 extension |
| **Voice** | HTML5 Speech Recognition API (Chrome/Edge) |

---

## 🔑 Environment Variables

```env
OPENWEATHERMAP_API_KEY=...   # Required
GEMINI_API_KEY=...           # Required
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
```

---

## 📜 License
MIT — Built for the WeatherGPT Hackathon 2026
