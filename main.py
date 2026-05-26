import csv
from collections import defaultdict

YEARLY_PAUSCHALE = 2600.0
MONTHLY_PAUSCHALE = YEARLY_PAUSCHALE / 12


def load_trips(filepath="fahrtenbuch.csv"):
    trips = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            # Validate date
            datum = row["datum"].strip()
            if len(datum) != 10 or datum[4] != "-" or datum[7] != "-":
                print(f"WARNUNG Zeile {i}: Ungültiges Datum '{datum}' (Format YYYY-MM-DD erwartet) - Zeile wird übersprungen.")
                continue

            # Validate km values
            try:
                km_start = float(row["km_start"].strip())
                km_end = float(row["km_end"].strip())
            except ValueError:
                print(f"WARNUNG Zeile {i}: Ungültige km-Werte - Zeile wird übersprungen.")
                continue

            if km_end < km_start:
                print(f"WARNUNG Zeile {i}: km_end ({km_end}) < km_start ({km_start}) - Zeile wird übersprungen.")
                continue

            # Validate fuel level (optional field)
            fuel_raw = row.get("fuel_level(1-20)", "").strip()
            fuel_level = None
            if fuel_raw:
                try:
                    fuel_level = int(fuel_raw)
                    if not (1 <= fuel_level <= 20):
                        print(f"WARNUNG Zeile {i}: Kraftstoffstand '{fuel_raw}' außerhalb 1-20 - wird ignoriert.")
                        fuel_level = None
                except ValueError:
                    print(f"WARNUNG Zeile {i}: Ungültiger Kraftstoffstand '{fuel_raw}' - wird ignoriert.")

            month = datum[:7]  # YYYY-MM
            trips.append({
                "datum": datum,
                "month": month,
                "km_start": km_start,
                "km_end": km_end,
                "jannis_km": km_end - km_start,
                "fuel_level": fuel_level,
            })

    return trips


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


def print_report(results):
    print(f"Fahrtenbuch - Monatliche Kostenaufteilung (Pauschale: {YEARLY_PAUSCHALE:.0f} EUR/Jahr)")
    print(f"Monatlicher Betrag: {MONTHLY_PAUSCHALE:.2f} EUR")
    print("-" * 70)
    print(f"{'Monat':<10} {'Jannis km':>10} {'%':>6} {'EUR':>8}   {'Lukas km':>10} {'%':>6} {'EUR':>8}")
    print("-" * 70)

    total_j_cost = 0.0
    total_l_cost = 0.0

    for month, j_km, j_pct, j_cost, l_km, l_pct, l_cost in results:
        total_j_cost += j_cost
        total_l_cost += l_cost
        print(f"{month:<10} {j_km:>10.1f} {j_pct:>5.1f}% {j_cost:>8.2f}   {l_km:>10.1f} {l_pct:>5.1f}% {l_cost:>8.2f}")

    print("-" * 70)
    print(f"{'GESAMT':<10} {'':>10} {'':>6} {total_j_cost:>8.2f}   {'':>10} {'':>6} {total_l_cost:>8.2f}")


if __name__ == "__main__":
    trips = load_trips()
    results = calculate_monthly_costs(trips)
    if results:
        print_report(results)
    else:
        print("Keine Fahrten gefunden.")
