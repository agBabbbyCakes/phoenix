// Alpine.js State Management for Dashboard
function dashboardState() {
  return {
    // Theme
    theme: localStorage.getItem('phoenix:theme') || 'dark',
    
    // KPIs
    kpis: {
      avg_latency_ms: 0,
      success_rate_pct: 0,
      throughput_1m: 0
    },
    
    // Health Summary
    healthSummary: {
      ok: 0,
      slow: 0,
      error: 0
    },
    
    // Bot Management
    availableBots: [],
    selectedBots: JSON.parse(localStorage.getItem('phoenix:selectedBots') || '[]'),
    favoriteBots: JSON.parse(localStorage.getItem('phoenix:favoriteBots') || '[]'),
    
    // Chart Settings
    selectedView: localStorage.getItem('phoenix:selectedView') || 'latency',
    showMovingAvg: localStorage.getItem('phoenix:showMovingAvg') === 'true',
    
    // Alerts
    alertLatencyThreshold: parseInt(localStorage.getItem('phoenix:alertLatencyThreshold') || '300'),
    alertRules: JSON.parse(localStorage.getItem('phoenix:alertRules') || '[]'),
    
    // Command Palette
    showCommandPalette: false,
    commandInput: '',
    
    // Connection Status
    connectionStatus: 'disconnected',
    
    // Bot Icons Mapping
    botIcons: {
      'arb-scout': '🎯',
      'mev-watch': '👁️',
      'tx-relay': '⚡',
      'sandwich-guard': '🛡️',
      'arbit-bot': '🤖',
      'eth-sniper': '🎯',
      'price-bot': '💰',
      'rsi-bot': '📊',
      'trading-bot': '📈',
      'strategy-bot': '🧠'
    },
    
    // Initialize
    init() {
      this.loadKPIs();
      this.loadHealthSummary();
      this.loadAvailableBots();
      this.setupSSE();
      this.setupKeyboardShortcuts();
      this.applyTheme();
      
      // Auto-refresh every 5 seconds
      setInterval(() => {
        this.loadKPIs();
        this.loadHealthSummary();
      }, 5000);
    },
    
    // Theme Management
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('phoenix:theme', this.theme);
      this.applyTheme();
    },
    
    applyTheme() {
      document.documentElement.classList.toggle('light-theme', this.theme === 'light');
      if (this.theme === 'light') {
        document.documentElement.style.colorScheme = 'light';
      } else {
        document.documentElement.style.colorScheme = 'dark';
      }
    },
    
    // Color Helpers
    getLatencyColor(latency) {
      if (latency > 300) return 'text-red-400';
      if (latency > 200) return 'text-yellow-400';
      return 'text-emerald-400';
    },
    
    getSuccessColor(rate) {
      if (rate < 80) return 'text-red-400';
      if (rate < 90) return 'text-yellow-400';
      return 'text-blue-400';
    },
    
    getBotIcon(botName) {
      for (const [key, icon] of Object.entries(this.botIcons)) {
        if (botName.toLowerCase().includes(key.toLowerCase())) {
          return icon;
        }
      }
      return '🤖';
    },
    
    // Bot Filtering
    toggleBot(bot) {
      const index = this.selectedBots.indexOf(bot);
      if (index > -1) {
        this.selectedBots.splice(index, 1);
      } else {
        this.selectedBots.push(bot);
      }
      localStorage.setItem('phoenix:selectedBots', JSON.stringify(this.selectedBots));
      this.applyFilters();
    },
    
    applyFilters() {
      // Filter table rows
      const rows = document.querySelectorAll('#events-table-body tr');
      rows.forEach(row => {
        const botName = row.dataset.botName;
        const shouldShow = this.selectedBots.length === 0 || this.selectedBots.includes(botName);
        row.style.display = shouldShow ? '' : 'none';
      });
      // Filter live stream feed (sidebar) if present
      const streamItems = document.querySelectorAll('#sidebar-event-feed .event-item');
      streamItems.forEach(div => {
        // bot name is in a span.font-semibold inside the event item
        const botSpan = div.querySelector('.font-semibold');
        const botText = botSpan ? botSpan.textContent.trim() : '';
        const shouldShow = this.selectedBots.length === 0 || this.selectedBots.includes(botText);
        div.style.display = shouldShow ? '' : 'none';
      });
    },
    
    // Load Data
    async loadKPIs() {
      try {
        const response = await fetch('/api/charts/data');
        const data = await response.json();
        if (data.kpis) {
          this.kpis = data.kpis;
        }
      } catch (e) {
        console.error('Failed to load KPIs', e);
      }
    },
    
    async loadHealthSummary() {
      try {
        const response = await fetch('/api/bots/status');
        const data = await response.json();
        const bots = data.bots || [];
        
        this.healthSummary = { ok: 0, slow: 0, error: 0 };
        
        bots.forEach(bot => {
          const latency = bot.latency_ms || bot.latency || 0;
          const successRatio = bot.success_ratio || 100;
          const status = bot.status || 'ok';
          
          if (status === 'error' || status === 'critical' || (bot.failure_count || 0) > 10) {
            this.healthSummary.error++;
          } else if (latency > 200 || successRatio < 80 || status === 'warning') {
            this.healthSummary.slow++;
          } else {
            this.healthSummary.ok++;
          }
        });
      } catch (e) {
        console.error('Failed to load health summary', e);
      }
    },
    
    async loadAvailableBots() {
      try {
        const response = await fetch('/api/bots/status');
        const data = await response.json();
        const bots = data.bots || [];
        this.availableBots = [...new Set(bots.map(b => b.bot_name || b.name).filter(Boolean))];
      } catch (e) {
        console.error('Failed to load bots', e);
      }
    },
    
    // Chart Management
    updateChartView() {
      localStorage.setItem('phoenix:selectedView', this.selectedView);
      // Trigger chart update via existing system
      const selector = document.getElementById('viewSelector');
      if (selector) {
        selector.value = this.selectedView;
        selector.dispatchEvent(new Event('change'));
      }
    },
    
    updateChartOptions() {
      localStorage.setItem('phoenix:showMovingAvg', this.showMovingAvg);
      // Update chart with moving average
      if (window.__chartPrimary && window.__chartPrimary.value) {
        const chart = window.__chartPrimary.value;
        if (chart.data.datasets[1]) {
          chart.data.datasets[1].hidden = !this.showMovingAvg;
          chart.update();
        }
      }
    },
    
    resetZoom() {
      if (window.__chartPrimary && window.__chartPrimary.value && window.__chartPrimary.value.resetZoom) {
        window.__chartPrimary.value.resetZoom();
      }
      if (window.__chartSecondary && window.__chartSecondary.value && window.__chartSecondary.value.resetZoom) {
        window.__chartSecondary.value.resetZoom();
      }
    },
    
    // Alert Management
    updateAlertThreshold() {
      localStorage.setItem('phoenix:alertLatencyThreshold', this.alertLatencyThreshold);
    },
    
    saveAlert() {
      if (!this.alertLatencyThreshold) return;
      
      const rule = {
        condition: `latency >= ${this.alertLatencyThreshold}ms`,
        action: 'Show notification',
        threshold: this.alertLatencyThreshold
      };
      
      this.alertRules.push(rule);
      localStorage.setItem('phoenix:alertRules', JSON.stringify(this.alertRules));
      
      // Show confirmation
      alert(`Alert saved: ${rule.condition}`);
    },
    
    removeAlert(index) {
      this.alertRules.splice(index, 1);
      localStorage.setItem('phoenix:alertRules', JSON.stringify(this.alertRules));
    },
    
    // Command Execution
    executeCommand() {
      const cmd = this.commandInput.trim().toLowerCase();
      const parts = cmd.split(' ');
      const action = parts[0];
      
      switch (action) {
        case 'restart':
          const bot = parts[1];
          if (bot) {
            alert(`Would restart ${bot} (simulated)`);
            // In real implementation: fetch(`/api/bots/${bot}/restart`, { method: 'POST' });
          } else {
            alert('Usage: restart <bot-name>');
          }
          break;
          
        case 'inspect':
          const botName = parts[1];
          const time = parts[2];
          if (botName && time) {
            alert(`Would inspect ${botName} at ${time} (simulated)`);
          } else {
            alert('Usage: inspect <bot-name> <time>');
          }
          break;
          
        case 'filter':
          if (parts[1]) {
            this.toggleBot(parts[1]);
          } else {
            alert('Usage: filter <bot-name>');
          }
          break;
          
        case 'clear':
          this.selectedBots = [];
          localStorage.setItem('phoenix:selectedBots', JSON.stringify(this.selectedBots));
          this.applyFilters();
          alert('Filters cleared');
          break;
          
        case 'export':
          this.exportData();
          break;
          
        case 'theme':
          this.toggleTheme();
          break;
          
        default:
          if (cmd) {
            alert(`Unknown command: ${action}\nTry: restart, inspect, filter, clear, export, theme`);
          }
      }
      
      this.commandInput = '';
      this.showCommandPalette = false;
    },
    
    exportData() {
      const data = {
        kpis: this.kpis,
        healthSummary: this.healthSummary,
        selectedBots: this.selectedBots,
        alertRules: this.alertRules,
        timestamp: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `botscope-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    
    // Row Highlighting
    highlightRow(row) {
      document.querySelectorAll('#events-table-body tr').forEach(r => {
        r.classList.remove('bg-blue-600/20');
      });
      row.classList.add('bg-blue-600/20');
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => {
        row.classList.remove('bg-blue-600/20');
      }, 2000);
    },
    
    // SSE Setup
    setupSSE() {
      // Listen for SSE connection status
      document.body.addEventListener('htmx:sseOpen', () => {
        this.connectionStatus = 'connected';
      });
      
      document.body.addEventListener('htmx:sseError', () => {
        this.connectionStatus = 'disconnected';
      });
      
      // Listen for metrics updates
      document.body.addEventListener('sse:metrics', (e) => {
        try {
          const evt = typeof e.detail === 'string' ? JSON.parse(e.detail) : e.detail;
          // Update KPIs if significant change
          if (evt.latency_ms && Math.abs(evt.latency_ms - this.kpis.avg_latency_ms) > 50) {
            this.loadKPIs();
          }
        } catch (e) {
          // Ignore
        }
      });
    },
    
    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
      document.addEventListener('keydown', (e) => {
        // Command palette (⌘K or Ctrl+K)
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
          e.preventDefault();
          this.showCommandPalette = !this.showCommandPalette;
          if (this.showCommandPalette) {
            setTimeout(() => {
              const input = document.querySelector('[x-model="commandInput"]');
              if (input) input.focus();
            }, 100);
          }
        }
        
        // Escape to close command palette
        if (e.key === 'Escape' && this.showCommandPalette) {
          this.showCommandPalette = false;
        }
      });
    }
  };
}

