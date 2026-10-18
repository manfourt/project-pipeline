import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

# список городов в том же порядке, что и в запросе к API (сохранён в 01_fetch_api.py)
cities = pd.read_parquet(DATA_DIR / "cities.parquet")

# читаем исходный JSON
with open(DATA_DIR / "air_quality_raw.json", encoding="utf-8") as file:
    data = json.load(file)

# JSON -> DataFrame: у каждого города берём объект hourly и добавляем город и регион
frames = []
for i, item in enumerate(data):
    df_city = pd.DataFrame(item["hourly"])
    df_city["city"] = cities.loc[i, "city"]
    df_city["region"] = cities.loc[i, "region"]
    frames.append(df_city)
df = pd.concat(frames, ignore_index=True)

# анализ качества данных
print('Количество строк:', len(df))
print('Колонки:', df.columns)
print('Пропуски в колонках:', df.isna().sum())
print('Типы колонок:', df.dtypes)
print('Дубликаты', df.duplicated().sum())
print('Дубликаты город + время', df.duplicated(subset=['city', 'time']).sum())

# ---------- Преобразования ----------

# удаление строк без значений загрязнителей
pollutants = ["pm2_5", "pm10", "carbon_monoxide", "nitrogen_dioxide",
              "sulphur_dioxide", "ozone", "us_aqi"]
df = df.dropna(subset=pollutants)

# удаление дубликатов: одна запись на город и час
df = df.drop_duplicates(subset=["city", "time"])

# приведение типов: строка "2024-01-01T00:00" -> дата и время
df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%dT%H:%M")

# новые измерения для группировки: год и месяц
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month

# структурные преобразования: сначала измерения, потом факты
df = df[["city", "region", "time", "year", "month"] + pollutants]

print(df.head())
print('Количество строк:', len(df))
print('Типы колонок:', df.dtypes)

# ---------- Сохранение в Parquet ----------
df.to_parquet(
    DATA_DIR / "air_quality.parquet",
    index=False
)
