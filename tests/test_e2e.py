import textwrap

import pytest

from main import load_trips_and_calculate_results
from calculator import MONTHLY_PAUSCHALE


E2E_CSV = textwrap.dedent("""\
    datum,km_start,km_end,fuel_start(1-20),fuel_end(1-20),fuel_price
    2026-05-01,1000,1100,10,0,
    2026-06-01,1200,1300,20,10,
""")


def test_given_no_csv_file_then_exception_is_raised(tmp_path):
    missing_file = str(tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError):
        load_trips_and_calculate_results(missing_file, start_date=None)


def test_given_two_months_with_renter_gap_then_results_show_correct_km_split_and_costs(tmp_path):
    csv_file = tmp_path / "fahrtenbuch.csv"
    csv_file.write_text(E2E_CSV)

    results = load_trips_and_calculate_results(str(csv_file), start_date=None)

    assert len(results) == 2
    may = results[0]
    june = results[1]
    assert may.month == "2026-05"
    assert may.owner_km == 100.0
    assert may.renter_km == 0.0
    assert round(may.owner_km_percentage, 1) == 100.0
    assert round(may.owner_costs, 2) == round(MONTHLY_PAUSCHALE * 1.0, 2)
    assert may.owner_fuel_debt == 54.0
    assert may.renter_fuel_debt == 0.0
    assert june.month == "2026-06"
    assert june.owner_km == 100.0
    assert june.renter_km == 100.0
    assert round(june.owner_km_percentage, 1) == 50.0
    assert round(june.renter_km_percentage, 1) == 50.0
    assert round(june.owner_costs, 2) == round(MONTHLY_PAUSCHALE * 0.5, 2)
    assert round(june.renter_costs, 2) == round(MONTHLY_PAUSCHALE * 0.5, 2)
    assert june.owner_fuel_debt == 54.0
    assert june.renter_fuel_debt == -108.0

# todo more  complex tests