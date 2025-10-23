import requests
with requests.get("http://localhost:8000/stream", stream=True, headers={"Accept": "text/event-stream"}) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode())
