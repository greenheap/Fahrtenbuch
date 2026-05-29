DEFAULT_FUEL_PRICE_PER_LITRE = 2.00
TOTAL_FUEL_CAPACITY = 54


def calculate_owner_fuel_debt(month_trips):
    total = 0.0
    for trip in month_trips:
        delta = trip["fuel_end"] - trip["fuel_start"]
        price = trip.get("fuel_price") or DEFAULT_FUEL_PRICE_PER_LITRE
        total += -delta * __get_litres_per_unit() * price
    return round(total, 2)


def calculate_renter_fuel_debt(month_trips, prev_month_fuel_end=None):
    total = 0.0
    if prev_month_fuel_end is not None and month_trips:
        delta = month_trips[0]["fuel_start"] - prev_month_fuel_end
        price = month_trips[0].get("fuel_price") or DEFAULT_FUEL_PRICE_PER_LITRE
        total += -delta * __get_litres_per_unit() * price
    for i in range(1, len(month_trips)):
        delta = month_trips[i]["fuel_start"] - month_trips[i - 1]["fuel_end"]
        price = month_trips[i].get("fuel_price") or DEFAULT_FUEL_PRICE_PER_LITRE
        total += -delta * __get_litres_per_unit() * price
    return round(total, 2)


def __get_litres_per_unit():
    return TOTAL_FUEL_CAPACITY / 20

