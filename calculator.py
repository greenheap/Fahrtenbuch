from collections import defaultdict

YEARLY_PAUSCHALE = 2600.0
MONTHLY_PAUSCHALE = YEARLY_PAUSCHALE / 12


def calculate_monthly_costs(trips):
    if not trips:
        return []

    # Sort trips by date to ensure correct odometer order
    trips_sorted = sorted(trips, key=lambda t: t["datum"])

    # Group by month
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
            results.append((month, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
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

        if total_km == 0:
            results.append((month, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        else:
            j_pct = jannis_km / total_km * 100
            l_pct = lukas_km / total_km * 100
            j_cost = MONTHLY_PAUSCHALE * (jannis_km / total_km)
            l_cost = MONTHLY_PAUSCHALE * (lukas_km / total_km)
            results.append((month, jannis_km, j_pct, j_cost, lukas_km, l_pct, l_cost))

    return results

