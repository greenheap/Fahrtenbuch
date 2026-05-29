import csv


def load_trips(filepath="fahrtenbuch.csv"):
    trips = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            datum = row["datum"].strip()
            if len(datum) != 10 or datum[4] != "-" or datum[7] != "-":
                raise ValueError(f"Zeile {i}: Ungültiges Datum '{datum}' (Format YYYY-MM-DD erwartet).")

            try:
                km_start = float(row["km_start"].strip())
                km_end = float(row["km_end"].strip())
            except ValueError:
                raise ValueError(f"Zeile {i}: Ungültige km-Werte.")

            if km_end < km_start:
                print(f"WARNUNG Zeile {i}: km_end ({km_end}) < km_start ({km_start}) - Zeile wird übersprungen.")
                raise ValueError(f"Zeile {i}: Ungültige km-Werte.")

            fuel_start = _parse_fuel(row.get("fuel_start(1-20)", "").strip(), i, "fuel_start")
            fuel_end = _parse_fuel(row.get("fuel_end(1-20)", "").strip(), i, "fuel_end")

            if fuel_start is None or fuel_end is None:
                raise ValueError(f"Zeile {i}: fuel_start und fuel_end sind Pflichtfelder.")

            month = datum[:7]
            trips.append({
                "datum": datum,
                "month": month,
                "km_start": km_start,
                "km_end": km_end,
                "owner_km": km_end - km_start,
                "fuel_start": fuel_start,
                "fuel_end": fuel_end,
                "fuel_price": float(row["fuel_price"].strip()) if row.get("fuel_price") and row["fuel_price"].strip() else 2.00,
            })

    return trips


def _parse_fuel(raw, row_index, field_name):
    if not raw:
        return None
    try:
        value = int(raw)
        if not (0 <= value <= 20):
            raise ValueError(f"Zeile {row_index}: {field_name} '{raw}' außerhalb 0-20.")
        return value
    except ValueError:
        raise ValueError(f"Zeile {row_index}: Ungültiger {field_name} '{raw}'.")

