import pytest
from report_calculator import calculate_report


def test_given_empty_results_when_calculate_report_then_returns_empty_rows_and_zero_totals():
    results = []

    report = calculate_report(results)

    assert report["rows"] == []
    assert report["totals"]["total_owner_cost"] == 0.0
    assert report["totals"]["total_renter_cost"] == 0.0
    assert report["totals"]["total_owner_fuel"] == 0.0
    assert report["totals"]["total_renter_fuel"] == 0.0
    assert report["totals"]["owner_grand_total"] == 0.0
    assert report["totals"]["renter_grand_total"] == 0.0
    assert report["totals"]["grand_renter_debt"] == 0.0


def test_given_single_row_with_zero_values_when_calculate_report_then_all_values_are_zero():
    results = [("2025-01", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)]

    report = calculate_report(results)

    row = report["rows"][0]
    assert row["month"] == "2025-01"
    assert row["owner_km"] == 0.0
    assert row["owner_percentage"] == 0.0
    assert row["owner_cost"] == 0.0
    assert row["owner_fuel_debt"] == 0.0
    assert row["owner_total"] == 0.0
    assert row["renter_km"] == 0.0
    assert row["renter_percentage"] == 0.0
    assert row["renter_cost"] == 0.0
    assert row["renter_fuel_debt"] == 0.0
    assert row["renter_total"] == 0.0
    assert row["renter_debt"] == 0.0


def test_given_single_row_when_calculate_report_then_row_totals_are_computed_correctly():
    results = [("2025-01", 100.0, 50.0, 108.33, 100.0, 50.0, 108.33, 10.80, 5.40)]

    report = calculate_report(results)

    row = report["rows"][0]
    assert row["month"] == "2025-01"
    assert row["owner_km"] == 100.0
    assert row["owner_percentage"] == 50.0
    assert row["owner_cost"] == 108.33
    assert row["owner_fuel_debt"] == 10.80
    assert row["owner_total"] == pytest.approx(119.13)
    assert row["renter_km"] == 100.0
    assert row["renter_percentage"] == 50.0
    assert row["renter_cost"] == 108.33
    assert row["renter_fuel_debt"] == 5.40
    assert row["renter_total"] == pytest.approx(113.73)
    assert row["renter_debt"] == pytest.approx(102.93)


def test_given_single_row_when_calculate_report_then_grand_totals_are_computed_correctly():
    results = [("2025-01", 100.0, 50.0, 108.33, 100.0, 50.0, 108.33, 10.80, 5.40)]

    report = calculate_report(results)

    totals = report["totals"]
    assert totals["total_owner_cost"] == pytest.approx(108.33)
    assert totals["total_renter_cost"] == pytest.approx(108.33)
    assert totals["total_owner_fuel"] == pytest.approx(10.80)
    assert totals["total_renter_fuel"] == pytest.approx(5.40)
    assert totals["owner_grand_total"] == pytest.approx(119.13)
    assert totals["renter_grand_total"] == pytest.approx(113.73)
    assert totals["grand_renter_debt"] == pytest.approx(102.93)


def test_given_multiple_rows_when_calculate_report_then_grand_totals_sum_all_rows():
    results = [
        ("2025-01", 100.0, 50.0, 108.33, 100.0, 50.0, 108.33, 10.80, 5.40),
        ("2025-02", 200.0, 66.7, 144.44, 100.0, 33.3, 72.22, 0.0, 16.20),
    ]

    report = calculate_report(results)

    totals = report["totals"]
    assert totals["total_owner_cost"] == pytest.approx(252.77)
    assert totals["total_renter_cost"] == pytest.approx(180.55)
    assert totals["total_owner_fuel"] == pytest.approx(10.80)
    assert totals["total_renter_fuel"] == pytest.approx(21.60)
    assert totals["owner_grand_total"] == pytest.approx(263.57)
    assert totals["renter_grand_total"] == pytest.approx(202.15)
    assert totals["grand_renter_debt"] == pytest.approx(191.35)


def test_given_multiple_rows_when_calculate_report_then_each_row_is_mapped_correctly():
    results = [
        ("2025-01", 100.0, 50.0, 108.33, 100.0, 50.0, 108.33, 10.80, 5.40),
        ("2025-02", 200.0, 66.7, 144.44, 100.0, 33.3, 72.22, 0.0, 16.20),
    ]

    report = calculate_report(results)

    assert len(report["rows"]) == 2
    assert report["rows"][0]["month"] == "2025-01"
    assert report["rows"][1]["month"] == "2025-02"


def test_given_renter_fuel_debt_higher_than_owner_fuel_debt_when_calculate_report_then_renter_debt_is_positive():
    results = [("2025-01", 50.0, 25.0, 54.17, 150.0, 75.0, 162.50, 0.0, 21.60)]

    report = calculate_report(results)

    row = report["rows"][0]
    assert row["renter_debt"] == pytest.approx(184.10)


def test_given_owner_fuel_debt_higher_than_renter_fuel_debt_when_calculate_report_then_renter_debt_is_reduced():
    results = [("2025-01", 150.0, 75.0, 162.50, 50.0, 25.0, 54.17, 21.60, 0.0)]

    report = calculate_report(results)

    row = report["rows"][0]
    assert row["renter_total"] == pytest.approx(54.17)
    assert row["renter_debt"] == pytest.approx(32.57)

