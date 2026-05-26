import csv
from calculator import calculate_monthly_costs, YEARLY_PAUSCHALE, MONTHLY_PAUSCHALE, FUEL_COST_PER_LITRE, TOTAL_FUEL_CAPACITY

OWNER_NAME = "Jannis"
RENTER_NAME = "Lukas"


def load_trips(filepath="fahrtenbuch.csv"):
    trips = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            datum = row["datum"].strip()
            if len(datum) != 10 or datum[4] != "-" or datum[7] != "-":
                print(f"WARNUNG Zeile {i}: Ungültiges Datum '{datum}' (Format YYYY-MM-DD erwartet) - Zeile wird übersprungen.")
                continue

            try:
                km_start = float(row["km_start"].strip())
                km_end = float(row["km_end"].strip())
            except ValueError:
                print(f"WARNUNG Zeile {i}: Ungültige km-Werte - Zeile wird übersprungen.")
                continue

            if km_end < km_start:
                print(f"WARNUNG Zeile {i}: km_end ({km_end}) < km_start ({km_start}) - Zeile wird übersprungen.")
                continue

            fuel_start = _parse_fuel(row.get("fuel_start(1-20)", "").strip(), i, "fuel_start")
            fuel_end = _parse_fuel(row.get("fuel_end(1-20)", "").strip(), i, "fuel_end")

            if fuel_end is not None and fuel_start is None:
                print(f"WARNUNG Zeile {i}: fuel_end ohne fuel_start angegeben - Kraftstoff wird ignoriert.")
                fuel_end = None

            month = datum[:7]
            trips.append({
                "datum": datum,
                "month": month,
                "km_start": km_start,
                "km_end": km_end,
                "owner_km": km_end - km_start,
                "fuel_start": fuel_start,
                "fuel_end": fuel_end,
            })

    return trips


def _parse_fuel(raw, row_index, field_name):
    if not raw:
        return None
    try:
        value = int(raw)
        if not (1 <= value <= 20):
            print(f"WARNUNG Zeile {row_index}: {field_name} '{raw}' außerhalb 1-20 - wird ignoriert.")
            return None
        return value
    except ValueError:
        print(f"WARNUNG Zeile {row_index}: Ungültiger {field_name} '{raw}' - wird ignoriert.")
        return None


def print_report(results):
    print(f"Fahrtenbuch - Monatliche Kostenaufteilung (Pauschale: {YEARLY_PAUSCHALE:.0f} EUR/Jahr)")
    print(f"Monatlicher Betrag: {MONTHLY_PAUSCHALE:.2f} EUR  |  Kraftstoff: {FUEL_COST_PER_LITRE:.2f} EUR/Liter  |  Tank: {TOTAL_FUEL_CAPACITY} Liter")
    print("-" * 136)
    print(f"{'Monat':<10} | {f'{OWNER_NAME} km':>10} {'%':>6} {'EUR':>8} {'Benzin':>8} {'Gesamt':>8} | {f'{RENTER_NAME} km':>10} {'%':>6} {'EUR':>8} {'Benzin':>8} {'Gesamt':>8} | {f'Schulden {RENTER_NAME}':>14} |")
    print("-" * 136)

    total_o_cost = 0.0
    total_r_cost = 0.0
    total_o_fuel = 0.0
    total_r_fuel = 0.0

    for month, o_km, o_pct, o_cost, r_km, r_pct, r_cost, o_fuel_debt, r_fuel_debt in results:
        total_o_cost += o_cost
        total_r_cost += r_cost
        total_o_fuel += o_fuel_debt
        total_r_fuel += r_fuel_debt
        o_total = o_cost + o_fuel_debt
        r_total = r_cost + r_fuel_debt
        schulden_renter = r_total - o_fuel_debt
        print(f"{month:<10} | {o_km:>10.1f} {o_pct:>5.1f}% {o_cost:>8.2f} {o_fuel_debt:>8.2f} {o_total:>8.2f} | {r_km:>10.1f} {r_pct:>5.1f}% {r_cost:>8.2f} {r_fuel_debt:>8.2f} {r_total:>8.2f} | {schulden_renter:>14.2f} |")

    print("-" * 136)
    o_grand_total = total_o_cost + total_o_fuel
    r_grand_total = total_r_cost + total_r_fuel
    grand_schulden_renter = r_grand_total - total_o_fuel
    print(f"{'GESAMT':<10} | {'':>10} {'':>6} {total_o_cost:>8.2f} {total_o_fuel:>8.2f} {o_grand_total:>8.2f} | {'':>10} {'':>6} {total_r_cost:>8.2f} {total_r_fuel:>8.2f} {r_grand_total:>8.2f} | {grand_schulden_renter:>14.2f} |")


if __name__ == "__main__":
    trips = load_trips()
    results = calculate_monthly_costs(trips)
    if results:
        print_report(results)
    else:
        print("Keine Fahrten gefunden.")
