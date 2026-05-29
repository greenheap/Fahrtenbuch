import sqlite3


class TripRepository:
    def __init__(self, db_path="fahrtenbuch.db"):
        self._connection = sqlite3.connect(db_path)
        self._initialize_database()

    def _initialize_database(self):
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datum TEXT NOT NULL,
                km_start INTEGER NOT NULL,
                km_end INTEGER NOT NULL,
                fuel_start INTEGER NOT NULL,
                fuel_end INTEGER NOT NULL,
                fuel_price REAL
            )
        """)
        self._connection.commit()

    def save_trip(self, trip):
        self._connection.execute(
            "INSERT INTO trips (datum, km_start, km_end, fuel_start, fuel_end, fuel_price) VALUES (?, ?, ?, ?, ?, ?)",
            (trip["datum"], trip["km_start"], trip["km_end"], trip["fuel_start"], trip["fuel_end"], trip.get("fuel_price")),
        )
        self._connection.commit()

    def get_latest_km_end(self):
        cursor = self._connection.execute(
            "SELECT km_end FROM trips ORDER BY datum DESC, id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return int(row[0])

    def get_latest_fuel_end(self):
        cursor = self._connection.execute(
            "SELECT fuel_end FROM trips ORDER BY datum DESC, id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return row[0]

    def load_all_trips(self):
        cursor = self._connection.execute(
            "SELECT datum, km_start, km_end, fuel_start, fuel_end, fuel_price FROM trips ORDER BY datum, id"
        )
        return [self._row_to_trip(row) for row in cursor.fetchall()]

    def _row_to_trip(self, row):
        datum, km_start, km_end, fuel_start, fuel_end, fuel_price = row
        return {
            "datum": datum,
            "month": datum[:7],
            "km_start": int(km_start),
            "km_end": int(km_end),
            "owner_km": int(km_end) - int(km_start),
            "fuel_start": fuel_start,
            "fuel_end": fuel_end,
            "fuel_price": fuel_price,
        }
