from __future__ import annotations

import argparse

from tools.pocket_parser.replay_engine import PocketOfflineReplayEngine
from tools.pocket_parser.report_generator import generate_reports

DEFAULT_HARS = (
    ".jarvis_private/pocket_hars/pocketoption.com.har",
    ".jarvis_private/pocket_hars/pocketoption.com(1).har",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline Pocket Option HAR protocol parser.")
    parser.add_argument("--har", action="append", dest="hars", help="Path to a local HAR file. Can be passed multiple times.")
    args = parser.parse_args()
    har_paths = tuple(args.hars or DEFAULT_HARS)

    engine = PocketOfflineReplayEngine()
    result = engine.replay(har_paths)
    paths = generate_reports(result, engine.store)
    print(
        "Pocket parser completed: "
        f"sessions={result.sessions_processed} "
        f"buckets={len(engine.store.list_buckets())} "
        f"candles={sum(len(batch.candles) for batch in result.history_batches)} "
        f"ticks={len(result.ticks)} "
        f"report={paths['parser_txt']}"
    )


if __name__ == "__main__":
    main()

