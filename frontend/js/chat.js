/**
 * chat.js — WeatherGPT AI Conversational Advisor Hub
 * Multilingual, domain-aware advisory engine with Speech Recognition & Synthesis.
 */

const ChatUI = (() => {
  let isListening = false;
  let speechRecognition = null;
  let autoTTS = true;

  const domainPrompts = {
    'General': [
      'What is the current atmospheric summary and 24h outlook?',
      'Should I carry an umbrella or rain gear today?',
      'What are the best hours for outdoor exercise today?',
      'Are there any health advisories for today\'s air quality?'
    ],
    'Agriculture / Farming': [
      'What is the optimal pesticide spraying window this week?',
      'How much irrigation is recommended given soil moisture?',
      'Are there frost or excessive rainfall risks for standing crops?',
      'When is the safest window for wheat/rice harvest operations?'
    ],
    'Aviation': [
      'Provide METAR / TAF ceiling, visibility, and wind shear briefing.',
      'Are there convective thunderstorm cells along flight corridors?',
      'What is the icing risk altitude profile for regional departures?',
      'Check SIGMET advisories for the departure airport.'
    ],
    'Flood & Cyclone Warning': [
      'Are there any flash flood warnings or cloudburst indicators?',
      'What is the estimated storm surge and coastal inundation risk?',
      'What are the mandatory evacuation protocols for low-lying zones?',
      'Summarize current IMD color-coded warnings and river gauge levels.'
    ],
    'Smart City / Urban': [
      'Assess urban heat island intensity and peak thermal hours.',
      'Which major traffic underpasses have high waterlogging susceptibility?',
      'What are the public health recommendations for sensitive AQI levels?',
      'Provide municipal drainage pumping priority recommendations.'
    ],
    'Marine & Fisheries': [
      'What is the significant wave height and sea surface roughness?',
      'Are squally gale winds expected beyond 10 nautical miles offshore?',
      'Is it safe for artisanal fishing boats to venture into deep sea?',
      'What are the tidal timings and high tide peak hours?'
    ],
    'Climate Research': [
      'How does today\'s temperature compare to the 1980–2020 normal?',
      'What is the current ENSO (El Niño/La Niña) influence on this region?',
      'Summarize long-term decadal precipitation trends for this station.',
      'Analyze statistical significance of recent precipitation anomalies.'
    ]
  };

  function init() {
    setupVoiceRecognition();
    setupEventListeners();
    updateDomainPrompts('General');
  }

  function setupVoiceRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
      speechRecognition = new SpeechRec();
      speechRecognition.continuous = false;
      speechRecognition.interimResults = false;

      speechRecognition.onstart = () => {
        isListening = true;
        const micBtn = document.getElementById('chat-mic-btn');
        if (micBtn) micBtn.classList.add('listening');
      };

      speechRecognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        const input = document.getElementById('chat-input');
        if (input) {
          input.value = transcript;
          sendMessage();
        }
      };

      speechRecognition.onend = () => {
        isListening = false;
        const micBtn = document.getElementById('chat-mic-btn');
        if (micBtn) micBtn.classList.remove('listening');
      };

      speechRecognition.onerror = () => {
        isListening = false;
        const micBtn = document.getElementById('chat-mic-btn');
        if (micBtn) micBtn.classList.remove('listening');
      };
    }
  }

  function toggleVoiceInput() {
    if (!speechRecognition) {
      alert('Speech recognition is not supported in this browser. Please use Google Chrome or Edge.');
      return;
    }
    if (isListening) {
      speechRecognition.stop();
    } else {
      const langCode = document.getElementById('chat-lang')?.value || 'en';
      const langMap = { en: 'en-IN', hi: 'hi-IN', ta: 'ta-IN', te: 'te-IN', bn: 'bn-IN', mr: 'mr-IN' };
      speechRecognition.lang = langMap[langCode] || 'en-IN';
      speechRecognition.start();
    }
  }

  function setupEventListeners() {
    const sendBtn = document.getElementById('chat-send-btn');
    const input = document.getElementById('chat-input');
    const micBtn = document.getElementById('chat-mic-btn');
    const clearBtn = document.getElementById('clear-chat-btn');
    const domainSelect = document.getElementById('chat-domain');
    const langSelect = document.getElementById('chat-lang');
    const ttsToggle = document.getElementById('tts-toggle-btn');

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
    }
    if (micBtn) micBtn.addEventListener('click', toggleVoiceInput);
    if (clearBtn) clearBtn.addEventListener('click', clearMessages);

    if (domainSelect) {
      domainSelect.addEventListener('change', (e) => {
        updateDomainPrompts(e.target.value);
        const activeDom = document.getElementById('chat-active-domain');
        if (activeDom) activeDom.textContent = `Domain: ${e.target.value.split('/')[0].trim()}`;
      });
    }

    if (langSelect) {
      langSelect.addEventListener('change', (e) => {
        const text = e.target.options[e.target.selectedIndex].text;
        const activeLang = document.getElementById('chat-active-lang');
        if (activeLang) activeLang.textContent = `Language: ${text.split(' ')[1] || text}`;
      });
    }

    if (ttsToggle) {
      ttsToggle.addEventListener('click', () => {
        autoTTS = !autoTTS;
        ttsToggle.textContent = `🔊 Voice: ${autoTTS ? 'On' : 'Off'}`;
        ttsToggle.style.color = autoTTS ? '#38bdf8' : '#94a3b8';
      });
    }
  }

  function updateDomainPrompts(domain) {
    const list = document.getElementById('suggestion-list');
    if (!list) return;
    list.innerHTML = '';
    const prompts = domainPrompts[domain] || domainPrompts['General'];
    prompts.forEach(p => {
      const btn = document.createElement('button');
      btn.className = 'suggestion-btn';
      btn.textContent = p;
      btn.addEventListener('click', () => {
        const input = document.getElementById('chat-input');
        if (input) {
          input.value = p;
          sendMessage();
        }
      });
      list.appendChild(btn);
    });
  }

  function appendUserMessage(text) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msg = document.createElement('div');
    msg.className = 'chat-msg user-msg';
    msg.innerHTML = `
      <div class="msg-avatar">👤</div>
      <div class="msg-bubble">
        <p>${escapeHtml(text)}</p>
        <div class="msg-time">${timeStr}</div>
      </div>
    `;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
  }

  function appendAIMessage(initialText = '') {
    const container = document.getElementById('chat-messages');
    if (!container) return null;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const msg = document.createElement('div');
    msg.className = 'chat-msg ai-msg';
    msg.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble">
        <div class="msg-header-tag">WeatherGPT AI Intel</div>
        <div class="msg-content">${renderMarkdown(initialText)}</div>
        <div class="chat-msg-actions">
          <span class="msg-action-chip copy-chip">📋 Copy</span>
          <span class="msg-action-chip speak-chip">🔊 Read Aloud</span>
        </div>
        <div class="msg-time">WeatherGPT · ${timeStr}</div>
      </div>
    `;

    const copyBtn = msg.querySelector('.copy-chip');
    const speakBtn = msg.querySelector('.speak-chip');
    const contentEl = msg.querySelector('.msg-content');

    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(contentEl.innerText);
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => copyBtn.textContent = '📋 Copy', 2000);
      });
    }

    if (speakBtn) {
      speakBtn.addEventListener('click', () => {
        speakText(contentEl.innerText);
      });
    }

    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
    return contentEl;
  }

  function speakText(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#_`]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  async function sendMessage(overrideText = null) {
    const input = document.getElementById('chat-input');
    const text = overrideText || input?.value.trim();
    if (!text) return;

    if (input && !overrideText) input.value = '';

    appendUserMessage(text);

    const typing = document.getElementById('typing-indicator');
    if (typing) typing.style.display = 'flex';

    const location = document.getElementById('chat-location')?.value.trim() || 'Mumbai';
    const domain = document.getElementById('chat-domain')?.value || 'General';
    const langCode = document.getElementById('chat-lang')?.value || 'en';

    const payload = {
      user_question: text,
      location: location,
      language_code: langCode,
      domain: domain
    };

    const aiContentEl = appendAIMessage('');
    let accumulatedText = '';

    try {
      await API.streamChat(
        payload,
        (chunk) => {
          accumulatedText += chunk;
          if (aiContentEl) aiContentEl.innerHTML = renderMarkdown(accumulatedText);
          const container = document.getElementById('chat-messages');
          if (container) container.scrollTop = container.scrollHeight;
        },
        (err) => {
          if (aiContentEl) aiContentEl.innerHTML = `<span style="color:#ef4444;">Advisory notice: ${escapeHtml(err)}</span>`;
        },
        (loc) => {
          if (typing) typing.style.display = 'none';
          if (autoTTS && accumulatedText) {
            speakText(accumulatedText);
          }
        }
      );
    } catch (_) {
      if (typing) typing.style.display = 'none';
    }
  }

  function clearMessages() {
    const container = document.getElementById('chat-messages');
    if (!container) return;
    container.innerHTML = `
      <div class="chat-msg ai-msg" id="welcome-msg">
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble">
          <div class="msg-header-tag">WeatherGPT Assistant</div>
          <p>Chat history cleared. What weather question can I solve for you today? 🌤️</p>
          <div class="msg-time">Just now</div>
        </div>
      </div>
    `;
  }

  function renderMarkdown(md) {
    if (typeof marked !== 'undefined' && marked.parse) {
      return marked.parse(md);
    }
    return escapeHtml(md).replace(/\n/g, '<br/>');
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  return {
    init,
    sendMessage,
    askQuestion: (q) => sendMessage(q)
  };
})();
