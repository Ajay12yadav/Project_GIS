import pandas as pd
import folium
from folium.plugins import HeatMap, Fullscreen
import numpy as np
from sklearn.neighbors import BallTree

print("🚀 Script started")

# -------------------------
# LOAD DATA
# -------------------------
try:
    df = pd.read_csv("MASTER_DATASET.csv")
    print("✅ CSV Loaded Successfully")
except Exception as e:
    print("❌ Error loading CSV:", e)
    exit()

# -------------------------
# CHECK COLUMNS
# -------------------------
print("📊 Columns in dataset:", df.columns)

# Auto-detect column names
lat_col = None
lon_col = None
pm25_col = None

for col in df.columns:
    col_lower = col.lower()
    
    if "lat" in col_lower:
        lat_col = col
    elif "lon" in col_lower or "lng" in col_lower:
        lon_col = col
    elif "pm25" in col_lower or "pm2.5" in col_lower:
        pm25_col = col

# Validate
if not lat_col or not lon_col or not pm25_col:
    print("❌ Required columns not found!")
    print("👉 Need latitude, longitude, pm25")
    exit()

print(f"✅ Using columns → {lat_col}, {lon_col}, {pm25_col}")

# Clean data
df = df.dropna(subset=[lat_col, lon_col, pm25_col])

# -------------------------
# CREATE MAP
# -------------------------
center_lat = df[lat_col].mean()
center_lon = df[lon_col].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles=None)
folium.TileLayer("CartoDB positron", name="Light Map", control=True).add_to(m)
folium.TileLayer("CartoDB dark_matter", name="Dark Map", control=True).add_to(m)
Fullscreen(position="topright").add_to(m)

heat_layer = folium.FeatureGroup(name="PM2.5 Heatmap", show=True)
risk_heat_layer = folium.FeatureGroup(name="Risk Heatmap", show=False)
high_zone_layer = folium.FeatureGroup(name="HIGH Risk Zones (Red)", show=True)
medium_zone_layer = folium.FeatureGroup(name="MEDIUM Risk Zones (Orange)", show=True)
low_zone_layer = folium.FeatureGroup(name="LOW Risk Points (Green)", show=False)

# -------------------------
# HEATMAP
# -------------------------
heat_data = [
    [row[lat_col], row[lon_col], row[pm25_col]]
    for _, row in df.iterrows()
]

HeatMap(
    heat_data,
    radius=20,
    blur=18,
    min_opacity=0.35,
    gradient={0.2: "#2ecc71", 0.45: "#f1c40f", 0.7: "#e67e22", 0.9: "#e74c3c"}
).add_to(heat_layer)

heat_layer.add_to(m)

print("🔥 Heatmap added")

# -------------------------
# ZONE ANALYSIS
# -------------------------
zone_results = []

def classify_risk(avg_pm25):
    if avg_pm25 > 150:
        return "HIGH"
    elif avg_pm25 > 80:
        return "MEDIUM"
    return "LOW"


def compute_zone_averages_fast(dataframe, lat_column, lon_column, pm25_column, radius_km=1.0):
    """Fast neighborhood averaging using BallTree + haversine distance."""
    earth_radius_km = 6371.0088

    coords_deg = dataframe[[lat_column, lon_column]].to_numpy(dtype=float)
    pm25_vals = pd.to_numeric(dataframe[pm25_column], errors="coerce").to_numpy(dtype=float)

    valid = np.isfinite(coords_deg).all(axis=1) & np.isfinite(pm25_vals)
    averages = np.zeros(len(dataframe), dtype=float)

    if not np.any(valid):
        return averages

    coords_rad = np.radians(coords_deg[valid])
    tree = BallTree(coords_rad, metric="haversine")
    neighbor_idx = tree.query_radius(coords_rad, r=(radius_km / earth_radius_km))

    valid_pm25 = pm25_vals[valid]
    valid_avg = np.array([
        valid_pm25[idxs].mean() if len(idxs) > 0 else 0.0
        for idxs in neighbor_idx
    ], dtype=float)

    averages[valid] = valid_avg
    return averages

# -------------------------
# APPLY ANALYSIS
# -------------------------
print("⚙️ Running zone analysis (fast mode)...")
avg_pm25_all = compute_zone_averages_fast(df, lat_col, lon_col, pm25_col, radius_km=1.0)
risk_heat_data = []

