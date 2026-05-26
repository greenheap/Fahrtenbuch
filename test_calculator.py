import pytest

from calculator import calculate_monthly_costs, MONTHLY_PAUSCHALE
from fuel_calculator import FUEL_COST_PER_LITRE, TOTAL_FUEL_CAPACITY


def test_empty_list():
    results = calculate_monthly_costs([])
    assert results == []

def test_given_first_trip_km_start_equals_second_trip_km_start_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "jannis_km": 100.0, "fuel_start": None, "fuel_end": None},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1000.0, "km_end": 1400.0, "jannis_km": 200.0, "fuel_start": None, "fuel_end": None},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_trip_with_km_end_less_than_km_start_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1100.0, "km_end": 1000.0, "jannis_km": -100.0, "fuel_start": None, "fuel_end": None},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_second_trip_km_start_before_first_trip_km_end_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1200.0, "jannis_km": 200.0, "fuel_start": None, "fuel_end": None},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1150.0, "km_end": 1400.0, "jannis_km": 250.0, "fuel_start": None, "fuel_end": None},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_no_fuel_data_then_fuel_debt_is_zero():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "jannis_km": 100.0, "fuel_start": None, "fuel_end": None},
    ]

    results = calculate_monthly_costs(trips)

    month, j_km, j_pct, j_cost, l_km, l_pct, l_cost, j_fuel_debt, l_fuel_debt = results[0]
    assert j_fuel_debt == 0.0
    assert l_fuel_debt == 0.0


def test_given_jannis_returns_car_with_less_fuel_then_jannis_has_fuel_debt():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "jannis_km": 100.0, "fuel_start": 10, "fuel_end": 0},
    ]

    results = calculate_monthly_costs(trips)

    month, j_km, j_pct, j_cost, l_km, l_pct, l_cost, j_fuel_debt, l_fuel_debt = results[0]
    assert j_fuel_debt == round(10 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)
    assert l_fuel_debt == 0.0

def test_given_lukas_drives_between_trips_and_returns_less_fuel_then_lukas_has_fuel_debt():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "jannis_km": 100.0, "fuel_start": 10, "fuel_end": 10},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1200.0, "km_end": 1400.0, "jannis_km": 200.0, "fuel_start": 7, "fuel_end": 7},
    ]

    results = calculate_monthly_costs(trips)

    month, j_km, j_pct, j_cost, l_km, l_pct, l_cost, j_fuel_debt, l_fuel_debt = results[0]
    assert j_fuel_debt == 0.0
    assert l_fuel_debt == round(3 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_100_percent():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "jannis_km": 100.0, "fuel_start": None, "fuel_end": None},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    month, jannis_km, jannis_percentage, jannis_costs, lukas_km, lukas_percentage, lukas_costs, j_fuel_debt, l_fuel_debt = results[0]

    assert month == "2026-05"
    assert jannis_km == 100.0
    assert lukas_km == 0.0
    assert round(jannis_percentage, 1) == 100.0
    assert round(lukas_percentage, 1) == 0.0
    assert round(jannis_costs, 2) == round(MONTHLY_PAUSCHALE * 1.0, 2)
    assert round(lukas_costs, 2) == 0.0


def test_75_percentage_split():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "jannis_km": 100.0, "fuel_start": None, "fuel_end": None},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1200.0, "km_end": 1400.0, "jannis_km": 200.0, "fuel_start": None, "fuel_end": None},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    month, jannis_km, jannis_percentage, jannis_costs, lukas_km, lukas_percentage, lukas_costs, j_fuel_debt, l_fuel_debt = results[0]

    assert month == "2026-05"
    assert jannis_km == 300.0
    assert lukas_km == 100.0
    assert round(jannis_percentage, 1) == 75.0
    assert round(lukas_percentage, 1) == 25.0
    assert round(jannis_costs, 2) == round(MONTHLY_PAUSCHALE * 0.75, 2)
    assert round(lukas_costs, 2) == round(MONTHLY_PAUSCHALE * 0.25, 2)
