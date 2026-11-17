"""Derived metrics (T-007). Pure functions; every constant here is documented and provisional.

Formulas (metric units):
- consumption_kwh_100km (estimate, only when no source gives it)
      = battery_kwh_net / wltp_range_km * 100
- ac_km_per_h       = ac_kw / consumption_kwh_100km * 100
- DC charging (Decision 009). With a charge curve (SoC %, kW points, linear in between):
      window          = 10 -> 80 % SoC, energy = battery_kwh_net * 0.7
      dc_minutes_10_80 = 60 * sum(dSoC/100 * battery_kwh_net / kW(SoC))
      dc_avg_10_80_kw  = energy / hours
      dc_peak_held_min = minutes inside the window with kW >= 90% of the curve's peak
  Without a curve but with dc_peak_kw we use DEFAULT_CURVE_SHAPE (status `default`,
  estimate): flat at peak from 10 to 25 % SoC, then linear down to 35 % of peak at 80 %.
  PROVISIONAL, from the typical shape of current 400 V curves; it gives an average of about
  0.67 x peak over 10-80 %, close to the older 0.6 x peak rule of thumb. The coordinator's
  sketch was flat to ~45 % and down to ~45 % at 80 % (about 0.82 x peak); we picked the more
  conservative shape (QUESTIONS.md Q-018). The average does not depend on battery size, minutes do.
- consumption_motorway_kwh_100km = measured fact if present, else WLTP consumption x 1.30
  (PROVISIONAL, estimate: ~120 km/h motorway vs the WLTP mix).
- km added in N minutes = dc_avg_10_80_kw * N/60 / motorway consumption * 100, capped by the
  energy of the 10->80 % window (battery_kwh_net * 0.7). dc_km_per_10min and dc_km_per_20min.
- battery_kwh_net (estimate, only when a source gives gross but not net)
      = 0.93 * battery_kwh_gross. PROVISIONAL; derived, confidence low.
- WLTP equivalent from EPA when only EPA is known: wltp ~= epa * 1.12 (EPA's 5-cycle test is
  stricter than WLTP; 1.12 is a common rough conversion). PROVISIONAL; derived.

Real range ladder (highest rung first, see RealRangeRung in the schema):
1. owner-data      our owners' logged trips for this variant (none yet)
2. exact-test      a real-world test of this exact variant (Bjørn Nyland: permission
                   pending, never in a release, so unused tonight; any other source's
                   real_range_km fact also counts here)
3. sibling-variant another variant of the same generation has rung 1/2 data: scale its real
                   range by battery_kwh_net ratio
4. brand-body-drivetrain-ratio  mean real/WLTP of variants with rung 1/2 data that share
                   make, body and drivetrain, times this variant's WLTP
5. body-ratio      WLTP times a generic ratio per body type (below) with a drivetrain
                   adjustment. PROVISIONAL: assumes mild-weather (about 15-20 °C) mixed
                   driving (roughly half motorway at 110-120 km/h). Not measured by us.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MOTORWAY_PER_WLTP = 1.30
WINDOW = (10.0, 80.0)
WINDOW_SHARE = (WINDOW[1] - WINDOW[0]) / 100  # 0.7 of net capacity
PEAK_HELD_SHARE = 0.9
# (SoC %, share of peak kW). PROVISIONAL generic shape, see module docstring.
DEFAULT_CURVE_SHAPE: tuple[tuple[float, float], ...] = (
    (0.0, 0.7),
    (10.0, 1.0),
    (25.0, 1.0),
    (80.0, 0.35),
    (100.0, 0.1),
)
# Usable share of gross capacity when a source gives only gross (coordinator, 2026-11-15).
# PROVISIONAL: typical buffers are 5-10%; 0.93 sits in the middle.
NET_PER_GROSS = 0.93
WLTP_PER_EPA = 1.12
# T-071 (Decision 047): official WLTP consumption is measured at the wall, so it includes
# charging losses; battery_kwh_net / wltp_range_km is battery basis and runs low. Median
# official / battery-basis ratio on release 1: 1.159 (n 138, IQR 1.13-1.20, rows with an
# official consumption, a non-estimated WLTP and a net capacity). Wall x 0.86 = battery,
# close to the matrix basis in Decision 041 (x 0.88).
WALL_PER_BATTERY_WLTP = 1.16

# PROVISIONAL generic real/WLTP ratios, mild-weather mixed driving. Boxier and taller bodies
# lose more at motorway speed. Replace with brand-body-drivetrain ratios once real data exists.
BODY_RATIOS: dict[str, float] = {
    "hatchback": 0.85,
    "sedan": 0.88,
    "estate": 0.86,
    "suv": 0.80,
    "crossover": 0.82,
    "coupe": 0.86,
    "mpv": 0.80,
    "cabrio": 0.84,  # not in the brief; between hatchback and coupe (QUESTIONS.md Q-016)
}
DRIVETRAIN_ADJ: dict[str, float] = {"awd": -0.02}
PROVISIONAL_NOTE = "PROVISIONAL generic ratio, mild-weather mixed driving"


def consumption_estimate(battery_kwh_net: float, wltp_range_km: float) -> float:
    """WLTP consumption (wall basis, kWh/100 km) estimated from net capacity and WLTP range."""
    return battery_kwh_net / wltp_range_km * 100 * WALL_PER_BATTERY_WLTP


def ac_km_per_h(ac_kw: float, consumption_kwh_100km: float) -> float:
    return ac_kw / consumption_kwh_100km * 100


def default_curve(dc_peak_kw: float) -> list[tuple[float, float]]:
    return [(soc, share * dc_peak_kw) for soc, share in DEFAULT_CURVE_SHAPE]


def cap_curve(points: list[tuple[float, float]], peak_kw: float) -> list[tuple[float, float]]:
    """The curve with every point above `peak_kw` lowered to it (shape kept below the cap)."""
    return [(soc, min(kw, peak_kw)) for soc, kw in points]


def _kw_at(points: list[tuple[float, float]], soc: float) -> float:
    pts = sorted(points)
    if soc <= pts[0][0]:
        return pts[0][1]
    for (s0, p0), (s1, p1) in zip(pts, pts[1:], strict=False):
        if s0 <= soc <= s1:
            return p0 if s1 == s0 else p0 + (p1 - p0) * (soc - s0) / (s1 - s0)
    return pts[-1][1]


@dataclass
class CurveStats:
    avg_kw: float
    minutes: float | None  # None without a battery size
    peak_held_min: float | None
    peak_kw: float


def integrate_curve(
    points: list[tuple[float, float]], battery_kwh_net: float | None, step: float = 0.1
) -> CurveStats | None:
    """Integrate a charge curve over the 10->80 % window. None if the curve is unusable."""
    if len(points) < 2:
        return None
    peak = max(p for _, p in points)
    lo, hi = WINDOW
    n = round((hi - lo) / step)
    hours_per_kwh = 0.0  # hours to charge the window per kWh of capacity
    held_per_kwh = 0.0
    for i in range(n):
        kw = _kw_at(points, lo + (i + 0.5) * step)
        if kw <= 0:
            return None
        dh = step / 100 / kw
        hours_per_kwh += dh
        if kw >= PEAK_HELD_SHARE * peak:
            held_per_kwh += dh
    avg = WINDOW_SHARE / hours_per_kwh
    if battery_kwh_net:
        return CurveStats(
            avg, hours_per_kwh * battery_kwh_net * 60, held_per_kwh * battery_kwh_net * 60, peak
        )
    return CurveStats(avg, None, None, peak)


def minutes_from_avg(battery_kwh_net: float, dc_avg_kw: float) -> float:
    return battery_kwh_net * WINDOW_SHARE / dc_avg_kw * 60


def motorway_consumption(consumption_kwh_100km: float) -> float:
    return consumption_kwh_100km * MOTORWAY_PER_WLTP


def km_in_minutes(
    dc_avg_kw: float,
    minutes: float,
    consumption_kwh_100km: float,
    battery_kwh_net: float | None = None,
) -> float:
    """km added in `minutes`, capped by the 10->80 % window when the battery is known."""
    kwh = dc_avg_kw * minutes / 60
    if battery_kwh_net:
        kwh = min(kwh, battery_kwh_net * WINDOW_SHARE)
    return kwh / consumption_kwh_100km * 100


def net_from_gross(battery_kwh_gross: float) -> float:
    return battery_kwh_gross * NET_PER_GROSS


def wltp_from_epa(epa_range_km: float) -> float:
    return epa_range_km * WLTP_PER_EPA


def era(year_start: int) -> str:
    if year_start < 2018:
        return "pre-2018"
    if year_start <= 2020:
        return "2018-20"
    if year_start <= 2022:
        return "2021-22"
    if year_start <= 2024:
        return "2023-24"
    return "2025+"


def quality_tier(battery_sources: int, range_sources: int, checked: bool = False) -> str:
    """checked: staff hand-checked (none tonight). sourced: battery and range each confirmed
    by 2+ agreeing independent sources. Otherwise single-source."""
    if checked:
        return "checked"
    if battery_sources >= 2 and range_sources >= 2:
        return "sourced"
    return "single-source"


@dataclass
class RealObservation:
    """A measured real range for one variant (rungs owner-data / exact-test)."""

    km: float
    rung: str  # "owner-data" or "exact-test"
    source_ids: list[str]
    fact_ids: list[str]
    confidence: str


@dataclass
class LadderInput:
    variant_id: str
    generation_id: str
    make_id: str
    body: str | None
    drivetrain: str | None
    battery_kwh_net: float | None
    wltp_km: float | None  # WLTP, or the EPA-derived equivalent
    wltp_source_ids: list[str] = field(default_factory=list)
    wltp_fact_ids: list[str] = field(default_factory=list)


@dataclass
class LadderResult:
    km: float
    rung: str
    confidence: str
    source_ids: list[str]
    fact_ids: list[str]
    note: str


_RUNG_ORDER = {"owner-data": 0, "exact-test": 1}


def brand_body_drivetrain_ratios(
    inputs: list[LadderInput], observations: dict[str, RealObservation]
) -> dict[tuple[str, str | None, str | None], tuple[float, list[str]]]:
    """(make, body, drivetrain) -> (mean real/WLTP, variant ids it came from)."""
    acc: dict[tuple[str, str | None, str | None], list[tuple[float, str]]] = {}
    for li in inputs:
        obs = observations.get(li.variant_id)
        if obs is None or not li.wltp_km:
            continue
        acc.setdefault((li.make_id, li.body, li.drivetrain), []).append(
            (obs.km / li.wltp_km, li.variant_id)
        )
    return {k: (sum(r for r, _ in v) / len(v), sorted(vid for _, vid in v)) for k, v in acc.items()}


def real_range(
    li: LadderInput,
    inputs: list[LadderInput],
    observations: dict[str, RealObservation],
    bbd_ratios: dict[tuple[str, str | None, str | None], tuple[float, list[str]]] | None = None,
) -> LadderResult | None:
    """Walk the ladder for one variant; None when no rung applies."""
    own = observations.get(li.variant_id)
    if own is not None:
        return LadderResult(own.km, own.rung, own.confidence, own.source_ids, own.fact_ids, "")

    if li.battery_kwh_net:
        siblings = [
            (s, observations[s.variant_id])
            for s in inputs
            if s.generation_id == li.generation_id
            and s.variant_id != li.variant_id
            and s.variant_id in observations
            and s.battery_kwh_net
        ]
        if siblings:
            sib, obs = min(
                siblings,
                key=lambda so: (
                    abs(so[0].battery_kwh_net - li.battery_kwh_net),
                    _RUNG_ORDER.get(so[1].rung, 9),
                    so[0].variant_id,
                ),
            )
            km = obs.km * li.battery_kwh_net / sib.battery_kwh_net
            return LadderResult(
                km,
                "sibling-variant",
                "low",
                sorted(set(obs.source_ids)),
                obs.fact_ids,
                f"scaled from {sib.variant_id} by battery ratio",
            )

    if not li.wltp_km:
        return None
    ratios = (
        bbd_ratios if bbd_ratios is not None else brand_body_drivetrain_ratios(inputs, observations)
    )
    k = (li.make_id, li.body, li.drivetrain)
    if k in ratios:
        ratio, from_ids = ratios[k]
        return LadderResult(
            li.wltp_km * ratio,
            "brand-body-drivetrain-ratio",
            "low",
            li.wltp_source_ids,
            li.wltp_fact_ids,
            f"ratio {ratio:.3f} from {len(from_ids)} variant(s)",
        )
    if li.body in BODY_RATIOS:
        ratio = BODY_RATIOS[li.body] + DRIVETRAIN_ADJ.get(li.drivetrain or "", 0.0)
        return LadderResult(
            li.wltp_km * ratio,
            "body-ratio",
            "low",
            li.wltp_source_ids,
            li.wltp_fact_ids,
            f"{PROVISIONAL_NOTE}: {li.body} {ratio:.2f} x WLTP",
        )
    return None
