"""
Professional GIS-Style City Pollution Monitoring Dashboard
Generates interactive heatmaps with advanced visualization layers
for PM2.5, Aerosol, Traffic, and combined Risk Score analysis
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any
import json
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# CONFIGURATION
# -------------------------
CSV_FILE = 'MASTER_DATASET.csv'
OUTPUT_MAP_FILE = 'city_map.html'
OUTPUT_ANALYSIS_FILE = 'zone_analysis.csv'
MAP_CENTER = [30.16315, 78.131]
MAP_ZOOM = 12

# Column mappings
LAT_COL = 'latitude'
LON_COL = 'longitude'
PM25_COL = 'pm25'
PM10_COL = 'pm10'
NO2_COL = 'no2'
SO2_COL = 'so2'
O3_COL = 'o3'
CO_COL = 'co'
AEROSOL_COL = 'aerosol'
SENSOR_COL = 'zone'
ZONE_TYPE_COL = 'zone_type'
WIND_SPEED_COL = 'wind_speed'
HUMIDITY_COL = 'humidity'
TRAFFIC_COL = 'traffic_flow_speed'
TRAFFIC_CONGESTION_COL = 'traffic_congestion'
AQI_COL = 'us_aqi'
DATETIME_COL = 'datetime'


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load CSV data with optimizations for large datasets
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        DataFrame with loaded data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    try:
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"File not found: {csv_path}")
        
        # Optimized CSV reading with dtype specification
        dtype_dict = {
            'latitude': 'float32',
            'longitude': 'float32',
            'pm25': 'float32',
            'pm10': 'float32',
            'no2': 'float32',
            'so2': 'float32',
            'o3': 'float32',
            'co': 'float32',
            'aerosol': 'float32',
            'humidity': 'float32',
            'wind_speed': 'float32',
            'traffic_flow_speed': 'float32',
            'traffic_congestion': 'float32',
            'us_aqi': 'float32'
        }
        
        df = pd.read_csv(csv_path, dtype=dtype_dict)
        logger.info(f"✓ Loaded {len(df):,} records from {csv_path}")
        return df
    
    except Exception as e:
        logger.error(f"✗ Error loading CSV: {str(e)}")
        raise


def validate_data(df: pd.DataFrame) -> bool:
    """Validate required columns exist"""
    required_cols = [LAT_COL, LON_COL, PM25_COL]
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        logger.error(f"✗ Missing columns: {missing}")
        return False
    
    logger.info("✓ Data validation passed")
    return True


@lru_cache(maxsize=256)
def get_risk_level(pm25: float) -> str:
    """Get risk level from PM2.5 value"""
    if pm25 > 150:
        return 'HIGH'
    elif pm25 > 80:
        return 'MEDIUM'
    else:
        return 'LOW'


@lru_cache(maxsize=256)
def get_risk_color(pm25: float) -> str:
    """Get color from PM2.5 value"""
    if pm25 > 150:
        return '#ff0000'  # RED
    elif pm25 > 80:
        return '#ff9900'  # ORANGE
    else:
        return '#00cc44'  # GREEN


def create_sensor_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by actual sensor location
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Aggregated DataFrame by sensor location
    """
    logger.info("Aggregating data by sensor location...")
    
    # Aggregate by unique sensor location
    sensor_agg = df.groupby([LAT_COL, LON_COL, SENSOR_COL, ZONE_TYPE_COL]).agg({
        PM25_COL: ['mean', 'max', 'min', 'std'],
        PM10_COL: 'mean',
        NO2_COL: 'mean',
        SO2_COL: 'mean',
        O3_COL: 'mean',
        CO_COL: 'mean',
        AEROSOL_COL: 'mean',
        HUMIDITY_COL: 'mean',
        WIND_SPEED_COL: 'mean',
        TRAFFIC_COL: 'mean',
        TRAFFIC_CONGESTION_COL: 'mean',
        AQI_COL: 'mean',
    }).reset_index()
    
    # Flatten columns
    sensor_agg.columns = [
        'latitude', 'longitude', 'zone', 'zone_type',
        'pm25_avg', 'pm25_max', 'pm25_min', 'pm25_std',
        'pm10_avg', 'no2_avg', 'so2_avg', 'o3_avg', 'co_avg',
        'aerosol_avg', 'humidity_avg', 'wind_speed_avg',
        'traffic_avg', 'congestion_avg', 'aqi_avg'
    ]
    
    # Add sensor count
    sensor_agg['sensor_count'] = len(df) // len(sensor_agg)
    
    logger.info(f"✓ Aggregated {len(df)} records into {len(sensor_agg)} sensor locations")
    return sensor_agg


