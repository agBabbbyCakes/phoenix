/**
 * BotHealthTable Component
 * Renders bot health status with bot name, last heartbeat, success ratio, 
 * failure count, last block, and color-coded status.
 * Fetches from /api/bots/status and sorts by latency descending.
 */

class BotHealthTable {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = null;
    this.options = {
      refreshInterval: options.refreshInterval || 5000, // 5 seconds default
      apiEndpoint: options.apiEndpoint || '/api/bots/status',
      ...options
    };
    this.bots = [];
    this.refreshTimer = null;
  }

  /**
   * Initialize the component
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`BotHealthTable: Container #${this.containerId} not found`);
      return;
    }

    this.render();
    this.fetchData();
    
    // Set up auto-refresh
    if (this.options.refreshInterval > 0) {
      this.refreshTimer = setInterval(() => {
        this.fetchData();
      }, this.options.refreshInterval);
    }
  }

  /**
   * Fetch bot status data from API
   */
  async fetchData() {
    try {
      const response = await fetch(this.options.apiEndpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      this.bots = data.bots || data || [];
      this.render();
    } catch (error) {
      console.error('BotHealthTable: Failed to fetch bot status', error);
      this.renderError(error.message);
    }
  }

  /**
   * Get status emoji based on bot health
   */
  getStatusEmoji(bot) {
    // Status can be: 'healthy', 'warning', 'error', or based on conditions
    const status = bot.status || this.determineStatus(bot);
    
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'ok':
      case 'active':
        return '🟢';
      case 'warning':
      case 'degraded':
        return '🟡';
      case 'error':
      case 'down':
      case 'inactive':
        return '🔴';
      default:
        return '⚪'; // Unknown
    }
  }

  /**
   * Determine status based on bot metrics
   */
  determineStatus(bot) {
    // Check if bot hasn't sent heartbeat recently (more than 60 seconds)
    const now = Date.now();
    const lastHeartbeat = bot.last_heartbeat ? new Date(bot.last_heartbeat).getTime() : 0;
    const heartbeatAge = (now - lastHeartbeat) / 1000; // seconds

    if (heartbeatAge > 120) {
      return 'error';
    } else if (heartbeatAge > 60) {
      return 'warning';
    }

    // Check success ratio
    const successRatio = bot.success_ratio || 0;
    if (successRatio < 50) {
      return 'error';
    } else if (successRatio < 80) {
      return 'warning';
    }

    // Check failure count
    const failureCount = bot.failure_count || 0;
    if (failureCount > 10) {
      return 'warning';
    }
    if (failureCount > 50) {
      return 'error';
    }

    return 'healthy';
  }

  /**
   * Format timestamp for display
   */
  formatTimestamp(timestamp) {
    if (!timestamp) return 'Never';
    
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);

      if (diffSec < 60) {
        return `${diffSec}s ago`;
      } else if (diffMin < 60) {
        return `${diffMin}m ago`;
      } else if (diffHour < 24) {
        return `${diffHour}h ago`;
      } else {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      }
    } catch (e) {
      return 'Invalid';
    }
  }

  /**
   * Format percentage
   */
  formatPercent(value) {
    if (value == null) return '-';
    return `${value.toFixed(1)}%`;
  }

  /**
   * Format block number
   */
  formatBlock(block) {
    if (!block) return '-';
    return typeof block === 'number' ? block.toLocaleString() : String(block);
  }

  /**
   * Render the table
   */
  render() {
    if (!this.container) return;

    // Sort by latency descending (highest first)
    const sortedBots = [...this.bots].sort((a, b) => {
      const latencyA = a.latency_ms || a.latency || 0;
      const latencyB = b.latency_ms || b.latency || 0;
      return latencyB - latencyA;
    });

    const tableHTML = `
      <div class="overflow-x-auto">
        <table class="table table-compact w-full glass-event-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Bot Name</th>
              <th>Last Heartbeat</th>
              <th>Success Ratio</th>
              <th>Failure Count</th>
              <th>Last Block</th>
              <th>Latency (ms)</th>
            </tr>
          </thead>
          <tbody>
            ${sortedBots.length === 0 ? `
              <tr>
                <td colspan="7" class="text-center text-gray-500 py-8">
                  No bot data available
                </td>
              </tr>
            ` : sortedBots.map(bot => `
              <tr class="hover:bg-primary/10">
                <td class="text-center">${this.getStatusEmoji(bot)}</td>
                <td class="font-semibold">${bot.bot_name || bot.name || 'Unknown'}</td>
                <td class="text-sm">${this.formatTimestamp(bot.last_heartbeat)}</td>
                <td class="text-sm">${this.formatPercent(bot.success_ratio)}</td>
                <td class="text-sm">${bot.failure_count || 0}</td>
                <td class="font-mono text-sm">${this.formatBlock(bot.last_block)}</td>
                <td class="font-mono text-sm">${bot.latency_ms || bot.latency || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    this.container.innerHTML = tableHTML;
  }

  /**
   * Render error state
   */
  renderError(message) {
    if (!this.container) return;
    
    this.container.innerHTML = `
      <div class="alert alert-error">
        <span>Failed to load bot status: ${message}</span>
      </div>
    `;
  }

  /**
   * Destroy the component and clean up
   */
  destroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BotHealthTable;
}

// Auto-initialize if data attribute is present
document.addEventListener('DOMContentLoaded', () => {
  const containers = document.querySelectorAll('[data-bot-health-table]');
  containers.forEach(container => {
    const containerId = container.id || `bot-health-table-${Date.now()}`;
    if (!container.id) {
      container.id = containerId;
    }
    
    const refreshInterval = container.dataset.refreshInterval 
      ? parseInt(container.dataset.refreshInterval, 10) 
      : 5000;
    
    const apiEndpoint = container.dataset.apiEndpoint || '/api/bots/status';
    
    const table = new BotHealthTable(containerId, {
      refreshInterval,
      apiEndpoint
    });
    table.init();
    
    // Store instance for potential cleanup
    container._botHealthTable = table;
  });
});





