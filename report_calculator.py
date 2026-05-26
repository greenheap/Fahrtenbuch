from calculator import MonthlyCostResult


def calculate_report(results: list[MonthlyCostResult]):
    rows = [_calculate_row(result) for result in results]
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


def _calculate_row(result: MonthlyCostResult):
    owner_total = result.owner_costs + result.owner_fuel_debt
    renter_total = result.renter_costs + result.renter_fuel_debt
    renter_debt = renter_total - result.owner_fuel_debt
    return {
        "month": result.month,
        "owner_km": result.owner_km,
        "owner_percentage": result.owner_km_percentage,
        "owner_cost": result.owner_costs,
        "owner_fuel_debt": result.owner_fuel_debt,
        "owner_total": owner_total,
        "renter_km": result.renter_km,
        "renter_percentage": result.renter_km_percentage,
        "renter_cost": result.renter_costs,
        "renter_fuel_debt": result.renter_fuel_debt,
        "renter_total": renter_total,
        "renter_debt": renter_debt,
    }
