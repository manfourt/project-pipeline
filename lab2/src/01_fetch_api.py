import json
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://air-quality-api.open-meteo.com/v1"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# подключение к MinIO
storage_options = {
    "key": "admin",
    "secret": "password",
    "client_kwargs": {
        "endpoint_url": "http://localhost:9000"
    }
}

# 20 крупнейших городов из Parquet-файла лабораторной работы 1 (последний год)
lab1 = pd.read_parquet(
    "s3://eco-data/processed/data_air_cities.parquet",
    storage_options=storage_options
)
cities = (
    lab1[lab1["year"] == lab1["year"].max()]
    .sort_values("air_population", ascending=False)
    .head(20)[["city", "region", "geo_lat", "geo_lon"]]
    .reset_index(drop=True)
)
print(cities)

cities.to_parquet(
      DATA_DIR / "cities.parquet",
      index=False
  )

# параметры запроса, проверенного в Postman
params = {
    "latitude": ",".join(cities["geo_lat"].astype(str)),
    "longitude": ",".join(cities["geo_lon"].astype(str)),
    "hourly": "pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi",
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
}

try:
    response = requests.get(
        f"{BASE_URL}/air-quality",
        params=params,
        timeout=60
    )
    response.raise_for_status()
except requests.exceptions.Timeout:
    raise SystemExit("Сервер не ответил за 60 секунд")
except requests.exceptions.ConnectionError:
    raise SystemExit("Нет соединения с сервером")
except requests.exceptions.HTTPError:
    # при ошибке API возвращает 400 и JSON {"error": true, "reason": "..."}
    raise SystemExit(f"Ошибка {response.status_code}: {response.json().get('reason')}")

print("HTTP-код:", response.status_code)

# для проверки выводим начало JSON-ответа
data = response.json()
print(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    )[:5000]
)
print("Получено городов:", len(data))

# сохраняем исходный JSON в файл (raw)
out_path = DATA_DIR / "air_quality_raw.json"
with open(
    out_path,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        data,
        file,
        ensure_ascii=False
    )

print("Сохранено:", out_path)