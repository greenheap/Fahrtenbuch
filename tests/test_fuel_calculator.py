from fuel_calculator import calculate_owner_fuel_debt, calculate_renter_fuel_debt, DEFAULT_FUEL_PRICE_PER_LITRE, TOTAL_FUEL_CAPACITY


def test_given_single_trip_with_no_fuel_change_then_owner_fuel_debt_is_zero():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
    ]

    result = calculate_owner_fuel_debt(trips)

    assert result == 0.0


def test_given_two_trips_with_no_renter_fuel_change_then_renter_fuel_debt_is_zero():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
        {"fuel_start": 10, "fuel_end": 10},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == 0.0


def test_given_prev_month_fuel_end_equals_current_fuel_start_then_renter_fuel_debt_is_zero():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
    ]

    result = calculate_renter_fuel_debt(trips, prev_month_fuel_end=10)

    assert result == 0.0


def test_given_cross_month_fuel_drop_then_renter_has_fuel_debt():
    trips = [
        {"fuel_start": 0, "fuel_end": 0},
    ]

    result = calculate_renter_fuel_debt(trips, prev_month_fuel_end=12)

    assert result == round(12 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_owner_returns_car_with_less_fuel_then_owner_has_fuel_debt():
    trips = [
        {"fuel_start": 10, "fuel_end": 0},
    ]

    result = calculate_owner_fuel_debt(trips)

    assert result == round(10 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_owner_returns_car_with_more_fuel_then_owner_has_negative_fuel_debt():
    trips = [
        {"fuel_start": 5, "fuel_end": 10},
    ]

    result = calculate_owner_fuel_debt(trips)

    assert result == round(-5 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_renter_returns_car_with_less_fuel_then_renter_has_fuel_debt():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
        {"fuel_start": 7, "fuel_end": 7},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == round(3 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_renter_returns_car_with_more_fuel_then_renter_has_negative_fuel_debt():
    trips = [
        {"fuel_start": 7, "fuel_end": 7},
        {"fuel_start": 10, "fuel_end": 10},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == round(-3 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)

def test_given_owner_trip_with_no_fuel_price_then_owner_debt_falls_back_to_default():
    trips = [{"fuel_start": 5, "fuel_end": 10},]

    result = calculate_owner_fuel_debt(trips)

    assert result == round(-5 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_owner_trip_with_explicit_fuel_price_then_uses_it():
    trips = [{"fuel_start": 5, "fuel_end": 10, "fuel_price": 1.50},]

    result = calculate_owner_fuel_debt(trips)

    assert result == round(-5 * (TOTAL_FUEL_CAPACITY / 20) * 1.50, 2)


def test_given_owner_multiple_trips_with_mixed_fuel_prices_then_each_trip_uses_its_own_price():
    trips = [
        {"fuel_start": 5, "fuel_end": 10, "fuel_price": 1.50},
        {"fuel_start": 10, "fuel_end": 5, "fuel_price": 2.50},
    ]

    result = calculate_owner_fuel_debt(trips)

    expected = round(-5 * (TOTAL_FUEL_CAPACITY / 20) * 1.50, 2) + round(5 * (TOTAL_FUEL_CAPACITY / 20) * 2.50, 2)
    assert result == round(expected, 2)


def test_given_gap_between_owner_trips_with_no_fuel_price_then_renter_debt_falls_back_to_default():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
        {"fuel_start": 7, "fuel_end": 7},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == round(3 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_gap_between_owner_trips_with_explicit_fuel_price_then_renter_debt_uses_it():
    trips = [
        {"fuel_start": 10, "fuel_end": 10, "fuel_price": None},
        {"fuel_start": 7, "fuel_end": 7, "fuel_price": 1.70},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == round(3 * (TOTAL_FUEL_CAPACITY / 20) * 1.70, 2)


def test_given_cross_month_with_no_fuel_price_then_falls_back_to_default():
    trips = [
        {"fuel_start": 0, "fuel_end": 0},
    ]

    result = calculate_renter_fuel_debt(trips, prev_month_fuel_end=12)

    assert result == round(12 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_cross_month_with_explicit_fuel_price_then_uses_it():
    trips = [
        {"fuel_start": 0, "fuel_end": 0, "fuel_price": 1.80},
    ]

    result = calculate_renter_fuel_debt(trips, prev_month_fuel_end=12)

    assert result == round(12 * (TOTAL_FUEL_CAPACITY / 20) * 1.80, 2)


def test_given_multiple_gaps_between_owner_trips_with_mixed_fuel_prices_then_each_gap_uses_its_own_price():
    trips = [
        {"fuel_start": 10, "fuel_end": 10, "fuel_price": None},
        {"fuel_start": 7, "fuel_end": 7, "fuel_price": 1.70},
        {"fuel_start": 5, "fuel_end": 5, "fuel_price": 2.10},
    ]

    result = calculate_renter_fuel_debt(trips)

    segment_one = round(3 * (TOTAL_FUEL_CAPACITY / 20) * 1.70, 2)
    segment_two = round(2 * (TOTAL_FUEL_CAPACITY / 20) * 2.10, 2)
    assert result == round(segment_one + segment_two, 2)

