import asyncio, os, time, sys
from collections import deque
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Any, Optional

from web3 import Web3
from web3.providers import HTTPProvider

AGG_ABI = [{
    "inputs": [],
    "name": "latestRoundData",
    "outputs": [
        {"internalType": "uint80", "name": "roundId", "type": "uint80"},
        {"internalType": "int256", "name": "answer", "type": "int256"},
        {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
        {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
        {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
    ],
    "stateMutability": "view", "type": "function"
}]

@dataclass
class Metrics:
    avg_latency_ms: float = 0.0
    success_rate_pct: float = 100.0
    throughput_1m: int = 0

class EthRealtime:
    def __init__(self):
        http_url = os.getenv("ETH_HTTP_URL") or os.getenv("ETH_WSS_URL")
        if not http_url:
            raise RuntimeError("ETH_HTTP_URL or ETH_WSS_URL missing")
        
        # Use HTTP provider for compatibility
        self.w3 = Web3(HTTPProvider(http_url))
        
        feed_addr = os.getenv("CHAINLINK_ETHUSD")
        if not feed_addr:
            raise RuntimeError("CHAINLINK_ETHUSD missing")
        # Use to_checksum_address from eth_utils in newer web3 versions
        from eth_utils import to_checksum_address
        self.cl = self.w3.eth.contract(address=to_checksum_address(feed_addr), abi=AGG_ABI)

        self._events_last_min = deque()
        self._lat_samples = deque(maxlen=120)
        self._ok = 0
        self._err = 0
        self._last_block_ts: Optional[int] = None

    def _mark_event(self):
        now = time.time()
        self._events_last_min.append(now)
        cutoff = now - 60.0
        while self._events_last_min and self._events_last_min[0] < cutoff:
            self._events_last_min.popleft()

    def _metrics(self) -> Metrics:
        total = max(1, self._ok + self._err)
        avg_lat = sum(self._lat_samples)/len(self._lat_samples) if self._lat_samples else 0.0
        return Metrics(
            avg_latency_ms=round(avg_lat, 1),
            success_rate_pct=round(self._ok/total*100, 1),
            throughput_1m=len(self._events_last_min),
        )

    async def stream(self) -> AsyncIterator[Dict[str, Any]]:
        last_block_number = None
        try:
            while True:
                try:
                    # Get latest block
                    latest_block = self.w3.eth.get_block('latest')
                    now_ms = time.time()*1000.0
                    
                    # Check if this is a new block
                    if last_block_number is None or latest_block.number > last_block_number:
                        block_ts = latest_block.timestamp
                        if self._last_block_ts is not None:
                            self._lat_samples.append((block_ts - self._last_block_ts)*1000.0)
                        self._last_block_ts = block_ts
                        last_block_number = latest_block.number

                        # Get Chainlink price
                        roundId, answer, startedAt, updatedAt, answeredInRound = self.cl.functions.latestRoundData().call()
                        price = float(answer) / 1e8

                        self._ok += 1
                        self._mark_event()

                        m = self._metrics()
                        yield {
                            "event": "metrics_update",
                            "data": {
                                "timestamp": int(now_ms),
                                "bot_name": "eth-heads",
                                "latency_ms": m.avg_latency_ms,
                                "avg_latency_ms": m.avg_latency_ms,
                                "success_rate_pct": m.success_rate_pct,
                                "throughput_1m": m.throughput_1m,
                                "tx_hash": latest_block.hash.hex(),
                                "price_eth_usd": price,
                                "error": False
                            }
                        }
                    else:
                        # No new block, just wait
                        await asyncio.sleep(1.0)
                        
                except Exception as e:
                    self._err += 1
                    self._mark_event()
                    print(f"[eth_feed] error: {e}", file=sys.stderr)
                    yield {
                        "event": "metrics_update",
                        "data": {
                            "timestamp": int(time.time()*1000.0),
                            "bot_name": "eth-heads",
                            "latency_ms": 0,
                            "avg_latency_ms": 0,
                            "success_rate_pct": self._metrics().success_rate_pct,
                            "throughput_1m": self._metrics().throughput_1m,
                            "tx_hash": "",
                            "price_eth_usd": None,
                            "error": True
                        }
                    }
                    await asyncio.sleep(5.0)
        except Exception as e:
            print(f"[eth_feed] fatal error: {e}", file=sys.stderr)