def calculate_pollution_risk_score(row: pd.Series) -> float:
    """Calculate combined pollution risk score (0-1)"""
    # Normalize values to 0-1
    pm25_norm = min(row['pm25_avg'] / 200, 1.0)  # 200 is max considered
    aerosol_norm = min(row['aerosol_avg'] / 100, 1.0)
    traffic_norm = min(row['congestion_avg'] / 100, 1.0)
    
    # Weighted combination
    risk_score = (pm25_norm * 0.6) + (aerosol_norm * 0.2) + (traffic_norm * 0.2)
    return min(risk_score, 1.0)


def create_detailed_popup(row: pd.Series) -> str:
    """
    Create detailed popup HTML for markers
    
    Args:
        row: DataFrame row with all sensor data
        
    Returns:
        HTML string for popup
    """
    def format_value(val, decimals=2):
        if pd.isna(val):
            return 'N/A'
        return f"{float(val):.{decimals}f}"
    
    html = f"""
    <div style="font-family: Arial; font-size: 12px; width: 320px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="margin: 0; font-size: 14px;">📍 {row.get('zone', 'Unknown Zone')}</h4>
            <small>{row.get('zone_type', 'Unknown Type')}</small>
        </div>
        
        <div style="background: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 8px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>🌫 PM2.5:</b></td>
                    <td style="text-align: right; color: {get_risk_color(row['pm25_avg'] if 'pm25_avg' in row else 0)};">
                        <b>{format_value(row.get('pm25_avg', row.get('pm25', 0)))} µg/m³</b>
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>💨 PM10:</b></td>
                    <td style="text-align: right;">{format_value(row.get('pm10_avg', row.get('pm10', 0)))}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>🔴 NO₂:</b></td>
                    <td style="text-align: right;">{format_value(row.get('no2_avg', row.get('no2', 0)))} ppb</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>🟡 SO₂:</b></td>
                    <td style="text-align: right;">{format_value(row.get('so2_avg', row.get('so2', 0)))} ppb</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>🟢 O₃:</b></td>
                    <td style="text-align: right;">{format_value(row.get('o3_avg', row.get('o3', 0)))} ppb</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>🧪 Aerosol:</b></td>
                    <td style="text-align: right;">{format_value(row.get('aerosol_avg', row.get('aerosol', 0)))}</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>🔥 CO:</b></td>
                    <td style="text-align: right;">{format_value(row.get('co_avg', row.get('co', 0)))} ppm</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                    <td><b>📊 AQI:</b></td>
                    <td style="text-align: right;"><b>{format_value(row.get('aqi_avg', row.get('us_aqi', 0)), 0)}</b></td>
                </tr>
            </table>
        </div>
        
        <div style="background: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 8px;">
            <b>🌡️ Weather Conditions</b>
            <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 5px;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td>Humidity:</td>
                    <td style="text-align: right;">{format_value(row.get('humidity_avg', row.get('humidity', 0)), 1)}%</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td>Wind Speed:</td>
                    <td style="text-align: right;">{format_value(row.get('wind_speed_avg', row.get('wind_speed', 0)), 1)} km/h</td>
                </tr>
            </table>
        </div>
        
        <div style="background: #fff3cd; padding: 10px; border-radius: 5px;">
            <b>🚗 Traffic</b>
            <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-top: 5px;">
                <tr style="border-bottom: 1px solid #ffc107;">
                    <td>Flow Speed:</td>
                    <td style="text-align: right;">{format_value(row.get('traffic_avg', row.get('traffic_flow_speed', 0)), 1)} km/h</td>
                </tr>
                <tr>
                    <td>Congestion:</td>
                    <td style="text-align: right;">{format_value(row.get('congestion_avg', row.get('traffic_congestion', 0)), 1)}%</td>
                </tr>
            </table>
        </div>
        
        <div style="font-size: 10px; color: #666; margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
            <b>📍 Coordinates:</b> {format_value(row.get('latitude', row.get(LAT_COL, 0)), 4)}, {format_value(row.get('longitude', row.get(LON_COL, 0)), 4)}
            <br><b>📡 Sensors in Grid:</b> {int(row.get('sensor_count', 1))}
        </div>
    </div>
    """
    return html


