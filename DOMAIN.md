# Fahrtenbuch — Domain & Business Logic Documentation

## Overview

This application calculates the monthly cost split between two parties sharing a car:
- **Owner** : the car owner, who drives the car and records every trip
- **Renter** : the renter, who uses the car between owner trips

The yearly cost (Pauschale) is split proportionally by kilometers driven each month.

---

## CSV Input Format

File: `fahrtenbuch.csv`

```
datum,km_start,km_end,fuel_start(1-20),fuel_end(1-20),fuel_price
```

| Column | Type | Required | Description |
|---|---|---|---|
| `datum` | `YYYY-MM-DD` | yes | Date of the owner's trip |
| `km_start` | float | yes | Odometer reading at trip start |
| `km_end` | float | yes | Odometer reading at trip end |
| `fuel_start(1-20)` | int 0–20 | yes | Fuel level at trip start (scale of 20) |
| `fuel_end(1-20)` | int 0–20 | yes | Fuel level at trip end (scale of 20) |
| `fuel_price` | float | **no** | Price per litre at time of fuelling. Falls back to `DEFAULT_FUEL_PRICE_PER_LITRE` (2.00 EUR) if absent or empty |

Every row represents exactly one **owner trip**. There are no renter trip rows.

---

## Fuel Scale

The fuel gauge is modelled as a scale from **0 to 20** (matching the car's display), mapping to the tank's physical capacity:

```
1 unit = TOTAL_FUEL_CAPACITY / 20 litres
       = 54 / 20
       = 2.7 litres
```

---

## Kilometer Logic

### Owner kilometers
The owner's km for a month is the sum of `km_end - km_start` across all owner trips in that month.

### Renter kilometers
The renter drives in the **gaps between owner trips**. Renter km is derived, not recorded:

```
total_km = last_km_end_of_month - first_km_start_of_month
           (or: last_km_end_of_month - prev_month_last_km_end, if the renter crossed into this month)

renter_km = max(0, total_km - owner_km)
```

---

## Fuel Debt Logic

Fuel debts express **who owes whom** for fuel consumption. A **positive** value means the party owes money; a **negative** value means they are owed money (they put in more than they used).

### Owner fuel debt (`calculate_owner_fuel_debt`)

Calculated per trip. If the owner ends a trip with less fuel than they started, they consumed fuel and owe money. If they end with more, they refuelled and are owed money.

```
for each trip:
    delta = fuel_end - fuel_start
    price = trip.fuel_price or DEFAULT_FUEL_PRICE_PER_LITRE
    owner_fuel_debt += -delta * litres_per_unit * price
```

### Renter fuel debt (`calculate_renter_fuel_debt`)

The renter's fuel consumption is derived from the **gaps between consecutive owner trips** — i.e. the difference between `trip[i].fuel_start` and `trip[i-1].fuel_end`. The price used is the `fuel_price` of `trip[i]` (the next owner trip, where the fuel level was re-recorded).

For the first trip of a month, the gap is measured from the previous month's last `fuel_end` (passed in as `prev_month_fuel_end`).

```
# Cross-month gap (if prev_month_fuel_end is known):
delta = trip[0].fuel_start - prev_month_fuel_end
price = trip[0].fuel_price or DEFAULT_FUEL_PRICE_PER_LITRE
renter_fuel_debt += -delta * litres_per_unit * price

# Within-month gaps:
for i in 1..n:
    delta = trip[i].fuel_start - trip[i-1].fuel_end
    price = trip[i].fuel_price or DEFAULT_FUEL_PRICE_PER_LITRE
    renter_fuel_debt += -delta * litres_per_unit * price
```

**fuel_price fallback:** If `fuel_price` is `None` or absent on a trip, `DEFAULT_FUEL_PRICE_PER_LITRE = 2.00` EUR/litre is used.

---

## Cost Split Logic

The monthly Pauschale (`YEARLY_PAUSCHALE / 12`) is split by km share:

```
owner_costs  = MONTHLY_PAUSCHALE * (owner_km / total_km)
renter_costs = MONTHLY_PAUSCHALE * (renter_km / total_km)
```

If `total_km == 0` for a month, km costs are `0.0` for both parties, but fuel debts are still calculated.

---

## Report / Final Debt

The `renter_debt` per month is:

```
renter_debt = (renter_costs + renter_fuel_debt) - owner_fuel_debt
```

The owner's fuel debt is subtracted because the owner refuelling effectively benefits the renter (the renter inherits a fuller tank).

---

## Constants

| Constant | Value | Location |
|---|---|---|
| `YEARLY_PAUSCHALE` | 2600.00 EUR | `calculator.py` |
| `MONTHLY_PAUSCHALE` | `2600 / 12` EUR | `calculator.py` |
| `TOTAL_FUEL_CAPACITY` | 54 litres | `fuel_calculator.py` |
| `DEFAULT_FUEL_PRICE_PER_LITRE` | 2.00 EUR | `fuel_calculator.py` |

---

## Module Overview

| Module | Responsibility |
|---|---|
| `trip_loader.py` | Parses `fahrtenbuch.csv` into a list of trip dicts |
| `calculator.py` | Aggregates trips into monthly `MonthlyCostResult` objects |
| `fuel_calculator.py` | Calculates owner and renter fuel debts per month |
| `report_calculator.py` | Aggregates monthly results into a printable report with totals |
| `main.py` | Entry point; prints the formatted report to stdout |

