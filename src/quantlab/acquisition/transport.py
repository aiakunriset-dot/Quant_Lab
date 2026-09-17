from __future__ import annotations

import logging
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

from .retry import RetryPolicy, backoff_seconds, is_retryable_status

LOGGER = logging.getLogger(__name__)


class NoDataError(Exception):
    """Raised when Dukascopy reports a missing historical chunk."""


class TransportError(Exception):
    """Raised when a transport operation fails permanently."""


@dataclass(frozen=True, slots=True)
class TransportConfig:
    """HTTP transport configuration with certificate verification enabled."""

    timeout_seconds: float = 60.0
    user_agent: str = "Quant_Lab/0.1"
    retry_policy: RetryPolicy = RetryPolicy()

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")


@dataclass(frozen=True, slots=True)
class DownloadResponse:
    """Successful raw HTTP response payload."""

    status_code: int
    body: bytes


class DukascopyTransport:
    """TLS-verified, bounded-retry transport for Dukascopy raw files."""

    def __init__(
        self,
        config: TransportConfig | None = None,
        opener: Callable[..., object] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config or TransportConfig()
        self._opener = opener or urllib.request.urlopen
        self._sleeper = sleeper

    def fetch(self, url: str) -> DownloadResponse:
        """Fetch a URL, classifying missing data separately from transport failure."""
        headers = {"User-Agent": self.config.user_agent}
        context = ssl.create_default_context()
        last_error: Exception | None = None
        for attempt in range(self.config.retry_policy.attempts):
            request = urllib.request.Request(url, headers=headers, method="GET")
            try:
                with self._opener(request, timeout=self.config.timeout_seconds, context=context) as response:  # type: ignore[arg-type]
                    status = int(response.status)
                    body = response.read()
                    if status == 404:
                        raise NoDataError(url)
                    if status != 200:
                        if is_retryable_status(status):
                            raise urllib.error.HTTPError(url, status, "retryable", None, None)
                        raise TransportError(f"HTTP {status} for {url}")
                    return DownloadResponse(status, body)
            except NoDataError:
                raise
            except (urllib.error.HTTPError, TimeoutError, OSError) as exc:
                last_error = exc
                if attempt + 1 >= self.config.retry_policy.attempts:
                    break
                delay = backoff_seconds(self.config.retry_policy, attempt + 1)
                LOGGER.warning("Retrying %s after %.2fs: %s", url, delay, exc)
                self._sleeper(delay)
        raise TransportError(f"Failed to fetch {url}: {last_error}") from last_error
