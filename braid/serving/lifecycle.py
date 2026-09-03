"""Server lifecycle management: graceful start/stop."""

from __future__ import annotations

import signal
from typing import Any

from braid.core.logging import getlogger


class lifecycleserver:
    """Wraps a serve-loop with graceful shutdown semantics."""

    def __init__(self, server: Any) -> None:
        self.server = server
        self._stop = False
        self._log = getlogger("braid.serving.lifecycle")

    def installsignals(self) -> None:
        """Trap SIGTERM/SIGINT for graceful shutdown."""
        signal.signal(signal.SIGTERM, lambda *_: self._requeststop())
        signal.signal(signal.SIGINT, lambda *_: self._requeststop())

    def _requeststop(self) -> None:
        self._stop = True
        try:
            self.server.shutdown()
        except Exception:  # noqa: BLE001
            pass
        self._log.info("server.shutdown.requested")

    def wait(self) -> None:
        """Block until stop is requested."""
        while not self._stop:
            signal.pause()
