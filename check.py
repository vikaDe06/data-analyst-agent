import pandas as pd

df = pd.read_csv("data/sales.csv")
df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

print("Top region:", df.groupby("region")["revenue_aed"].sum().idxmax())
print("Orders in March 2025:", (df["month"] == "2025-03").sum())
print("Average Laptop discount:", round(df.loc[df["product"] == "Laptop", "discount"].mean(), 4))
print("Total Phone revenue:", round(df.loc[df["product"] == "Phone", "revenue_aed"].sum(), 2))