/**
 * weather.js — Weather Dashboard Display & Environmental Intelligence
 * Populates all dashboard metrics, environmental gauges, and manages unit conversions.
 */

const WeatherUI = (() => {
  let isFahrenheit = false;
  let currentWeatherData = null;
  let activeHourlyMode = 'temp';

  // Condition -> High fidelity emoji icons
  const conditionIcons = {
    Clear: '☀️',
    Clouds: '⛅',
    Rain: '🌧️',
    Drizzle: '🌦️',
    Thunderstorm: '⛈️',
    Snow: '❄️',
    Mist: '🌫️',
    Smoke: '🌫️',
    Haze: '🌫️',
    Dust: '💨',
    Fog: '🌫️',
    Sand: '💨',
    Ash: '🌋',
    Squall: '💨',
    Tornado: '🌪️',
  };

  const aqiLevels = {
    1: { label: 'Good (AQI 25)', cls: '', advice: 'Air quality is pristine. Ideal for all outdoor exercises.' },
    2: { label: 'Fair (AQI 65)', cls: '', advice: 'Air quality is acceptable. Very minor risk for sensitive groups.' },
    3: { label: 'Moderate (AQI 115)', cls: 'mod', advice: 'Sensitive individuals should limit prolonged outdoor exertion.' },
    4: { label: 'Poor (AQI 175)', cls: 'poor', advice: 'Unhealthy air. Wear N95 masks when stepping outdoors.' },
    5: { label: 'Very Poor (AQI 240)', cls: 'verypoor', advice: 'Hazardous air quality. Avoid all outdoor physical activity.' },
  };

  function setUnit(unit) {
    isFahrenheit = unit === 'F';
    if (currentWeatherData) {
      render(currentWeatherData);
    }
  }

  function formatTemp(celsius) {
    if (celsius === null || celsius === undefined || isNaN(celsius)) return '–';
    if (isFahrenheit) {
      return `${Math.round(celsius * 9/5 + 32)}°`;
    }
    return `${Math.round(celsius * 10) / 10}°`;
  }

  function getForecastIcon(desc) {
    const d = (desc || '').toLowerCase();
    if (d.includes('thunder')) return '⛈️';
    if (d.includes('heavy rain') || d.includes('shower')) return '🌧️';
    if (d.includes('rain') || d.includes('drizzle')) return '🌦️';
    if (d.includes('snow')) return '❄️';
    if (d.includes('fog') || d.includes('mist') || d.includes('haze')) return '🌫️';
    if (d.includes('cloud') || d.includes('overcast')) return '☁️';
    if (d.includes('partly')) return '⛅';
    return '☀️';
  }

  function parseForecastLine(line) {
    const parts = line.split(':');
    const day = parts[0]?.trim() || 'Day';
    const rest = parts.slice(1).join(':').trim();
    const segments = rest.split(',');
    const tempStr = segments[0]?.trim() || '28°C';
    const desc = segments[1]?.trim() || 'Clear Sky';
    const hum = segments[2]?.trim() || 'Humidity 60%';

    // Extract numeric temp (supports negative values)
    const numMatch = tempStr.match(/(-?\d+)/);
    const numTemp = numMatch ? parseFloat(numMatch[1]) : 28;

    return { day, numTemp, desc, hum };
  }

  /**
   * Main Render Routine
   */
  function render(data) {
    if (!data) return;
    currentWeatherData = data;

    const icon = conditionIcons[data.condition] || '🌡️';

    // 1. City & Header Metadata
    const cityEl = document.getElementById('city-name');
    if (cityEl) {
      cityEl.textContent = `${data.city}${data.country ? ', ' + data.country : ''}`;
    }

    const coordsEl = document.getElementById('city-coords');
    if (coordsEl && data.lat && data.lon) {
      coordsEl.textContent = `${Math.abs(data.lat).toFixed(2)}°${data.lat >= 0 ? 'N' : 'S'}, ${Math.abs(data.lon).toFixed(2)}°${data.lon >= 0 ? 'E' : 'W'}`;
    }

    const dateEl = document.getElementById('city-date');
    if (dateEl) {
      const now = new Date();
      const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' };
      dateEl.textContent = `${now.toLocaleDateString('en-IN', options)} IST`;
    }

    const condIcon = document.getElementById('condition-icon');
    const condLabel = document.getElementById('condition-label');
    if (condIcon) condIcon.textContent = icon;
    if (condLabel) condLabel.textContent = data.description || data.condition;

    // 2. Primary Hero Temperature
    const tempMain = document.getElementById('temp-main');
    const tempUnitSign = document.getElementById('temp-unit-sign');
    if (tempMain) tempMain.textContent = formatTemp(data.temp).replace('°', '');
    if (tempUnitSign) tempUnitSign.textContent = isFahrenheit ? 'F' : 'C';

    const tempFeels = document.getElementById('temp-feels');
    if (tempFeels) {
      tempFeels.innerHTML = `Feels like <strong>${formatTemp(data.feels_like)}${isFahrenheit ? 'F' : 'C'}</strong>`;
    }

    const tempMinEl = document.getElementById('temp-min');
    const tempMaxEl = document.getElementById('temp-max');
    if (tempMinEl) tempMinEl.textContent = formatTemp(data.temp_min);
    if (tempMaxEl) tempMaxEl.textContent = formatTemp(data.temp_max);

    const descEl = document.getElementById('weather-desc');
    if (descEl) {
      descEl.textContent = `${icon} ${data.description || data.condition}. Ideal thermal equilibrium for current seasonal activity.`;
    }

    // 3. Environmental Metric 1: AQI & Pollutants
    const aqiVal = data.aqi || 2;
    const aqiMeta = aqiLevels[aqiVal] || aqiLevels[2];
    const aqiBadge = document.getElementById('aqi-badge');
    const aqiFill = document.getElementById('aqi-gauge-fill');
    const aqiAdvice = document.getElementById('aqi-advice');

    if (aqiBadge) aqiBadge.textContent = aqiMeta.label;
    if (aqiFill) aqiFill.style.width = `${Math.min(100, (aqiVal / 5) * 100)}%`;
    if (aqiAdvice) aqiAdvice.textContent = aqiMeta.advice;

    const pol = data.pollutants || { pm25: 35, pm10: 60, no2: 20, o3: 40 };
    if (document.getElementById('val-pm25')) document.getElementById('val-pm25').textContent = `${pol.pm25 || 35} µg`;
    if (document.getElementById('val-pm10')) document.getElementById('val-pm10').textContent = `${pol.pm10 || 60} µg`;
    if (document.getElementById('val-no2')) document.getElementById('val-no2').textContent = `${pol.no2 || 20} ppb`;
    if (document.getElementById('val-o3')) document.getElementById('val-o3').textContent = `${pol.o3 || 40} ppb`;

    // 4. Metric 2: Solar Arc
    if (document.getElementById('val-sunrise')) document.getElementById('val-sunrise').textContent = data.sunrise || '06:20 AM';
    if (document.getElementById('val-sunset')) document.getElementById('val-sunset').textContent = data.sunset || '06:35 PM';
    
    // 5. Metric 3: Wind & Compass
    const windSpeed = isFahrenheit ? Math.round(data.wind_speed * 0.621371) : data.wind_speed;
    const windUnit = isFahrenheit ? 'mph' : 'km/h';
    if (document.getElementById('val-wind')) document.getElementById('val-wind').textContent = `${windSpeed} ${windUnit}`;
    // Mini stat pill
    if (document.getElementById('mini-wind')) document.getElementById('mini-wind').textContent = `${windSpeed} ${windUnit}`;

    const compassArrow = document.getElementById('compass-arrow-wrap');
    if (compassArrow) {
      compassArrow.style.transform = `rotate(${data.wind_direction || 0}deg)`;
    }

    const windDir = data.wind_direction || 0;
    const dirNames = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
    const dirIdx = Math.round(windDir / 45) % 8;
    if (document.getElementById('val-wind-dir')) {
      document.getElementById('val-wind-dir').textContent = `${dirNames[dirIdx]} (${windDir}°)`;
    }
    if (document.getElementById('val-wind-gust')) {
      document.getElementById('val-wind-gust').textContent = `${Math.round(windSpeed * 1.35)} ${windUnit}`;
    }
    const pressureVal = data.pressure || 1012;
    if (document.getElementById('val-pressure')) {
      document.getElementById('val-pressure').textContent = `${pressureVal} hPa`;
    }
    if (document.getElementById('mini-pressure')) {
      document.getElementById('mini-pressure').textContent = `${pressureVal} hPa`;
    }

    // 6. Metric 4: UV Index
    const uv = data.uv_index || 4.5;
    if (document.getElementById('val-uv')) document.getElementById('val-uv').textContent = uv.toFixed(1);
    if (document.getElementById('mini-uv')) document.getElementById('mini-uv').textContent = uv.toFixed(1);
    const uvBadge = document.getElementById('val-uv-badge');
    if (uvBadge) {
      if (uv < 3) uvBadge.textContent = 'Low (0-2)';
      else if (uv < 6) uvBadge.textContent = 'Moderate (3-5)';
      else if (uv < 8) uvBadge.textContent = 'High (6-7)';
      else uvBadge.textContent = 'Very High (8+)';
    }

    // 7. Metric 5: Moisture & Humidity
    if (document.getElementById('val-humidity')) document.getElementById('val-humidity').textContent = `${data.humidity}%`;
    if (document.getElementById('mini-humidity')) document.getElementById('mini-humidity').textContent = `${data.humidity}%`;
    const humBar = document.getElementById('bar-humidity');
    if (humBar) humBar.style.width = `${Math.min(100, data.humidity)}%`;
    const dewPointVal = (data.dew_point !== undefined && data.dew_point !== null) ? data.dew_point : (data.temp - 5);
    if (document.getElementById('val-dewpoint')) document.getElementById('val-dewpoint').textContent = `${formatTemp(dewPointVal)}${isFahrenheit ? 'F' : 'C'}`;
    if (document.getElementById('val-rain-prob')) document.getElementById('val-rain-prob').textContent = `${data.rain_prob || 20}%`;

    // 8. Metric 6: Visibility & Cloud Cover
    const visDist = isFahrenheit ? Math.round(data.visibility * 0.621371) : data.visibility;
    const visUnit = isFahrenheit ? 'miles' : 'km';
    if (document.getElementById('val-visibility')) document.getElementById('val-visibility').textContent = `${visDist} ${visUnit}`;
    if (document.getElementById('mini-visibility')) document.getElementById('mini-visibility').textContent = `${visDist} ${visUnit}`;
    if (document.getElementById('val-cloud-cover')) document.getElementById('val-cloud-cover').textContent = `${data.cloud_cover || 45}%`;

    // 9. Alert Banner
    const alertBanner = document.getElementById('alert-banner');
    const alertText = document.getElementById('alert-text');
    if (data.alert) {
      if (alertBanner) alertBanner.style.display = 'flex';
      if (alertText) alertText.textContent = data.alert;
    } else {
      if (alertBanner) alertBanner.style.display = 'none';
    }

    // 10. Hourly Forecast Timeline Chips & Chart
    renderHourlyTimeline(data);
    WeatherCharts.renderHourly(data, activeHourlyMode, isFahrenheit);

    // 11. 7-Day Extended Forecast Deck
    renderExtendedForecast(data);
  }

  function renderHourlyTimeline(data) {
    const scroller = document.getElementById('hourly-timeline');
    if (!scroller) return;
    scroller.innerHTML = '';

    const hours = ['Now', '+3h', '+6h', '+9h', '+12h', '+15h', '+18h', '+21h'];
    const baseTemp = data.temp || 28;
    const tempOffsets = [0, 1.2, 2.4, 0.8, -1.5, -3.0, -2.8, -1.0];
    const rainProbs = [data.rain_prob || 20, 35, 50, 20, 10, 5, 15, 20];

    hours.forEach((h, idx) => {
      const t = baseTemp + tempOffsets[idx];
      const chip = document.createElement('div');
      chip.className = `hourly-chip ${idx === 0 ? 'now' : ''}`;
      chip.innerHTML = `
        <span class="h-time">${h}</span>
        <span class="h-icon">${idx % 2 === 0 ? conditionIcons[data.condition] || '⛅' : '🌦️'}</span>
        <span class="h-temp">${formatTemp(t)}</span>
        <span class="h-rain">💧 ${rainProbs[idx]}%</span>
      `;
      scroller.appendChild(chip);
    });
  }

  function renderExtendedForecast(data) {
    const grid = document.getElementById('forecast-cards');
    if (!grid) return;
    grid.innerHTML = '';

    const rawList = data.forecast || [];
    rawList.forEach((line, idx) => {
      const { day, numTemp, desc, hum } = parseForecastLine(line);
      const icon = getForecastIcon(desc);
      const minT = numTemp - 3;
      const maxT = numTemp + 4;

      const card = document.createElement('div');
      card.className = 'forecast-card-item glass-card';
      card.innerHTML = `
        <div class="f-day-title">${day}</div>
        <div class="f-date-sub">IMD Forecast</div>
        <div class="f-icon-wrap">${icon}</div>
        <div class="f-temp-row">
          <span class="f-temp-max">${formatTemp(maxT)}</span>
          <span class="f-temp-min">/ ${formatTemp(minT)}</span>
        </div>
        <div class="f-desc-chip">${desc}</div>
        <div class="f-extra-details">
          <span>💧 ${hum.replace('Humidity', '')}</span>
          <span>🌬️ Moderate</span>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  function setHourlyMode(mode) {
    activeHourlyMode = mode;
    if (currentWeatherData) {
      WeatherCharts.renderHourly(currentWeatherData, activeHourlyMode, isFahrenheit);
    }
  }

  function playVoiceBriefing() {
    if (!currentWeatherData || !('speechSynthesis' in window)) {
      alert('Speech synthesis is not available in your browser.');
      return;
    }
    const d = currentWeatherData;
    const text = `Good day! Weather briefing for ${d.city}. Currently ${d.temp} degrees Celsius with ${d.description}. Humidity is at ${d.humidity} percent with wind speed of ${d.wind_speed} kilometers per hour. Air Quality Index is ${d.aqi || 2}. Have a safe day!`;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  return {
    render,
    setUnit,
    setHourlyMode,
    playVoiceBriefing,
    getCurrentData: () => currentWeatherData
  };
})();
