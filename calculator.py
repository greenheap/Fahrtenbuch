from collections import defaultdict
from typing import Any

YEARLY_PAUSCHALE = 2600.0
MONTHLY_PAUSCHALE = YEARLY_PAUSCHALE / 12
FUEL_COST_PER_LITRE = 2.00
TOTAL_FUEL_CAPACITY = 54


def calculate_monthly_costs(trips):
    if not trips:
        return []

    trips_sorted = sorted(trips, key=lambda t: t["datum"])

    __check_invalid_kilometers(trips_sorted)

    months_trips = defaultdict(list)
    for t in trips_sorted:
        months_trips[t["month"]].append(t)

    all_months = sorted(months_trips.keys())
    start_year, start_month = map(int, all_months[0].split("-"))
    end_year, end_month = map(int, all_months[-1].split("-"))

    # Build full month range (no gaps)
    months_range = []
    y, m = start_year, start_month
    while (y, m) <= (end_year, end_month):
        months_range.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1

    # Track running odometer across months to detect gaps
    prev_last_km = None

    results = []
    for month in months_range:
        month_trips = months_trips.get(month, [])

        if not month_trips:
            results.append((month, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            continue

        first_km_start = month_trips[0]["km_start"]
        last_km_end = month_trips[-1]["km_end"]

        # Total km driven this month from odometer
        if prev_last_km is not None and prev_last_km < first_km_start:
            # Odometer gap at month start: include it as Lukas km
            total_km = last_km_end - prev_last_km
        else:
            total_km = last_km_end - first_km_start

        jannis_km = sum(t["jannis_km"] for t in month_trips)
        lukas_km = max(0.0, total_km - jannis_km)

        prev_last_km = last_km_end

        jannis_fuel_delta = _calculate_jannis_fuel_delta(month_trips)
        lukas_fuel_delta = _calculate_lukas_fuel_delta(month_trips)
        litres_per_unit = TOTAL_FUEL_CAPACITY / 20
        j_fuel_debt = round(-jannis_fuel_delta * litres_per_unit * FUEL_COST_PER_LITRE, 2)
        l_fuel_debt = round(-lukas_fuel_delta * litres_per_unit * FUEL_COST_PER_LITRE, 2)

        if total_km == 0:
            results.append((month, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, j_fuel_debt, l_fuel_debt))
        else:
            jannis_km_percentage = jannis_km / total_km * 100
            lukas_km_percentage = lukas_km / total_km * 100
            jannis_costs = MONTHLY_PAUSCHALE * (jannis_km / total_km)
            lukas_costs = MONTHLY_PAUSCHALE * (lukas_km / total_km)
            results.append((month, jannis_km, jannis_km_percentage, jannis_costs, lukas_km, lukas_km_percentage, lukas_costs, j_fuel_debt, l_fuel_debt))

    return results


def _calculate_jannis_fuel_delta(month_trips):
    total = 0
    for trip in month_trips:
        if trip["fuel_start"] is not None and trip["fuel_end"] is not None:
            total += trip["fuel_end"] - trip["fuel_start"]
    return total


def _calculate_lukas_fuel_delta(month_trips):
    total = 0
    for i in range(1, len(month_trips)):
        prev_fuel_end = month_trips[i - 1]["fuel_end"]
        curr_fuel_start = month_trips[i]["fuel_start"]
        if prev_fuel_end is not None and curr_fuel_start is not None:
            total += curr_fuel_start - prev_fuel_end
    return total


def __check_invalid_kilometers(trips_sorted: list[Any]):
    for i, trip in enumerate(trips_sorted, start=1):
        if trip["km_end"] < trip["km_start"]:
            raise ValueError(
                f"Ungültige km-Werte in Eintrag {i}: km_end={trip['km_end']} "
                f"kleiner als km_start={trip['km_start']}."
            )

    for i in range(1, len(trips_sorted)):
        prev_end = trips_sorted[i - 1]["km_end"]
        curr_start = trips_sorted[i]["km_start"]
        if curr_start < prev_end:
            raise ValueError(
                f"Ungültige km-Reihenfolge: Eintrag {i + 1} hat km_start={curr_start} "
                f"kleiner als vorheriges km_end={prev_end}."
            )
