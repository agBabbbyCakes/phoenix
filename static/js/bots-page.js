// Bots Page State Management
function botsPageState() {
  return {
    theme: localStorage.getItem('phoenix:theme') || 'dark',
    kpis: { avg_latency_ms: 0, success_rate_pct: 0 },
    bots: [],
    filterStatus: 'all',
    showAddBotModal: false,
    showMiscMenu: false,
    newBot: { name: '', address: '', strategy: 'arbitrage', apiKey: '' },
    lastUpdated: new Date().toLocaleTimeString(),
    
    init() {
      this.loadBots();
      this.loadKPIs();
      this.loadHealthSummary();
      this.loadAvailableBots();
      this.applyTheme();
      
      setInterval(() => {
        this.loadBots();
        this.loadKPIs();
        this.loadHealthSummary();
        this.lastUpdated = new Date().toLocaleTimeString();
      }, 5000);
    },
    
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('phoenix:theme', this.theme);
      this.applyTheme();
    },
    
    applyTheme() {
      document.documentElement.classList.toggle('light-theme', this.theme === 'light');
    },
    
    async loadBots() {
      try {
        const response = await fetch('/api/bots/status');
        const data = await response.json();
        const apiBots = data.bots || [];
        
        // Merge with stored bots (from localStorage for now)
        const storedBots = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
        
        // Create bot registry from API data + stored config
        this.bots = apiBots.map(apiBot => {
          const stored = storedBots.find(b => b.name === apiBot.bot_name);
          return {
            id: apiBot.bot_name.toLowerCase().replace(/\s+/g, '-'),
            name: apiBot.bot_name,
            status: this.determineStatus(apiBot),
            avg_latency: apiBot.latency_ms || 0,
            success_rate: apiBot.success_ratio || 0,
            strategy: stored?.strategy || 'unknown',
            address: stored?.address || '',
            enabled: stored?.enabled !== false,
            uptime: this.calculateUptime(apiBot.last_heartbeat),
            last_heartbeat: apiBot.last_heartbeat
          };
        });
        
        // Add any stored bots not in API
        storedBots.forEach(stored => {
          if (!this.bots.find(b => b.name === stored.name)) {
            this.bots.push({
              id: stored.name.toLowerCase().replace(/\s+/g, '-'),
              name: stored.name,
              status: 'idle',
              avg_latency: 0,
              success_rate: 0,
              strategy: stored.strategy || 'unknown',
              address: stored.address || '',
              enabled: stored.enabled !== false,
              uptime: 'N/A',
              last_heartbeat: null
            });
          }
        });
      } catch (e) {
        console.error('Failed to load bots', e);
      }
    },
    
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
    
    determineStatus(bot) {
      const latency = bot.latency_ms || 0;
      const successRatio = bot.success_ratio || 100;
      const failureCount = bot.failure_count || 0;
      
      if (failureCount > 10 || bot.status === 'error' || bot.status === 'critical') {
        return 'error';
      } else if (latency > 200 || successRatio < 80 || bot.status === 'warning') {
        return 'warning';
      } else if (latency > 0 || successRatio > 0) {
        return 'active';
      }
      return 'idle';
    },
    
    calculateUptime(lastHeartbeat) {
      if (!lastHeartbeat) return 'N/A';
      try {
        const then = new Date(lastHeartbeat);
        const now = new Date();
        const diffMs = now - then;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays > 0) return `${diffDays}d ${diffHours % 24}h`;
        if (diffHours > 0) return `${diffHours}h ${diffMins % 60}m`;
        return `${diffMins}m`;
      } catch (e) {
        return 'N/A';
      }
    },
    
    get filteredBots() {
      if (this.filterStatus === 'all') return this.bots;
      return this.bots.filter(bot => bot.status === this.filterStatus);
    },
    
    getStatusEmoji(status) {
      const emojis = {
        'active': '🟢',
        'warning': '🟡',
        'error': '🔴',
        'idle': '⚪'
      };
      return emojis[status] || '⚪';
    },
    
    getStatusClass(status) {
      const classes = {
        'active': 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
        'warning': 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
        'error': 'text-red-400 border-red-500/30 bg-red-500/10',
        'idle': 'text-gray-400 border-gray-500/30 bg-gray-500/10'
      };
      return classes[status] || classes.idle;
    },
    
    getLatencyColor(latency) {
      if (latency > 300) return 'text-red-400';
      if (latency > 200) return 'text-yellow-400';
      return 'text-emerald-400';
    },
    
    getSuccessColor(rate) {
      if (rate < 80) return 'text-red-400';
      if (rate < 90) return 'text-yellow-400';
      return 'text-emerald-400';
    },
    
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
      this.loadBots();
      
      alert(`Bot "${bot.name}" added successfully!`);
    },
    
    inspectBot(botId) {
      window.location.href = `/bots/${botId}`;
    },
    
    restartBot(botId) {
      const bot = this.bots.find(b => b.id === botId);
      if (bot && confirm(`Restart ${bot.name}?`)) {
        alert(`Would restart ${bot.name} (simulated)`);
        // In real implementation: fetch(`/api/bots/${botId}/restart`, { method: 'POST' });
      }
    },
    
    toggleBotEnabled(botId) {
      const stored = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
      const bot = stored.find(b => b.id === botId || b.name.toLowerCase().replace(/\s+/g, '-') === botId);
      if (bot) {
        bot.enabled = !bot.enabled;
        localStorage.setItem('phoenix:registeredBots', JSON.stringify(stored));
        this.loadBots();
      }
    }
  };
}

