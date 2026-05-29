import pytest
from unittest.mock import patch, mock_open

from trip_loader import load_trips, _parse_fuel


def make_csv(rows):
    header = "datum,km_start,km_end,fuel_start(1-20),fuel_end(1-20),fuel_price\n"
    return header + "\n".join(rows)


def test_given_missing_fuel_start_when_loading_then_raises_value_error():
    csv_content = make_csv(["2026-05-01,1000,1100,,10"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError):
            load_trips()


def test_given_missing_fuel_end_when_loading_then_raises_value_error():
    csv_content = make_csv(["2026-05-01,1000,1100,10,"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError):
            load_trips()


def test_given_fuel_start_out_of_range_when_loading_then_raises_value_error():
    csv_content = make_csv(["2026-05-01,1000,1100,21,10"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError):
            load_trips()


def test_given_fuel_end_out_of_range_when_loading_then_raises_value_error():
    csv_content = make_csv(["2026-05-01,1000,1100,10,21"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError):
            load_trips()


def test_given_invalid_fuel_value_when_parsing_then_raises_value_error():
    with pytest.raises(ValueError):
        _parse_fuel("abc", 2, "fuel_start")


def test_given_empty_csv_when_loading_then_returns_empty_list():
    csv_content = make_csv([])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = load_trips()

    assert result == []


def test_given_invalid_date_format_when_loading_then_raises_value_error():
    csv_content = make_csv(["01.05.2026,1000,1100,10,10"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError):
            load_trips()


def test_given_km_end_less_than_km_start_when_loading_then_raise_value_error():
    csv_content = make_csv(["2026-05-01,1100,1000,10,10"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError):
            load_trips()

def test_given_valid_row_when_loading_then_returns_correct_trip():
    csv_content = make_csv(["2026-05-01,1000,1100,10,8,2.40"])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = load_trips()

    assert len(result) == 1
    trip = result[0]
    assert trip["datum"] == "2026-05-01"
    assert trip["month"] == "2026-05"
    assert trip["km_start"] == 1000.0
    assert trip["km_end"] == 1100.0
    assert trip["owner_km"] == 100.0
    assert trip["fuel_start"] == 10
    assert trip["fuel_end"] == 8
    assert trip["fuel_price"] == 2.40


def test_given_multiple_valid_rows_when_loading_then_returns_all_trips():
    csv_content = make_csv([
        "2026-05-01,1000,1100,10,8",
        "2026-05-10,1100,1300,8,5",
    ])

    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = load_trips()

    assert len(result) == 2
    assert result[0]["owner_km"] == 100.0
    assert result[1]["owner_km"] == 200.0
    assert result[1]["fuel_price"] is None


def test_given_fuel_value_of_zero_when_parsing_then_returns_zero():
    result = _parse_fuel("0", 2, "fuel_start")

    assert result == 0


def test_given_fuel_value_of_twenty_when_parsing_then_returns_twenty():
    result = _parse_fuel("20", 2, "fuel_end")

    assert result == 20


def test_given_empty_raw_when_parsing_then_returns_none():
    result = _parse_fuel("", 2, "fuel_start")

    assert result is None

