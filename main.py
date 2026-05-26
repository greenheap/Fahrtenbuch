import csv
from calculator import calculate_monthly_costs, YEARLY_PAUSCHALE, MONTHLY_PAUSCHALE, FUEL_COST_PER_LITRE, TOTAL_FUEL_CAPACITY
from report_calculator import calculate_report

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
    report = calculate_report(results)
    schulden_header = f"Schulden {RENTER_NAME}"
    hint_text = f"(Gesamt {RENTER_NAME} - Benzin {OWNER_NAME})"
    last_col_width = max(len(schulden_header), len(hint_text))
    separator_width = 10 + 3 + 44 + 3 + 44 + 3 + last_col_width + 2
    separator = "-" * separator_width
    print(f"Fahrtenbuch - Monatliche Kostenaufteilung (Pauschale: {YEARLY_PAUSCHALE:.0f} EUR/Jahr)")
    print(f"Monatlicher Betrag: {MONTHLY_PAUSCHALE:.2f} EUR  |  Kraftstoff: {FUEL_COST_PER_LITRE:.2f} EUR/Liter  |  Tank: {TOTAL_FUEL_CAPACITY} Liter")
    print(separator)
    print(f"{'Monat':<10} | {f'{OWNER_NAME} km':>10} {'%':>6} {'EUR':>8} {'Benzin':>8} {'Gesamt':>8} | {f'{RENTER_NAME} km':>10} {'%':>6} {'EUR':>8} {'Benzin':>8} {'Gesamt':>8} | {schulden_header:>{last_col_width}} |")
    print(f"{'':10} | {'':10} {'':6} {'':8} {'':8} {'':8} | {'':10} {'':6} {'':8} {'':8} {'':8} | {hint_text:>{last_col_width}} |")
    print(separator)

    for row in report["rows"]:
        print(f"{row['month']:<10} | {row['owner_km']:>10.1f} {row['owner_percentage']:>5.1f}% {row['owner_cost']:>8.2f} {row['owner_fuel_debt']:>8.2f} {row['owner_total']:>8.2f} | {row['renter_km']:>10.1f} {row['renter_percentage']:>5.1f}% {row['renter_cost']:>8.2f} {row['renter_fuel_debt']:>8.2f} {row['renter_total']:>8.2f} | {row['renter_debt']:>{last_col_width}.2f} |")

    print(separator)
    totals = report["totals"]
    print(f"{'GESAMT':<10} | {'':>10} {'':>6} {totals['total_owner_cost']:>8.2f} {totals['total_owner_fuel']:>8.2f} {totals['owner_grand_total']:>8.2f} | {'':>10} {'':>6} {totals['total_renter_cost']:>8.2f} {totals['total_renter_fuel']:>8.2f} {totals['renter_grand_total']:>8.2f} | {totals['grand_renter_debt']:>{last_col_width}.2f} |")


if __name__ == "__main__":
    trips = load_trips()
    results = calculate_monthly_costs(trips)
    if results:
        print_report(results)
    else:
        print("Keine Fahrten gefunden.")
