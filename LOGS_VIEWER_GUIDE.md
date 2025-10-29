# Logs Viewer Guide

## What Your App Does

**BotScope** is a real-time monitoring dashboard for Ethereum trading bots. It tracks:

- **Performance Metrics**: Latency, success rate, throughput per minute
- **Profit Tracking**: Cumulative profit from bot operations
- **Transaction Monitoring**: Live transaction hashes with Etherscan links
- **Log Analysis**: Structured JSON log viewing and debugging
- **Visualizations**: Charts, heatmaps, and 3D network graphs

## How to Demo the Logs Viewer

### Quick Demo
1. Start the server:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

2. Navigate to: `http://localhost:8000/logs`

3. Click **"🎬 Load Demo"** button - this loads sample trading bot logs with:
   - Price fetching operations
   - RSI calculations
   - Trade executions
   - Transaction confirmations
   - Rate limiting warnings

### Manual Demo
1. Paste your JSON logs into the textarea (newline-delimited or JSON array format)
2. Click **"Parse & Display"**
3. Use filters to explore:
   - Search for specific messages
   - Filter by log level (INFO, WARNING, ERROR)
   - Set time ranges
   - Save frequent queries

## Habit-Building Features

### 1. **Saved Queries** 💾
- Save frequently used filter combinations
- Quick access dropdown for common searches
- Store: search terms, log levels, time ranges
- Usage: Filter logs → Click "💾 Save Query" → Name it → Load anytime

### 2. **Export Functionality** 📥
- Export filtered logs as JSON or CSV
- Share findings with your team
- Archive important debugging sessions
- Usage: Filter logs → Click "📥 Export JSON" or "📥 Export CSV"

### 3. **Quick Navigation** 🔗
- Click transaction hashes → Opens Optimistic Etherscan
- Auto-detects transaction URLs in messages
- Extracts structured data from brackets (e.g., `[metric=price]`)

### 4. **Statistics Dashboard** 📊
- Real-time counts: Total logs, INFO, WARNING, ERROR, Transactions
- Visual feedback on log distribution
- Helps identify patterns quickly

### 5. **Search History** (Coming Soon)
- LocalStorage remembers your searches
- Quick re-run of previous queries

## Building Daily Habits

### Morning Routine
1. **Check Dashboard** (`/`) - Review overnight bot performance
2. **Review Logs** (`/logs`) - Click "Load Demo" or paste overnight logs
3. **Filter for Errors** - Set level filter to "ERROR" or "WARNING"
4. **Export Findings** - Save CSV for your morning report

### Debugging Workflow
1. **Reproduce Issue** - Filter logs by time range around the incident
2. **Search for Keywords** - Find specific bot names or error messages
3. **Save Query** - Name it after the issue (e.g., "rate-limit errors")
4. **Share Export** - Send JSON/CSV to team members

### Weekly Review
1. **Export All Logs** - Get full week's data
2. **Analyze Trends** - Look for patterns in warning/error counts
3. **Update Saved Queries** - Refine based on what you learned
4. **Check Statistics** - Compare week-over-week metrics

## Integration Tips

### Link from Main Dashboard
The main dashboard (`/`) already has a "📋 View All Logs" button in the Recent Events section.

### Custom Sample Data
Replace `/static/data/sample_logs.json` with your own sample data to customize the demo.

### Browser Bookmarks
Bookmark common queries by saving them, then bookmarking the logs page with query parameters (future feature).

## Future Enhancements

Consider adding:
- **Daily/Weekly Email Summaries** - Automated reports sent to your inbox
- **Alert Thresholds** - Browser notifications for critical errors
- **Dashboard Widgets** - Quick stats on the main page
- **Collaborative Features** - Share saved queries with team
- **Timeline View** - Visual timeline of events
- **Pattern Detection** - Auto-identify common error patterns

## Tips for Adoption

1. **Start Small**: Use the demo button to explore first
2. **Save Common Queries**: Create 3-5 saved queries for your most frequent needs
3. **Export Regularly**: Build a habit of exporting interesting findings
4. **Check Daily**: Make logs viewer part of your morning routine
5. **Share Findings**: Use exports to discuss issues with your team

---

**Remember**: Habits form through repetition. Use the saved queries feature to make your common workflows one-click easy!
