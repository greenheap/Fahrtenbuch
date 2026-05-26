from fuel_calculator import calculate_jannis_fuel_debt, calculate_lukas_fuel_debt, FUEL_COST_PER_LITRE, TOTAL_FUEL_CAPACITY


def test_given_no_fuel_data_then_jannis_fuel_debt_is_zero():
    trips = [
        {"fuel_start": None, "fuel_end": None},
    ]

    result = calculate_jannis_fuel_debt(trips)

    assert result == 0.0


def test_given_no_fuel_data_then_lukas_fuel_debt_is_zero():
    trips = [
        {"fuel_start": None, "fuel_end": None},
        {"fuel_start": None, "fuel_end": None},
    ]

    result = calculate_lukas_fuel_debt(trips)

    assert result == 0.0


def test_given_jannis_returns_car_with_less_fuel_then_jannis_has_fuel_debt():
    trips = [
        {"fuel_start": 10, "fuel_end": 0},
    ]

    result = calculate_jannis_fuel_debt(trips)

    assert result == round(10 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_jannis_returns_car_with_more_fuel_then_jannis_has_negative_fuel_debt():
    trips = [
        {"fuel_start": 5, "fuel_end": 10},
    ]

    result = calculate_jannis_fuel_debt(trips)

    assert result == round(-5 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_lukas_returns_car_with_less_fuel_then_lukas_has_fuel_debt():
    trips = [
        {"fuel_start": 10, "fuel_end": 10},
        {"fuel_start": 7, "fuel_end": 7},
    ]

    result = calculate_lukas_fuel_debt(trips)

    assert result == round(3 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_given_lukas_returns_car_with_more_fuel_then_lukas_has_negative_fuel_debt():
    trips = [
        {"fuel_start": 7, "fuel_end": 7},
        {"fuel_start": 10, "fuel_end": 10},
    ]

    result = calculate_lukas_fuel_debt(trips)

    assert result == round(-3 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)

