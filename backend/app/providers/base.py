"""
Provider abstraction shared by every external data source.

Pattern (per docs/ARCHITECTURE.md):

    External API -> fetch -> validate -> normalize -> cache -> get_status

`resolve()` implements the mandatory fallback chain once, so every domain
provider (environment, water, forest, air_quality, infrastructure, weather,
elevation, geocoding, population, llm) only has to implement fetch/validate/
normalize for its own Live and Mock variants.
"""
from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class SourceStatus(str, Enum):
    """Data honesty classification shown on every metric in the UI (RULE_4)."""

    REAL = "REAL"
    CACHED = "CACHED"
    DERIVED = "DERIVED"
    MODELLED = "MODELLED"
    SIMULATED = "SIMULATED"
    DEMO = "DEMO"


class ConnectionStatus(str, Enum):
    """Provider health, surfaced by GET /api/status."""

    CONNECTED = "CONNECTED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    USING_CACHE = "USING_CACHE"
    USING_DEMO_DATA = "USING_DEMO_DATA"


class ProviderError(Exception):
    """Raised by a Live provider's fetch()/validate() on any recoverable failure."""

    def __init__(self, message: str, status: ConnectionStatus = ConnectionStatus.TEMPORARILY_UNAVAILABLE):
        super().__init__(message)
        self.status = status


@dataclass
class NormalizedResult:
    data: Any
    source_status: SourceStatus
    source_name: str
    retrieved_at: str
    confidence: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["data"] = _to_jsonable(self.data)
        return d


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, Enum):
        return value.value
    return value


class DataProvider(ABC):
    """Base class for every Live/Mock provider."""

    name: str = "unnamed"

    @abstractmethod
    def is_configured(self) -> bool:
        """True if the credentials/config needed for this provider are present."""

    @abstractmethod
    def fetch(self, **params) -> Any:
        """Call the external API / read the source. Raise ProviderError on failure."""

    def validate(self, raw: Any) -> bool:  # noqa: D401 - default permissive
        return raw is not None

    @abstractmethod
    def normalize(self, raw: Any, **params) -> NormalizedResult:
        """Convert raw provider output into a NormalizedResult with the correct SourceStatus."""

    def get_status(self) -> ConnectionStatus:
        return ConnectionStatus.CONNECTED if self.is_configured() else ConnectionStatus.NOT_CONFIGURED


class FileCache:
    """Minimal JSON file cache — enough for a hackathon/demo deployment.

    A production deployment would back this with PostGIS/Redis; the interface
    (get/set) is what matters for swapping it later.
    """

    def __init__(self, cache_dir: str | Path = "app/data/cache", ttl_seconds: int = 6 * 3600):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _path(self, key: str) -> Path:
        safe = key.replace("/", "_").replace(":", "_")
        return self.dir / f"{safe}.json"

    def get(self, key: str) -> NormalizedResult | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - payload["_cached_at"] > self.ttl_seconds:
            return None
        return NormalizedResult(
            data=payload["data"],
            source_status=SourceStatus.CACHED,
            source_name=payload["source_name"],
            retrieved_at=payload["retrieved_at"],
            confidence=payload.get("confidence"),
            notes=payload.get("notes"),
        )

    def set(self, key: str, result: NormalizedResult) -> None:
        payload = result.to_dict()
        payload["_cached_at"] = time.time()
        try:
            self._path(key).write_text(json.dumps(payload, default=str), encoding="utf-8")
        except OSError:
            pass  # caching is best-effort; never fail the request over it


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve(
    *,
    live: DataProvider,
    mock: DataProvider,
    cache: FileCache,
    cache_key: str,
    params: dict | None = None,
) -> tuple[NormalizedResult, ConnectionStatus]:
    """
    The mandatory fallback chain: LIVE -> CACHE -> DEMO.
    Returns (result, connection_status_used) so callers/status endpoints can
    report exactly what happened.
    """
    params = params or {}

    if live.is_configured():
        try:
            raw = live.fetch(**params)
            if live.validate(raw):
                result = live.normalize(raw, **params)
                cache.set(cache_key, result)
                return result, ConnectionStatus.CONNECTED
        except ProviderError:
            pass  # fall through to cache/demo
        except Exception:  # noqa: BLE001 - any unexpected provider failure must not crash the request
            pass

    cached = cache.get(cache_key)
    if cached is not None:
        return cached, ConnectionStatus.USING_CACHE

    raw = mock.fetch(**params)
    result = mock.normalize(raw, **params)
    return result, ConnectionStatus.USING_DEMO_DATA
