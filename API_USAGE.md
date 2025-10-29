# 🔌 API Usage - Live Bot Log Integration

## POST `/api/logs`

Send live JSON log data from your bots to update the dashboard in real-time.

### Request Format

**Endpoint:** `POST https://your-app.onrender.com/api/logs`

**Content-Type:** `text/plain` or `application/json`

**Body:** JSONL (newline-delimited JSON) or JSON array

### Example: JSONL Format

```bash
curl -X POST https://your-app.onrender.com/api/logs \
  -H "Content-Type: text/plain" \
  -d '{"level":20,"timestamp":"2025-10-29T07:30:00Z","message":"price - Started"}
{"level":30,"timestamp":"2025-10-29T07:30:00Z","message":"Request was rate-limited..."}
{"level":20,"timestamp":"2025-10-29T07:30:39Z","message":"Confirmed 0xa92fded92b1aa10f574789cdfc023eb884a0fa3b8a1c18b461eaca671730fb56 (total fees paid = 199865718976)"}'
```

### Example: JSON Array Format

```bash
curl -X POST https://your-app.onrender.com/api/logs \
  -H "Content-Type: application/json" \
  -d '[
    {"level":20,"timestamp":"2025-10-29T07:30:00Z","message":"price - Started"},
    {"level":30,"timestamp":"2025-10-29T07:30:00Z","message":"Request was rate-limited..."},
    {"level":20,"timestamp":"2025-10-29T07:30:39Z","message":"Confirmed 0xabc..."}
  ]'
```

### Response

```json
{
  "status": "success",
  "logs_received": 3,
  "metrics_created": 2
}
```

### What Gets Extracted

The API automatically extracts:

- **Transaction Hashes** - From messages containing `0x...` hex addresses
- **Latency** - From timing messages like `"10.560s (528.0%)"`
- **Bot Names** - Inferred from message patterns (price-bot, rsi-bot, trading-bot, etc.)
- **Status** - From log levels:
  - `level: 20` = OK
  - `level: 21` = OK (with timing)
  - `level: 30` = WARNING
  - `level: 40+` = CRITICAL
- **Fees** - From messages like `"total fees paid = 199865718976"`

### Real-Time Updates

When metrics are extracted, the dashboard automatically:
- ✅ Updates latency charts
- ✅ Updates success rate
- ✅ Adds events to the Recent Events table
- ✅ Broadcasts to all connected SSE clients

### Python Example

```python
import requests
import json

# Your bot logs
logs = [
    {"level": 20, "timestamp": "2025-10-29T07:30:00Z", "message": "price - Started"},
    {"level": 30, "timestamp": "2025-10-29T07:30:00Z", "message": "Request was rate-limited..."},
]

# Send to dashboard
response = requests.post(
    "https://your-app.onrender.com/api/logs",
    data="\n".join(json.dumps(log) for log in logs),
    headers={"Content-Type": "text/plain"}
)

print(response.json())
```

### Integration Tips

1. **Send logs in batches** - Don't send one log at a time
2. **Include timestamps** - Helps with time-based filtering
3. **Use structured messages** - Makes parsing easier
4. **Include transaction hashes** - Gets auto-linked to Etherscan
5. **Send regularly** - Every 5-10 seconds for real-time feel

### Error Handling

The API gracefully handles:
- Invalid JSON - Skips malformed lines
- Missing fields - Uses defaults
- Parsing errors - Returns success with `metrics_created: 0`

Check `metrics_created` in response to see if metrics were extracted.

---

**Ready to integrate?** Just POST your bot logs to `/api/logs` and watch your dashboard update in real-time! 🚀
