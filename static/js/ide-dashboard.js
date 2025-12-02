// IDE Dashboard State Management
function ideDashboardState() {
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
    
    // Command Palette
    showCommandPalette: false,
    commandInput: '',
    showMiscMenu: false,
    
    // Connection Status
    connectionStatus: 'disconnected',
    
    // Bot Icons
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
    
    // Current page tracking
    currentPage: 'dashboard',
    
    // Add Bot Modal
    showAddBotModal: false,
    newBot: { name: '', address: '', strategy: 'arbitrage', apiKey: '' },
    
    // Last updated timestamp
    lastUpdated: new Date().toLocaleTimeString(),
    
    // Initialize
    init() {
      this.detectCurrentPage();
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
        this.lastUpdated = new Date().toLocaleTimeString();
      }, 5000);
    },
    
    detectCurrentPage() {
      const path = window.location.pathname;
      if (path === '/bots' || path.startsWith('/bots/')) {
        this.currentPage = 'bots';
      } else if (path === '/logs') {
        this.currentPage = 'logs';
      } else if (path === '/report') {
        this.currentPage = 'reports';
      } else if (path === '/settings') {
        this.currentPage = 'settings';
      } else {
        this.currentPage = 'dashboard';
      }
    },
    
    // Theme Management
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('phoenix:theme', this.theme);
      this.applyTheme();
    },
    
    applyTheme() {
      document.documentElement.classList.toggle('light-theme', this.theme === 'light');
    },
    
    // Color Helpers
    getLatencyColor(latency) {
      if (latency > 300) return 'text-red-400';
      if (latency > 200) return 'text-yellow-400';
      return 'text-emerald-400';
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
      const rows = document.querySelectorAll('#event-stream > div');
      rows.forEach(row => {
        const botName = row.dataset.botName;
        const shouldShow = this.selectedBots.length === 0 || this.selectedBots.includes(botName);
        row.style.display = shouldShow ? '' : 'none';
      });
    },
    
    // Load Data
    async loadKPIs() {
      try {
        const response = await fetch('/api/charts/data');
        const data = await response.json();
        if (data.kpis) {
          this.kpis = data.kpis;
          // Update global sidebar stats
          this.updateSidebarStats();
        }
      } catch (e) {
        console.error('Failed to load KPIs', e);
      }
    },
    
    updateSidebarStats() {
      const latencyEl = document.getElementById('sidebar-latency');
      const successEl = document.getElementById('sidebar-success');
      const throughputEl = document.getElementById('sidebar-throughput');
      
      if (latencyEl) latencyEl.textContent = (this.kpis.avg_latency_ms || 0) + 'ms';
      if (successEl) successEl.textContent = (this.kpis.success_rate_pct || 0) + '%';
      if (throughputEl) throughputEl.textContent = (this.kpis.throughput_1m || 0);
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
        
        // Update global sidebar health
        this.updateSidebarHealth();
      } catch (e) {
        console.error('Failed to load health summary', e);
      }
    },
    
    updateSidebarHealth() {
      const okEl = document.getElementById('sidebar-health-ok');
      const slowEl = document.getElementById('sidebar-health-slow');
      const errorEl = document.getElementById('sidebar-health-error');
      
      if (okEl) okEl.textContent = (this.healthSummary.ok || 0);
      if (slowEl) slowEl.textContent = (this.healthSummary.slow || 0);
      if (errorEl) errorEl.textContent = (this.healthSummary.error || 0);
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
    
    // Event Highlighting
    highlightEvent(element) {
      document.querySelectorAll('#event-stream > div').forEach(el => {
        el.classList.remove('bg-cyan-500/20', 'border-cyan-500');
      });
      element.classList.add('bg-cyan-500/20', 'border-cyan-500');
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => {
        element.classList.remove('bg-cyan-500/20', 'border-cyan-500');
      }, 2000);
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
            this.toggleBot(parts[1]);
          }
          break;
        case 'clear':
          this.selectedBots = [];
          localStorage.setItem('phoenix:selectedBots', JSON.stringify(this.selectedBots));
          this.applyFilters();
          break;
        case 'export':
          this.exportData();
          break;
        case 'theme':
          this.toggleTheme();
          break;
      }
      
      this.commandInput = '';
      this.showCommandPalette = false;
    },
    
    exportData() {
      const data = {
        kpis: this.kpis,
        healthSummary: this.healthSummary,
        selectedBots: this.selectedBots,
        timestamp: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `silverback-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    
    // SSE Setup
    setupSSE() {
      document.body.addEventListener('htmx:sseOpen', () => {
        this.connectionStatus = 'connected';
      });
      
      document.body.addEventListener('htmx:sseError', () => {
        this.connectionStatus = 'disconnected';
      });
      
      // Listen for new events and add to right sidebar
      document.body.addEventListener('sse:metrics', (e) => {
        try {
          const evt = typeof e.detail === 'string' ? JSON.parse(e.detail) : e.detail;
          this.addEventToStream(evt);
        } catch (e) {
          // Ignore
        }
      });
    },
    
    addEventToStream(event) {
      const stream = document.getElementById('event-stream');
      if (!stream) return;
      
      const eventDiv = document.createElement('div');
      eventDiv.className = 'p-3 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-cyan-500/50 transition-colors cursor-pointer animate-fade-in';
      eventDiv.dataset.botName = event.bot_name || 'unknown';
      
      const timestamp = new Date(event.timestamp || Date.now()).toLocaleTimeString();
      const botIcon = this.getBotIcon(event.bot_name || 'unknown');
      const latencyColor = this.getLatencyColor(event.latency_ms || 0);
      
      eventDiv.innerHTML = `
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-2">
            <span class="text-lg">${botIcon}</span>
            <span class="text-sm font-semibold text-gray-300">${event.bot_name || 'unknown'}</span>
          </div>
          <span class="text-xs text-gray-500 font-mono">${timestamp}</span>
        </div>
        <div class="flex items-center gap-3 text-xs">
          <span class="font-mono ${latencyColor}">${event.latency_ms || 0}ms</span>
          <span class="${event.error ? 'text-red-400' : 'text-emerald-400'}">${event.error ? 'Error' : 'OK'}</span>
        </div>
        ${event.tx_hash ? `
        <div class="mt-2">
          <a href="https://etherscan.io/tx/${event.tx_hash}" 
             target="_blank"
             class="text-xs text-cyan-400 hover:text-cyan-300 font-mono hover:underline">
            ${event.tx_hash.substring(0, 16)}...
          </a>
        </div>
        ` : ''}
      `;
      
      eventDiv.addEventListener('click', () => this.highlightEvent(eventDiv));
      
      stream.insertBefore(eventDiv, stream.firstChild);
      
      // Keep only last 50 events
      while (stream.children.length > 50) {
        stream.removeChild(stream.lastChild);
      }
    },
    
    // Keyboard Shortcuts
    setupKeyboardShortcuts() {
      document.addEventListener('keydown', (e) => {
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
        
        if (e.key === 'Escape' && this.showCommandPalette) {
          this.showCommandPalette = false;
        }
      });
    },
    
    // Add Bot
    addBot() {
      const bot = {
        id: this.newBot.name.toLowerCase().replace(/\s+/g, '-'),
        name: this.newBot.name,
        address: this.newBot.address,
        strategy: this.newBot.strategy,
        apiKey: this.newBot.apiKey,
        enabled: true,
        createdAt: new Date().toISOString()
      };
      
      const stored = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
      stored.push(bot);
      localStorage.setItem('phoenix:registeredBots', JSON.stringify(stored));
      
      this.newBot = { name: '', address: '', strategy: 'arbitrage', apiKey: '' };
      this.showAddBotModal = false;
      this.loadAvailableBots();
      
      alert(`Bot "${bot.name}" added successfully!`);
    }
  };
}