draw_every = 1
if len(df) > 5000:
    draw_every = max(1, len(df) // 5000)
    print(f"🗺️ Large dataset detected. Drawing 1 out of every {draw_every} circles for speed.")

city_col = next((c for c in df.columns if c.lower() == "city"), None)
sensor_col = next((c for c in df.columns if c.lower() in ["sensor_name", "sensor_id"]), None)

for i, (idx, row) in enumerate(df.iterrows()):
    avg_pm25 = float(avg_pm25_all[i])
    risk = classify_risk(avg_pm25)
    lat_val = float(row[lat_col])
    lon_val = float(row[lon_col])
    
    zone_results.append({
        "index": idx,
        "lat": row[lat_col],
        "lon": row[lon_col],
        "avg_pm25": avg_pm25,
        "risk": risk
    })
    
    if i % draw_every == 0:
        tooltip = f"Risk: {risk} | Avg PM2.5: {avg_pm25:.1f}"

        if risk == "HIGH":
            folium.Circle(
                location=[lat_val, lon_val],
                radius=1000,
                color="#c0392b",
                weight=2,
                fill=True,
                fill_color="#e74c3c",
                fill_opacity=0.28,
                tooltip=tooltip,
            ).add_to(high_zone_layer)
        elif risk == "MEDIUM":
            folium.Circle(
                location=[lat_val, lon_val],
                radius=850,
                color="#d35400",
                weight=2,
                fill=True,
                fill_color="#f39c12",
                fill_opacity=0.24,
                tooltip=tooltip,
            ).add_to(medium_zone_layer)
        else:
            city_text = str(row[city_col]) if city_col else "Unknown City"
            sensor_text = str(row[sensor_col]) if sensor_col else "Unknown Sensor"
            low_risk_tooltip = (
                f"LOW Risk\n"
                f"City: {city_text}\n"
                f"Sensor: {sensor_text}\n"
                f"Lat: {lat_val:.6f}, Lon: {lon_val:.6f}\n"
                f"Avg PM2.5: {avg_pm25:.1f}"
            )
            folium.CircleMarker(
                location=[lat_val, lon_val],
                radius=4,
                color="#27ae60",
                fill=True,
                fill_color="#2ecc71",
                fill_opacity=0.55,
                weight=1,
                tooltip=low_risk_tooltip,
            ).add_to(low_zone_layer)

        # risk heatmap based on computed neighborhood risk score
        risk_weight = 0.0
        if avg_pm25 > 150:
            risk_weight = 1.0
        elif avg_pm25 > 80:
            risk_weight = 0.6
        else:
            risk_weight = 0.2
        risk_heat_data.append([lat_val, lon_val, risk_weight])

    if (i + 1) % 1000 == 0:
        print(f"⏳ Processed {i + 1} points...")

HeatMap(
    risk_heat_data,
    radius=26,
    blur=24,
    min_opacity=0.2,
    gradient={0.2: "#2ecc71", 0.6: "#f39c12", 1.0: "#e74c3c"}
).add_to(risk_heat_layer)

high_zone_layer.add_to(m)
medium_zone_layer.add_to(m)
low_zone_layer.add_to(m)
risk_heat_layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

legend_html = """
<div style="
position: fixed;
bottom: 28px;
left: 28px;
z-index: 9999;
background: white;
border: 2px solid #444;
border-radius: 8px;
padding: 10px 12px;
font-size: 12px;
box-shadow: 0 1px 6px rgba(0,0,0,0.3);
">
<b>PM2.5 Risk Legend</b><br>
<span style="display:inline-block;width:10px;height:10px;background:#e74c3c;border-radius:50%;margin-right:6px;"></span>HIGH (&gt; 150)<br>
<span style="display:inline-block;width:10px;height:10px;background:#f39c12;border-radius:50%;margin-right:6px;"></span>MEDIUM (81 - 150)<br>
<span style="display:inline-block;width:10px;height:10px;background:#2ecc71;border-radius:50%;margin-right:6px;"></span>LOW (≤ 80)
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

print("🧠 Zone analysis done")

# -------------------------
# SAVE OUTPUTS
# -------------------------
try:
    zone_df = pd.DataFrame(zone_results)
    zone_df.to_csv("zone_analysis.csv", index=False)
    print("✅ zone_analysis.csv saved")
except Exception as e:
    print("❌ Error saving CSV:", e)

try:
    m.save("city_map.html")
    print("✅ city_map.html saved")
except Exception as e:
    print("❌ Error saving map:", e)

print("🎯 Script finished successfully")