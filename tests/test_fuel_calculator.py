from fuel_calculator import calculate_owner_fuel_debt, calculate_renter_fuel_debt, FUEL_COST_PER_LITRE, TOTAL_FUEL_CAPACITY


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

    assert result == round(12 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_owner_returns_car_with_less_fuel_then_owner_has_fuel_debt():
    trips = [
        {"fuel_start": 10, "fuel_end": 0},
    ]

    result = calculate_owner_fuel_debt(trips)

    assert result == round(10 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_owner_returns_car_with_more_fuel_then_owner_has_negative_fuel_debt():
    trips = [
        {"fuel_start": 5, "fuel_end": 10},
    ]

    result = calculate_owner_fuel_debt(trips)

    assert result == round(-5 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_renter_returns_car_with_less_fuel_then_renter_has_fuel_debt():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
        {"fuel_start": 7, "fuel_end": 7},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == round(3 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_renter_returns_car_with_more_fuel_then_renter_has_negative_fuel_debt():
    trips = [
        {"fuel_start": 7, "fuel_end": 7},
        {"fuel_start": 10, "fuel_end": 10},
    ]

    result = calculate_renter_fuel_debt(trips)

    assert result == round(-3 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)
