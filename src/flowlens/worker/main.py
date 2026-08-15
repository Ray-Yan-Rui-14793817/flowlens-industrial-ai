"""Minimal long-running worker placeholder."""

import logging
import signal
from threading import Event
from types import FrameType

from flowlens.config import Settings, get_settings

LOGGER = logging.getLogger(__name__)


def run_worker(settings: Settings, stop_event: Event) -> None:
    """Log startup and wait efficiently until shutdown is requested."""

    LOGGER.info(
        "FlowLens worker started (environment=%s)",
        settings.app_environment,
    )
    stop_event.wait()
    LOGGER.info("FlowLens worker stopped")


def main() -> None:
    """Load canonical settings and run the placeholder until termination."""

    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    stop_event = Event()

    def request_stop(signum: int, frame: FrameType | None) -> None:
        del signum, frame
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    run_worker(settings, stop_event)


if __name__ == "__main__":
    main()
