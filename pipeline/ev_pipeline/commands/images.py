"""`ev images check | fetch` (T-134): validate data/images/photos.yaml; fetch originals once."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from ev_pipeline.images.photos import load_photos
from ev_pipeline.images.store import CACHE_DIR, fetch_originals
from ev_pipeline.match.seed import load_seed
from ev_pipeline.refresh.runner import write_run_log
from ev_pipeline.release.build import default_data_dir


def _photos(data_dir: Path):
    seed = load_seed(data_dir / "seed" / "models.yaml")
    return load_photos(data_dir, set(seed.generations), datetime.now(UTC).date())


def cmd_images(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir) if args.data_dir else default_data_dir()
    started = datetime.now(UTC)
    photos, problems = _photos(data_dir)
    log: dict = {
        "step": f"images-{args.action}",
        "at": started.isoformat(timespec="seconds"),
        "inputs": [{"path": "images/photos.yaml", "valid": len(photos), "problems": len(problems)}],
        "problems": [{"generation_id": p.generation_id, "reason": p.reason} for p in problems],
    }
    if args.action == "fetch":
        rep = fetch_originals(photos, data_dir / CACHE_DIR)
        log["outputs"] = rep.log()
        log["outcome"] = "partial" if rep.failed else "ok"
        write_run_log(data_dir, log, started)
    print(json.dumps(log, indent=1, ensure_ascii=False))
    return 1 if (args.action == "check" and problems) else 0


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("images", help="car photos: check photos.yaml, fetch originals (T-134)")
    p.add_argument("action", choices=("check", "fetch"))
    p.add_argument("--data-dir", help="data folder (default: repo data/ or EV_DATA_DIR)")
    p.set_defaults(func=cmd_images)
