import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.controller import Controller


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        controller = Controller()
        controller.run()
        return 0
    except Exception:
        logging.exception("Run failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
