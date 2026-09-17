from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from quantlab.acquisition.service import AcquisitionService
from quantlab.core.logging import configure_logging
from quantlab.orchestration.config import ControlPlaneConfig
from quantlab.orchestration.doctor import doctor_dict


def _utc_date(value: str) -> datetime:
    """Parse an ISO date/datetime into an aware UTC datetime."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_parser() -> argparse.ArgumentParser:
    """Build the Quant_Lab CLI parser."""
    parser = argparse.ArgumentParser(prog="quantlab")
    parser.add_argument("--log-level", default="INFO")
    sub = parser.add_subparsers(dest="command")
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--root", default="C:/QUANT_LAB")

    acquisition = sub.add_parser("acquisition")
    acquisition_sub = acquisition.add_subparsers(dest="acquisition_command", required=True)

    plan = acquisition_sub.add_parser("plan")
    plan.add_argument("--instrument", required=True)
    plan.add_argument("--start", required=True)
    plan.add_argument("--end", required=True)
    plan.add_argument("--root", default="data")

    download = acquisition_sub.add_parser("download")
    download.add_argument("--instrument", required=True)
    download.add_argument("--start", required=True)
    download.add_argument("--end", required=True)
    download.add_argument("--root", default="data")
    download.add_argument("--workers", type=int, default=2)
    download.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    """Run the Quant_Lab CLI entry point."""
    args = build_parser().parse_args()
    configure_logging(args.log_level)
    if args.command == "doctor":
        config = ControlPlaneConfig.from_environment(args.root)
        for item in doctor_dict(config):
            print(f"{item["name"]}={item["status"]} ({item["detail"]})")
        return 0 if all(item["status"] not in {"FAIL"} for item in doctor_dict(config)) else 1
    if args.command != "acquisition":
        return 0
    service = AcquisitionService(Path(args.root))
    start = _utc_date(args.start)
    end = _utc_date(args.end)
    chunks = service.plan(args.instrument, start, end)
    if args.acquisition_command == "plan":
        print(f"instrument={args.instrument}")
        print(f"chunks={len(chunks)}")
        if chunks:
            print(f"first={chunks[0].url}")
            print(f"last={chunks[-1].url}")
        return 0
    counts = service.download(chunks, workers=args.workers, overwrite=args.overwrite)
    for status, count in sorted(counts.items(), key=lambda item: item[0].value):
        if count:
            print(f"{status.value}={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
