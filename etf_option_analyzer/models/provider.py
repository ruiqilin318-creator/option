from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
import csv
import json

from .market import MarketSnapshot


class MarketDataProvider(ABC):
    """Provider adapter contract; concrete sources must normalize data to MarketSnapshot."""

    name: str

    @abstractmethod
    def fetch_snapshot(self, symbol: str) -> MarketSnapshot:
        raise NotImplementedError


class SnapshotCache:
    def __init__(self, root: str | Path = ".cache/snapshots") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot: MarketSnapshot) -> Path:
        path = self.root / f"{snapshot.underlying.symbol}_{snapshot.fetched_at:%Y%m%d_%H%M%S}_{snapshot.provider_name}.json"
        path.write_text(json.dumps(_snapshot_to_dict(snapshot), ensure_ascii=False, default=str, indent=2), encoding="utf-8")
        return path


class CsvOfflineProvider(MarketDataProvider):
    """Offline adapter placeholder for deterministic CSV snapshots."""

    name = "csv_offline"

    def __init__(self, snapshot_loader) -> None:
        self._snapshot_loader = snapshot_loader

    def fetch_snapshot(self, symbol: str) -> MarketSnapshot:
        return self._snapshot_loader(symbol)


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _snapshot_to_dict(snapshot: MarketSnapshot) -> dict:
    return {
        "provider_name": snapshot.provider_name,
        "fetched_at": snapshot.fetched_at.isoformat(),
        "underlying": snapshot.underlying.__dict__,
        "history": [row.__dict__ for row in snapshot.history],
        "expiries": [d.isoformat() for d in snapshot.expiries],
        "chains": [
            {"symbol": c.symbol, "expiry": c.expiry.isoformat(), "calls": [o.__dict__ for o in c.calls], "puts": [o.__dict__ for o in c.puts], "meta": c.meta.__dict__}
            for c in snapshot.chains
        ],
        "conflicts": snapshot.conflicts,
    }
