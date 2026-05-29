import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

from fuel_calculator import calculate_owner_fuel_debt, calculate_renter_fuel_debt, DEFAULT_FUEL_PRICE_PER_LITRE, TOTAL_FUEL_CAPACITY

YEARLY_PAUSCHALE = 2600.0
MONTHLY_PAUSCHALE = YEARLY_PAUSCHALE / 12


@dataclass
class MonthlyCostResult:
    month: str
    owner_km: float
    owner_km_percentage: float
    owner_costs: float
    renter_km: float
    renter_km_percentage: float
    renter_costs: float
    owner_fuel_debt: float
    renter_fuel_debt: float


def calculate_monthly_costs(trips, start_date: date = None) -> list[MonthlyCostResult]:
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

    prev_last_km = None
    prev_month_fuel_end = None
    first_month = months_range[0]

    results = []
    for month in months_range:
        month_trips = months_trips.get(month, [])
        effective_pauschale = __effective_pauschale_for_month(month, first_month, start_date)
        if not month_trips:
            results.append(MonthlyCostResult(month=month,
                                             owner_km=0.0,
                                             owner_km_percentage=0.0,
                                             owner_costs=0.0,
                                             renter_km=0.0,
                                             renter_km_percentage=0.0,
                                             renter_costs=0.0,
                                             owner_fuel_debt=0.0,
                                             renter_fuel_debt=0.0))
            continue

        first_km_start = month_trips[0]["km_start"]
        last_km_end = month_trips[-1]["km_end"]

        if prev_last_km is not None and prev_last_km < first_km_start:
            total_km = last_km_end - prev_last_km
        else:
            total_km = last_km_end - first_km_start

        owner_km = sum(t["owner_km"] for t in month_trips)
        renter_km = max(0.0, total_km - owner_km)

        prev_last_km = last_km_end

        owner_fuel_debt = calculate_owner_fuel_debt(month_trips)
        renter_fuel_debt = calculate_renter_fuel_debt(month_trips, prev_month_fuel_end)

        last_trip_with_fuel = next((t for t in reversed(month_trips) if t["fuel_end"] is not None), None)
        prev_month_fuel_end = last_trip_with_fuel["fuel_end"] if last_trip_with_fuel else prev_month_fuel_end

        if total_km == 0:
            results.append(MonthlyCostResult(month=month,
                                             owner_km=0.0,
                                             owner_km_percentage=0.0,
                                             owner_costs=0.0,
                                             renter_km=0.0,
                                             renter_km_percentage=0.0,
                                             renter_costs=0.0,
                                             owner_fuel_debt=owner_fuel_debt,
                                             renter_fuel_debt=renter_fuel_debt))
        else:
            owner_km_percentage = owner_km / total_km * 100
            renter_km_percentage = renter_km / total_km * 100
            owner_costs = effective_pauschale * (owner_km / total_km)
            renter_costs = effective_pauschale * (renter_km / total_km)
            results.append(MonthlyCostResult(
                month=month,
                owner_km=owner_km,
                owner_km_percentage=owner_km_percentage,
                owner_costs=owner_costs,
                renter_km=renter_km,
                renter_km_percentage=renter_km_percentage,
                renter_costs=renter_costs,
                owner_fuel_debt=owner_fuel_debt,
                renter_fuel_debt=renter_fuel_debt,
            ))

    return results


def __effective_pauschale_for_month(month: str, first_month: str, start_date: date) -> float:
    if start_date is None or month != first_month:
        return MONTHLY_PAUSCHALE
    year, month_number = map(int, month.split("-"))
    days_in_month = calendar.monthrange(year, month_number)[1]
    days_used = days_in_month - start_date.day + 1
    return MONTHLY_PAUSCHALE * (days_used / days_in_month)


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
