import pytest
from repository import TripRepository
@pytest.fixture
def repository():
    return TripRepository(db_path=":memory:")
def test_given_empty_database_when_loading_all_trips_then_returns_empty_list(repository):
    result = repository.load_all_trips()
    assert result == []
def test_given_trip_without_fuel_price_when_saving_then_loads_with_fuel_price_none(repository):
    trip = {"datum": "2026-05-01", "km_start": 1000.0, "km_end": 1100.0, "fuel_start": 10, "fuel_end": 8, "fuel_price": None}
    repository.save_trip(trip)
    result = repository.load_all_trips()
    assert result[0]["fuel_price"] is None
def test_given_valid_trip_when_saving_then_loads_with_correct_fields(repository):
    trip = {"datum": "2026-05-01", "km_start": 1000.0, "km_end": 1100.0, "fuel_start": 10, "fuel_end": 8, "fuel_price": 2.40}
    repository.save_trip(trip)
    result = repository.load_all_trips()
    assert len(result) == 1
    loaded = result[0]
    assert loaded["datum"] == "2026-05-01"
    assert loaded["month"] == "2026-05"
    assert loaded["km_start"] == 1000.0
    assert loaded["km_end"] == 1100.0
    assert loaded["owner_km"] == 100.0
    assert loaded["fuel_start"] == 10
    assert loaded["fuel_end"] == 8
    assert loaded["fuel_price"] == 2.40
def test_given_multiple_trips_when_saving_then_loads_all_trips_in_insertion_order(repository):
    trip_one = {"datum": "2026-05-01", "km_start": 1000.0, "km_end": 1100.0, "fuel_start": 10, "fuel_end": 8, "fuel_price": None}
    trip_two = {"datum": "2026-05-10", "km_start": 1100.0, "km_end": 1300.0, "fuel_start": 8, "fuel_end": 5, "fuel_price": 1.90}
    repository.save_trip(trip_one)
    repository.save_trip(trip_two)
    result = repository.load_all_trips()
    assert len(result) == 2
    assert result[0]["datum"] == "2026-05-01"
    assert result[0]["owner_km"] == 100.0
    assert result[1]["datum"] == "2026-05-10"
    assert result[1]["owner_km"] == 200.0
    assert result[1]["fuel_price"] == 1.90
