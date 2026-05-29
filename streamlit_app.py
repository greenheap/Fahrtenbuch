from datetime import date

import streamlit as st

from calculator import calculate_monthly_costs
from report_calculator import calculate_report
from repository import TripRepository

START_DATE = date(2026, 5, 25)


def build_report_dataframe(report):
    import pandas as pd
    rows = []
    for row in report["rows"]:
        rows.append({
            "Monat": row["month"],
            "Jannis km": row["owner_km"],
            "Jannis %": round(row["owner_percentage"], 1),
            "Jannis EUR": round(row["owner_cost"], 2),
            "Jannis Benzin": round(row["owner_fuel_debt"], 2),
            "Jannis Gesamt": round(row["owner_total"], 2),
            "Lukas km": row["renter_km"],
            "Lukas %": round(row["renter_percentage"], 1),
            "Lukas EUR": round(row["renter_cost"], 2),
            "Lukas Benzin": round(row["renter_fuel_debt"], 2),
            "Lukas Gesamt": round(row["renter_total"], 2),
            "Schulden Lukas": round(row["renter_debt"], 2),
        })
    totals = report["totals"]
    rows.append({
        "Monat": "GESAMT",
        "Jannis km": "",
        "Jannis %": "",
        "Jannis EUR": round(totals["total_owner_cost"], 2),
        "Jannis Benzin": round(totals["total_owner_fuel"], 2),
        "Jannis Gesamt": round(totals["owner_grand_total"], 2),
        "Lukas km": "",
        "Lukas %": "",
        "Lukas EUR": round(totals["total_renter_cost"], 2),
        "Lukas Benzin": round(totals["total_renter_fuel"], 2),
        "Lukas Gesamt": round(totals["renter_grand_total"], 2),
        "Schulden Lukas": round(totals["grand_renter_debt"], 2),
    })
    return pd.DataFrame(rows)


def render_add_trip_form(repository):
    st.header("Fahrt hinzufügen")
    latest_km_end = int(repository.get_latest_km_end() or 0)
    with st.form("add_trip_form"):
        trip_date = st.date_input("Datum", value=date.today())
        km_start = st.number_input("km Start", min_value=0, value=latest_km_end, step=5)
        km_end = st.number_input("km Ende", min_value=0, value=latest_km_end, step=5)
        fuel_start = st.number_input("Tank Start (0-20)", min_value=0, max_value=20, step=1)
        fuel_end = st.number_input("Tank Ende (0-20)", min_value=0, max_value=20, step=1)
        fuel_price_input = st.number_input("Benzinpreis EUR/L (optional, 0 = kein Eintrag)", min_value=0.0, step=0.1, format="%.2f")
        submitted = st.form_submit_button("Fahrt speichern")

    if submitted:
        if km_end < km_start:
            st.error("km Ende darf nicht kleiner als km Start sein.")
            return
        fuel_price = fuel_price_input if fuel_price_input > 0 else None
        trip = {
            "datum": trip_date.strftime("%Y-%m-%d"),
            "km_start": km_start,
            "km_end": km_end,
            "fuel_start": fuel_start,
            "fuel_end": fuel_end,
            "fuel_price": fuel_price,
        }
        repository.save_trip(trip)
        st.success(f"Fahrt vom {trip_date.strftime('%d.%m.%Y')} gespeichert.")


def render_report(repository):
    st.header("Monatsbericht")
    trips = repository.load_all_trips()
    if not trips:
        st.info("Noch keine Fahrten vorhanden.")
        return
    results = calculate_monthly_costs(trips, start_date=START_DATE)
    report = calculate_report(results)
    dataframe = build_report_dataframe(report)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)


def render_database_view(repository):
    st.header("Alle Einträge")
    trips = repository.load_all_trips()
    if not trips:
        st.info("Noch keine Einträge vorhanden.")
        return
    import pandas as pd
    rows = [
        {
            "Datum": trip["datum"],
            "km Start": trip["km_start"],
            "km Ende": trip["km_end"],
            "km": trip["owner_km"],
            "Tank Start": trip["fuel_start"],
            "Tank Ende": trip["fuel_end"],
            "Benzinpreis": trip["fuel_price"],
        }
        for trip in trips
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def main():
    st.title("Fahrtenbuch")
    repository = TripRepository()
    render_add_trip_form(repository)
    st.divider()
    col_report, col_db = st.columns(2)
    with col_report:
        if st.button("Bericht anzeigen"):
            render_report(repository)
    with col_db:
        if st.button("Datenbank anzeigen"):
            render_database_view(repository)


main()

