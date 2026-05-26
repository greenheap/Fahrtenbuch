FUEL_COST_PER_LITRE = 2.00
TOTAL_FUEL_CAPACITY = 54


def calculate_owner_fuel_debt(month_trips):
    fuel_delta = __calculate_owner_fuel_delta(month_trips)
    return round(-fuel_delta * __get_litres_per_unit() * FUEL_COST_PER_LITRE, 2)


def calculate_renter_fuel_debt(month_trips, prev_month_fuel_end=None):
    fuel_delta = __calculate_renter_fuel_delta(month_trips, prev_month_fuel_end)
    return round(-fuel_delta * __get_litres_per_unit() * FUEL_COST_PER_LITRE, 2)


def __get_litres_per_unit():
    return TOTAL_FUEL_CAPACITY / 20


def __calculate_owner_fuel_delta(month_trips):
    total = 0
    for trip in month_trips:
        if trip["fuel_start"] is not None and trip["fuel_end"] is not None:
            total += trip["fuel_end"] - trip["fuel_start"]
    return total


def __calculate_renter_fuel_delta(month_trips, prev_month_fuel_end=None):
    total = 0
    if prev_month_fuel_end is not None and month_trips and month_trips[0]["fuel_start"] is not None:
        total += month_trips[0]["fuel_start"] - prev_month_fuel_end
    for i in range(1, len(month_trips)):
        prev_fuel_end = month_trips[i - 1]["fuel_end"]
        curr_fuel_start = month_trips[i]["fuel_start"]
        if prev_fuel_end is not None and curr_fuel_start is not None:
            total += curr_fuel_start - prev_fuel_end
    return total

