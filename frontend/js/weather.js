/**
 * weather.js — Environmental & Meteorological Telemetry Engine
 * Manages operations dashboard data, atmospheric metrics, and forecast timelines.
 */

const WeatherUI = (() => {
  let isFahrenheit = false;
  let currentWeatherData = null;
  let activeHourlyMode = 'temp';

  const aqiLevels = {
    1: { label: 'Good (AQI 25)', cls: '', advice: 'Air quality is pristine. Ideal for all operational activities.' },
    2: { label: 'Fair (AQI 65)', cls: '', advice: 'Air quality is acceptable. Minor particulate density.' },
    3: { label: 'Moderate (AQI 115)', cls: 'mod', advice: 'Elevated particulate concentration. Sensitive groups take precaution.' },
    4: { label: 'Poor (AQI 175)', cls: 'poor', advice: 'High atmospheric pollution. Wear N95 protection outdoors.' },
    5: { label: 'Very Poor (AQI 240)', cls: 'verypoor', advice: 'Hazardous air quality. Restrict outdoor workforce operations.' },
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

  function parseForecastLine(line) {
    const parts = line.split(':');
    const day = parts[0]?.trim() || 'Day';
    const rest = parts.slice(1).join(':').trim();
    const segments = rest.split(',');
    const tempStr = segments[0]?.trim() || '28°C';
    const desc = segments[1]?.trim() || 'Clear Sky';
    const hum = segments[2]?.trim() || 'Humidity 60%';

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
      const langCode = (typeof i18n !== 'undefined') ? i18n.getLang() : 'en';
      const localeMap = { en: 'en-IN', hi: 'hi-IN', es: 'es-ES', fr: 'fr-FR', de: 'de-DE', ja: 'ja-JP', ta: 'ta-IN', mr: 'mr-IN', bn: 'bn-IN' };
      const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' };
      dateEl.textContent = `${now.toLocaleDateString(localeMap[langCode] || 'en-IN', options)}`;
    }

    const condLabel = document.getElementById('condition-label');
    if (condLabel) {
      const rawCond = data.description || data.condition || 'Clear Sky';
      condLabel.textContent = (typeof i18n !== 'undefined') ? i18n.translateCondition(rawCond) : rawCond;
    }

    // 2. Primary Hero Temperature
    const tempMain = document.getElementById('temp-main');
    const tempUnitSign = document.getElementById('temp-unit-sign');
    if (tempMain) tempMain.textContent = formatTemp(data.temp).replace('°', '');
    if (tempUnitSign) tempUnitSign.textContent = isFahrenheit ? 'F' : 'C';

    const tempFeels = document.getElementById('temp-feels');
    if (tempFeels) {
      const feelsLabel = (typeof i18n !== 'undefined') ? i18n.t('hero.feels_like') : 'Feels like';
      tempFeels.innerHTML = `${feelsLabel} <strong>${formatTemp(data.feels_like)}${isFahrenheit ? 'F' : 'C'}</strong>`;
    }

    const tempMinEl = document.getElementById('temp-min');
    const tempMaxEl = document.getElementById('temp-max');
    if (tempMinEl) tempMinEl.textContent = formatTemp(data.temp_min);
    if (tempMaxEl) tempMaxEl.textContent = formatTemp(data.temp_max);

    const descEl = document.getElementById('weather-desc');
    if (descEl) {
      const translatedCond = (typeof i18n !== 'undefined') ? i18n.translateCondition(data.description || data.condition) : (data.description || data.condition);
      const summaryTail = (typeof i18n !== 'undefined') ? i18n.t('hero.summary_default') : 'Atmospheric profile within target baseline parameters.';
      descEl.textContent = `${translatedCond}. ${summaryTail}`;
    }

    // 3. Environmental Metric 1: AQI & Pollutants
    const aqiVal = data.aqi || 2;
    const aqiKeys = { 1: 'good', 2: 'fair', 3: 'moderate', 4: 'poor', 5: 'very_poor' };
    const aqiKey = aqiKeys[aqiVal] || 'fair';

    const aqiBadge = document.getElementById('aqi-badge');
    const aqiFill = document.getElementById('aqi-gauge-fill');
    const aqiAdvice = document.getElementById('aqi-advice');

    if (aqiBadge) {
      aqiBadge.textContent = (typeof i18n !== 'undefined') ? i18n.t(`aqi.${aqiKey}`) : aqiLevels[aqiVal]?.label;
      if (aqiVal >= 4) aqiBadge.classList.add('poor');
      else aqiBadge.classList.remove('poor');
    }
    if (aqiFill) aqiFill.style.width = `${Math.min(100, (aqiVal / 5) * 100)}%`;
    if (aqiAdvice) {
      aqiAdvice.textContent = (typeof i18n !== 'undefined') ? i18n.t(`aqi.advice_${aqiKey}`) : aqiLevels[aqiVal]?.advice;
    }

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
    const uvAdvice = document.getElementById('uv-advice');
    if (uvBadge) {
      let uvKey = 'moderate';
      if (uv < 3) uvKey = 'low';
      else if (uv < 6) uvKey = 'moderate';
      else if (uv < 8) uvKey = 'high';
      else if (uv < 11) uvKey = 'very_high';
      else uvKey = 'extreme';

      uvBadge.textContent = (typeof i18n !== 'undefined') ? i18n.t(`uv.${uvKey}`) : 'Moderate (3-5)';
      if (uvAdvice) {
        uvAdvice.textContent = (typeof i18n !== 'undefined') ? i18n.t(`uv.advice_${uvKey}`) : 'Standard solar protection recommended.';
      }
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

    const visDescEl = document.getElementById('val-vis-desc');
    if (visDescEl) {
      const visKey = data.visibility > 8 ? 'vis.clear' : (data.visibility > 4 ? 'vis.hazy' : 'vis.poor');
      visDescEl.textContent = (typeof i18n !== 'undefined') ? i18n.t(visKey) : 'Clear View';
    }

    // 9. Alert Banner
    const alertBanner = document.getElementById('alert-banner');
    const alertText = document.getElementById('alert-text');
    if (data.alert) {
      if (alertBanner) alertBanner.style.display = 'flex';
      if (alertText) alertText.textContent = data.alert;
    } else {
      if (alertBanner) alertBanner.style.display = 'none';
    }

    // 10. Hourly Forecast Timeline & Chart
    renderHourlyTimeline(data);
    WeatherCharts.renderHourly(data, activeHourlyMode, isFahrenheit);

    // 11. 7-Day Extended Forecast Deck
    renderExtendedForecast(data);
  }

  function renderHourlyTimeline(data) {
    const scroller = document.getElementById('hourly-timeline');
    if (!scroller) return;
    scroller.innerHTML = '';

    const nowStr = (typeof i18n !== 'undefined') ? i18n.t('radar.now') : 'Now';
    const rainStr = (typeof i18n !== 'undefined') ? i18n.t('forecast.rain_label') : 'Rain';
    const hours = [nowStr, '+3h', '+6h', '+9h', '+12h', '+15h', '+18h', '+21h'];
    const baseTemp = data.temp || 28;
    const tempOffsets = [0, 1.2, 2.4, 0.8, -1.5, -3.0, -2.8, -1.0];
    const rainProbs = [data.rain_prob || 20, 35, 50, 20, 10, 5, 15, 20];

    hours.forEach((h, idx) => {
      const t = baseTemp + tempOffsets[idx];
      const chip = document.createElement('div');
      chip.className = `hourly-item ${idx === 0 ? 'now' : ''}`;
      chip.innerHTML = `
        <span class="h-time">${h}</span>
        <span class="h-temp">${formatTemp(t)}</span>
        <span class="h-rain">${rainStr} ${rainProbs[idx]}%</span>
      `;
      scroller.appendChild(chip);
    });
  }

  function renderExtendedForecast(data) {
    const grid = document.getElementById('forecast-cards');
    if (!grid) return;
    grid.innerHTML = '';

    const rawList = data.forecast || [];
    rawList.forEach((line) => {
      const { day, numTemp, desc, hum } = parseForecastLine(line);
      const minT = numTemp - 3;
      const maxT = numTemp + 4;
      const translatedDesc = (typeof i18n !== 'undefined') ? i18n.translateCondition(desc) : desc;

      const card = document.createElement('div');
      card.className = 'forecast-day-card glass-card';
      card.innerHTML = `
        <div class="f-day-name">${day}</div>
        <span class="f-date-str">${translatedDesc}</span>
        <div class="f-temps">
          <span class="f-high">${formatTemp(maxT)}</span>
          <span class="f-low">${formatTemp(minT)}</span>
        </div>
        <div style="font-size:0.68rem;color:var(--text-low);margin-top:6px;">${hum}</div>
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
      alert('Audio synthesis is not supported on this device.');
      return;
    }
    const d = currentWeatherData;
    const langCode = (typeof i18n !== 'undefined') ? i18n.getLang() : 'en';
    const text = `Meteorological briefing for ${d.city}. Current temperature is ${d.temp} degrees Celsius with ${d.description}. Relative humidity is at ${d.humidity} percent.`;
    const utterance = new SpeechSynthesisUtterance(text);
    const langMap = { en: 'en-IN', hi: 'hi-IN', es: 'es-ES', fr: 'fr-FR', de: 'de-DE', ja: 'ja-JP', ta: 'ta-IN', mr: 'mr-IN' };
    utterance.lang = langMap[langCode] || 'en-IN';
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  // Listen for language change events
  window.addEventListener('meteor:langchange', () => {
    if (currentWeatherData) {
      render(currentWeatherData);
    }
  });

  return {
    render,
    setUnit,
    setHourlyMode,
    playVoiceBriefing,
    getCurrentData: () => currentWeatherData
  };
})();
