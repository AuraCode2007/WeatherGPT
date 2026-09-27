/**
 * sandbox.js — WeatherGPT Atmospheric AI Twin & Impact Sandbox Module
 * Manages microclimate scenario simulations, sector risk radar, and WebSocket live telemetry.
 */

const Sandbox = (() => {
  let activePreset = null;
  let wsConnection = null;

  function init() {
    setupEventListeners();
    initWebSocketTelemetry();
  }

  let debounceTimer = null;
  function debouncedTrigger() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      triggerSimulation();
    }, 350);
  }

  function setupEventListeners() {
    const tempSlider = document.getElementById('sandbox-temp-slider');
    const humSlider = document.getElementById('sandbox-hum-slider');
    const rainSlider = document.getElementById('sandbox-rain-slider');
    const windSlider = document.getElementById('sandbox-wind-slider');

    if (tempSlider) {
      tempSlider.addEventListener('input', (e) => {
        document.getElementById('sandbox-temp-val').textContent = (e.target.value > 0 ? '+' : '') + e.target.value + '°C';
        debouncedTrigger();
      });
    }
    if (humSlider) {
      humSlider.addEventListener('input', (e) => {
        document.getElementById('sandbox-hum-val').textContent = (e.target.value > 0 ? '+' : '') + e.target.value + '%';
        debouncedTrigger();
      });
    }
    if (rainSlider) {
      rainSlider.addEventListener('input', (e) => {
        document.getElementById('sandbox-rain-val').textContent = e.target.value + ' mm/h';
        debouncedTrigger();
      });
    }
    if (windSlider) {
      windSlider.addEventListener('input', (e) => {
        document.getElementById('sandbox-wind-val').textContent = e.target.value + ' km/h';
        debouncedTrigger();
      });
    }

    // Preset buttons
    const presetBtns = document.querySelectorAll('.preset-btn');
    presetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const preset = btn.dataset.preset;
        applyPreset(preset);
      });
    });

    // Run simulation button
    const runBtn = document.getElementById('sandbox-run-btn');
    if (runBtn) {
      runBtn.addEventListener('click', () => triggerSimulation());
    }
  }

  function applyPreset(preset) {
    activePreset = preset;
    const tempSlider = document.getElementById('sandbox-temp-slider');
    const humSlider = document.getElementById('sandbox-hum-slider');
    const rainSlider = document.getElementById('sandbox-rain-slider');
    const windSlider = document.getElementById('sandbox-wind-slider');

    if (preset === 'heatwave') {
      if (tempSlider) tempSlider.value = 8;
      if (humSlider) humSlider.value = -20;
      if (rainSlider) rainSlider.value = 0;
      if (windSlider) windSlider.value = 15;
    } else if (preset === 'cloudburst') {
      if (tempSlider) tempSlider.value = -2;
      if (humSlider) humSlider.value = 35;
      if (rainSlider) rainSlider.value = 110;
      if (windSlider) windSlider.value = 45;
    } else if (preset === 'cyclone') {
      if (tempSlider) tempSlider.value = -3;
      if (humSlider) humSlider.value = 40;
      if (rainSlider) rainSlider.value = 75;
      if (windSlider) windSlider.value = 105;
    } else if (preset === 'frost') {
      if (tempSlider) tempSlider.value = -9;
      if (humSlider) humSlider.value = -30;
      if (rainSlider) rainSlider.value = 0;
      if (windSlider) windSlider.value = 25;
    }

    // Dispatch input events to update label text
    [tempSlider, humSlider, rainSlider, windSlider].forEach(s => {
      if (s) s.dispatchEvent(new Event('input'));
    });

    triggerSimulation(preset);
  }

  async function triggerSimulation(presetTitle = null) {
    const location = (typeof App !== 'undefined' && App.getCity) ? App.getCity() : 'Mumbai';
    const domainSelect = document.getElementById('chat-domain-select');
    const domain = domainSelect ? domainSelect.value : 'General';

    const tempDelta = parseFloat(document.getElementById('sandbox-temp-slider')?.value || 0);
    const humDelta = parseFloat(document.getElementById('sandbox-hum-slider')?.value || 0);
    const rainRate = parseFloat(document.getElementById('sandbox-rain-slider')?.value || 0);
    const windGust = parseFloat(document.getElementById('sandbox-wind-slider')?.value || 0);

    const langCode = (typeof i18n !== 'undefined') ? i18n.getLang() : 'en';

    const payload = {
      location,
      temp_delta: tempDelta,
      humidity_delta: humDelta,
      rain_rate_mm_hr: rainRate,
      wind_gust_kmh: windGust,
      domain,
      preset_name: presetTitle || activePreset,
      language_code: langCode
    };

    const playBookContainer = document.getElementById('sandbox-playbook-content');
    if (playBookContainer) {
      playBookContainer.innerHTML = '<div class="sandbox-loading-pulse">⚡ Synthesizing AI Twin Simulation Matrix & Emergency Playbook...</div>';
    }

    try {
      const res = await API.runSimulation(payload);
      renderSimulationResults(res);
    } catch (err) {
      console.error('[Sandbox] Simulation failed:', err);
      if (playBookContainer) {
        playBookContainer.innerHTML = `<div class="sandbox-error">⚠️ Simulation failed: ${err.message}</div>`;
      }
    }
  }

  function renderSimulationResults(data) {
    // 1. Overall Hazard Level Gauge
    const indexValEl = document.getElementById('sandbox-hazard-index');
    const levelValEl = document.getElementById('sandbox-hazard-level');
    const simTempEl = document.getElementById('sandbox-sim-temp');
    const simWindEl = document.getElementById('sandbox-sim-wind');
    const simRainEl = document.getElementById('sandbox-sim-rain');

    if (indexValEl) indexValEl.textContent = data.overall_hazard_index + '/100';
    if (levelValEl) {
      const translatedLevel = (typeof i18n !== 'undefined') ? i18n.t('risk.' + data.hazard_level) : data.hazard_level;
      levelValEl.textContent = translatedLevel || data.hazard_level;
      levelValEl.className = 'hazard-badge ' + (data.overall_hazard_index > 70 ? 'critical' : data.overall_hazard_index > 45 ? 'severe' : 'moderate');
    }
    if (simTempEl) simTempEl.textContent = data.simulated_weather.temp + '°C';
    if (simWindEl) simWindEl.textContent = data.simulated_weather.wind_speed + ' km/h';
    if (simRainEl) simRainEl.textContent = data.simulated_weather.rain_rate + ' mm/h';

    // 2. Render Sector Impact Cards
    const matrixContainer = document.getElementById('sandbox-impact-matrix');
    if (matrixContainer && data.impact_matrix) {
      let html = '';
      const sectorIcons = {
        'Agriculture': '🌾',
        'Aviation': '✈️',
        'Smart City': '🏙️',
        'Energy Grid': '⚡',
        'Public Health': '🏥'
      };

      const primaryDriverStr = (typeof i18n !== 'undefined') ? i18n.t('sandbox.primary_driver') : 'Primary Driver';

      for (const [sector, item] of Object.entries(data.impact_matrix)) {
        const icon = sectorIcons[sector] || '🎯';
        const translatedSector = (typeof i18n !== 'undefined') ? i18n.t('sector.' + sector) : sector;
        const translatedRisk = (typeof i18n !== 'undefined') ? i18n.t('risk.' + item.risk_level) : item.risk_level;
        const barColor = item.score > 75 ? '#ef4444' : item.score > 50 ? '#f97316' : item.score > 25 ? '#eab308' : '#10b981';

        html += `
          <div class="sector-card">
            <div class="sector-card-header">
              <span class="sector-title">${icon} ${translatedSector}</span>
              <span class="sector-score-badge" style="background:${barColor}22; color:${barColor}; border:1px solid ${barColor}55;">
                ${translatedRisk} (${item.score}/100)
              </span>
            </div>
            <div class="sector-bar-wrapper">
              <div class="sector-bar-fill" style="width: ${item.score}%; background: ${barColor};"></div>
            </div>
            <div class="sector-meta">
              <div class="sector-factor"><strong>${primaryDriverStr}:</strong> ${item.key_factor}</div>
              <div class="sector-advisory">${item.advisory}</div>
            </div>
          </div>
        `;
      }
      matrixContainer.innerHTML = html;
    }

    // 3. Render AI Playbook Markdown
    const playBookContainer = document.getElementById('sandbox-playbook-content');
    if (playBookContainer && data.ai_playbook) {
      if (typeof marked !== 'undefined') {
        playBookContainer.innerHTML = marked.parse(data.ai_playbook);
      } else {
        playBookContainer.textContent = data.ai_playbook;
      }
    }
  }

  function initWebSocketTelemetry() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.port === '8000' || window.location.port === '8001' ? window.location.host : 'localhost:8000';
    const wsUrl = `${protocol}//${host}/ws/telemetry`;

    try {
      wsConnection = new WebSocket(wsUrl);
      wsConnection.onopen = () => {
        const pill = document.getElementById('backend-status');
        if (pill) {
          pill.title = 'Live Doppler WebSocket Telemetry Streaming';
          const label = document.getElementById('status-label');
          if (label) label.textContent = 'ONLINE (WS STREAM)';
        }
      };
      wsConnection.onmessage = (event) => {
        try {
          const tick = JSON.parse(event.data);
          updateTelemetryWidget(tick);
        } catch (_) {}
      };
      wsConnection.onerror = () => {};
    } catch (_) {}
  }

  function updateTelemetryWidget(tick) {
    const dopplerSweep = document.getElementById('ws-doppler-sweep');
    const signalDbz = document.getElementById('ws-signal-dbz');
    const pressure = document.getElementById('ws-pressure');

    if (dopplerSweep) dopplerSweep.textContent = tick.doppler_sweep_deg + '°';
    if (signalDbz) signalDbz.textContent = tick.signal_dbz + ' dBZ';
    if (pressure) pressure.textContent = tick.pressure_hpa + ' hPa';
  }

  return {
    init,
    triggerSimulation,
    applyPreset
  };
})();

document.addEventListener('DOMContentLoaded', () => {
  Sandbox.init();
});

window.addEventListener('meteor:langchange', () => {
  if (typeof Sandbox !== 'undefined') {
    Sandbox.triggerSimulation();
  }
});
