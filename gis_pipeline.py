"""
GIS Pipeline for PM2.5 Air Quality Analysis
Generates interactive maps and risk heatmaps for air quality monitoring
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any

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
SENSOR_COL = 'sensor_name'
TEMP_COL = 'temperature_c'
HUMIDITY_COL = 'humidity_pct'
WEATHER_COL = 'weather'


def load_data(csv_path: str) -> pd.DataFrame:
    """
    Load CSV data with error handling
    
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
        
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} records from {csv_path}")
        return df
    
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        raise


def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate that required columns exist in DataFrame
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if all required columns exist
    """
    required_cols = [LAT_COL, LON_COL, PM25_COL, SENSOR_COL]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return False
    
    logger.info("Data validation passed")
    return True


def calculate_risk_metrics(pm25: float) -> Dict[str, Any]:
    """
    Calculate risk classification and visual properties based on PM2.5
    
    Args:
        pm25: PM2.5 concentration value
        
    Returns:
        Dictionary with risk, color, heat_weight, and radius
    """
    if pm25 > 150:
        return {
            'risk': 'HIGH',
            'color': '#ff0000',      # RED
            'heat_weight': 1.0,
            'radius_size': 1400
        }
    elif pm25 > 80:
        return {
            'risk': 'MEDIUM',
            'color': '#ff9900',      # ORANGE
            'heat_weight': 0.6,
            'radius_size': 1100
        }
    else:
        return {
            'risk': 'LOW',
            'color': '#00cc44',      # GREEN
            'heat_weight': 0.25,
            'radius_size': 850
        }


def create_popup_html(row: pd.Series, pm25: float, risk: str) -> str:
    """
    Create HTML popup content for map markers
    
    Args:
        row: DataFrame row with sensor data
        pm25: PM2.5 value
        risk: Risk category
        
    Returns:
        HTML string for popup
    """
    html = f"""
    <div style='font-size:13px; max-width:250px;'>
    <b>📍 Sensor:</b> {row.get(SENSOR_COL, 'Unknown')}<br>
    <b>🌫 PM2.5:</b> {pm25:.2f} µg/m³<br>
    <b>🧪 Aerosol:</b> {row.get('aerosol_index', 'N/A'):.2f if pd.notna(row.get('aerosol_index')) else 'N/A'}<br>
    <b>🚗 Traffic:</b> {row.get('traffic_level', 'N/A')}<br>
    <b>🌡 Temperature:</b> {row.get(TEMP_COL, 'N/A')}°C<br>
    <b>💧 Humidity:</b> {row.get(HUMIDITY_COL, 'N/A')}%<br>
    <b>☁ Weather:</b> {row.get(WEATHER_COL, 'N/A')}<br>
    <b>⚠ Risk Level:</b> <span style='color:{calculate_risk_metrics(pm25)["color"]};'><b>{risk}</b></span>
    </div>
    """
    return html


def generate_zone_analysis(df: pd.DataFrame, output_file: str = OUTPUT_ANALYSIS_FILE) -> None:
    """
    Generate zone-wise analysis and save to CSV
    
    Args:
        df: DataFrame with sensor data
        output_file: Output CSV file path
    """
    try:
        # Group by zone and calculate statistics
        zone_stats = df.groupby('zone_type').agg({
            PM25_COL: ['mean', 'max', 'min', 'count'],
            'sensor_name': 'nunique',
            'city': 'nunique'
        }).round(2)
        
        zone_stats.columns = ['avg_pm25', 'max_pm25', 'min_pm25', 'readings', 
                              'unique_sensors', 'unique_cities']
        zone_stats['risk_level'] = zone_stats['avg_pm25'].apply(
            lambda x: calculate_risk_metrics(x)['risk']
        )
        
        zone_stats.to_csv(output_file)
        logger.info(f"Zone analysis saved to {output_file}")
        logger.info(f"\nZone Statistics:\n{zone_stats}")
        
    except Exception as e:
        logger.error(f"Error generating zone analysis: {str(e)}")


def create_map(df: pd.DataFrame, output_file: str = OUTPUT_MAP_FILE) -> folium.Map:
    """
    Create interactive folium map with heatmap, markers, and dynamic metrics panel
    
    Args:
        df: DataFrame with sensor data
        output_file: Output HTML file path
        
    Returns:
        Folium Map object
    """
    try:
        logger.info("Creating interactive map with dynamic metrics...")
        
        # Initialize map
        m = folium.Map(
            location=MAP_CENTER,
            zoom_start=MAP_ZOOM,
            tiles='OpenStreetMap'
        )
        
        # Data for heatmap
        risk_heat_data = []
        
        # Add markers and collect heatmap data
        for idx, row in df.iterrows():
            try:
                lat_val = float(row[LAT_COL])
                lon_val = float(row[LON_COL])
                pm25_val = float(row[PM25_COL])
                
                # Validate coordinates
                if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
                    logger.warning(f"Invalid coordinates at row {idx}: {lat_val}, {lon_val}")
                    continue
                
                # Calculate risk metrics
                risk_metrics = calculate_risk_metrics(pm25_val)
                risk = risk_metrics['risk']
                color = risk_metrics['color']
                heat_weight = risk_metrics['heat_weight']
                radius_size = risk_metrics['radius_size']
                
                # Add heatmap data
                risk_heat_data.append([lat_val, lon_val, heat_weight])
                
                # Create popup
                popup_html = create_popup_html(row, pm25_val, risk)
                
                # Add circle marker
                folium.Circle(
                    location=[lat_val, lon_val],
                    radius=radius_size,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.32,
                    weight=2,
                    popup=folium.Popup(popup_html, max_width=280),
                    tooltip=f"{risk} Zone | PM2.5: {pm25_val:.1f}"
                ).add_to(m)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing row {idx}: {str(e)}")
                continue
        
        # Add heatmap layer
        if risk_heat_data:
            HeatMap(
                risk_heat_data,
                radius=45,
                blur=38,
                min_opacity=0.35,
                max_zoom=13,
                gradient={
                    0.15: "#00cc44",   # GREEN
                    0.45: "#ffee00",   # YELLOW
                    0.70: "#ff9900",   # ORANGE
                    1.00: "#ff0000"    # RED
                }
            ).add_to(m)
            logger.info(f"Added {len(risk_heat_data)} points to heatmap")
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p style="margin: 0; font-weight: bold;">PM2.5 Risk Legend</p>
        <p style="margin: 5px 0;"><i style="background:#ff0000; width: 18px; height: 18px; 
           float: left; margin-right: 8px; border-radius: 50%;"></i>HIGH (&gt; 150)</p>
        <p style="margin: 5px 0;"><i style="background:#ff9900; width: 18px; height: 18px; 
           float: left; margin-right: 8px; border-radius: 50%;"></i>MEDIUM (81-150)</p>
        <p style="margin: 5px 0;"><i style="background:#00cc44; width: 18px; height: 18px; 
           float: left; margin-right: 8px; border-radius: 50%;"></i>LOW (≤ 80)</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add metrics panel styling and functionality
        metrics_style = '''
        <style>
            /* Enhanced metrics panel styling */
            .metrics-panel {
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #333;
                border-radius: 8px;
                padding: 15px;
                z-index: 9998;
                max-width: 380px;
                max-height: 500px;
                overflow-y: auto;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                font-family: Arial, sans-serif;
                font-size: 12px;
            }
            
            .metrics-panel h4 {
                margin: 0 0 12px 0;
                font-size: 14px;
                color: #333;
                border-bottom: 2px solid #ddd;
                padding-bottom: 8px;
            }
            
            .metrics-group {
                margin: 10px 0;
                padding: 10px;
                background: #f9f9f9;
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }
            
            .metrics-group-title {
                font-weight: bold;
                color: #333;
                margin-bottom: 8px;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .metric-row {
                display: flex;
                justify-content: space-between;
                margin: 5px 0;
                padding: 3px 0;
                border-bottom: 1px solid #eee;
            }
            
            .metric-label {
                font-weight: 600;
                color: #555;
                flex: 1;
            }
            
            .metric-value {
                font-weight: bold;
                color: #333;
                text-align: right;
                flex: 0 0 45%;
            }
            
            .metric-value.high { color: #e74c3c; }
            .metric-value.medium { color: #f39c12; }
            .metric-value.low { color: #27ae60; }
            
            .zoom-info {
                background: #e8f4f8;
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 10px;
                font-size: 11px;
                color: #0066cc;
            }
        </style>
        '''
        m.get_root().html.add_child(folium.Element(metrics_style))
        
        # Add metrics panel HTML and JavaScript
        metrics_html = '''
        <div id="metricsPanel" class="metrics-panel">
            <h4>📊 Area Metrics</h4>
            <div class="zoom-info">
                <strong>Zoom Level:</strong> <span id="zoomLevel">12</span> | 
                <strong>Points:</strong> <span id="visiblePoints">0</span>
            </div>
            <div id="metricsContent">
                <div style="text-align: center; padding: 10px; color: #666;">
                    ⏳ Loading metrics...
                </div>
            </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(metrics_html))
        
        # Save map
        m.save(output_file)
        logger.info(f"Enhanced map with metrics saved to {output_file}")
        
        # Inject metrics JavaScript after saving
        inject_metrics_javascript(output_file)
        
        return m
        
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        raise


def inject_metrics_javascript(html_file: str) -> None:
    """
    Inject metrics calculation JavaScript into the HTML file
    
    Args:
        html_file: Path to the HTML file to update
    """
    metrics_js = '''
    <script>
        // Global CSV data storage
        var csvData = [];
        
        // Function to load CSV data
        function loadCSVData() {
            fetch('MASTER_DATASET.csv')
                .then(response => response.text())
                .then(csvText => {
                    const lines = csvText.trim().split('\\n');
                    const headers = lines[0].split(',').map(h => h.trim());
                    
                    const latIdx = headers.findIndex(h => h.toLowerCase().includes('latitude') || h.toLowerCase() === 'lat');
                    const lonIdx = headers.findIndex(h => h.toLowerCase().includes('longitude') || h.toLowerCase() === 'lon');
                    const pm25Idx = headers.findIndex(h => h.toLowerCase().includes('pm25') || h.toLowerCase() === 'pm2.5');
                    const sensorIdx = headers.findIndex(h => h.toLowerCase().includes('sensor_name'));
                    const cityIdx = headers.findIndex(h => h.toLowerCase().includes('city'));
                    const zoneIdx = headers.findIndex(h => h.toLowerCase().includes('zone_type'));
                    const tempIdx = headers.findIndex(h => h.toLowerCase().includes('temperature'));
                    const humidityIdx = headers.findIndex(h => h.toLowerCase().includes('humidity'));
                    const windIdx = headers.findIndex(h => h.toLowerCase().includes('wind_speed'));
                    
                    for (let i = 1; i < lines.length; i++) {
                        if (!lines[i].trim()) continue;
                        const values = lines[i].split(',').map(v => v.trim());
                        const lat = parseFloat(values[latIdx]);
                        const lon = parseFloat(values[lonIdx]);
                        const pm25 = parseFloat(values[pm25Idx]);
                        
                        if (!isNaN(lat) && !isNaN(lon) && !isNaN(pm25)) {
                            csvData.push({
                                lat, lon, pm25,
                                sensor_name: values[sensorIdx] || 'Unknown',
                                city: values[cityIdx] || 'Unknown',
                                zone_type: values[zoneIdx] || 'Unknown',
                                temperature_c: tempIdx >= 0 ? parseFloat(values[tempIdx]) : null,
                                humidity_pct: humidityIdx >= 0 ? parseFloat(values[humidityIdx]) : null,
                                wind_speed_kmh: windIdx >= 0 ? parseFloat(values[windIdx]) : null
                            });
                        }
                    }
                    
                    console.log('Loaded ' + csvData.length + ' sensor records');
                    updateMetricsOnMapChange();
                })
                .catch(e => console.error('Error loading CSV:', e));
        }
        
        // Function to find map object (works with folium)
        function getMapObject() {
            for (var key in window) {
                if (key.startsWith('map_') && typeof window[key] === 'object' && window[key].getBounds) {
                    return window[key];
                }
            }
            return null;
        }
        
        // Function to calculate and update metrics
        function updateMetricsOnMapChange() {
            var map = getMapObject();
            if (!map) return;
            
            var bounds = map.getBounds();
            var zoomLevel = map.getZoom();
            var visibleData = csvData.filter(point => 
                point.lat >= bounds.getSouth() && 
                point.lat <= bounds.getNorth() && 
                point.lon >= bounds.getWest() && 
                point.lon <= bounds.getEast()
            );
            
            document.getElementById('zoomLevel').textContent = zoomLevel;
            document.getElementById('visiblePoints').textContent = visibleData.length;
            
            if (visibleData.length > 0) {
                var pm25Values = visibleData.map(d => d.pm25);
                var tempValues = visibleData.map(d => d.temperature_c).filter(v => v !== null && v > -50);
                var humidityValues = visibleData.map(d => d.humidity_pct).filter(v => v !== null && v > 0);
                
                var stats = {
                    pm25_avg: (pm25Values.reduce((a, b) => a + b, 0) / pm25Values.length).toFixed(2),
                    pm25_max: Math.max(...pm25Values).toFixed(2),
                    pm25_min: Math.min(...pm25Values).toFixed(2),
                    temp_avg: tempValues.length > 0 ? (tempValues.reduce((a, b) => a + b, 0) / tempValues.length).toFixed(1) : 'N/A',
                    humidity_avg: humidityValues.length > 0 ? (humidityValues.reduce((a, b) => a + b, 0) / humidityValues.length).toFixed(1) : 'N/A'
                };
                
                var highCount = pm25Values.filter(v => v > 150).length;
                var mediumCount = pm25Values.filter(v => v > 80 && v <= 150).length;
                var lowCount = pm25Values.filter(v => v <= 80).length;
                
                var html = '';
                html += '<div class="metrics-group"><div class="metrics-group-title">📊 PM2.5 Levels (µg/m³)</div>';
                html += '<div class="metric-row"><span class="metric-label">Average:</span><span class="metric-value">' + stats.pm25_avg + '</span></div>';
                html += '<div class="metric-row"><span class="metric-label">Maximum:</span><span class="metric-value high">' + stats.pm25_max + '</span></div>';
                html += '<div class="metric-row"><span class="metric-label">Minimum:</span><span class="metric-value low">' + stats.pm25_min + '</span></div>';
                html += '</div>';
                
                html += '<div class="metrics-group"><div class="metrics-group-title">⚠️ Risk Distribution</div>';
                html += '<div class="metric-row"><span class="metric-label">🔴 High (>150):</span><span class="metric-value high">' + highCount + ' (' + ((highCount/visibleData.length)*100).toFixed(1) + '%)</span></div>';
                html += '<div class="metric-row"><span class="metric-label">🟠 Medium (81-150):</span><span class="metric-value medium">' + mediumCount + ' (' + ((mediumCount/visibleData.length)*100).toFixed(1) + '%)</span></div>';
                html += '<div class="metric-row"><span class="metric-label">🟢 Low (≤80):</span><span class="metric-value low">' + lowCount + ' (' + ((lowCount/visibleData.length)*100).toFixed(1) + '%)</span></div>';
                html += '</div>';
                
                if (stats.temp_avg !== 'N/A') {
                    html += '<div class="metrics-group"><div class="metrics-group-title">🌡️ Climate</div>';
                    html += '<div class="metric-row"><span class="metric-label">Avg Temperature:</span><span class="metric-value">' + stats.temp_avg + '°C</span></div>';
                    if (stats.humidity_avg !== 'N/A') {
                        html += '<div class="metric-row"><span class="metric-label">Avg Humidity:</span><span class="metric-value">' + stats.humidity_avg + '%</span></div>';
                    }
                    html += '</div>';
                }
                
                html += '<div class="zoom-info"><strong>📍 Visible Data Points:</strong> ' + visibleData.length + ' sensors</div>';
                
                document.getElementById('metricsContent').innerHTML = html;
            } else {
                document.getElementById('metricsContent').innerHTML = '<div style="padding: 10px; color: #666;">Zoom in to view metrics for this area</div>';
            }
        }
        
        // Wait for map to be ready and load data
        setTimeout(() => {
            var map = getMapObject();
            if (map) {
                loadCSVData();
                map.on('zoomend', updateMetricsOnMapChange);
                map.on('moveend', updateMetricsOnMapChange);
            }
        }, 1000);
    </script>
    '''
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Insert JavaScript before closing body tag
        if '</body>' in content:
            content = content.replace('</body>', metrics_js + '\n</body>')
        else:
            content = content + metrics_js
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Metrics JavaScript successfully injected into HTML")
    except Exception as e:
        logger.warning(f"Could not inject metrics JavaScript: {str(e)}")


def main():
    """Main pipeline execution"""
    try:
        logger.info("Starting GIS PM2.5 Analysis Pipeline...")
        
        # Load data
        df = load_data(CSV_FILE)
        
        # Validate data
        if not validate_data(df):
            raise ValueError("Data validation failed")
        
        # Generate analysis
        generate_zone_analysis(df)
        
        # Create interactive map
        create_map(df)
        
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()