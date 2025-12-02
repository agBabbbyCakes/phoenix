// Bot Explorer Component - Yahoo Finance / Fidelity Style
function botExplorerState() {
  return {
    // State
    bots: [],
    filteredBots: [],
    searchQuery: '',
    sortBy: 'name',
    sortOrder: 'asc',
    selectedCategory: 'all',
    showRentModal: false,
    selectedBot: null,
    selectedPaymentMethod: 'Credit Card',
    favorites: JSON.parse(localStorage.getItem('phoenix:botFavorites') || '[]'),
    watchlist: JSON.parse(localStorage.getItem('phoenix:botWatchlist') || '[]'),
    savedBots: JSON.parse(localStorage.getItem('phoenix:savedBots') || '[]'),
    rentedBots: JSON.parse(localStorage.getItem('phoenix:rentedBots') || '[]'),
    
    // View modes
    viewMode: localStorage.getItem('phoenix:botExplorerView') || 'list', // list, grid, compact
    
    // Filters
    statusFilter: 'all', // all, active, warning, error, idle
    strategyFilter: 'all',
    priceRange: [0, 10000],
    
    // Pagination
    currentPage: 1,
    itemsPerPage: 20,
    
    // Categories
    categories: {
      'all': 'All Bots',
      'arbitrage': 'Arbitrage',
      'mev': 'MEV',
      'trading': 'Trading',
      'monitoring': 'Monitoring',
      'defi': 'DeFi',
      'nft': 'NFT',
      'rented': 'My Rentals',
      'favorites': 'Favorites'
    },
    
    // KPIs and Health Summary
    kpis: {
      avg_latency_ms: 0,
      success_rate_pct: 0,
      throughput_1m: 0
    },
    healthSummary: {
      ok: 0,
      slow: 0,
      error: 0
    },
    
    init() {
      this.loadBots();
      this.loadKPIs();
      this.loadHealthSummary();
      this.setupAutoRefresh();
    },
    
    async loadKPIs() {
      try {
        const response = await fetch('/api/charts/data');
        const data = await response.json();
        if (data.kpis) {
          this.kpis = data.kpis;
          this.updateSidebarStats();
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
        
        this.updateSidebarHealth();
      } catch (e) {
        console.error('Failed to load health summary', e);
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
    
    updateSidebarHealth() {
      const okEl = document.getElementById('sidebar-health-ok');
      const slowEl = document.getElementById('sidebar-health-slow');
      const errorEl = document.getElementById('sidebar-health-error');
      
      if (okEl) okEl.textContent = (this.healthSummary.ok || 0);
      if (slowEl) slowEl.textContent = (this.healthSummary.slow || 0);
      if (errorEl) errorEl.textContent = (this.healthSummary.error || 0);
    },
    
    async loadBots() {
      try {
        // Load from API
        const response = await fetch('/api/bots/status');
        const data = await response.json();
        const apiBots = data.bots || [];
        
        // Load stored bots (localStorage for now)
        const storedBots = JSON.parse(localStorage.getItem('phoenix:registeredBots') || '[]');
        
        // Merge and enrich bot data
        this.bots = apiBots.map(apiBot => {
          const stored = storedBots.find(b => b.name === apiBot.bot_name);
          const botId = apiBot.bot_name.toLowerCase().replace(/\s+/g, '-');
          
          // Determine rental status
          const rental = this.rentedBots.find(r => r.botId === botId);
          const isRented = rental && new Date(rental.expiresAt) > new Date();
          
          return {
            id: botId,
            name: apiBot.bot_name,
            symbol: this.getBotSymbol(apiBot.bot_name),
            status: this.determineStatus(apiBot),
            avg_latency: apiBot.latency_ms || 0,
            success_rate: apiBot.success_ratio || 0,
            strategy: stored?.strategy || this.inferStrategy(apiBot.bot_name),
            category: this.getCategory(stored?.strategy || this.inferStrategy(apiBot.bot_name)),
            address: stored?.address || '',
            enabled: stored?.enabled !== false,
            uptime: this.calculateUptime(apiBot.last_heartbeat),
            last_heartbeat: apiBot.last_heartbeat,
            
            // Performance metrics
            performance_24h: this.calculatePerformance24h(apiBot),
            performance_7d: this.calculatePerformance7d(apiBot),
            volume_24h: this.calculateVolume24h(apiBot),
            
            // Rental info
            isRented: isRented,
            rentalPrice: this.getRentalPrice(apiBot.bot_name, stored?.strategy),
            rentalPriceDaily: this.getRentalPriceDaily(apiBot.bot_name, stored?.strategy),
            rentalPriceMonthly: this.getRentalPriceMonthly(apiBot.bot_name, stored?.strategy),
            rentalStatus: isRented ? rental.status : 'available',
            rentalExpiresAt: isRented ? rental.expiresAt : null,
            
            // Social metrics
            isFavorite: this.favorites.includes(botId),
            isInWatchlist: this.watchlist.includes(botId),
            isSaved: this.savedBots.some(s => s.id === botId || s.name === apiBot.bot_name),
            rating: stored?.rating || this.calculateRating(apiBot),
            reviews: stored?.reviews || Math.floor(Math.random() * 50) + 5,
            
            // Additional metadata
            description: stored?.description || this.getDefaultDescription(apiBot.bot_name),
            tags: stored?.tags || this.getDefaultTags(apiBot.bot_name),
            creator: stored?.creator || 'Community',
            createdAt: stored?.createdAt || new Date().toISOString()
          };
        });
        
        // Add stored bots not in API
        storedBots.forEach(stored => {
          if (!this.bots.find(b => b.id === stored.id || b.name === stored.name)) {
            const botId = stored.id || stored.name.toLowerCase().replace(/\s+/g, '-');
            const rental = this.rentedBots.find(r => r.botId === botId);
            const isRented = rental && new Date(rental.expiresAt) > new Date();
            
            this.bots.push({
              id: botId,
              name: stored.name,
              symbol: this.getBotSymbol(stored.name),
              status: 'idle',
              avg_latency: 0,
              success_rate: 0,
              strategy: stored.strategy || 'unknown',
              category: this.getCategory(stored.strategy || 'unknown'),
              address: stored.address || '',
              enabled: stored.enabled !== false,
              uptime: 'N/A',
              last_heartbeat: null,
              performance_24h: 0,
              performance_7d: 0,
              volume_24h: 0,
              isRented: isRented,
              rentalPrice: this.getRentalPrice(stored.name, stored.strategy),
              rentalPriceDaily: this.getRentalPriceDaily(stored.name, stored.strategy),
              rentalPriceMonthly: this.getRentalPriceMonthly(stored.name, stored.strategy),
              rentalStatus: isRented ? rental.status : 'available',
              rentalExpiresAt: isRented ? rental.expiresAt : null,
              isFavorite: this.favorites.includes(botId),
              isInWatchlist: this.watchlist.includes(botId),
              isSaved: this.savedBots.some(s => s.id === botId || s.name === stored.name),
              rating: stored?.rating || 4.0,
              reviews: stored?.reviews || 0,
              description: stored?.description || '',
              tags: stored?.tags || [],
              creator: stored?.creator || 'Community',
              createdAt: stored?.createdAt || new Date().toISOString()
            });
          }
        });
        
        this.applyFilters();
      } catch (e) {
        console.error('Failed to load bots', e);
      }
    },
    
    setupAutoRefresh() {
      setInterval(() => {
        this.loadBots();
        this.loadKPIs();
        this.loadHealthSummary();
      }, 5000);
    },
    
    getBotSymbol(name) {
      // Generate symbol from bot name (like stock tickers)
      const words = name.split(/[\s-]+/);
      if (words.length >= 2) {
        return (words[0].substring(0, 2) + words[1].substring(0, 2)).toUpperCase();
      }
      return name.substring(0, 4).toUpperCase();
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
    
    inferStrategy(botName) {
      const name = botName.toLowerCase();
      if (name.includes('arb') || name.includes('arbitrage')) return 'arbitrage';
      if (name.includes('mev')) return 'mev';
      if (name.includes('trade') || name.includes('snipe')) return 'trading';
      if (name.includes('monitor') || name.includes('watch')) return 'monitoring';
      if (name.includes('defi') || name.includes('liquidity')) return 'defi';
      if (name.includes('nft')) return 'nft';
      return 'other';
    },
    
    getCategory(strategy) {
      const categoryMap = {
        'arbitrage': 'arbitrage',
        'mev': 'mev',
        'trading': 'trading',
        'monitoring': 'monitoring',
        'defi': 'defi',
        'nft': 'nft'
      };
      return categoryMap[strategy] || 'all';
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
        
        if (diffDays > 0) return `${diffDays}d`;
        if (diffHours > 0) return `${diffHours}h`;
        return `${diffMins}m`;
      } catch (e) {
        return 'N/A';
      }
    },
    
    calculatePerformance24h(bot) {
      // Simulated performance calculation
      const base = bot.success_ratio || 50;
      return (Math.random() * 20 - 10 + base).toFixed(2);
    },
    
    calculatePerformance7d(bot) {
      const base = bot.success_ratio || 50;
      return (Math.random() * 30 - 15 + base).toFixed(2);
    },
    
    calculateVolume24h(bot) {
      // Simulated volume
      return Math.floor(Math.random() * 1000000) + 10000;
    },
    
    calculateRating(bot) {
      // Calculate rating based on performance
      const successRate = bot.success_ratio || 0;
      const latency = bot.latency_ms || 500;
      
      let rating = 3.0;
      if (successRate > 95 && latency < 200) rating = 5.0;
      else if (successRate > 90 && latency < 300) rating = 4.5;
      else if (successRate > 85 && latency < 400) rating = 4.0;
      else if (successRate > 80) rating = 3.5;
      else if (successRate > 70) rating = 3.0;
      else rating = 2.5;
      
      return parseFloat(rating.toFixed(1));
    },
    
    getRentalPrice(botName, strategy) {
      // Base pricing on strategy and performance
      const basePrices = {
        'arbitrage': 0.5,
        'mev': 0.8,
        'trading': 0.6,
        'monitoring': 0.3,
        'defi': 0.7,
        'nft': 0.4
      };
      return basePrices[strategy] || 0.5;
    },
    
    getRentalPriceDaily(botName, strategy) {
      return this.getRentalPrice(botName, strategy) * 24;
    },
    
    getRentalPriceMonthly(botName, strategy) {
      return this.getRentalPrice(botName, strategy) * 24 * 30;
    },
    
    getDefaultDescription(botName) {
      const descriptions = {
        'arb-scout': 'Advanced arbitrage detection bot with multi-DEX support',
        'mev-watch': 'MEV opportunity scanner and executor',
        'tx-relay': 'High-speed transaction relay service',
        'eth-sniper': 'Ethereum token sniper with gas optimization'
      };
      return descriptions[botName.toLowerCase()] || 'Professional trading bot';
    },
    
    getDefaultTags(botName) {
      const name = botName.toLowerCase();
      const tags = [];
      if (name.includes('arb')) tags.push('arbitrage', 'defi');
      if (name.includes('mev')) tags.push('mev', 'advanced');
      if (name.includes('trade')) tags.push('trading', 'automated');
      if (name.includes('snipe')) tags.push('sniping', 'fast');
      return tags.length > 0 ? tags : ['trading', 'automated'];
    },
    
    // Filtering and sorting
    applyFilters() {
      let filtered = [...this.bots];
      
      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(bot => 
          bot.name.toLowerCase().includes(query) ||
          bot.symbol.toLowerCase().includes(query) ||
          bot.strategy.toLowerCase().includes(query) ||
          bot.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
      
      // Category filter
      if (this.selectedCategory === 'favorites') {
        filtered = filtered.filter(bot => bot.isFavorite);
      } else if (this.selectedCategory === 'rented') {
        filtered = filtered.filter(bot => bot.isRented);
      } else if (this.selectedCategory !== 'all') {
        filtered = filtered.filter(bot => bot.category === this.selectedCategory);
      }
      
      // Status filter
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(bot => bot.status === this.statusFilter);
      }
      
      // Strategy filter
      if (this.strategyFilter !== 'all') {
        filtered = filtered.filter(bot => bot.strategy === this.strategyFilter);
      }
      
      // Sort
      filtered.sort((a, b) => {
        let aVal = a[this.sortBy];
        let bVal = b[this.sortBy];
        
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase();
          bVal = bVal.toLowerCase();
        }
        
        if (this.sortOrder === 'asc') {
          return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
        } else {
          return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
        }
      });
      
      this.filteredBots = filtered;
    },
    
    sort(column) {
      if (this.sortBy === column) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = column;
        this.sortOrder = 'asc';
      }
      this.applyFilters();
    },
    
    toggleFavorite(botId) {
      const index = this.favorites.indexOf(botId);
      if (index > -1) {
        this.favorites.splice(index, 1);
      } else {
        this.favorites.push(botId);
      }
      localStorage.setItem('phoenix:botFavorites', JSON.stringify(this.favorites));
      this.loadBots();
    },
    
    toggleWatchlist(botId) {
      const index = this.watchlist.indexOf(botId);
      if (index > -1) {
        this.watchlist.splice(index, 1);
      } else {
        this.watchlist.push(botId);
      }
      localStorage.setItem('phoenix:botWatchlist', JSON.stringify(this.watchlist));
      this.loadBots();
    },
    
    saveBot(bot) {
      const savedBot = {
        id: bot.id,
        name: bot.name,
        symbol: bot.symbol,
        strategy: bot.strategy,
        savedAt: new Date().toISOString(),
        notes: ''
      };
      
      const existingIndex = this.savedBots.findIndex(s => s.id === bot.id);
      if (existingIndex > -1) {
        this.savedBots[existingIndex] = savedBot;
      } else {
        this.savedBots.push(savedBot);
      }
      
      localStorage.setItem('phoenix:savedBots', JSON.stringify(this.savedBots));
      this.loadBots();
      
      // Show notification
      this.showNotification(`Bot "${bot.name}" saved!`);
    },
    
    showNotification(message) {
      // Simple notification - can be enhanced
      const notification = document.createElement('div');
      notification.className = 'fixed top-20 right-6 bg-cyan-500/20 border border-cyan-500/50 backdrop-blur-xl rounded-lg px-4 py-2 text-sm text-cyan-400 z-50';
      notification.textContent = message;
      document.body.appendChild(notification);
      setTimeout(() => notification.remove(), 3000);
    },
    
    saveBot(bot) {
      const savedBots = JSON.parse(localStorage.getItem('phoenix:savedBots') || '[]');
      const existingIndex = savedBots.findIndex(b => b.id === bot.id);
      
      if (existingIndex > -1) {
        savedBots.splice(existingIndex, 1);
        alert(`${bot.name} removed from saved bots`);
      } else {
        savedBots.push({
          id: bot.id,
          name: bot.name,
          symbol: bot.symbol,
          strategy: bot.strategy,
          savedAt: new Date().toISOString()
        });
        alert(`${bot.name} saved!`);
      }
      
      localStorage.setItem('phoenix:savedBots', JSON.stringify(savedBots));
    },
    
    openRentModal(bot) {
      this.selectedBot = bot;
      this.showRentModal = true;
    },
    
    async rentBot(bot, duration, paymentMethod) {
      try {
        // Map payment method
        const paymentMethodMap = {
          'Credit Card': 'credit_card',
          'Crypto (ETH/USDC)': 'crypto',
          'PayPal': 'paypal'
        };
        
        const rentalRequest = {
          bot_id: bot.id,
          duration: duration,
          payment_method: paymentMethodMap[paymentMethod] || 'credit_card'
        };
        
        // Call API endpoint
        const response = await fetch('/api/bots/rent', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(rentalRequest)
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.rental) {
          const rental = {
            id: data.rental.id,
            botId: bot.id,
            botName: bot.name,
            duration: duration,
            price: data.rental.price,
            paymentMethod: paymentMethod,
            status: data.rental.status,
            rentedAt: data.rental.rented_at,
            expiresAt: data.rental.expires_at
          };
          
          // Add to rented bots
          const existingIndex = this.rentedBots.findIndex(r => r.botId === bot.id);
          if (existingIndex > -1) {
            this.rentedBots[existingIndex] = rental;
          } else {
            this.rentedBots.push(rental);
          }
          
          localStorage.setItem('phoenix:rentedBots', JSON.stringify(this.rentedBots));
          
          this.showRentModal = false;
          this.selectedBot = null;
          this.loadBots();
          
          alert(`Successfully rented ${bot.name} for ${duration}!`);
        } else {
          throw new Error(data.message || 'Failed to rent bot');
        }
      } catch (e) {
        console.error('Failed to rent bot', e);
        alert('Failed to rent bot. Please try again.');
      }
    },
    
    calculateExpiry(duration) {
      const now = new Date();
      if (duration === 'hourly') {
        now.setHours(now.getHours() + 1);
      } else if (duration === 'daily') {
        now.setDate(now.getDate() + 1);
      } else if (duration === 'monthly') {
        now.setMonth(now.getMonth() + 1);
      }
      return now.toISOString();
    },
    
    getStatusColor(status) {
      const colors = {
        'active': 'text-emerald-400',
        'warning': 'text-yellow-400',
        'error': 'text-red-400',
        'idle': 'text-gray-400'
      };
      return colors[status] || 'text-gray-400';
    },
    
    getStatusIcon(status) {
      const icons = {
        'active': '🟢',
        'warning': '🟡',
        'error': '🔴',
        'idle': '⚪'
      };
      return icons[status] || '⚪';
    },
    
    formatPrice(price) {
      return `$${price.toFixed(2)}`;
    },
    
    formatPerformance(value) {
      const sign = value >= 0 ? '+' : '';
      const color = value >= 0 ? 'text-emerald-400' : 'text-red-400';
      return { value: `${sign}${value}%`, color };
    },
    
    getStatusClass(status) {
      const classes = {
        'active': 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
        'warning': 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
        'error': 'text-red-400 border-red-500/30 bg-red-500/10',
        'idle': 'text-gray-400 border-gray-500/30 bg-gray-500/10'
      };
      return classes[status] || classes.idle;
    }
  };
}

