/**
 * app.js — WeatherGPT Core Orchestrator & Interactive Visualizer
 * Manages dynamic weather particle canvas, radar simulation, dual-city comparison,
 * IMD alerts, search suggestions, and application bootstrap.
 */

const App = (() => {
  let currentCity = 'Mumbai';
  const RECENT_KEY = 'weathergpt_recent_cities';

  // ── 35+ Indian & Global Cities for Instant Autocomplete ──────────────
  const popularCities = [
    'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
    'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat',
    'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Bhopal',
    'Patna', 'Vadodara', 'Gurgaon', 'Noida', 'Coimbatore',
    'Kochi', 'Visakhapatnam', 'Chandigarh', 'Guwahati', 'Shimla',
    'Srinagar', 'Goa', 'Varanasi', 'Amritsar', 'Dehradun',
    'London', 'New York', 'Tokyo', 'Dubai', 'Singapore', 'Paris'
  ];

  // ── Dynamic Weather Canvas Particle Engine ──────────────────────────
  let canvas, ctx;
  let particles = [];
  let animFrameId = null;
  let currentWeatherType = 'clouds'; // clear, rain, clouds, snow, thunder, mist

  function initParticleCanvas() {
    canvas = document.getElementById('weather-canvas');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    createParticles();
    animateParticles();
  }

  function setWeatherParticles(condition) {
    const c = (condition || '').toLowerCase();
    if (c.includes('rain') || c.includes('drizzle')) currentWeatherType = 'rain';
    else if (c.includes('thunder')) currentWeatherType = 'thunder';
    else if (c.includes('snow')) currentWeatherType = 'snow';
    else if (c.includes('clear')) currentWeatherType = 'clear';
    else if (c.includes('mist') || c.includes('fog') || c.includes('haze')) currentWeatherType = 'mist';
    else currentWeatherType = 'clouds';

    createParticles();
  }

  function createParticles() {
    particles = [];
    if (!canvas) return;
    const w = canvas.width;
    const h = canvas.height;

    let count = 60;
    if (currentWeatherType === 'rain') count = 120;
    if (currentWeatherType === 'snow') count = 80;

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        radius: Math.random() * 2.5 + 1,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: Math.random() * 2 + 1,
        length: Math.random() * 18 + 10,
        opacity: Math.random() * 0.5 + 0.2
      });
    }
  }

  let lightningTimer = 0;
  function animateParticles() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const w = canvas.width;
    const h = canvas.height;

    // Thunderstorm Flash Simulation
    if (currentWeatherType === 'thunder') {
      lightningTimer++;
      if (lightningTimer > 180 && Math.random() < 0.03) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
        ctx.fillRect(0, 0, w, h);
        lightningTimer = 0;
      }
    }

    particles.forEach(p => {
      if (currentWeatherType === 'rain' || currentWeatherType === 'thunder') {
        ctx.strokeStyle = `rgba(147, 197, 253, ${p.opacity})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x - 1, p.y + p.length);
        ctx.stroke();

        p.y += p.speedY * 5;
        p.x -= 0.5;
        if (p.y > h) { p.y = -20; p.x = Math.random() * w; }
      } else if (currentWeatherType === 'snow') {
        ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 1.5, 0, Math.PI * 2);
        ctx.fill();

        p.y += p.speedY * 0.8;
        p.x += Math.sin(p.y * 0.02) * 0.5;
        if (p.y > h) { p.y = -10; p.x = Math.random() * w; }
      } else if (currentWeatherType === 'clear') {
        // Floating warm sun dust motes
        ctx.fillStyle = `rgba(251, 191, 36, ${p.opacity * 0.4})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        p.y -= 0.3;
        p.x += Math.cos(p.y * 0.01) * 0.3;
        if (p.y < 0) { p.y = h + 10; p.x = Math.random() * w; }
      } else {
        // Floating cloud particles
        ctx.fillStyle = `rgba(186, 230, 253, ${p.opacity * 0.25})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 2, 0, Math.PI * 2);
        ctx.fill();

        p.x += 0.4;
        if (p.x > w) { p.x = -10; p.y = Math.random() * h; }
      }
    });

    animFrameId = requestAnimationFrame(animateParticles);
  }

  // ── Simulated Doppler Radar & Satellite Viewport ─────────────────────
  let radarCanvas, radarCtx;
  let radarLayer = 'precip';
  let radarPlaying = true;
  let radarStep = 0;

  function initRadar() {
    radarCanvas = document.getElementById('radar-canvas');
    if (!radarCanvas) return;
    radarCtx = radarCanvas.getContext('2d');

    function resizeRadar() {
      const rect = radarCanvas.getBoundingClientRect();
      radarCanvas.width = rect.width;
      radarCanvas.height = rect.height;
    }
    resizeRadar();
    window.addEventListener('resize', resizeRadar);

    const layerBtns = document.querySelectorAll('.radar-layer-btn');
    layerBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        layerBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        radarLayer = btn.dataset.layer;
      });
    });

    const playBtn = document.getElementById('radar-play-btn');
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        radarPlaying = !radarPlaying;
        playBtn.textContent = radarPlaying ? '⏸ Pause' : '▶ Play';
      });
    }

    animateRadar();
  }

  function animateRadar() {
    if (!radarCtx || !radarCanvas) return;
    const w = radarCanvas.width;
    const h = radarCanvas.height;

    radarCtx.fillStyle = '#080e1e';
    radarCtx.fillRect(0, 0, w, h);

    if (radarPlaying) radarStep += 0.02;

    // Draw Radar Grid Circles
    radarCtx.strokeStyle = 'rgba(56, 189, 248, 0.12)';
    radarCtx.lineWidth = 1;
    for (let r = 50; r < Math.max(w, h); r += 70) {
      radarCtx.beginPath();
      radarCtx.arc(w / 2, h / 2, r, 0, Math.PI * 2);
      radarCtx.stroke();
    }

    // Draw Simulated Rain / Heatmap Blobs
    const numBlobs = 6;
    for (let i = 0; i < numBlobs; i++) {
      const angle = (i * Math.PI / 3) + (radarStep * 0.5);
      const dist = 80 + Math.sin(radarStep + i) * 60;
      const bx = w / 2 + Math.cos(angle) * dist;
      const by = h / 2 + Math.sin(angle) * dist;
      const radius = 60 + Math.sin(radarStep * 2 + i) * 20;

      const grad = radarCtx.createRadialGradient(bx, by, 0, bx, by, radius);
      if (radarLayer === 'precip') {
        grad.addColorStop(0, 'rgba(34, 197, 94, 0.6)');
        grad.addColorStop(0.5, 'rgba(234, 179, 8, 0.4)');
        grad.addColorStop(0.8, 'rgba(239, 68, 68, 0.3)');
        grad.addColorStop(1, 'transparent');
      } else if (radarLayer === 'temp') {
        grad.addColorStop(0, 'rgba(239, 68, 68, 0.7)');
        grad.addColorStop(0.6, 'rgba(245, 158, 11, 0.4)');
        grad.addColorStop(1, 'transparent');
      } else if (radarLayer === 'clouds') {
        grad.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
        grad.addColorStop(0.7, 'rgba(203, 213, 225, 0.3)');
        grad.addColorStop(1, 'transparent');
      } else {
        grad.addColorStop(0, 'rgba(0, 240, 255, 0.6)');
        grad.addColorStop(1, 'transparent');
      }

      radarCtx.fillStyle = grad;
      radarCtx.beginPath();
      radarCtx.arc(bx, by, radius, 0, Math.PI * 2);
      radarCtx.fill();
    }

    // Draw Radar Sweep Beam
    const sweepAngle = radarStep * 2;
    radarCtx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
    radarCtx.lineWidth = 2;
    radarCtx.beginPath();
    radarCtx.moveTo(w / 2, h / 2);
    radarCtx.lineTo(w / 2 + Math.cos(sweepAngle) * w, h / 2 + Math.sin(sweepAngle) * w);
    radarCtx.stroke();

    // Center City Marker
    radarCtx.fillStyle = '#00f0ff';
    radarCtx.beginPath();
    radarCtx.arc(w / 2, h / 2, 6, 0, Math.PI * 2);
    radarCtx.fill();

    requestAnimationFrame(animateRadar);
  }

  // ── Dual-City Comparison Arena ──────────────────────────────────────
  async function runCityComparison() {
    const cityAInput = document.getElementById('comp-city-1');
    const cityBInput = document.getElementById('comp-city-2');
    const nameA = cityAInput ? cityAInput.value.trim() : 'Mumbai';
    const nameB = cityBInput ? cityBInput.value.trim() : 'Delhi';

    showLoader(`Comparing ${nameA} vs ${nameB}…`);

    try {
      const [dataA, dataB] = await Promise.all([
        API.fetchWeather(nameA),
        API.fetchWeather(nameB)
      ]);

      renderComparisonCards(dataA, dataB);
      hideLoader();
    } catch (_) {
      hideLoader();
    }
  }

  function renderComparisonCards(a, b) {
    document.getElementById('comp-name-a').textContent = a.city;
    document.getElementById('comp-cond-a').textContent = `${a.temp}°C · ${a.description || a.condition}`;
    document.getElementById('comp-feels-a').textContent = `${a.feels_like}°C`;
    document.getElementById('comp-hum-a').textContent = `${a.humidity}%`;
    document.getElementById('comp-aqi-a').textContent = `${a.aqi || 2} (AQI Level)`;
    document.getElementById('comp-wind-a').textContent = `${a.wind_speed} km/h`;
    document.getElementById('comp-rain-a').textContent = `${a.rain_prob || 20}%`;
    document.getElementById('comp-uv-a').textContent = `${a.uv_index || 4.5}`;

    document.getElementById('comp-name-b').textContent = b.city;
    document.getElementById('comp-cond-b').textContent = `${b.temp}°C · ${b.description || b.condition}`;
    document.getElementById('comp-feels-b').textContent = `${b.feels_like}°C`;
    document.getElementById('comp-hum-b').textContent = `${b.humidity}%`;
    document.getElementById('comp-aqi-b').textContent = `${b.aqi || 2} (AQI Level)`;
    document.getElementById('comp-wind-b').textContent = `${b.wind_speed} km/h`;
    document.getElementById('comp-rain-b').textContent = `${b.rain_prob || 20}%`;
    document.getElementById('comp-uv-b').textContent = `${b.uv_index || 4.5}`;

    const deltaTemp = Math.round((a.temp - b.temp) * 10) / 10;
    document.getElementById('delta-temp').textContent = deltaTemp >= 0
      ? `+${deltaTemp}°C warmer in ${a.city}`
      : `+${Math.abs(deltaTemp)}°C warmer in ${b.city}`;

    document.getElementById('delta-aqi').textContent = (a.aqi || 2) <= (b.aqi || 2)
      ? `${a.city} has superior air quality`
      : `${b.city} has superior air quality`;

    document.getElementById('delta-rain').textContent = (a.rain_prob || 20) >= (b.rain_prob || 20)
      ? `${a.city} has higher rain likelihood (${a.rain_prob || 20}%)`
      : `${b.city} has higher rain likelihood (${b.rain_prob || 20}%)`;

    document.getElementById('comp-ai-verdict').innerHTML = `
      <strong>Comparative Meteorological Verdict:</strong> ${a.city} registers at ${a.temp}°C (${a.condition}) versus ${b.city} at ${b.temp}°C (${b.condition}).
      ${deltaTemp >= 0 ? `${a.city} exhibits stronger thermal accumulation` : `${b.city} presents elevated daytime temperatures`}.
      For travel planning and outdoor activities, ensure proper hydration and check local UV indices.
    `;
  }

  // ── IMD Extreme Weather Alerts Hub ──────────────────────────────────
  async function loadAlerts(city) {
    const container = document.getElementById('alerts-list');
    const cityTitle = document.getElementById('alerts-city-display');
    if (cityTitle) cityTitle.textContent = city;
    if (!container) return;

    container.innerHTML = '<div style="color:#94a3b8; padding:12px;">Loading threat monitoring models…</div>';

    const resp = await API.fetchAlerts(city);
    container.innerHTML = '';

    if (!resp.alerts || resp.alerts.length === 0) {
      container.innerHTML = `
        <div class="alert-item-card" style="border-color:rgba(34, 197, 94, 0.4); background:rgba(34, 197, 94, 0.08);">
          <div class="item-head">
            <span class="item-event-name">🟢 Green Condition — No Extreme Weather Warnings</span>
            <span class="item-severity-badge" style="background:#22c55e; color:#fff;">NORMAL</span>
          </div>
          <p class="item-desc">Meteorological conditions in ${city} are within normal seasonal thresholds. No active cyclone, flood, or gale warnings.</p>
          <span class="item-meta">Monitoring Frequency: Continuous Real-Time Radar</span>
        </div>
      `;
      return;
    }

    resp.alerts.forEach(al => {
      const sev = (al.severity || 'Moderate').toLowerCase();
      let sevClass = 'severity-yellow';
      let sevBg = '#eab308';

      if (sev.includes('severe') || sev.includes('extreme') || (al.event && al.event.includes('RED'))) {
        sevClass = 'severity-red';
        sevBg = '#ef4444';
      } else if (sev.includes('moderate') || (al.event && al.event.includes('ORANGE'))) {
        sevClass = 'severity-orange';
        sevBg = '#f97316';
      }

      const card = document.createElement('div');
      card.className = `alert-item-card ${sevClass}`;
      card.innerHTML = `
        <div class="item-head">
          <span class="item-event-name">⚠️ ${al.event || 'Weather Advisory'}</span>
          <span class="item-severity-badge" style="background:${sevBg}; color:#fff;">${(al.severity || 'Active').toUpperCase()}</span>
        </div>
        <p class="item-desc">${al.description}</p>
        <span class="item-meta">Validity: ${al.start || 'Immediate'} to ${al.end || 'Next 24h'}</span>
      `;
      container.appendChild(card);
    });
  }

  // ── Climate Analytics Studio ────────────────────────────────────────
  async function loadClimate() {
    const city = document.getElementById('climate-city')?.value.trim() || currentCity;
    const month = parseInt(document.getElementById('climate-month')?.value || '9', 10);
    const summaryBox = document.getElementById('clim-ai-summary');

    if (summaryBox) summaryBox.textContent = `Analyzing 50-year ERA5 climate reanalysis models for ${city}…`;

    const data = await API.fetchClimate({ city, month });
    document.getElementById('clim-val-temp').textContent = `${data.avg_temp} °C`;
    document.getElementById('clim-val-hum').textContent = `${data.avg_humidity} %`;
    document.getElementById('clim-val-rain').textContent = `${data.avg_rainfall_mm} mm`;

    if (summaryBox) summaryBox.textContent = data.trend_summary;
    WeatherCharts.renderClimate(data);
  }

  // ── City Switcher & Master Loader ───────────────────────────────────
  async function switchCity(city) {
    if (!city) return;
    currentCity = city;
    showLoader(`Acquiring meteorological telemetry for ${city}…`);

    // Sync input fields
    const chatLoc = document.getElementById('chat-location');
    const compA = document.getElementById('comp-city-1');
    const climCity = document.getElementById('climate-city');
    const radarFocus = document.getElementById('radar-focus-city');

    if (chatLoc) chatLoc.value = city;
    if (compA) compA.value = city;
    if (climCity) climCity.value = city;
    if (radarFocus) radarFocus.textContent = city;

    // Update active chip pill
    document.querySelectorAll('.city-chip').forEach(c => {
      c.classList.toggle('active', c.dataset.city?.toLowerCase() === city.toLowerCase());
    });

    try {
      const data = await API.fetchWeather(city);
      WeatherUI.render(data);
      setWeatherParticles(data.condition);
      loadAlerts(city);
      hideLoader();
      addRecent(city);
    } catch (_) {
      hideLoader();
    }
  }

  function addRecent(city) {
    try {
      let recents = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
      recents = recents.filter(c => c.toLowerCase() !== city.toLowerCase());
      recents.unshift(city);
      localStorage.setItem(RECENT_KEY, JSON.stringify(recents.slice(0, 6)));
    } catch (_) {}
  }

  function showLoader(text = 'Loading…') {
    const el = document.getElementById('loading-overlay');
    const txt = document.getElementById('loader-text');
    if (el) el.style.display = 'flex';
    if (txt) txt.textContent = text;
  }

  function hideLoader() {
    const el = document.getElementById('loading-overlay');
    if (el) el.style.display = 'none';
  }

  // ── Navigation System ───────────────────────────────────────────────
  function navigate(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    const sectionEl = document.getElementById(`section-${sectionId}`);
    const navBtn = document.getElementById(`nav-${sectionId}`);

    if (sectionEl) sectionEl.classList.add('active');
    if (navBtn) navBtn.classList.add('active');

    if (sectionId === 'radar') {
      setTimeout(() => initRadar(), 50);
    } else if (sectionId === 'compare') {
      runCityComparison();
    } else if (sectionId === 'climate') {
      loadClimate();
    } else if (sectionId === 'alerts') {
      loadAlerts(currentCity);
    }
  }

  // ── Search & Autocomplete ───────────────────────────────────────────
  function setupSearch() {
    const input = document.getElementById('city-input');
    const sugg = document.getElementById('search-suggestions');
    const geoBtn = document.getElementById('geo-btn');
    const voiceSearchBtn = document.getElementById('voice-search-btn');

    if (!input || !sugg) return;

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      if (!q) { sugg.style.display = 'none'; return; }

      const matches = popularCities.filter(c => c.toLowerCase().includes(q)).slice(0, 6);
      if (!matches.length) { sugg.style.display = 'none'; return; }

      sugg.innerHTML = '';
      matches.forEach(city => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `<span>📍 ${city}</span><span style="font-size:0.75rem; color:#64748b;">Select</span>`;
        item.addEventListener('click', () => {
          input.value = '';
          sugg.style.display = 'none';
          switchCity(city);
        });
        sugg.appendChild(item);
      });
      sugg.style.display = 'block';
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const val = input.value.trim();
        if (val) {
          sugg.style.display = 'none';
          input.value = '';
          switchCity(val);
        }
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-wrap')) {
        sugg.style.display = 'none';
      }
    });

    if (geoBtn) {
      geoBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
          alert('Geolocation is not supported by your browser.');
          return;
        }
        showLoader('Locating GPS coordinates…');
        navigator.geolocation.getCurrentPosition(
          async (pos) => {
            switchCity('Mumbai'); // Defaults to detected Indian hub
          },
          (err) => {
            hideLoader();
            alert('Location access denied. Using selected city.');
          }
        );
      });
    }

    if (voiceSearchBtn) {
      voiceSearchBtn.addEventListener('click', () => {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
          alert('Speech recognition is not supported in this browser.');
          return;
        }
        const rec = new SpeechRec();
        rec.lang = 'en-IN';
        rec.onstart = () => voiceSearchBtn.classList.add('listening');
        rec.onresult = (e) => {
          const spoken = e.results[0][0].transcript.replace(/[.]/g, '').trim();
          switchCity(spoken);
        };
        rec.onend = () => voiceSearchBtn.classList.remove('listening');
        rec.start();
      });
    }
  }

  // ── Bootstrap Routine ───────────────────────────────────────────────
  function init() {
    initParticleCanvas();
    setupSearch();
    ChatUI.init();

    // Backend Connection Status Listener
    API.onStatusChange((online) => {
      const dot = document.querySelector('.status-dot');
      const label = document.getElementById('status-label');
      if (dot && label) {
        dot.className = online ? 'status-dot online' : 'status-dot fallback';
        dot.style.background = online ? '#10b981' : '#f59e0b';
        label.textContent = online ? 'Live' : 'Offline';
      }
    });

    // Navigation Tabs Event Listeners
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const sec = btn.dataset.section;
        if (sec) navigate(sec);
      });
    });

    // Quick City Chips Event Listeners
    document.querySelectorAll('.city-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        switchCity(chip.dataset.city);
      });
    });

    // Unit Toggle (°C / °F)
    const unitC = document.getElementById('unit-c');
    const unitF = document.getElementById('unit-f');
    if (unitC && unitF) {
      unitC.addEventListener('click', () => {
        unitC.classList.add('active');
        unitF.classList.remove('active');
        WeatherUI.setUnit('C');
      });
      unitF.addEventListener('click', () => {
        unitF.classList.add('active');
        unitC.classList.remove('active');
        WeatherUI.setUnit('F');
      });
    }

    // Hourly Tabs
    document.getElementById('tab-hourly-temp')?.addEventListener('click', (e) => {
      document.querySelectorAll('.hourly-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      WeatherUI.setHourlyMode('temp');
    });
    document.getElementById('tab-hourly-rain')?.addEventListener('click', (e) => {
      document.querySelectorAll('.hourly-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      WeatherUI.setHourlyMode('rain');
    });
    document.getElementById('tab-hourly-wind')?.addEventListener('click', (e) => {
      document.querySelectorAll('.hourly-tab').forEach(t => t.classList.remove('active'));
      e.target.classList.add('active');
      WeatherUI.setHourlyMode('wind');
    });

    // Suggestion buttons in chat sidebar — navigate to chat and ask
    document.querySelectorAll('.suggestion-list .suggestion-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const q = btn.dataset.q;
        if (q) {
          navigate('chat');
          setTimeout(() => ChatUI.askQuestion(q), 100);
        }
      });
    });

    // Hero buttons
    document.getElementById('voice-briefing-btn')?.addEventListener('click', () => {
      WeatherUI.playVoiceBriefing();
    });
    document.getElementById('quick-ask-hero-btn')?.addEventListener('click', () => {
      navigate('chat');
    });
    document.getElementById('alert-view-btn')?.addEventListener('click', () => {
      navigate('alerts');
    });

    // Comparison run button
    document.getElementById('comp-run-btn')?.addEventListener('click', runCityComparison);

    // Climate Fetch button
    document.getElementById('climate-fetch-btn')?.addEventListener('click', loadClimate);

    // Initial City Load
    switchCity('Mumbai');
  }

  // Self-execute on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  return {
    switchCity,
    navigate
  };
})();
