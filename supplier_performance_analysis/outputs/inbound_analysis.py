import pandas as pd

# Load dataset
df = pd.read_csv("inbound_compras.csv")
# print("\nRows:", len(df))

# Convert date columns to datetime
date_cols = ["order_date", "dispatch_date", "receipt_date"]

for col in date_cols:
    df[col] = pd.to_datetime(df[col])
# print(df.dtypes)

# Calculate Lead Time (days)
df["lead_time_days"] = (df["receipt_date"] - df["order_date"]).dt.days
# print(df[["order_id", "supplier", "lead_time_days"]].head())

# Average lead time per supplier
supplier_lead_time = (
    df
    .groupby("supplier")["lead_time_days"]
    .mean()
    .sort_values()
)
# print(supplier_lead_time)

# Lead time variability per supplier
supplier_variability = (
    df
    .groupby("supplier")["lead_time_days"]
    .std()
    .sort_values()
)
# print(supplier_variability)

# Cost per unit
df["cost_per_unit"] = df["transport_cost"] / df["quantity_ordered"]
supplier_cpu = (
    df
    .groupby("supplier")["cost_per_unit"]
    .mean()
    .sort_values()
)
# print(supplier_cpu)

# Normalize lead time and cost per unit
df["lead_time_norm"] = (
    df["lead_time_days"] - df["lead_time_days"].min()
) / (
    df["lead_time_days"].max() - df["lead_time_days"].min()
)

df["cost_norm"] = (
    df["cost_per_unit"] - df["cost_per_unit"].min()
) / (
    df["cost_per_unit"].max() - df["cost_per_unit"].min()
)

# Combined score (lower is better)
df["supplier_score"] = df["lead_time_norm"] + df["cost_norm"]

supplier_score = (
    df
    .groupby("supplier")["supplier_score"]
    .mean()
    .sort_values()
)
# print(supplier_score)

# Variables Weights (Give a weight by the importance of each one for the company)
w_time = 1
w_cost = 1.5

# Weighted score
df["weighted_score"] = (
    df["lead_time_norm"] * w_time +
    df["cost_norm"] * w_cost
)

supplier_weighted_score = (
    df
    .groupby("supplier")["weighted_score"]
    .mean()
    .sort_values()
)

print(supplier_weighted_score)

#Save calculated data as new csv
#df.to_csv(
#    "inbound_compras_enriched.csv",
#    index=False
#)

#Kpi's dataframe
supplier_kpis = (
    df
    .groupby("supplier")
    .agg(
        avg_lead_time=("lead_time_days", "mean"),
        std_lead_time=("lead_time_days", "std"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
        weighted_score=("weighted_score", "mean")
    )
    .sort_values("weighted_score")
    .reset_index()
)

#Save supplier_kpis as csv
#supplier_kpis.to_csv(
#    "supplier_kpis.csv",
#    index=False
#)

#Visuals
import matplotlib.pyplot as plt

#Bar chart suppliers lead times
plt.figure()
plt.bar(
    supplier_kpis["supplier"],
    supplier_kpis["avg_lead_time"],
    color="#5B2C6F",
    edgecolor="#291444",
    linewidth=1.2
)
plt.title("Average Lead Time per Supplier")
plt.ylabel("Days")
plt.xlabel("Supplier")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#Scatter plot lead time and cost per unit by each supplier
plt.figure()
plt.scatter(
    supplier_kpis["avg_lead_time"],
    supplier_kpis["avg_cost_per_unit"]
)

for _, row in supplier_kpis.iterrows():
    plt.text(
        row["avg_lead_time"] + 0.1,
        row["avg_cost_per_unit"] + 0.1,
        row["supplier"]
    )

plt.xlabel("Average Lead Time (days)")
plt.ylabel("Average Cost per Unit")
plt.title("Cost vs Lead Time by Supplier")
plt.tight_layout()
plt.show()
