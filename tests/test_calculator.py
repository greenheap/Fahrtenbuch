import calendar
from datetime import date

import pytest

from calculator import calculate_monthly_costs, MONTHLY_PAUSCHALE
from fuel_calculator import DEFAULT_FUEL_PRICE_PER_LITRE, TOTAL_FUEL_CAPACITY


def test_empty_list():
    with pytest.raises(ValueError):
        calculate_monthly_costs([])


def test_given_first_trip_km_start_equals_second_trip_km_start_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": 10, "fuel_end": 10},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1000.0, "km_end": 1400.0, "owner_km": 200.0, "fuel_start": 10, "fuel_end": 10},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_trip_with_km_end_less_than_km_start_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1100.0, "km_end": 1000.0, "owner_km": -100.0, "fuel_start": 10, "fuel_end": 10},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_second_trip_km_start_before_first_trip_km_end_then_throw_exception():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1200.0, "owner_km": 200.0, "fuel_start": 10, "fuel_end": 10},
        {"datum": "2026-05-10", "month": "2026-05", "km_start": 1150.0, "km_end": 1400.0, "owner_km": 250.0, "fuel_start": 10, "fuel_end": 10},
    ]

    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_given_owner_returns_car_with_less_fuel_then_owner_has_fuel_debt():
    trips = [
        {"datum": "2026-05-01", "month": "2026-05", "km_start": 1000.0, "km_end": 1100.0, "owner_km": 100.0, "fuel_start": 10, "fuel_end": 0},
    ]

    results = calculate_monthly_costs(trips)

    assert results[0].owner_fuel_debt == round(10 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)
    assert results[0].renter_fuel_debt == 0.0


def test_given_renter_drives_between_trips_and_returns_less_fuel_then_renter_has_fuel_debt():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 10},
        {"datum": "2026-05-10",
         "month": "2026-05",
         "km_start": 1200.0,
         "km_end": 1400.0,
         "owner_km": 200.0,
         "fuel_start": 7,
         "fuel_end": 7},
    ]

    results = calculate_monthly_costs(trips)

    assert results[0].owner_fuel_debt == 0.0
    assert results[0].renter_fuel_debt == round(3 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_renter_drives_between_trips_and_returns_more_fuel_then_renter_has_fuel_plus():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 10,
         "fuel_price": 3.90},
        {"datum": "2026-05-10",
         "month": "2026-05",
         "km_start": 1200.0,
         "km_end": 1200.0,
         "owner_km": 200.0,
         "fuel_start": 20,
         "fuel_end": 20,
         "fuel_price": 1.90},
    ]

    results = calculate_monthly_costs(trips)

    assert results[0].renter_fuel_debt == -51.3


def test_given_one_month_with_no_trips_then():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 1,
         "fuel_end": 2},
        {"datum": "2026-07-01",
         "month": "2026-07",
         "km_start": 1100.0,
         "km_end": 1200.0,
         "owner_km": 200.0,
         "fuel_start": 1,
         "fuel_end": 2},
    ]

    results = calculate_monthly_costs(trips)

    empty_month = results[1]
    assert empty_month.month == "2026-06"
    assert empty_month.owner_km == 0.0
    assert empty_month.renter_km == 0.0
    assert empty_month.owner_costs == 0.0
    assert empty_month.renter_costs == 0.0
    assert empty_month.owner_fuel_debt == 0.0
    assert empty_month.renter_fuel_debt == 0.0


def test_100_percent():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 1,
         "fuel_end": 2},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    result = results[0]
    assert result.month == "2026-05"
    assert result.owner_km == 100.0
    assert result.renter_km == 0.0
    assert round(result.owner_km_percentage, 1) == 100.0
    assert round(result.renter_km_percentage, 1) == 0.0
    assert round(result.owner_costs, 2) == round(MONTHLY_PAUSCHALE * 1.0, 2)
    assert round(result.renter_costs, 2) == 0.0


def test_75_percentage_split():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 0,
         "fuel_end": 0},
        {"datum": "2026-05-10",
         "month": "2026-05",
         "km_start": 1200.0,
         "km_end": 1400.0,
         "owner_km": 200.0,
         "fuel_start": 0,
         "fuel_end": 0},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    result = results[0]
    assert result.month == "2026-05"
    assert result.owner_km == 300.0
    assert result.renter_km == 100.0
    assert round(result.owner_km_percentage, 1) == 75.0
    assert round(result.renter_km_percentage, 1) == 25.0
    assert round(result.owner_costs, 2) == round(MONTHLY_PAUSCHALE * 0.75, 2)
    assert round(result.renter_costs, 2) == round(MONTHLY_PAUSCHALE * 0.25, 2)


def test_given_start_date_mid_month_and_zero_km_then_costs_are_zero():
    trips = [
        {"datum": "2026-05-25",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1000.0,
         "owner_km": 0.0,
         "fuel_start": 10,
         "fuel_end": 10},
    ]
    start_date = date(2026, 5, 25)

    results = calculate_monthly_costs(trips, start_date=start_date)

    assert round(results[0].owner_costs, 2) == 0.0
    assert round(results[0].renter_costs, 2) == 0.0


def test_given_fuel_drop_between_months_then_renter_fuel_debt_is_charged_in_second_month():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 12},
        {"datum": "2026-06-01",
         "month": "2026-06",
         "km_start": 1200.0,
         "km_end": 1300.0,
         "owner_km": 100.0,
         "fuel_start": 0,
         "fuel_end": 0},
    ]

    results = calculate_monthly_costs(trips)

    may_result = results[0]
    june_result = results[1]
    assert may_result.renter_fuel_debt == 0.0
    assert june_result.renter_fuel_debt == round(12 * (TOTAL_FUEL_CAPACITY / 20) * DEFAULT_FUEL_PRICE_PER_LITRE, 2)


def test_given_trips_spanning_year_boundary_then_month_range_includes_all_months():
    trips = [
        {"datum": "2026-11-01",
         "month": "2026-11",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 10},
        {"datum": "2027-02-01",
         "month": "2027-02",
         "km_start": 1100.0,
         "km_end": 1200.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 10},
    ]

    results = calculate_monthly_costs(trips)

    months = [r.month for r in results]
    assert months == ["2026-11", "2026-12", "2027-01", "2027-02"]
    december = results[1]
    january = results[2]
    assert december.month == "2026-12"
    assert january.month == "2027-01"
    assert december.owner_costs == 0.0
    assert january.owner_costs == 0.0


def test_given_gap_between_months_then_gap_km_assigned_to_renter():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 10},
        {"datum": "2026-06-01",
         "month": "2026-06",
         "km_start": 1150.0,
         "km_end": 1250.0,
         "owner_km": 100.0,
         "fuel_start": 10,
         "fuel_end": 10},
    ]

    results = calculate_monthly_costs(trips)

    may_result = results[0]
    june_result = results[1]
    assert may_result.owner_km == 100.0
    assert may_result.renter_km == 0.0
    assert june_result.owner_km == 100.0
    assert june_result.renter_km == 50.0

