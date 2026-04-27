import pandas as pd
import json

print("读取数据中...")
df = pd.read_excel(
    r"D:\Portfolio\wings-and-wires\data\raw\Missing_Migrants_Global_Figures_allData.xlsx"
)

print(f"原始数据：{len(df)} 行")

# 解析坐标
def parse_coords(coord_str):
    try:
        parts = str(coord_str).split(",")
        return float(parts[0].strip()), float(parts[1].strip())
    except:
        return None, None

df["lat"], df["lon"] = zip(*df["Coordinates"].apply(parse_coords))

# 处理地中海
med = df[df["Region of Incident"] == "Mediterranean"].copy()
med = med.dropna(subset=["lat", "lon"])
print(f"地中海有坐标记录：{len(med)} 行")

# 处理美洲
americas_regions = ["North America", "Central America", "South America", "Caribbean"]
ame = df[df["Region of Incident"].isin(americas_regions)].copy()
ame = ame.dropna(subset=["lat", "lon"])
print(f"美洲有坐标记录：{len(ame)} 行")

def to_geojson(data):
    features = []
    for _, row in data.iterrows():
        count = row["Total Number of Dead and Missing"]
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["lon"], row["lat"]]
            },
            "properties": {
                "id": row["Main ID"],
                "year": int(row["Incident Year"]),
                "month": row["Month"],
                "region": row["Region of Incident"],
                "route": row["Migration Route"] if pd.notna(row["Migration Route"]) else None,
                "cause": row["Cause of Death"] if pd.notna(row["Cause of Death"]) else None,
                "location": row["Location of Incident"] if pd.notna(row["Location of Incident"]) else None,
                "count": int(count) if pd.notna(count) else None,
                "data_missing": pd.isna(count)
            }
        })
    return {"type": "FeatureCollection", "features": features}

# 保存地中海
med_geojson = to_geojson(med)
with open(r"D:\Portfolio\wings-and-wires\data\processed\migrants_mediterranean.geojson", "w", encoding="utf-8") as f:
    json.dump(med_geojson, f, ensure_ascii=False)

# 保存美洲
ame_geojson = to_geojson(ame)
with open(r"D:\Portfolio\wings-and-wires\data\processed\migrants_americas.geojson", "w", encoding="utf-8") as f:
    json.dump(ame_geojson, f, ensure_ascii=False)

med_total = sum(f["properties"]["count"] for f in med_geojson["features"] if f["properties"]["count"])
ame_total = sum(f["properties"]["count"] for f in ame_geojson["features"] if f["properties"]["count"])

print(f"\n完成！")
print(f"地中海：{len(med_geojson['features'])} 条记录，{med_total} 人")
print(f"美洲：{len(ame_geojson['features'])} 条记录，{ame_total} 人")