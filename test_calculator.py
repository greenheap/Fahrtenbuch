import pytest

from calculator import calculate_monthly_costs, MONTHLY_PAUSCHALE
from fuel_calculator import FUEL_COST_PER_LITRE, TOTAL_FUEL_CAPACITY


def test_empty_list():
    results = calculate_monthly_costs([])
    assert results == []

def test_given_first_trip_km_start_equals_second_trip_km_start_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": None, "fuel_end": None},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1000.0, "km_end": 1400.0, "owner_km": 200.0, "fuel_start": None, "fuel_end": None},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_trip_with_km_end_less_than_km_start_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1100.0, "km_end": 1000.0, "owner_km": -100.0, "fuel_start": None, "fuel_end": None},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_second_trip_km_start_before_first_trip_km_end_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1200.0, "owner_km": 200.0, "fuel_start": None, "fuel_end": None},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1150.0, "km_end": 1400.0, "owner_km": 250.0, "fuel_start": None, "fuel_end": None},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_no_fuel_data_then_fuel_debt_is_zero():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": None, "fuel_end": None},
    ]

    results = calculate_monthly_costs(trips)

    month, owner_km, owner_percentage, owner_cost, renter_km, renter_percentage, renter_cost, owner_fuel_debt, renter_fuel_debt = results[0]
    assert owner_fuel_debt == 0.0
    assert renter_fuel_debt == 0.0


def test_given_owner_returns_car_with_less_fuel_then_owner_has_fuel_debt():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": 10, "fuel_end": 0},
    ]

    results = calculate_monthly_costs(trips)

    month, owner_km, owner_percentage, owner_cost, renter_km, renter_percentage, renter_cost, owner_fuel_debt, renter_fuel_debt = results[0]
    assert owner_fuel_debt == round(10 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)
    assert renter_fuel_debt == 0.0

def test_given_renter_drives_between_trips_and_returns_less_fuel_then_renter_has_fuel_debt():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": 10, "fuel_end": 10},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1200.0, "km_end": 1400.0, "owner_km": 200.0, "fuel_start": 7, "fuel_end": 7},
    ]

    results = calculate_monthly_costs(trips)

    month, owner_km, owner_percentage, owner_cost, renter_km, renter_percentage, renter_cost, owner_fuel_debt, renter_fuel_debt = results[0]
    assert owner_fuel_debt == 0.0
    assert renter_fuel_debt == round(3 * (TOTAL_FUEL_CAPACITY / 20) * FUEL_COST_PER_LITRE, 2)


def test_100_percent():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": None, "fuel_end": None},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    month, owner_km, owner_percentage, owner_costs, renter_km, renter_percentage, renter_costs, owner_fuel_debt, renter_fuel_debt = results[0]

    assert month == "2026-05"
    assert owner_km == 100.0
    assert renter_km == 0.0
    assert round(owner_percentage, 1) == 100.0
    assert round(renter_percentage, 1) == 0.0
    assert round(owner_costs, 2) == round(MONTHLY_PAUSCHALE * 1.0, 2)
    assert round(renter_costs, 2) == 0.0


def test_75_percentage_split():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": None, "fuel_end": None},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1200.0, "km_end": 1400.0, "owner_km": 200.0, "fuel_start": None, "fuel_end": None},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    month, owner_km, owner_percentage, owner_costs, renter_km, renter_percentage, renter_costs, owner_fuel_debt, renter_fuel_debt = results[0]

    assert month == "2026-05"
    assert owner_km == 300.0
    assert renter_km == 100.0
    assert round(owner_percentage, 1) == 75.0
    assert round(renter_percentage, 1) == 25.0
    assert round(owner_costs, 2) == round(MONTHLY_PAUSCHALE * 0.75, 2)
    assert round(renter_costs, 2) == round(MONTHLY_PAUSCHALE * 0.25, 2)
