# Graph Report - WeatherGPT  (2026-09-21)

## Corpus Check
- 32 files · ~18,965 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .css 1, .bat 1)

## Summary
- 201 nodes · 308 edges · 21 communities (12 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b1255d0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- chat.py
- llm_service.py
- db/models.py
- fetch_weather
- 🌦️ WeatherGPT — AI-Powered Weather Intelligence Platform
- alert_service.py
- weather_gpt_frontend.py
- package.json
- setup.py
- test_chat.py
- config.py
- location_parser.py
- api.js
- app.js
- charts.js
- chat.js
- weather.js

## God Nodes (most connected - your core abstractions)
1. `fetch_weather()` - 14 edges
2. `generate_weather_response()` - 13 edges
3. `🌦️ WeatherGPT — AI-Powered Weather Intelligence Platform` - 11 edges
4. `chat()` - 9 edges
5. `get_climate()` - 9 edges
6. `stream_weather_response()` - 8 edges
7. `generate_climate_summary()` - 8 edges
8. `get_cached()` - 8 edges
9. `set_cached()` - 8 edges
10. `Base` - 7 edges

## Surprising Connections (you probably didn't know these)
- `event_generator()` --calls--> `stream_weather_response()`  [EXTRACTED]
  backend/routes/chat.py → backend/services/llm_service.py
- `test_generate_response_fallback_on_api_error()` --calls--> `generate_weather_response()`  [EXTRACTED]
  tests/test_llm.py → backend/services/llm_service.py
- `test_generate_weather_response_domain_aviation()` --calls--> `generate_weather_response()`  [EXTRACTED]
  tests/test_llm.py → backend/services/llm_service.py
- `test_generate_weather_response_english()` --calls--> `generate_weather_response()`  [EXTRACTED]
  tests/test_llm.py → backend/services/llm_service.py
- `test_generate_weather_response_hindi()` --calls--> `generate_weather_response()`  [EXTRACTED]
  tests/test_llm.py → backend/services/llm_service.py

## Import Cycles
- None detected.

## Communities (21 total, 5 thin omitted)

### Community 0 - "chat.py"
Cohesion: 0.11
Nodes (29): add_no_cache_header(), health(), get, backend/main.py WeatherGPT — FastAPI entry point. Provides conversational AI…, ChatRequest, ChatResponse, ClimateRequest, ClimateResponse (+21 more)

### Community 1 - "llm_service.py"
Cohesion: 0.14
Nodes (26): _build_prompt(), generate_climate_summary(), _generate_fallback_advisory(), generate_weather_response(), _get_candidate_models(), _get_client(), backend/services/llm_service.py Gemini-1.5-Flash powered query understanding…, Generate high-fidelity domain-aware weather advisory when Gemini API is offline. (+18 more)

### Community 2 - "db/models.py"
Cohesion: 0.14
Nodes (18): init_db(), db/init_db.py Creates all database tables on application startup. Run directly…, Create all tables defined in ORM models (no-op if already exist)., AlertLog, Base, ChatLog, backend/db/models.py SQLAlchemy ORM models for WeatherGPT., Stores every conversational query, language, domain, and AI response. (+10 more)

### Community 3 - "fetch_weather"
Cohesion: 0.17
Nodes (19): _derive_local_alert(), _fetch_aqi(), fetch_weather(), backend/services/weather_service.py OpenWeatherMap integration: - Current…, Generate a simple IMD-style advisory from current conditions., Return (lat, lon, resolved_name, country)., Fetch Air Quality Index (1=Good … 5=Very Poor)., Fetch comprehensive current weather + 5-day forecast for a city. Returns a… (+11 more)

### Community 4 - "🌦️ WeatherGPT — AI-Powered Weather Intelligence Platform"
Cohesion: 0.11
Nodes (18): 1. Clone & set up environment, 2. Install dependencies, 3. Run backend, 4. Run frontend (new terminal), 5. Or use Docker (one command), 🧠 AI / LLM Design, 🌐 API Endpoints, 🏗️ Architecture (+10 more)

### Community 5 - "alert_service.py"
Cohesion: 0.24
Nodes (12): AlertDetail, AlertResponse, get_alerts(), get, Returns active extreme weather alerts for the specified city. Sourced from OWM…, get_alert_summary(), get_alerts_for_city(), _get_coords() (+4 more)

### Community 6 - "weather_gpt_frontend.py"
Cohesion: 0.20
Nodes (6): _mock_response(), frontend/weather_gpt_frontend.py WeatherGPT — AI-powered weather intelligence…, Friendly fallback when backend is offline., render_weather_card(), send_chat(), wind_direction_arrow()

### Community 7 - "package.json"
Cohesion: 0.17
Nodes (11): author, description, keywords, license, name, scripts, dev, serve:frontend (+3 more)

### Community 8 - "setup.py"
Cohesion: 0.25
Nodes (7): check_env_file(), get_setup_instructions(), Check if .env file exists and has required keys, WeatherGPT Setup Script This script helps you get started with WeatherGPT by:…, Test if backend health endpoint is working, Print setup instructions, test_backend_health()

### Community 9 - "test_chat.py"
Cohesion: 0.38
Nodes (5): patch, tests/test_chat.py — WeatherGPT chat endpoint tests., test_chat_404_for_unknown_city(), test_chat_live_response(), test_chat_returns_cached_response()

### Community 10 - "config.py"
Cohesion: 0.40
Nodes (4): fetch_climate_data(), _get_coords(), backend/services/climate_service.py Historical climate analytics using Open-…, Fetch historical daily climate averages for a city in a given month. Uses the…

### Community 11 - "location_parser.py"
Cohesion: 0.50
Nodes (3): extract_city(), backend/utils/location_parser.py Extract a city/location name from a free-text…, Try to pull a city name from the query string. Returns the matched city (Title-…

## Knowledge Gaps
- **30 isolated node(s):** `API`, `App`, `WeatherCharts`, `ChatUI`, `WeatherUI` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 103 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `fetch_weather()` connect `fetch_weather` to `chat.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `generate_weather_response()` connect `llm_service.py` to `chat.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `chat()` (e.g. with `ChatRequest` and `ChatResponse`) actually correct?**
  _`chat()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `get_climate()` (e.g. with `ClimateRequest` and `ClimateResponse`) actually correct?**
  _`get_climate()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `API`, `App`, `WeatherCharts` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `chat.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11092436974789915 - nodes in this community are weakly interconnected._
- **Should `llm_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1402116402116402 - nodes in this community are weakly interconnected._