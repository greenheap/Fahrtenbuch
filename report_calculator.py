def calculate_report(results):
    rows = [__calculate_row(*result) for result in results]
    total_owner_cost = sum(row["owner_cost"] for row in rows)
    total_renter_cost = sum(row["renter_cost"] for row in rows)
    total_owner_fuel = sum(row["owner_fuel_debt"] for row in rows)
    total_renter_fuel = sum(row["renter_fuel_debt"] for row in rows)
    owner_grand_total = total_owner_cost + total_owner_fuel
    renter_grand_total = total_renter_cost + total_renter_fuel
    grand_renter_debt = renter_grand_total - total_owner_fuel
    return {
        "rows": rows,
        "totals": {
            "total_owner_cost": total_owner_cost,
            "total_renter_cost": total_renter_cost,
            "total_owner_fuel": total_owner_fuel,
            "total_renter_fuel": total_renter_fuel,
            "owner_grand_total": owner_grand_total,
            "renter_grand_total": renter_grand_total,
            "grand_renter_debt": grand_renter_debt,
        },
    }


def __calculate_row(month, owner_km, owner_percentage, owner_cost, renter_km, renter_percentage, renter_cost, owner_fuel_debt, renter_fuel_debt):
    owner_total = owner_cost + owner_fuel_debt
    renter_total = renter_cost + renter_fuel_debt
    renter_debt = renter_total - owner_fuel_debt
    return {
        "month": month,
        "owner_km": owner_km,
        "owner_percentage": owner_percentage,
        "owner_cost": owner_cost,
        "owner_fuel_debt": owner_fuel_debt,
        "owner_total": owner_total,
        "renter_km": renter_km,
        "renter_percentage": renter_percentage,
        "renter_cost": renter_cost,
        "renter_fuel_debt": renter_fuel_debt,
        "renter_total": renter_total,
        "renter_debt": renter_debt,
    }

