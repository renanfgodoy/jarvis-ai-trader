from __future__ import annotations

import sys

from tools.pocket_discovery.report_generator import generate_pocket_discovery_reports

DEFAULT_HARS = (
    ".jarvis_private/pocket_hars/pocketoption.com.har",
    ".jarvis_private/pocket_hars/pocketoption.com(1).har",
)


def main() -> int:
    har_paths = tuple(sys.argv[1:]) or DEFAULT_HARS
    report = generate_pocket_discovery_reports(har_paths)
    print(
        "Pocket discovery completed: "
        f"websockets={report.websocket_count} "
        f"events={len(report.event_catalog)} "
        f"viability={report.viability_classification}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
