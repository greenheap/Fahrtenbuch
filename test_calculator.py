import pytest

from calculator import calculate_monthly_costs, MONTHLY_PAUSCHALE


def test_empty_list():
    results = calculate_monthly_costs([])
    assert results == []

def test_given_invalid_km_then_throw_exception():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "jannis_km": 100.0,
         "fuel_level": 10},
        {"datum": "2026-05-10",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1400.0,
         "jannis_km": 200.0,
         "fuel_level": 8},
    ]
    with pytest.raises(ValueError):
        calculate_monthly_costs(trips)


def test_100_percent():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "jannis_km": 100.0,
         "fuel_level": 10},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    month, jannis_km, jannis_percentage, jannis_costs, lukas_km, lukas_percentage, lukas_costs = results[0]

    assert month == "2026-05"
    assert jannis_km == 100.0
    assert lukas_km == 0.0
    assert round(jannis_percentage, 1) == 100.0
    assert round(lukas_percentage, 1) == 0.0
    assert round(jannis_costs, 2) == round(MONTHLY_PAUSCHALE * 1.0, 2)
    assert round(lukas_costs, 2) == 0.0


def test_75_percentage_split():
    trips = [
        {"datum": "2026-05-01",
         "month": "2026-05",
         "km_start": 1000.0,
         "km_end": 1100.0,
         "jannis_km": 100.0,
         "fuel_level": 10},
        {"datum": "2026-05-10",
         "month": "2026-05",
         "km_start": 1200.0,
         "km_end": 1400.0,
         "jannis_km": 200.0,
         "fuel_level": 8},
    ]

    results = calculate_monthly_costs(trips)

    assert len(results) == 1
    month, jannis_km, jannis_percentage, jannis_costs, lukas_km, lukas_percentage, lukas_costs = results[0]

    assert month == "2026-05"
    assert jannis_km == 300.0
    assert lukas_km == 100.0
    assert round(jannis_percentage, 1) == 75.0
    assert round(lukas_percentage, 1) == 25.0
    assert round(jannis_costs, 2) == round(MONTHLY_PAUSCHALE * 0.75, 2)
    assert round(lukas_costs, 2) == round(MONTHLY_PAUSCHALE * 0.25, 2)

