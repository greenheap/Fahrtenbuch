import csv
from calculator import calculate_monthly_costs, YEARLY_PAUSCHALE, MONTHLY_PAUSCHALE


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
