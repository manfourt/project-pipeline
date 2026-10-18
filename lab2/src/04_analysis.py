from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

storage_options = {
    "key": "admin",
    "secret": "password",
    "client_kwargs": {
        "endpoint_url": "http://localhost:9000"
    }
}

# чтение Parquet из MinIO
df = pd.read_parquet(
    "s3://air-quality/processed/air_quality.parquet",
    storage_options=storage_options
)
print(df.head())

# 1. средние концентрации загрязнителей по городам за 2023-2024
result1 = (
    df.groupby(["city", "region"])
    .agg(
        pm2_5=("pm2_5", "mean"),
        pm10=("pm10", "mean"),
        no2=("nitrogen_dioxide", "mean"),
        so2=("sulphur_dioxide", "mean"),
        co=("carbon_monoxide", "mean"),
        us_aqi=("us_aqi", "mean")
    )
    .round(1)
    .sort_values("pm2_5", ascending=False)
    .reset_index()
)
print(result1)

# 2. средние, минимальные и максимальные значения NO2 и SO2 по годам (все города)
result2 = (
    df.groupby("year")
    .agg(
        no2_avg=("nitrogen_dioxide", "mean"),
        no2_max=("nitrogen_dioxide", "max"),
        so2_avg=("sulphur_dioxide", "mean"),
        so2_max=("sulphur_dioxide", "max")
    )
    .round(1)
    .reset_index()
)
print(result2)

# 3. сезонность: средний PM2.5 по месяцам (все города)
result3 = (
    df.groupby("month")["pm2_5"].mean()
    .round(1)
    .reset_index()
)
print(result3)

# сохранение результатов анализа в analytics/
result1.to_parquet(
    "s3://air-quality/analytics/avg_pollution_by_city.parquet",
    storage_options=storage_options,
    index=False
)
result2.to_parquet(
    "s3://air-quality/analytics/no2_so2_by_year.parquet",
    storage_options=storage_options,
    index=False
)
result3.to_parquet(
    "s3://air-quality/analytics/pm2_5_by_month.parquet",
    storage_options=storage_options,
    index=False
)

# график 1: средний PM2.5 по городам
result1.sort_values("pm2_5").plot(
    x="city",
    y="pm2_5",
    kind="barh",
    figsize=(10, 7),
    legend=False
)
plt.title("Средняя концентрация PM2.5 по городам, 2023–2024")
plt.xlabel("PM2.5, мкг/м³")
plt.ylabel("Город")
plt.grid(axis="x")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "pm2_5_by_city.png")
plt.show()

# график 2: сезонность PM2.5
result3.plot(
    x="month",
    y="pm2_5",
    marker="o",
    figsize=(10, 5),
    legend=False
)
plt.title("Средняя концентрация PM2.5 по месяцам (20 городов), 2023–2024")
plt.xlabel("Месяц")
plt.ylabel("PM2.5, мкг/м³")
plt.xticks(range(1, 13))
plt.grid()
plt.tight_layout()
plt.savefig(CHARTS_DIR / "pm2_5_by_month.png")
plt.show()