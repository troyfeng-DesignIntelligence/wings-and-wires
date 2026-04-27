import pandas as pd
import json

print("读取数据中...")
df = pd.read_csv(
    r"D:\Portfolio\wings-and-wires\data\raw\Swainson_s_Hawks.csv",
    usecols=["timestamp", "location-lat", "location-long", "individual-local-identifier"]
)

print(f"原始数据：{len(df)} 行")

# 删掉没有坐标的行
df = df.dropna(subset=["location-lat", "location-long"])

# 只保留美洲范围（西经170度到西经30度，南纬60度到北纬75度）
df = df[
    (df["location-long"] >= -170) & (df["location-long"] <= -30) &
    (df["location-lat"] >= -60) & (df["location-lat"] <= 75)
]

print(f"筛选后：{len(df)} 行")

# 降采样：每只鸟每天只保留一条
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date
df = df.groupby(["individual-local-identifier", "date"]).first().reset_index()

print(f"降采样后：{len(df)} 行")

# 转成 GeoJSON
features = []
for _, row in df.iterrows():
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row["location-long"], row["location-lat"]]
        },
        "properties": {
            "timestamp": str(row["timestamp"]),
            "individual": row["individual-local-identifier"]
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

output_path = r"D:\Portfolio\wings-and-wires\data\processed\hawks_americas.geojson"
with open(output_path, "w") as f:
    json.dump(geojson, f)

print(f"完成！保存到 {output_path}")
print(f"共 {len(features)} 个数据点")