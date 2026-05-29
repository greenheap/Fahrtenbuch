from calculator import calculate_monthly_costs, YEARLY_PAUSCHALE, MONTHLY_PAUSCHALE, DEFAULT_FUEL_PRICE_PER_LITRE, TOTAL_FUEL_CAPACITY
from report_calculator import calculate_report
from trip_loader import load_trips

OWNER_NAME = "Jannis"
RENTER_NAME = "Lukas"


def print_report(results):
    report = calculate_report(results)
    schulden_header = f"Schulden {RENTER_NAME}"
    hint_text = f"(Gesamt {RENTER_NAME} - Benzin {OWNER_NAME})"
    last_col_width = max(len(schulden_header), len(hint_text))
    separator_width = 10 + 3 + 44 + 3 + 44 + 3 + last_col_width + 2
    separator = "-" * separator_width
    print(f"Fahrtenbuch - Monatliche Kostenaufteilung (Pauschale: {YEARLY_PAUSCHALE:.0f} EUR/Jahr)")
    print(f"Monatlicher Betrag: {MONTHLY_PAUSCHALE:.2f} EUR  |  Tank: {TOTAL_FUEL_CAPACITY} Liter")
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