def generate_heatmap_data(df: pd.DataFrame, pollutant_col: str, max_val: float = None) -> List[List[float]]:
    """Generate heatmap data for a specific pollutant"""
    if max_val is None:
        max_val = df[pollutant_col].max()
    
    # Normalize to 0-1 range
    heatmap_data = []
    for _, row in df.iterrows():
        val = float(row[pollutant_col])
        normalized = min(val / max_val, 1.0) if max_val > 0 else 0
        heatmap_data.append([float(row[LAT_COL]), float(row[LON_COL]), normalized])
    
    return heatmap_data


def create_professional_map(df: pd.DataFrame, output_file: str = OUTPUT_MAP_FILE) -> folium.Map:
    """
    Create professional GIS-style pollution dashboard
    
    Args:
        df: DataFrame with aggregated grid data
        output_file: Output HTML file path
        
    Returns:
        Folium Map object
    """
    logger.info("🗺️ Creating professional pollution dashboard...")
    
    # Initialize map with custom style
    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles='CartoDB positron',
        prefer_canvas=True
    )
    
    # =====================
    # DATA PREPARATION
    # =====================
    
    # Generate heatmap data for different pollutants
    pm25_data = generate_heatmap_data(df, 'pm25_avg', 200)
    aerosol_data = generate_heatmap_data(df, 'aerosol_avg', 100)
    traffic_data = generate_heatmap_data(df, 'congestion_avg', 100)
    
    # Calculate combined risk score
    df['risk_score'] = df.apply(calculate_pollution_risk_score, axis=1)
    risk_data = []
    for _, row in df.iterrows():
        risk_data.append([float(row['latitude']), float(row['longitude']), row['risk_score']])
    
    # =====================
    # LAYER: PM2.5 HEATMAP
    # =====================
    pm25_layer = folium.FeatureGroup(name='🌫️ PM2.5 Heatmap', show=True)
    HeatMap(
        pm25_data,
        name='PM2.5',
        radius=50,
        blur=35,
        min_opacity=0.4,
        max_zoom=14,
        gradient={
            0.0: '#00cc44',    # Green
            0.3: '#ffee00',    # Yellow
            0.6: '#ff9900',    # Orange
            1.0: '#ff0000'     # Red
        }
    ).add_to(pm25_layer)
    pm25_layer.add_to(m)
    
    # =====================
    # LAYER: AEROSOL HEATMAP
    # =====================
    aerosol_layer = folium.FeatureGroup(name='🧪 Aerosol Heatmap', show=False)
    HeatMap(
        aerosol_data,
        name='Aerosol',
        radius=50,
        blur=35,
        min_opacity=0.4,
        max_zoom=14,
        gradient={
            0.0: '#e8f4f8',
            0.3: '#87ceeb',
            0.6: '#4a90e2',
            1.0: '#1e3a8a'
        }
    ).add_to(aerosol_layer)
    aerosol_layer.add_to(m)
    
    # =====================
    # LAYER: TRAFFIC CONGESTION HEATMAP
    # =====================
    traffic_layer = folium.FeatureGroup(name='🚗 Traffic Heatmap', show=False)
    HeatMap(
        traffic_data,
        name='Traffic',
        radius=50,
        blur=35,
        min_opacity=0.4,
        max_zoom=14,
        gradient={
            0.0: '#90ee90',
            0.3: '#ffd700',
            0.6: '#ff8c00',
            1.0: '#dc143c'
        }
    ).add_to(traffic_layer)
    traffic_layer.add_to(m)
    
    # =====================
    # LAYER: COMBINED RISK HEATMAP
    # =====================
    risk_layer = folium.FeatureGroup(name='⚠️ Combined Risk Score', show=False)
    HeatMap(
        risk_data,
        name='Risk',
        radius=50,
        blur=35,
        min_opacity=0.4,
        max_zoom=14,
        gradient={
            0.0: '#00cc44',
            0.35: '#ffee00',
            0.65: '#ff9900',
            1.0: '#ff0000'
        }
    ).add_to(risk_layer)
    risk_layer.add_to(m)
    
    # =====================
    # LAYER: DETAILED MARKERS
    # =====================
    markers_layer = folium.FeatureGroup(name='📍 Sensor Details', show=True)
    
    for _, row in df.iterrows():
        pm25 = float(row['pm25_avg'])
        color = get_risk_color(pm25)
        risk_level = get_risk_level(pm25)
        
        # Create popup with detailed info
        popup_html = create_detailed_popup(row)
        
        folium.CircleMarker(
            location=[float(row['latitude']), float(row['longitude'])],
            radius=8,
            popup=folium.Popup(popup_html, max_width=350),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2,
            tooltip=f"{risk_level} | PM2.5: {pm25:.1f}"
        ).add_to(markers_layer)
    
    markers_layer.add_to(m)
    
    # =====================
    # LAYER: RISK ZONES
    # =====================
    high_risk = df[df['pm25_avg'] > 150]
    medium_risk = df[(df['pm25_avg'] > 80) & (df['pm25_avg'] <= 150)]
    low_risk = df[df['pm25_avg'] <= 80]
    
    high_layer = folium.FeatureGroup(name='🔴 High Risk Zones (>150)', show=False)
    for _, row in high_risk.iterrows():
        folium.CircleMarker(
            location=[float(row['latitude']), float(row['longitude'])],
            radius=12,
            color='#ff0000',
            fill=True,
            fillColor='#ff0000',
            fillOpacity=0.5,
            weight=2
        ).add_to(high_layer)
    high_layer.add_to(m)
    
    medium_layer = folium.FeatureGroup(name='🟠 Medium Risk Zones (80-150)', show=False)
    for _, row in medium_risk.iterrows():
        folium.CircleMarker(
            location=[float(row['latitude']), float(row['longitude'])],
            radius=10,
            color='#ff9900',
            fill=True,
            fillColor='#ff9900',
            fillOpacity=0.5,
            weight=2
        ).add_to(medium_layer)
    medium_layer.add_to(m)
    
    green_layer = folium.FeatureGroup(name='🟢 Low Risk Zones (≤80)', show=False)
    for _, row in low_risk.iterrows():
        folium.CircleMarker(
            location=[float(row['latitude']), float(row['longitude'])],
            radius=8,
            color='#00cc44',
            fill=True,
            fillColor='#00cc44',
            fillOpacity=0.5,
            weight=2
        ).add_to(green_layer)
    green_layer.add_to(m)
    
    high_layer.add_to(m)
    medium_layer.add_to(m)
    green_layer.add_to(m)
    
    # =====================
    # ADD LAYER CONTROL
    # =====================
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Save map
    m.save(output_file)
    logger.info(f"✓ Professional dashboard saved to {output_file}")
    
    return m


