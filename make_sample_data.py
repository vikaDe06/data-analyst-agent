import csv
import os
import random
from datetime import date, timedelta

random.seed(42)  # same random numbers every run, so results are repeatable

regions = ["North", "South", "East", "West"]
products = ["Laptop", "Phone", "Tablet", "Headphones"]
unit_price_aed = {"Laptop": 2500, "Phone": 1800, "Tablet": 1200, "Headphones": 350}

start = date(2025, 1, 1)
os.makedirs("data", exist_ok=True)

with open("data/sales.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "region", "product", "quantity", "discount", "revenue_aed"])
    for _ in range(500):
        order_date = start + timedelta(days=random.randint(0, 364))
        region = random.choice(regions)
        product = random.choice(products)
        quantity = random.randint(1, 5)
        discount = random.choice([0, 0.05, 0.10, 0.15])
        revenue = round(unit_price_aed[product] * quantity * (1 - discount), 2)
        writer.writerow([order_date.isoformat(), region, product, quantity, discount, revenue])

print("Wrote 500 rows to data/sales.csv")