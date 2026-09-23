/**
 * app.js — METEOR Operations Orchestrator & Telemetry Visualizer
 * Controls particle engine, radar simulation, city analytics, hazard alerts,
 * and application state management.
 */

const App = (() => {
  let currentCity = 'Mumbai';
  const RECENT_KEY = 'meteor_recent_stations';

  // ── 50+ Indian & Global Meteorological Stations for Autocomplete & Hub ──────
  const popularCities = [
    'Mumbai', 'Delhi', 'Bengaluru', 'Chennai', 'Kolkata', 'Hyderabad',
    'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur',
    'Nagpur', 'Indore', 'Bhopal', 'Patna', 'Vadodara', 'Ghaziabad',
    'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut', 'Rajkot',
    'Varanasi', 'Srinagar', 'Aurangabad', 'Dhanbad', 'Amritsar', 'Prayagraj',
    'Ranchi', 'Howrah', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Jodhpur',
    'Madurai', 'Raipur', 'Kota', 'Guwahati', 'Chandigarh', 'Solapur',
    'Hubballi', 'Bareilly', 'Moradabad', 'Mysuru', 'Gurugram', 'Aligarh',
    'Jalandhar', 'Tiruchirappalli', 'Bhubaneswar', 'Salem', 'Warangal',
    'Thiruvananthapuram', 'Kochi', 'Visakhapatnam', 'Shimla', 'Dehradun',
    'Gangtok', 'Panaji', 'Imphal', 'Shillong', 'Aizawl', 'Kohima',
    'Agartala', 'Itanagar', 'Leh', 'Puducherry', 'Port Blair',
    'London', 'New York', 'Tokyo', 'Dubai', 'Singapore', 'Paris'
  ];

  const stationHubList = [
    { city: 'Mumbai', state: 'Maharashtra', region: 'West & Central', icon: '🏙️' },
    { city: 'Delhi', state: 'Delhi NCR', region: 'Northern Region', icon: '🏛️' },
    { city: 'Bengaluru', state: 'Karnataka', region: 'Southern Region', icon: '💻' },
    { city: 'Chennai', state: 'Tamil Nadu', region: 'Southern Region', icon: '🌊' },
    { city: 'Kolkata', state: 'West Bengal', region: 'Eastern Region', icon: '🎭' },
    { city: 'Hyderabad', state: 'Telangana', region: 'Southern Region', icon: '🏰' },
    { city: 'Srinagar', state: 'Jammu & Kashmir', region: 'Northern Region', icon: '🏔️' },
    { city: 'Leh', state: 'Ladakh UT', region: 'Northern Region', icon: '❄️' },
    { city: 'Shimla', state: 'Himachal Pradesh', region: 'Northern Region', icon: '🌲' },
    { city: 'Chandigarh', state: 'Chandigarh UT', region: 'Northern Region', icon: '🪴' },
    { city: 'Amritsar', state: 'Punjab', region: 'Northern Region', icon: '🕌' },
    { city: 'Ludhiana', state: 'Punjab', region: 'Northern Region', icon: '🌾' },
    { city: 'Jalandhar', state: 'Punjab', region: 'Northern Region', icon: '⚽' },
    { city: 'Dehradun', state: 'Uttarakhand', region: 'Northern Region', icon: '⛰️' },
    { city: 'Lucknow', state: 'Uttar Pradesh', region: 'Northern Region', icon: '🏯' },
    { city: 'Kanpur', state: 'Uttar Pradesh', region: 'Northern Region', icon: '🏭' },
    { city: 'Varanasi', state: 'Uttar Pradesh', region: 'Northern Region', icon: '🪔' },
    { city: 'Agra', state: 'Uttar Pradesh', region: 'Northern Region', icon: '🕌' },
    { city: 'Prayagraj', state: 'Uttar Pradesh', region: 'Northern Region', icon: '⛵' },
    { city: 'Ghaziabad', state: 'Uttar Pradesh', region: 'Northern Region', icon: '🌇' },
    { city: 'Noida', state: 'Uttar Pradesh', region: 'Northern Region', icon: '🏙️' },
    { city: 'Gurugram', state: 'Haryana', region: 'Northern Region', icon: '🏢' },
    { city: 'Pune', state: 'Maharashtra', region: 'West & Central', icon: '🎓' },
    { city: 'Nagpur', state: 'Maharashtra', region: 'West & Central', icon: '🍊' },
    { city: 'Nashik', state: 'Maharashtra', region: 'West & Central', icon: '🍇' },
    { city: 'Aurangabad', state: 'Maharashtra', region: 'West & Central', icon: '🗿' },
    { city: 'Solapur', state: 'Maharashtra', region: 'West & Central', icon: '🧵' },
    { city: 'Ahmedabad', state: 'Gujarat', region: 'West & Central', icon: '🪁' },
    { city: 'Surat', state: 'Gujarat', region: 'West & Central', icon: '💎' },
    { city: 'Vadodara', state: 'Gujarat', region: 'West & Central', icon: '🎨' },
    { city: 'Rajkot', state: 'Gujarat', region: 'West & Central', icon: '⚙️' },
    { city: 'Jaipur', state: 'Rajasthan', region: 'West & Central', icon: '🏰' },
    { city: 'Jodhpur', state: 'Rajasthan', region: 'West & Central', icon: '🏜️' },
    { city: 'Udaipur', state: 'Rajasthan', region: 'West & Central', icon: '⛵' },
    { city: 'Kota', state: 'Rajasthan', region: 'West & Central', icon: '📚' },
    { city: 'Bhopal', state: 'Madhya Pradesh', region: 'West & Central', icon: '🏞️' },
    { city: 'Indore', state: 'Madhya Pradesh', region: 'West & Central', icon: '✨' },
    { city: 'Gwalior', state: 'Madhya Pradesh', region: 'West & Central', icon: '🏰' },
    { city: 'Jabalpur', state: 'Madhya Pradesh', region: 'West & Central', icon: '🌊' },
    { city: 'Panaji', state: 'Goa', region: 'West & Central', icon: '🏖️' },
    { city: 'Howrah', state: 'West Bengal', region: 'Eastern Region', icon: '🌉' },
    { city: 'Patna', state: 'Bihar', region: 'Eastern Region', icon: '🏛️' },
    { city: 'Gaya', state: 'Bihar', region: 'Eastern Region', icon: '🪔' },
    { city: 'Ranchi', state: 'Jharkhand', region: 'Eastern Region', icon: '🌲' },
    { city: 'Dhanbad', state: 'Jharkhand', region: 'Eastern Region', icon: '⛏️' },
    { city: 'Bhubaneswar', state: 'Odisha', region: 'Eastern Region', icon: '🛕' },
    { city: 'Cuttack', state: 'Odisha', region: 'Eastern Region', icon: '🚣' },
    { city: 'Raipur', state: 'Chhattisgarh', region: 'Eastern Region', icon: '🏭' },
    { city: 'Mysuru', state: 'Karnataka', region: 'Southern Region', icon: '👑' },
    { city: 'Hubballi', state: 'Karnataka', region: 'Southern Region', icon: '🚉' },
    { city: 'Coimbatore', state: 'Tamil Nadu', region: 'Southern Region', icon: '🏭' },
    { city: 'Madurai', state: 'Tamil Nadu', region: 'Southern Region', icon: '🛕' },
    { city: 'Tiruchirappalli', state: 'Tamil Nadu', region: 'Southern Region', icon: '🏰' },
    { city: 'Salem', state: 'Tamil Nadu', region: 'Southern Region', icon: '⛰️' },
    { city: 'Warangal', state: 'Telangana', region: 'Southern Region', icon: '🗿' },
    { city: 'Vijayawada', state: 'Andhra Pradesh', region: 'Southern Region', icon: '🌊' },
    { city: 'Visakhapatnam', state: 'Andhra Pradesh', region: 'Southern Region', icon: '⚓' },
    { city: 'Thiruvananthapuram', state: 'Kerala', region: 'Southern Region', icon: '🌴' },
    { city: 'Kochi', state: 'Kerala', region: 'Southern Region', icon: '⛵' },
    { city: 'Guwahati', state: 'Assam', region: 'North-East Region', icon: '🦏' },
    { city: 'Gangtok', state: 'Sikkim', region: 'North-East Region', icon: '🏔️' },
    { city: 'Shillong', state: 'Meghalaya', region: 'North-East Region', icon: '🌧️' },
    { city: 'Imphal', state: 'Manipur', region: 'North-East Region', icon: '🌸' },
    { city: 'Aizawl', state: 'Mizoram', region: 'North-East Region', icon: '🏞️' },
    { city: 'Kohima', state: 'Nagaland', region: 'North-East Region', icon: '🌄' },
    { city: 'Agartala', state: 'Tripura', region: 'North-East Region', icon: '🏛️' },
    { city: 'Itanagar', state: 'Arunachal Pradesh', region: 'North-East Region', icon: '🌄' },
    { city: 'Puducherry', state: 'Puducherry UT', region: 'Islands & UT', icon: '🏖️' },
    { city: 'Port Blair', state: 'Andaman & Nicobar UT', region: 'Islands & UT', icon: '🏝️' },
    { city: 'London', state: 'UK', region: 'Global', icon: '🇬🇧' },
    { city: 'New York', state: 'USA', region: 'Global', icon: '🇺🇸' },
    { city: 'Tokyo', state: 'Japan', region: 'Global', icon: '🇯🇵' },
    { city: 'Dubai', state: 'UAE', region: 'Global', icon: '🇦🇪' },
    { city: 'Singapore', state: 'Singapore', region: 'Global', icon: '🇸🇬' },
    { city: 'Paris', state: 'France', region: 'Global', icon: '🇫🇷' }
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
        radius: Math.random() * 2 + 1,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: Math.random() * 2 + 1,
        length: Math.random() * 16 + 8,
        opacity: Math.random() * 0.4 + 0.15
      });
    }
  }

  let lightningTimer = 0;
  function animateParticles() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const w = canvas.width;
    const h = canvas.height;

    if (currentWeatherType === 'thunder') {
      lightningTimer++;
      if (lightningTimer > 180 && Math.random() < 0.03) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.fillRect(0, 0, w, h);
        lightningTimer = 0;
      }
    }

    particles.forEach(p => {
      if (currentWeatherType === 'rain' || currentWeatherType === 'thunder') {
        ctx.strokeStyle = `rgba(56, 189, 248, ${p.opacity})`;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x - 1, p.y + p.length);
        ctx.stroke();

        p.y += p.speedY * 4.5;
        p.x -= 0.5;
        if (p.y > h) { p.y = -20; p.x = Math.random() * w; }
      } else if (currentWeatherType === 'snow') {
        ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 1.3, 0, Math.PI * 2);
        ctx.fill();

        p.y += p.speedY * 0.8;
        p.x += Math.sin(p.y * 0.02) * 0.5;
        if (p.y > h) { p.y = -10; p.x = Math.random() * w; }
      } else if (currentWeatherType === 'clear') {
        ctx.fillStyle = `rgba(245, 158, 11, ${p.opacity * 0.3})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        p.y -= 0.3;
        p.x += Math.cos(p.y * 0.01) * 0.3;
        if (p.y < 0) { p.y = h + 10; p.x = Math.random() * w; }
      } else {
        ctx.fillStyle = `rgba(148, 163, 184, ${p.opacity * 0.2})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 2, 0, Math.PI * 2);
        ctx.fill();

        p.x += 0.3;
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

    radarCtx.fillStyle = '#040810';
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
        grad.addColorStop(0, 'rgba(16, 185, 129, 0.6)');
        grad.addColorStop(0.5, 'rgba(245, 158, 11, 0.4)');
        grad.addColorStop(0.8, 'rgba(239, 68, 68, 0.3)');
        grad.addColorStop(1, 'transparent');
      } else if (radarLayer === 'temp') {
        grad.addColorStop(0, 'rgba(239, 68, 68, 0.7)');
        grad.addColorStop(0.6, 'rgba(245, 158, 11, 0.4)');
        grad.addColorStop(1, 'transparent');
      } else if (radarLayer === 'clouds') {
        grad.addColorStop(0, 'rgba(255, 255, 255, 0.5)');
        grad.addColorStop(0.7, 'rgba(148, 163, 184, 0.25)');
        grad.addColorStop(1, 'transparent');
      } else {
        grad.addColorStop(0, 'rgba(56, 189, 248, 0.6)');
        grad.addColorStop(1, 'transparent');
      }

      radarCtx.fillStyle = grad;
      radarCtx.beginPath();
      radarCtx.arc(bx, by, radius, 0, Math.PI * 2);
      radarCtx.fill();
    }

    // Draw Radar Sweep Beam
    const sweepAngle = radarStep * 2;
    radarCtx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
    radarCtx.lineWidth = 1.5;
    radarCtx.beginPath();
    radarCtx.moveTo(w / 2, h / 2);
    radarCtx.lineTo(w / 2 + Math.cos(sweepAngle) * w, h / 2 + Math.sin(sweepAngle) * w);
    radarCtx.stroke();

    // Center City Marker
    radarCtx.fillStyle = '#38bdf8';
    radarCtx.beginPath();
    radarCtx.arc(w / 2, h / 2, 5, 0, Math.PI * 2);
    radarCtx.fill();

    requestAnimationFrame(animateRadar);
  }

  // ── Dual-City Comparison Arena ──────────────────────────────────────
  async function runCityComparison() {
    const cityAInput = document.getElementById('comp-city-1');
    const cityBInput = document.getElementById('comp-city-2');
    const nameA = cityAInput ? cityAInput.value.trim() : 'Mumbai';
    const nameB = cityBInput ? cityBInput.value.trim() : 'Delhi';

    showLoader(`Acquiring comparison metrics for ${nameA} vs ${nameB}…`);

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
    const condA = (typeof i18n !== 'undefined') ? i18n.translateCondition(a.description || a.condition) : (a.description || a.condition);
    const condB = (typeof i18n !== 'undefined') ? i18n.translateCondition(b.description || b.condition) : (b.description || b.condition);
    document.getElementById('comp-name-a').textContent = a.city;
    document.getElementById('comp-cond-a').textContent = `${a.temp}°C · ${condA}`;
    document.getElementById('comp-feels-a').textContent = `${a.feels_like}°C`;
    document.getElementById('comp-hum-a').textContent = `${a.humidity}%`;
    document.getElementById('comp-aqi-a').textContent = `${a.aqi || 2} (AQI)`;
    document.getElementById('comp-wind-a').textContent = `${a.wind_speed} km/h`;
    document.getElementById('comp-rain-a').textContent = `${a.rain_prob || 20}%`;
    document.getElementById('comp-uv-a').textContent = `${a.uv_index || 4.5}`;

    document.getElementById('comp-name-b').textContent = b.city;
    document.getElementById('comp-cond-b').textContent = `${b.temp}°C · ${condB}`;
    document.getElementById('comp-feels-b').textContent = `${b.feels_like}°C`;
    document.getElementById('comp-hum-b').textContent = `${b.humidity}%`;
    document.getElementById('comp-aqi-b').textContent = `${b.aqi || 2} (AQI)`;
    document.getElementById('comp-wind-b').textContent = `${b.wind_speed} km/h`;
    document.getElementById('comp-rain-b').textContent = `${b.rain_prob || 20}%`;
    document.getElementById('comp-uv-b').textContent = `${b.uv_index || 4.5}`;

    const warmerStr = (typeof i18n !== 'undefined') ? i18n.t('comp.warmer_in') : 'warmer in';
    const cleanerStr = (typeof i18n !== 'undefined') ? i18n.t('comp.cleaner_aqi') : 'has cleaner AQI';
    const drierStr = (typeof i18n !== 'undefined') ? i18n.t('comp.drier_today') : 'is drier today';

    const deltaTemp = Math.round((a.temp - b.temp) * 10) / 10;
    document.getElementById('delta-temp').textContent = deltaTemp >= 0
      ? `+${deltaTemp}°C ${warmerStr} ${a.city}`
      : `+${Math.abs(deltaTemp)}°C ${warmerStr} ${b.city}`;

    document.getElementById('delta-aqi').textContent = (a.aqi || 2) <= (b.aqi || 2)
      ? `${a.city} ${cleanerStr}`
      : `${b.city} ${cleanerStr}`;

    document.getElementById('delta-rain').textContent = (a.rain_prob || 20) >= (b.rain_prob || 20)
      ? `${b.city} ${drierStr}`
      : `${a.city} ${drierStr}`;

    document.getElementById('comp-ai-verdict').innerHTML = `
      Station ${a.city} registers at ${a.temp}°C (${a.condition}) versus ${b.city} at ${b.temp}°C (${b.condition}).
      ${deltaTemp >= 0 ? `${a.city} exhibits stronger thermal accumulation` : `${b.city} presents elevated daytime temperatures`}.
      For operational planning, ensure thermal equilibrium protocols and monitor localized UV indices.
    `;
  }

  // ── IMD Extreme Weather Alerts Hub ──────────────────────────────────
  async function loadAlerts(city) {
    const container = document.getElementById('alerts-list');
    const cityTitle = document.getElementById('alerts-city-display');
    if (cityTitle) cityTitle.textContent = city;
    if (!container) return;

    container.innerHTML = '<div style="color:#94a3b8; padding:12px; font-family:var(--font-mono); font-size:0.8rem;">Querying threat monitoring models…</div>';

    const resp = await API.fetchAlerts(city);
    container.innerHTML = '';

    if (!resp.alerts || resp.alerts.length === 0) {
      container.innerHTML = `
        <div class="alert-item-card" style="border-left-color:#10b981; background:rgba(16, 185, 129, 0.06);">
          <div class="item-head" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span class="item-event-name" style="font-weight:700; color:#10b981;">Normal Operational Status — No Hazard Warnings</span>
            <span class="item-severity-badge" style="background:#10b981; color:#fff; font-family:var(--font-mono); font-size:0.65rem; padding:2px 6px; border-radius:4px;">GREEN</span>
          </div>
          <p class="item-desc" style="font-size:0.78rem; color:var(--text-med);">Meteorological conditions in ${city} are within normal seasonal thresholds. No active cyclone, flood, or gale warnings.</p>
          <span class="item-meta" style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-low); margin-top:6px; display:block;">Telemetry Monitoring: Continuous Real-Time Doppler Radar</span>
        </div>
      `;
      return;
    }

    resp.alerts.forEach(al => {
      const sev = (al.severity || 'Moderate').toLowerCase();
      let sevClass = 'severity-yellow';
      let sevBg = '#eab308';

      if (sev.includes('severe') || sev.includes('extreme') || (al.event && al.event.includes('RED'))) {
        sevClass = 'red';
        sevBg = '#ef4444';
      } else if (sev.includes('moderate') || (al.event && al.event.includes('ORANGE'))) {
        sevClass = 'orange';
        sevBg = '#f97316';
      }

      const card = document.createElement('div');
      card.className = `alert-item-card ${sevClass}`;
      card.innerHTML = `
        <div class="item-head" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="item-event-name" style="font-weight:700; color:var(--text-pure);">${al.event || 'Weather Advisory'}</span>
          <span class="item-severity-badge" style="background:${sevBg}; color:#fff; font-family:var(--font-mono); font-size:0.65rem; padding:2px 6px; border-radius:4px;">${(al.severity || 'Active').toUpperCase()}</span>
        </div>
        <p class="item-desc" style="font-size:0.78rem; color:var(--text-med);">${al.description}</p>
        <span class="item-meta" style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-low); margin-top:6px; display:block;">Validity: ${al.start || 'Immediate'} to ${al.end || 'Next 24h'}</span>
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

  let activeRegionFilter = 'all';
  let activeStationSearch = '';

  function sumChars(str) {
    let s = 0;
    for (let i = 0; i < str.length; i++) s += str.charCodeAt(i);
    return s;
  }

  function renderStationHub() {
    const grid = document.getElementById('station-grid');
    if (!grid) return;

    grid.innerHTML = '';
    const filtered = stationHubList.filter(item => {
      const matchRegion = (activeRegionFilter === 'all' || item.region === activeRegionFilter);
      const q = activeStationSearch.toLowerCase().trim();
      const matchText = !q || item.city.toLowerCase().includes(q) || item.state.toLowerCase().includes(q) || item.region.toLowerCase().includes(q);
      return matchRegion && matchText;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `<div class="station-empty-msg">No meteorological stations match "${activeStationSearch}".</div>`;
      return;
    }

    filtered.forEach(item => {
      const card = document.createElement('div');
      const isActive = item.city.toLowerCase() === currentCity.toLowerCase();
      card.className = `station-card ${isActive ? 'active' : ''}`;
      card.dataset.city = item.city;
      
      const seed = sumChars(item.city);
      const estTemp = 20 + (seed % 14);

      card.innerHTML = `
        <div class="station-card-top">
          <span class="station-icon">${item.icon}</span>
          <span class="station-state-badge">${item.state}</span>
        </div>
        <div class="station-card-main">
          <div class="station-name">${item.city}</div>
          <div class="station-region-tag">${item.region}</div>
        </div>
        <div class="station-card-foot">
          <span class="station-temp-est">~${estTemp}°C</span>
          <span class="station-live-dot" title="Station Operational"></span>
        </div>
      `;

      card.addEventListener('click', () => {
        switchCity(item.city);
      });

      grid.appendChild(card);
    });
  }

  // ── Station Switcher & Master Loader ──────────────────────────────────
  async function switchCity(city) {
    if (!city) return;
    currentCity = city;
    showLoader(`Acquiring meteorological telemetry for ${city}…`);

    const chatLoc = document.getElementById('chat-location');
    const compA = document.getElementById('comp-city-1');
    const climCity = document.getElementById('climate-city');
    const radarFocus = document.getElementById('radar-focus-city');
    const stationSel = document.getElementById('station-select');

    if (chatLoc) chatLoc.value = city;
    if (compA) compA.value = city;
    if (climCity) climCity.value = city;
    if (radarFocus) radarFocus.textContent = city;
    if (stationSel) {
      const opts = Array.from(stationSel.options);
      const match = opts.find(o => o.value.toLowerCase() === city.toLowerCase());
      if (match) stationSel.value = match.value;
    }

    document.querySelectorAll('.station-card').forEach(c => {
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
        item.innerHTML = `<span>${city}</span><span style="font-size:0.7rem; color:var(--text-low); font-family:var(--font-mono);">STATION</span>`;
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
        showLoader('Acquiring GPS coordinates…');
        navigator.geolocation.getCurrentPosition(
          async (pos) => {
            switchCity('Mumbai');
          },
          (err) => {
            hideLoader();
            alert('Location access denied. Retaining selected station.');
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

    if (typeof i18n !== 'undefined') {
      i18n.applyTranslations();
      const initialLang = i18n.getLang();
      const headerSel = document.getElementById('header-lang-select');
      const chatSel = document.getElementById('chat-lang');
      if (headerSel) headerSel.value = initialLang;
      if (chatSel) chatSel.value = initialLang;
    }

    window.addEventListener('meteor:langchange', () => {
      if (typeof i18n !== 'undefined') {
        i18n.applyTranslations();
      }
    });

    API.onStatusChange((online) => {
      const dot = document.querySelector('.status-dot');
      const label = document.getElementById('status-label');
      if (dot && label) {
        dot.className = online ? 'status-dot online' : 'status-dot fallback';
        dot.style.background = online ? '#10b981' : '#f59e0b';
        label.textContent = online ? 'ONLINE' : 'OFFLINE';
      }
    });

    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const sec = btn.dataset.section;
        if (sec) navigate(sec);
      });
    });

    document.querySelectorAll('.city-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        switchCity(chip.dataset.city);
      });
    });

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

    document.querySelectorAll('.suggestion-list .suggestion-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const q = btn.dataset.q;
        if (q) {
          navigate('chat');
          setTimeout(() => ChatUI.askQuestion(q), 100);
        }
      });
    });

    document.getElementById('voice-briefing-btn')?.addEventListener('click', () => {
      WeatherUI.playVoiceBriefing();
    });
    document.getElementById('quick-ask-hero-btn')?.addEventListener('click', () => {
      navigate('chat');
    });
    document.getElementById('alert-view-btn')?.addEventListener('click', () => {
      navigate('alerts');
    });

    // Station Select Dropdown in Header
    const stationSel = document.getElementById('station-select');
    if (stationSel) {
      stationSel.addEventListener('change', (e) => {
        switchCity(e.target.value);
      });
    }

    // Station Hub Search & Filter Pills
    const stationFilterInput = document.getElementById('station-hub-filter');
    if (stationFilterInput) {
      stationFilterInput.addEventListener('input', (e) => {
        activeStationSearch = e.target.value;
        renderStationHub();
      });
    }

    const regionPills = document.querySelectorAll('.region-pill');
    regionPills.forEach(pill => {
      pill.addEventListener('click', () => {
        regionPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        activeRegionFilter = pill.dataset.region;
        renderStationHub();
      });
    });

    renderStationHub();

    document.getElementById('comp-run-btn')?.addEventListener('click', runCityComparison);
    document.getElementById('climate-fetch-btn')?.addEventListener('click', loadClimate);

    switchCity('Mumbai');
  }

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