def add_professional_sidebar(m: folium.Map, df: pd.DataFrame) -> None:
    """Add professional information sidebar to map"""
    
    # Calculate statistics
    total_sensors = int(df['sensor_count'].sum())
    high_risk_count = len(df[df['pm25_avg'] > 150])
    medium_risk_count = len(df[(df['pm25_avg'] > 80) & (df['pm25_avg'] <= 150)])
    low_risk_count = len(df[df['pm25_avg'] <= 80])
    avg_pm25 = float(df['pm25_avg'].mean())
    max_pm25 = float(df['pm25_avg'].max())
    min_pm25 = float(df['pm25_avg'].min())
    
    sidebar_html = f"""
    <div style="position: fixed; 
                left: 10px; top: 60px; width: 320px; height: auto; max-height: 85vh;
                background-color: rgba(255, 255, 255, 0.95); 
                border: 2px solid #333; border-radius: 8px; z-index: 9999; 
                padding: 20px; overflow-y: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        
        <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
            📊 Pollution Dashboard
        </h2>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <h3 style="margin: 0 0 10px 0; font-size: 14px;">🌍 City Statistics</h3>
            <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.3);">
                    <td>📡 Total Sensors:</td>
                    <td style="text-align: right;"><b>{total_sensors:,}</b></td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.3);">
                    <td>📍 Grid Cells:</td>
                    <td style="text-align: right;"><b>{len(df)}</b></td>
                </tr>
            </table>
        </div>
        
        <div style="background: #fff5e6; border-left: 4px solid #ff9900; padding: 12px; border-radius: 4px; margin-bottom: 15px;">
            <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #333;">📈 PM2.5 Overview (µg/m³)</h3>
            <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
                <tr><td>Average:</td><td style="text-align: right;"><b>{avg_pm25:.1f}</b></td></tr>
                <tr><td>Maximum:</td><td style="text-align: right;"><b style="color: #ff0000;">{max_pm25:.1f}</b></td></tr>
                <tr><td>Minimum:</td><td style="text-align: right;"><b style="color: #00cc44;">{min_pm25:.1f}</b></td></tr>
            </table>
        </div>
        
        <div style="background: #f0f0f0; border-radius: 6px; padding: 12px; margin-bottom: 15px;">
            <h3 style="margin: 0 0 12px 0; font-size: 13px; color: #333;">⚠️ Risk Distribution</h3>
            
            <div style="background: #ff0000; color: white; padding: 8px; border-radius: 4px; margin-bottom: 8px; text-align: center;">
                <div style="font-size: 11px; opacity: 0.8;">🔴 HIGH RISK (>150)</div>
                <div style="font-size: 18px; font-weight: bold;">{high_risk_count}</div>
                <div style="font-size: 10px; opacity: 0.8;">Zones</div>
            </div>
            
            <div style="background: #ff9900; color: white; padding: 8px; border-radius: 4px; margin-bottom: 8px; text-align: center;">
                <div style="font-size: 11px; opacity: 0.8;">🟠 MEDIUM RISK (80-150)</div>
                <div style="font-size: 18px; font-weight: bold;">{medium_risk_count}</div>
                <div style="font-size: 10px; opacity: 0.8;">Zones</div>
            </div>
            
            <div style="background: #00cc44; color: white; padding: 8px; border-radius: 4px; text-align: center;">
                <div style="font-size: 11px; opacity: 0.8;">🟢 LOW RISK (≤80)</div>
                <div style="font-size: 18px; font-weight: bold;">{low_risk_count}</div>
                <div style="font-size: 10px; opacity: 0.8;">Zones</div>
            </div>
        </div>
        
        <div style="background: #e8f4f8; border-left: 4px solid #4a90e2; padding: 12px; border-radius: 4px;">
            <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #333;">💡 How to Use</h3>
            <ul style="margin: 0; padding-left: 18px; font-size: 11px; color: #555;">
                <li>Zoom in to see detailed sensor data</li>
                <li>Click markers for detailed pollution data</li>
                <li>Toggle layers to compare pollutants</li>
                <li>Red = Danger, Orange = Caution, Green = Safe</li>
            </ul>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(sidebar_html))


def add_legend(m: folium.Map) -> None:
    """Add professional legend to map"""
    legend_html = """
    <div style="position: fixed; 
                bottom: 20px; right: 20px; width: 280px; height: auto;
                background-color: rgba(255, 255, 255, 0.95); 
                border: 2px solid #333; border-radius: 8px; z-index: 9998; 
                padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        
        <h3 style="margin: 0 0 12px 0; font-size: 14px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 8px;">
            🎨 PM2.5 Scale & Categories
        </h3>
        
        <div style="margin: 10px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 20px; height: 20px; background: #ff0000; border-radius: 50%; margin-right: 10px;"></div>
                <div>
                    <b style="color: #ff0000;">HIGH RISK</b><br>
                    <small style="color: #666;">PM2.5 > 150 µg/m³<br>Unhealthy - Avoid outdoor activity</small>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 20px; height: 20px; background: #ff9900; border-radius: 50%; margin-right: 10px;"></div>
                <div>
                    <b style="color: #ff9900;">MEDIUM RISK</b><br>
                    <small style="color: #666;">PM2.5 80-150 µg/m³<br>Sensitive groups should limit activity</small>
                </div>
            </div>
            
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background: #00cc44; border-radius: 50%; margin-right: 10px;"></div>
                <div>
                    <b style="color: #00cc44;">LOW RISK</b><br>
                    <small style="color: #666;">PM2.5 ≤ 80 µg/m³<br>Good air quality</small>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #ddd; font-size: 11px; color: #666;">
            <b>📡 Data Layers:</b>
            <ul style="margin: 5px 0; padding-left: 18px;">
                <li>Heatmaps show pollutant intensity</li>
                <li>Colored zones highlight risk areas</li>
                <li>Marker size = sensor density</li>
            </ul>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))


