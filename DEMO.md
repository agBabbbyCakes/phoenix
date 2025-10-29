# 🎬 BotScope Dashboard - Demo Guide

## Quick Demo for Stakeholders

### 30-Second Setup

1. **Start the server:**
   ```bash
   ./start.sh
   ```
   Or:
   ```bash
   python start.py
   ```

2. **Open in browser:**
   - Main Dashboard: http://localhost:8000
   - Logs Viewer: http://localhost:8000/logs

3. **That's it!** The dashboard automatically loads with demo data.

---

## 🎯 Demo Flow (5 Minutes)

### Part 1: Main Dashboard (2 min)
**URL: http://localhost:8000**

**Show:**
- ✅ **Real-time Metrics**: Latency, Success Rate, Throughput
- ✅ **Live Charts**: Latency trends, throughput over time
- ✅ **Recent Events**: Latest bot transactions with status
- ✅ **Multiple Views**: Switch between latency, throughput, profit, heatmaps

**Key Points:**
- "This is a real-time monitoring dashboard for our Ethereum trading bots"
- "All data updates live every 2 seconds"
- "We can track performance, errors, and profit in real-time"

### Part 2: Logs Viewer (3 min)
**URL: http://localhost:8000/logs**

**Show:**
1. **Click "🎬 Load Demo"** - Instantly loads sample trading logs
2. **Demonstrate Filters:**
   - Search for "trade" or "error"
   - Filter by log level (WARNING, ERROR)
   - Set time ranges
3. **Show Features:**
   - Click transaction hashes → Opens Etherscan
   - Extract structured data from logs
   - Export as JSON/CSV
4. **Saved Queries:**
   - Create a filter → Click "💾 Save Query"
   - Load it from dropdown

**Key Points:**
- "We can analyze any bot logs in a structured way"
- "Transaction hashes are clickable links to Etherscan"
- "Filters and exports make debugging fast"
- "Saved queries save time on repetitive searches"

---

## 🌐 Sharing Options

### Option 1: Local Demo (In-Person)
```bash
./start.sh
```
Show on your laptop. Fastest, works offline.

### Option 2: Network Access (Same Office)
Start with network binding:
```bash
PORT=8000 HOST=0.0.0.0 python start.py
```
Then share: `http://YOUR_IP:8000`

### Option 3: Cloud Deployment (Best for Remote)
Deploy to:
- **Render.com** (see `render.yaml`)
- **Heroku**
- **Railway**
- **Fly.io**

Share the public URL with your boss.

### Option 4: Demo Video
Record a quick screen capture showing:
1. Starting the server
2. Main dashboard with live updates
3. Logs viewer with demo data
4. Filtering and exporting

---

## 📋 Demo Checklist

**Before the demo:**
- [ ] Run `./start.sh` to ensure it starts
- [ ] Test that demo data loads
- [ ] Verify browser opens correctly
- [ ] Have backup: video recording ready

**During the demo:**
- [ ] Show main dashboard first
- [ ] Explain real-time updates
- [ ] Switch to logs viewer
- [ ] Load demo logs
- [ ] Show filtering capabilities
- [ ] Demonstrate export functionality
- [ ] Highlight transaction links

**After the demo:**
- [ ] Provide access (deploy or share locally)
- [ ] Send this guide
- [ ] Answer questions about deployment

---

## 💼 Value Proposition for Boss

### What This Solves:
1. **Real-time Monitoring** - See bot performance as it happens
2. **Faster Debugging** - Logs viewer with filters and export
3. **Better Visibility** - Charts, metrics, and transaction tracking
4. **Team Efficiency** - Shared dashboards and exported reports

### Key Metrics Shown:
- **Latency** - How fast bots respond
- **Success Rate** - Percentage of successful operations
- **Throughput** - Events per minute
- **Profit Tracking** - Cumulative profit over time
- **Error Detection** - Automatic error flagging

### ROI Points:
- **Time Saved**: Quick log analysis vs. grep/awk searches
- **Better Decisions**: Real-time data for faster responses
- **Team Alignment**: Shared view of bot health
- **Debugging Speed**: Filtered, exported logs = faster fixes

---

## 🚀 Deployment for Production

### Quick Deploy to Render.com

1. **Push to GitHub** (if not already)
2. **Go to Render.com** → New Web Service
3. **Connect GitHub** repo
4. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment: `FORCE_SAMPLE=1` (for demo mode)

5. **Deploy** → Get public URL
6. **Share** with team/boss

### Environment Variables for Production:
```bash
FORCE_SAMPLE=1              # Use demo data
SILVERBACK_LOG_PATH=       # Path to real logs (if available)
PORT=8000                  # Server port
```

---

## 📧 Email Template for Sharing

```
Subject: BotScope Dashboard - Live Demo Ready

Hi [Boss Name],

I've set up our bot monitoring dashboard and wanted to share it with you.

Quick Access:
- Local: Run ./start.sh then open http://localhost:8000
- Demo Guide: See DEMO.md for full walkthrough

Features:
✅ Real-time bot performance metrics
✅ Live charts (latency, throughput, profit)
✅ Advanced log viewer with filters
✅ Transaction tracking with Etherscan links
✅ Export capabilities for reports

The dashboard runs with demo data so you can explore all features.

Let me know if you'd like a walkthrough or if you have questions!

Best,
[Your Name]
```

---

## 🎥 Screen Recording Script

**Record this sequence (2-3 minutes):**

1. **Terminal:** Show `./start.sh` command
2. **Browser:** Open dashboard, show live updates
3. **Navigate to logs:** Click "View All Logs" button
4. **Load demo:** Click "🎬 Load Demo"
5. **Filter:** Show search, level filter
6. **Export:** Show JSON/CSV export
7. **Transaction links:** Click a hash, show Etherscan

**Narrate:**
- "This is our real-time bot monitoring dashboard..."
- "Here we can view and analyze logs..."
- "Filters make it easy to find specific issues..."
- "Transaction hashes link directly to Etherscan..."

---

## 🔗 Quick Links Reference

- **Main Dashboard**: http://localhost:8000
- **Logs Viewer**: http://localhost:8000/logs
- **Daily Report**: http://localhost:8000/report
- **Health Check**: http://localhost:8000/health

---

## ❓ FAQ for Demo

**Q: Does this work with our real bot data?**  
A: Yes! Set `SILVERBACK_LOG_PATH` environment variable to point to your log files.

**Q: Can multiple people access it?**  
A: Yes, deploy to a server or use `HOST=0.0.0.0` for network access.

**Q: How do we customize it?**  
A: Modify templates, add new metrics in `app/data.py`, extend the logs viewer.

**Q: Is it production-ready?**  
A: Core features are solid. Add authentication/authorization for production use.

**Q: What data does it show?**  
A: By default, it shows realistic demo data. Configure with real log paths for live data.

---

**Ready to demo?** Run `./start.sh` and open http://localhost:8000! 🚀
