"""Shared test setup. Hypothesis profiles (T-124): `ci` (default) is derandomised, so a
run is the same on every machine and never flaky; `nightly` explores far more examples.
Pick one with HYPOTHESIS_PROFILE=nightly."""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "ci",
    max_examples=200,
    derandomize=True,
    deadline=None,
    database=None,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile("nightly", max_examples=5000, deadline=None, database=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "ci"))