def generate_zone_analysis(df: pd.DataFrame, original_df: pd.DataFrame, output_file: str = OUTPUT_ANALYSIS_FILE) -> None:
    """
    Generate detailed zone-wise analysis and save to CSV
    
    Args:
        df: Aggregated grid DataFrame
        original_df: Original sensor DataFrame
        output_file: Output CSV file path
    """
    logger.info("📊 Generating zone analysis...")
    
    try:
        # Zone-level statistics from original data
        zone_stats = original_df.groupby(ZONE_TYPE_COL).agg({
            PM25_COL: ['mean', 'max', 'min', 'std'],
            PM10_COL: 'mean',
            NO2_COL: 'mean',
            SO2_COL: 'mean',
            O3_COL: 'mean',
            AEROSOL_COL: 'mean',
            SENSOR_COL: 'count',
            HUMIDITY_COL: 'mean',
            WIND_SPEED_COL: 'mean',
            TRAFFIC_COL: 'mean'
        }).round(2)
        
        # Flatten columns
        zone_stats.columns = [
            'PM25_Mean', 'PM25_Max', 'PM25_Min', 'PM25_StdDev',
            'PM10_Mean', 'NO2_Mean', 'SO2_Mean', 'O3_Mean', 'Aerosol_Mean',
            'Sensor_Count', 'Humidity_Mean', 'Wind_Speed_Mean', 'Traffic_Mean'
        ]
        
        # Add risk classification
        zone_stats['Risk_Level'] = pd.cut(
            zone_stats['PM25_Mean'],
            bins=[0, 80, 150, float('inf')],
            labels=['LOW', 'MEDIUM', 'HIGH'],
            right=True
        )
        
        # Reset index to include zone_type as column
        zone_stats = zone_stats.reset_index()
        
        zone_stats.to_csv(output_file, index=False)
        logger.info(f"✓ Zone analysis saved to {output_file}")
        logger.info(f"\n📋 Zone Statistics Summary:\n{zone_stats.to_string()}")
        
    except Exception as e:
        logger.error(f"✗ Error generating zone analysis: {str(e)}")


def main():
    """Main pipeline execution"""
    try:
        logger.info("=" * 60)
        logger.info("🚀 GIS Pollution Monitoring Dashboard Pipeline")
        logger.info("=" * 60)
        
        # Load data
        df = load_data(CSV_FILE)
        
        # Validate data
        if not validate_data(df):
            raise ValueError("Data validation failed")
        
        # Aggregate by sensor location
        sensor_df = create_sensor_aggregation(df)
        
        # Generate zone analysis from original data
        generate_zone_analysis(df, df)
        
        # Create professional map
        create_professional_map(sensor_df)
        
        logger.info("=" * 60)
        logger.info("✅ Pipeline completed successfully!")
        logger.info("=" * 60)
        logger.info(f"📍 Output files:")
        logger.info(f"   • {OUTPUT_MAP_FILE} (Professional Dashboard)")
        logger.info(f"   • {OUTPUT_ANALYSIS_FILE} (Zone Analysis)")
        
    except Exception as e:
        logger.error(f"✗ Pipeline failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
