// Bot Profile Page State
function botProfileState() {
  return {
    botId: window.location.pathname.split('/').pop(),
    bot: {},
    selectedChart: 'latency',
    chart: null,
    recentTransactions: [],
    insights: {
      summary: 'Loading insights...',
      lastUpdated: new Date().toLocaleString()
    },
    notesThisWeek: 0,
    lastUpdated: new Date().toLocaleTimeString(),
    theme: localStorage.getItem('phoenix:theme') || 'dark',
    showCommandPalette: false,
    
    init() {
      this.loadBot();
      this.loadTransactions();
      this.loadInsights();
      this.initChart();
      this.applyTheme();
      
      setInterval(() => {
        this.loadBot();
        this.loadTransactions();
        this.loadInsights();
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
    
    exportData() {
      const data = {
        bot: this.bot,
        transactions: this.recentTransactions,
        insights: this.insights,
        timestamp: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `silverback-bot-${this.botId}-export-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    
    async loadBot() {
      try {
        // Load from API
        const response = await fetch('/api/bots/status');
        const data = await response.json();
        const apiBot = data.bots?.find(b => 
          b.bot_name.toLowerCase().replace(/\s+/g, '-') === this.botId
        );
        
        // Load stored config
        const stored = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
        const storedBot = stored.find(b => b.id === this.botId);
        
        if (apiBot) {
          this.bot = {
            id: this.botId,
            name: apiBot.bot_name,
            status: this.determineStatus(apiBot),
            avg_latency: apiBot.latency_ms || 0,
            success_rate: apiBot.success_ratio || 0,
            strategy: storedBot?.strategy || 'unknown',
            address: storedBot?.address || '',
            enabled: storedBot?.enabled !== false,
            uptime: this.calculateUptime(apiBot.last_heartbeat),
            notes: storedBot?.notes || '',
            lastNote: storedBot?.lastNote || null,
            total_tx: storedBot?.total_tx || 0
          };
        } else if (storedBot) {
          this.bot = {
            ...storedBot,
            status: 'idle',
            avg_latency: 0,
            success_rate: 0,
            uptime: 'N/A'
          };
        }
      } catch (e) {
        console.error('Failed to load bot', e);
      }
    },
    
    async loadTransactions() {
      // Load from events
      try {
        const response = await fetch('/api/charts/data');
        const data = await response.json();
        const events = data.events || [];
        
        this.recentTransactions = events
          .filter(e => e.bot_name && e.bot_name.toLowerCase().replace(/\s+/g, '-') === this.botId)
          .slice(0, 10)
          .map(e => ({
            hash: e.tx_hash || 'N/A',
            time: new Date(e.timestamp).toLocaleTimeString(),
            status: e.error ? 'failed' : 'success',
            latency: e.latency_ms || 0,
            profit: e.profit
          }));
      } catch (e) {
        console.error('Failed to load transactions', e);
      }
    },
    
    async loadInsights() {
      // Generate insights from bot data
      const latency = this.bot.avg_latency || 0;
      const success = this.bot.success_rate || 0;
      const prevLatency = parseFloat(localStorage.getItem(`phoenix:bot:${this.botId}:prevLatency`) || latency);
      
      const latencyChange = latency - prevLatency;
      const latencyPercent = prevLatency > 0 ? ((latencyChange / prevLatency) * 100).toFixed(1) : 0;
      
      let summary = '';
      if (latencyChange < -50) {
        summary = `✅ <strong>${this.bot.name}</strong> improved latency by ${Math.abs(latencyPercent)}% over the last 30 minutes.`;
      } else if (latencyChange > 50) {
        summary = `⚠️ <strong>${this.bot.name}</strong> latency increased by ${latencyPercent}% - may need attention.`;
      } else {
        summary = `📊 <strong>${this.bot.name}</strong> is performing steadily with ${success}% success rate.`;
      }
      
      if (success < 80) {
        summary += ` Low success rate detected - review recent transactions.`;
      }
      
      this.insights = {
        summary: summary,
        lastUpdated: new Date().toLocaleString()
      };
      
      localStorage.setItem(`phoenix:bot:${this.botId}:prevLatency`, latency);
    },
    
    determineStatus(bot) {
      const latency = bot.latency_ms || 0;
      const successRatio = bot.success_ratio || 100;
      const failureCount = bot.failure_count || 0;
      
      if (failureCount > 10 || bot.status === 'error') return 'error';
      if (latency > 200 || successRatio < 80) return 'warning';
      if (latency > 0 || successRatio > 0) return 'active';
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
    
    getStatusEmoji(status) {
      const emojis = { 'active': '🟢', 'warning': '🟡', 'error': '🔴', 'idle': '⚪' };
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
    
    initChart() {
      const ctx = document.getElementById('bot-chart');
      if (!ctx) return;
      
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Latency',
            data: [],
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
            x: { grid: { color: 'rgba(255, 255, 255, 0.1)' } }
          }
        }
      });
      
      this.updateChart();
    },
    
    updateChart() {
      if (!this.chart) return;
      
      // Load chart data for this bot
      fetch('/api/charts/data')
        .then(r => r.json())
        .then(data => {
          const events = (data.events || []).filter(e => 
            e.bot_name && e.bot_name.toLowerCase().replace(/\s+/g, '-') === this.botId
          );
          
          const labels = events.map(e => new Date(e.timestamp).toLocaleTimeString());
          let values = [];
          
          switch (this.selectedChart) {
            case 'latency':
              values = events.map(e => e.latency_ms || 0);
              this.chart.data.datasets[0].label = 'Latency (ms)';
              this.chart.data.datasets[0].borderColor = '#06b6d4';
              break;
            case 'success':
              values = events.map(e => e.success_rate || e.success_ratio || 0);
              this.chart.data.datasets[0].label = 'Success Rate (%)';
              this.chart.data.datasets[0].borderColor = '#10b981';
              break;
            case 'throughput':
              values = events.map((_, i) => i + 1);
              this.chart.data.datasets[0].label = 'Throughput';
              this.chart.data.datasets[0].borderColor = '#f59e0b';
              break;
            case 'profit':
              values = events.map(e => e.profit || 0);
              this.chart.data.datasets[0].label = 'Profit';
              this.chart.data.datasets[0].borderColor = '#8b5cf6';
              break;
          }
          
          this.chart.data.labels = labels;
          this.chart.data.datasets[0].data = values;
          this.chart.update();
        });
    },
    
    saveConfig() {
      const stored = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
      const index = stored.findIndex(b => b.id === this.botId);
      
      if (index > -1) {
        stored[index].address = this.bot.address;
        stored[index].strategy = this.bot.strategy;
      } else {
        stored.push({
          id: this.botId,
          name: this.bot.name,
          address: this.bot.address,
          strategy: this.bot.strategy,
          enabled: true
        });
      }
      
      localStorage.setItem('phoenix:registeredBots', JSON.stringify(stored));
      alert('Configuration saved!');
    },
    
    saveNotes() {
      const stored = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
      const index = stored.findIndex(b => b.id === this.botId);
      
      if (index > -1) {
        stored[index].notes = this.bot.notes;
        stored[index].lastNote = new Date().toISOString();
      }
      
      localStorage.setItem('phoenix:registeredBots', JSON.stringify(stored));
      
      // Count notes this week
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      this.notesThisWeek = stored.filter(b => 
        b.id === this.botId && 
        b.lastNote && 
        new Date(b.lastNote) > weekAgo
      ).length;
    },
    
    restartBot() {
      if (confirm(`Restart ${this.bot.name}?`)) {
        alert(`Would restart ${this.bot.name} (simulated)`);
      }
    },
    
    toggleEnabled() {
      const stored = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
      const index = stored.findIndex(b => b.id === this.botId);
      
      if (index > -1) {
        stored[index].enabled = !stored[index].enabled;
        this.bot.enabled = stored[index].enabled;
        localStorage.setItem('phoenix:registeredBots', JSON.stringify(stored));
      }
    }
  };
}

