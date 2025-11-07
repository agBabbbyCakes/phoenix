// Expert UI Dashboard Enhancements
// Live state transitions, filters, alerts, command palette, and more
(function() {
  'use strict';
  
  let userSettings = {
    timeRange: '60s',
    selectedBots: [],
    favoriteBots: [],
    alertRules: [],
    theme: 'dark',
    ...loadSettings()
  };
  
  let botStatusSummary = { ok: 0, slow: 0, error: 0 };
  let commandPaletteOpen = false;
  let incidentTimeline = [];
  
  // Bot icons/avatars mapping
  const BOT_ICONS = {
    'arb-scout': '🎯',
    'mev-watch': '👁️',
    'tx-relay': '⚡',
    'sandwich-guard': '🛡️',
    'arbit-bot': '🤖',
    'eth-sniper': '🎯',
    'price-bot': '💰',
    'rsi-bot': '📊',
    'trading-bot': '📈',
    'strategy-bot': '🧠',
    'default': '🤖'
  };
  
  // Bot color mapping (consistent across UI)
  const BOT_COLORS = {
    'arb-scout': '#00bfff',
    'mev-watch': '#9b59b6',
    'tx-relay': '#00ff88',
    'sandwich-guard': '#ffa500',
    'arbit-bot': '#4a90e2',
    'eth-sniper': '#e74c3c',
    'price-bot': '#00ff88',
    'rsi-bot': '#00bfff',
    'trading-bot': '#9b59b6',
    'strategy-bot': '#4a90e2',
    'default': '#888'
  };
  
  // Load settings from localStorage
  function loadSettings() {
    try {
      const saved = localStorage.getItem('phoenix:dashboard-settings');
      return saved ? JSON.parse(saved) : {};
    } catch (e) {
      return {};
    }
  }
  
  // Save settings to localStorage
  function saveSettings() {
    try {
      localStorage.setItem('phoenix:dashboard-settings', JSON.stringify(userSettings));
    } catch (e) {
      console.warn('Failed to save settings', e);
    }
  }
  
  // Initialize dashboard UI
  function initDashboardUI() {
    createHealthSummaryChips();
    createBotFilterBar();
    createTimeRangeControl();
    createAlertBuilder();
    createCommandPalette();
    createIncidentTimeline();
    setupCommandPaletteShortcut();
    setupThemeToggle();
    updateBotAvatars();
    
    // Auto-update health summary every 5s
    setInterval(updateHealthSummary, 5000);
    setInterval(updateBotAvatars, 5000);
  }
  
  // Create health summary chips (🟢 4 OK 🟡 1 Slow 🔴 2 Errors)
  function createHealthSummaryChips() {
    const container = document.getElementById('metrics-panel');
    if (!container) return;
    
    let summaryEl = document.getElementById('health-summary-chips');
    if (!summaryEl) {
      summaryEl = document.createElement('div');
      summaryEl.id = 'health-summary-chips';
      summaryEl.className = 'health-summary-chips';
      summaryEl.style.cssText = `
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        flex-wrap: wrap;
        align-items: center;
      `;
      
      const kpiCards = container.querySelector('.grid.grid-cols-1');
      if (kpiCards) {
        kpiCards.parentNode.insertBefore(summaryEl, kpiCards);
      }
    }
    
    updateHealthSummary();
  }
  
  // Update health summary from bot data
  async function updateHealthSummary() {
    const summaryEl = document.getElementById('health-summary-chips');
    if (!summaryEl) return;
    
    try {
      const response = await fetch('/api/bots/status');
      const data = await response.json();
      const bots = data.bots || [];
      
      botStatusSummary = { ok: 0, slow: 0, error: 0 };
      
      bots.forEach(bot => {
        const latency = bot.latency_ms || bot.latency || 0;
        const successRatio = bot.success_ratio || 100;
        const status = bot.status || 'ok';
        
        if (status === 'error' || status === 'critical' || (bot.failure_count || 0) > 10) {
          botStatusSummary.error++;
        } else if (latency > 200 || successRatio < 80 || status === 'warning') {
          botStatusSummary.slow++;
        } else {
          botStatusSummary.ok++;
        }
      });
      
      // Animate changes
      summaryEl.innerHTML = `
        <div class="health-chip health-chip-ok" data-count="${botStatusSummary.ok}">
          <span class="health-icon">🟢</span>
          <span class="health-count">${botStatusSummary.ok}</span>
          <span class="health-label">OK</span>
        </div>
        <div class="health-chip health-chip-slow" data-count="${botStatusSummary.slow}">
          <span class="health-icon">🟡</span>
          <span class="health-count">${botStatusSummary.slow}</span>
          <span class="health-label">Slow</span>
        </div>
        <div class="health-chip health-chip-error" data-count="${botStatusSummary.error}">
          <span class="health-icon">🔴</span>
          <span class="health-count">${botStatusSummary.error}</span>
          <span class="health-label">Errors</span>
        </div>
      `;
      
      // Add pulse animation on change
      summaryEl.querySelectorAll('.health-chip').forEach(chip => {
        chip.classList.add('pulse-on-update');
        setTimeout(() => chip.classList.remove('pulse-on-update'), 600);
      });
    } catch (e) {
      console.error('Failed to update health summary', e);
    }
  }
  
  // Create bot filter bar
  function createBotFilterBar() {
    const container = document.getElementById('metrics-panel');
    if (!container) return;
    
    let filterBar = document.getElementById('bot-filter-bar');
    if (!filterBar) {
      filterBar = document.createElement('div');
      filterBar.id = 'bot-filter-bar';
      filterBar.className = 'bot-filter-bar';
      filterBar.style.cssText = `
        position: sticky;
        top: 0;
        z-index: 100;
        background: rgba(10, 10, 15, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 12px 16px;
        margin: -16px -16px 16px -16px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        align-items: center;
      `;
      
      const viewSelector = container.querySelector('#viewSelector');
      if (viewSelector && viewSelector.parentNode) {
        viewSelector.parentNode.insertBefore(filterBar, viewSelector);
      }
    }
    
    updateBotFilterBar();
  }
  
  // Update bot filter bar with available bots
  async function updateBotFilterBar() {
    const filterBar = document.getElementById('bot-filter-bar');
    if (!filterBar) return;
    
    try {
      const response = await fetch('/api/bots/status');
      const data = await response.json();
      const bots = data.bots || [];
      const botNames = [...new Set(bots.map(b => b.bot_name || b.name).filter(Boolean))];
      
      filterBar.innerHTML = `
        <div style="font-weight: 600; color: #00bfff; margin-right: 8px;">Filter:</div>
        <button class="bot-filter-btn ${userSettings.selectedBots.length === 0 ? 'active' : ''}" 
                data-bot="all" onclick="window.dashboardUIFilterBot('all')">
          All
        </button>
        ${botNames.map(botName => `
          <button class="bot-filter-btn ${userSettings.selectedBots.includes(botName) ? 'active' : ''}" 
                  data-bot="${botName}" 
                  onclick="window.dashboardUIFilterBot('${botName}')"
                  style="border-left: 3px solid ${BOT_COLORS[botName] || BOT_COLORS.default};">
            ${BOT_ICONS[botName] || BOT_ICONS.default} ${botName}
          </button>
        `).join('')}
        <div style="margin-left: auto; display: flex; gap: 8px; align-items: center;">
          <button class="bot-filter-btn" onclick="window.dashboardUIToggleFavorites()" title="Show favorites only">
            ⭐ Favorites
          </button>
        </div>
      `;
    } catch (e) {
      console.error('Failed to update bot filter', e);
    }
  }
  
  // Filter bot
  window.dashboardUIFilterBot = function(botName) {
    if (botName === 'all') {
      userSettings.selectedBots = [];
    } else {
      const index = userSettings.selectedBots.indexOf(botName);
      if (index > -1) {
        userSettings.selectedBots.splice(index, 1);
      } else {
        userSettings.selectedBots.push(botName);
      }
    }
    saveSettings();
    updateBotFilterBar();
    applyFilters();
  };
  
  // Toggle favorites
  window.dashboardUIToggleFavorites = function() {
    if (userSettings.selectedBots.length === 0 && userSettings.favoriteBots.length > 0) {
      userSettings.selectedBots = [...userSettings.favoriteBots];
    } else {
      userSettings.selectedBots = [];
    }
    saveSettings();
    updateBotFilterBar();
    applyFilters();
  };
  
  // Apply filters to charts and tables
  function applyFilters() {
    // Filter event table
    const tableRows = document.querySelectorAll('#recent-events-table tbody tr');
    tableRows.forEach(row => {
      const botName = row.querySelector('td:nth-child(2)')?.textContent.trim();
      const shouldShow = userSettings.selectedBots.length === 0 || 
                        userSettings.selectedBots.includes(botName);
      row.style.display = shouldShow ? '' : 'none';
    });
    
    // Update charts (would need chart data filtering)
    // This is a placeholder - actual implementation would filter chart datasets
  }
  
  // Create time range control
  function createTimeRangeControl() {
    const container = document.getElementById('metrics-panel');
    if (!container) return;
    
    const kpiCards = container.querySelectorAll('.stat');
    kpiCards.forEach(card => {
      const desc = card.querySelector('.stat-desc');
      if (desc && desc.textContent.includes('Last 60s')) {
        const timeRangeSelect = document.createElement('select');
        timeRangeSelect.className = 'time-range-select';
        timeRangeSelect.style.cssText = `
          background: rgba(26, 26, 30, 0.6);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 4px;
          padding: 2px 6px;
          color: #f0f0f0;
          font-size: 11px;
          margin-left: 8px;
        `;
        timeRangeSelect.innerHTML = `
          <option value="15m" ${userSettings.timeRange === '15m' ? 'selected' : ''}>15m</option>
          <option value="1h" ${userSettings.timeRange === '1h' ? 'selected' : ''}>1h</option>
          <option value="24h" ${userSettings.timeRange === '24h' ? 'selected' : ''}>24h</option>
          <option value="60s" ${userSettings.timeRange === '60s' ? 'selected' : ''}>60s</option>
          <option value="custom">Custom</option>
        `;
        timeRangeSelect.addEventListener('change', (e) => {
          userSettings.timeRange = e.target.value;
          saveSettings();
          if (e.target.value === 'custom') {
            // Show custom range picker
            showCustomRangePicker();
          }
        });
        desc.appendChild(timeRangeSelect);
      }
    });
  }
  
  // Show custom range picker
  function showCustomRangePicker() {
    // Placeholder - would show a date/time picker
    const start = prompt('Start time (YYYY-MM-DD HH:MM):');
    const end = prompt('End time (YYYY-MM-DD HH:MM):');
    if (start && end) {
      userSettings.timeRange = `custom:${start}:${end}`;
      saveSettings();
    }
  }
  
  // Create alert builder
  function createAlertBuilder() {
    const container = document.getElementById('metrics-panel');
    if (!container) return;
    
    const chartToolbar = container.querySelector('#chartToolbar');
    if (!chartToolbar) return;
    
    let alertBuilderBtn = document.getElementById('alert-builder-btn');
    if (!alertBuilderBtn) {
      alertBuilderBtn = document.createElement('button');
      alertBuilderBtn.id = 'alert-builder-btn';
      alertBuilderBtn.className = 'btn btn-xs';
      alertBuilderBtn.textContent = '⚙️ Alert Builder';
      alertBuilderBtn.onclick = showAlertBuilder;
      chartToolbar.appendChild(alertBuilderBtn);
    }
  }
  
  // Show alert builder modal
  function showAlertBuilder() {
    const modal = document.createElement('div');
    modal.className = 'alert-builder-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(10px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    
    modal.innerHTML = `
      <div style="
        background: rgba(10, 10, 15, 0.95);
        border: 1px solid rgba(0, 191, 255, 0.5);
        border-radius: 12px;
        padding: 24px;
        max-width: 600px;
        width: 90%;
        color: #f0f0f0;
      ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <h3 style="margin: 0; color: #00bfff;">⚙️ Alert Builder</h3>
          <button onclick="this.closest('.alert-builder-modal').remove()" style="
            background: transparent;
            border: none;
            color: #888;
            font-size: 24px;
            cursor: pointer;
          ">×</button>
        </div>
        <div id="alert-rules-list" style="margin-bottom: 20px; max-height: 300px; overflow-y: auto;">
          ${renderAlertRules()}
        </div>
        <button onclick="window.dashboardUIAddAlertRule()" style="
          width: 100%;
          padding: 12px;
          background: rgba(0, 191, 255, 0.2);
          border: 1px solid rgba(0, 191, 255, 0.5);
          border-radius: 6px;
          color: #00bfff;
          cursor: pointer;
          margin-bottom: 12px;
        ">+ Add Alert Rule</button>
        <div style="display: flex; gap: 8px;">
          <button onclick="this.closest('.alert-builder-modal').remove()" style="
            flex: 1;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            color: #f0f0f0;
            cursor: pointer;
          ">Close</button>
          <button onclick="window.dashboardUISaveAlerts()" style="
            flex: 1;
            padding: 10px;
            background: rgba(0, 191, 255, 0.3);
            border: 1px solid rgba(0, 191, 255, 0.5);
            border-radius: 6px;
            color: #00bfff;
            cursor: pointer;
          ">Save</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
  }
  
  // Render alert rules
  function renderAlertRules() {
    if (userSettings.alertRules.length === 0) {
      return '<div style="text-align: center; color: #888; padding: 20px;">No alert rules yet. Click "Add Alert Rule" to create one.</div>';
    }
    
    return userSettings.alertRules.map((rule, idx) => `
      <div style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
      ">
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div style="flex: 1;">
            <div style="font-weight: 600; margin-bottom: 4px;">IF ${rule.condition}</div>
            <div style="font-size: 12px; color: #888;">THEN ${rule.action}</div>
          </div>
          <button onclick="window.dashboardUIDeleteAlertRule(${idx})" style="
            background: transparent;
            border: none;
            color: #ff3b5c;
            cursor: pointer;
          ">×</button>
        </div>
      </div>
    `).join('');
  }
  
  // Add alert rule
  window.dashboardUIAddAlertRule = function() {
    const condition = prompt('Condition (e.g., "latency > 300 AND success < 90"):');
    const action = prompt('Action (e.g., "Send Slack DM"):');
    if (condition && action) {
      userSettings.alertRules.push({ condition, action, enabled: true });
      saveSettings();
      document.getElementById('alert-rules-list').innerHTML = renderAlertRules();
    }
  };
  
  // Delete alert rule
  window.dashboardUIDeleteAlertRule = function(idx) {
    userSettings.alertRules.splice(idx, 1);
    saveSettings();
    document.getElementById('alert-rules-list').innerHTML = renderAlertRules();
  };
  
  // Save alerts
  window.dashboardUISaveAlerts = function() {
    saveSettings();
    document.querySelector('.alert-builder-modal')?.remove();
  };
  
  // Create command palette (⌘K)
  function createCommandPalette() {
    const palette = document.createElement('div');
    palette.id = 'command-palette';
    palette.className = 'command-palette';
    palette.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(10, 10, 15, 0.98);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 191, 255, 0.5);
      border-radius: 12px;
      padding: 0;
      width: 600px;
      max-width: 90vw;
      max-height: 70vh;
      z-index: 10001;
      display: none;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.9);
      color: #f0f0f0;
    `;
    
    palette.innerHTML = `
      <div style="padding: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
        <input type="text" id="command-input" placeholder="Type a command... (e.g., 'restart arb-scout', 'inspect tx-relay')" 
               style="
                 width: 100%;
                 background: rgba(26, 26, 30, 0.6);
                 border: 1px solid rgba(255, 255, 255, 0.1);
                 border-radius: 6px;
                 padding: 12px;
                 color: #f0f0f0;
                 font-size: 14px;
               " autofocus>
      </div>
      <div id="command-suggestions" style="
        max-height: 400px;
        overflow-y: auto;
        padding: 8px;
      ">
        ${renderCommandSuggestions()}
      </div>
    `;
    
    document.body.appendChild(palette);
    
    const input = palette.querySelector('#command-input');
    input.addEventListener('input', (e) => {
      filterCommandSuggestions(e.target.value);
    });
    
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        hideCommandPalette();
      } else if (e.key === 'Enter') {
        executeCommand(e.target.value);
      }
    });
  }
  
  // Render command suggestions
  function renderCommandSuggestions() {
    const commands = [
      { cmd: 'restart', desc: 'Restart a bot (e.g., restart arb-scout)' },
      { cmd: 'inspect', desc: 'Inspect bot at time (e.g., inspect tx-relay 14:29:15)' },
      { cmd: 'filter', desc: 'Filter by bot (e.g., filter mev-watch)' },
      { cmd: 'clear', desc: 'Clear filters' },
      { cmd: 'export', desc: 'Export data' },
      { cmd: 'theme', desc: 'Toggle theme' }
    ];
    
    return commands.map(c => `
      <div class="command-suggestion" data-cmd="${c.cmd}" style="
        padding: 12px;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 4px;
        transition: background 0.2s;
      " onmouseover="this.style.background='rgba(0, 191, 255, 0.1)'"
         onmouseout="this.style.background='transparent'"
         onclick="window.dashboardUIExecuteCommand('${c.cmd}')">
        <div style="font-weight: 600; color: #00bfff;">${c.cmd}</div>
        <div style="font-size: 12px; color: #888; margin-top: 2px;">${c.desc}</div>
      </div>
    `).join('');
  }
  
  // Filter command suggestions
  function filterCommandSuggestions(query) {
    const suggestions = document.querySelectorAll('.command-suggestion');
    suggestions.forEach(s => {
      const cmd = s.dataset.cmd;
      const matches = cmd.includes(query.toLowerCase()) || 
                     s.textContent.toLowerCase().includes(query.toLowerCase());
      s.style.display = matches ? '' : 'none';
    });
  }
  
  // Execute command
  function executeCommand(cmd) {
    const parts = cmd.trim().split(' ');
    const action = parts[0];
    
    switch (action) {
      case 'restart':
        const bot = parts[1];
        if (bot) {
          alert(`Would restart ${bot} (simulated)`);
          // In real implementation: fetch(`/api/bots/${bot}/restart`, { method: 'POST' });
        }
        break;
      case 'inspect':
        const botName = parts[1];
        const time = parts[2];
        if (botName && time) {
          alert(`Would inspect ${botName} at ${time} (simulated)`);
        }
        break;
      case 'filter':
        if (parts[1]) {
          window.dashboardUIFilterBot(parts[1]);
        }
        break;
      case 'clear':
        userSettings.selectedBots = [];
        saveSettings();
        updateBotFilterBar();
        applyFilters();
        break;
      case 'theme':
        toggleTheme();
        break;
    }
    
    hideCommandPalette();
  }
  
  window.dashboardUIExecuteCommand = executeCommand;
  
  // Show command palette
  function showCommandPalette() {
    const palette = document.getElementById('command-palette');
    if (palette) {
      palette.style.display = 'block';
      const input = palette.querySelector('#command-input');
      if (input) {
        input.value = '';
        input.focus();
      }
      commandPaletteOpen = true;
    }
  }
  
  // Hide command palette
  function hideCommandPalette() {
    const palette = document.getElementById('command-palette');
    if (palette) {
      palette.style.display = 'none';
      commandPaletteOpen = false;
    }
  }
  
  // Setup command palette shortcut (⌘K or Ctrl+K)
  function setupCommandPaletteShortcut() {
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (commandPaletteOpen) {
          hideCommandPalette();
        } else {
          showCommandPalette();
        }
      } else if (e.key === 'Escape' && commandPaletteOpen) {
        hideCommandPalette();
      }
    });
  }
  
  // Update bot avatars with glow effects
  function updateBotAvatars() {
    // Add glow to bot names in tables
    document.querySelectorAll('[data-bot-name]').forEach(el => {
      const botName = el.dataset.botName;
      const color = BOT_COLORS[botName] || BOT_COLORS.default;
      el.style.borderLeft = `3px solid ${color}`;
    });
  }
  
  // Create incident timeline
  function createIncidentTimeline() {
    // Placeholder - would show error events in a timeline
  }
  
  // Setup theme toggle
  function setupThemeToggle() {
    // Sync with system theme
    if (window.matchMedia) {
      const darkMode = window.matchMedia('(prefers-color-scheme: dark)');
      if (darkMode.matches && userSettings.theme !== 'dark') {
        userSettings.theme = 'dark';
        saveSettings();
      }
    }
  }
  
  // Toggle theme
  function toggleTheme() {
    userSettings.theme = userSettings.theme === 'dark' ? 'light' : 'dark';
    saveSettings();
    document.body.classList.toggle('light-theme', userSettings.theme === 'light');
  }
  
  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboardUI);
  } else {
    initDashboardUI();
  }
  
  // Re-initialize on HTMX swaps
  document.body.addEventListener('htmx:afterSwap', (e) => {
    if (e.target.id === 'metrics-panel') {
      setTimeout(initDashboardUI, 100);
    }
  });
  
  // Highlight row function
  window.dashboardUIHighlightRow = function(row) {
    // Remove previous highlights
    document.querySelectorAll('#recent-events-table tbody tr').forEach(r => {
      r.classList.remove('highlighted');
    });
    
    // Highlight clicked row
    row.classList.add('highlighted');
    
    // Scroll to row
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Remove highlight after 2 seconds
    setTimeout(() => {
      row.classList.remove('highlighted');
    }, 2000);
  };
  
  // Animate KPI value changes
  function animateKPIValue(elementId, newValue, status) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    const oldValue = el.textContent;
    if (oldValue === newValue) return;
    
    // Add pulse animation
    el.classList.add('pulse');
    setTimeout(() => el.classList.remove('pulse'), 600);
    
    // Update value with fade transition
    el.style.opacity = '0.5';
    setTimeout(() => {
      el.textContent = newValue;
      if (status) {
        el.setAttribute('data-status', status);
      }
      el.style.opacity = '1';
    }, 150);
  }
  
  // Update KPIs from SSE events
  document.body.addEventListener('sse:metrics', function(e) {
    try {
      const evt = typeof e.detail === 'string' ? JSON.parse(e.detail) : e.detail;
      
      // Update latency KPI if needed
      const latencyEl = document.getElementById('kpi-latency-value');
      if (latencyEl && evt.latency_ms) {
        const status = evt.latency_ms > 300 ? 'error' : evt.latency_ms > 200 ? 'warning' : 'ok';
        // Don't update on every event, just animate if significant change
      }
      
      // Update success rate
      const successEl = document.getElementById('kpi-success-value');
      if (successEl && evt.success_rate) {
        const status = evt.success_rate < 80 ? 'error' : evt.success_rate < 90 ? 'warning' : 'ok';
        // Animate on significant changes
      }
    } catch (e) {
      // Ignore
    }
  });
  
  // Export functions
  window.dashboardUI = {
    init: initDashboardUI,
    showCommandPalette,
    hideCommandPalette,
    updateHealthSummary,
    updateBotFilterBar,
    highlightRow: window.dashboardUIHighlightRow
  };
  
})();

