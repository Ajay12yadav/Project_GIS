# Zoom Metrics Feature Documentation

## Overview

The Enhanced GIS Map now includes a **Dynamic Metrics Panel** that updates in real-time as you zoom and pan around the map. This provides instant insights into air quality metrics for any geographic area you're viewing.

## Feature Details

### What Is the Metrics Panel?

The Metrics Panel is a fixed box on the right side of the map that displays:

1. **Zoom Information**
   - Current zoom level
   - Number of visible sensor data points in the current view

2. **PM2.5 Statistics** 📊
   - Average PM2.5 concentration
   - Maximum PM2.5 value
   - Minimum PM2.5 value
   - Standard deviation (data spread)

3. **Risk Distribution** ⚠️
   - Count and percentage of HIGH risk areas (>150 µg/m³)
   - Count and percentage of MEDIUM risk areas (81-150 µg/m³)
   - Count and percentage of LOW risk areas (≤80 µg/m³)

4. **Climate Conditions** 🌡️
   - Average temperature
   - Average humidity
   - Average wind speed
   - (Only shown when data is available)

5. **Coverage Information**
   - Number of cities in the visible area
   - Number of zone types
   - Number of unique sensors

## How to Use

### Basic Usage

1. **Open the Map**
   ```bash
   python gis_pipeline.py
   # Then open city_map.html in your browser
   ```

2. **View Initial Metrics**
   - The Metrics Panel appears on the right side automatically
   - It shows data for the default zoom level (12)

3. **Zoom to See Local Data**
   - Use your mouse scroll wheel or the Zoom buttons to zoom in/out
   - The metrics update automatically after you finish zooming
   - The panel shows "Zoom in to view metrics for this area" if no points are visible

4. **Pan to Different Areas**
   - Click and drag the map to move around
   - Metrics update automatically for the new area

### Interpretation Guide

#### PM2.5 Levels
- **0-35 µg/m³**: Good air quality (no health concerns)
- **36-75 µg/m³**: Moderate (some concern for sensitive groups)
- **76-115 µg/m³**: Unhealthy for sensitive groups (all groups affected)
- **116-150 µg/m³**: Unhealthy (everyone affected)
- **>150 µg/m³**: Very Unhealthy (hazardous conditions)

#### Risk Distribution
The percentages show the proportion of monitored areas in each risk category:
- **High % > 50%**: Air quality crisis in the region
- **Medium % > 50%**: Many areas affected
- **Low % > 75%**: Generally good air quality

#### Temperature & Humidity
- High temperature + High humidity = increased PM2.5 settling
- Low wind speed = PM2.5 accumulation
- These factors compound air quality issues

## Color Coding

The metrics panel uses intuitive color coding:

- 🔴 **Red (#e74c3c)**: HIGH RISK - Hazardous conditions
- 🟠 **Orange (#f39c12)**: MEDIUM RISK - Unhealthy for sensitive groups
- 🟢 **Green (#27ae60)**: LOW RISK - Acceptable air quality

## Advanced Features

### Real-Time Updates

The metrics panel updates automatically whenever:
- You zoom in or out
- You pan (move) the map
- New CSV data is loaded (if refreshed)

### Zoom Level Tips

Different zoom levels provide different insights:

| Zoom Level | Best For |
|-----------|----------|
| 5-8 | Regional overview |
| 9-12 | City/district level |
| 13-16 | Neighborhood/zone level |
| 17+ | Street-level detail |

**Tip:** The panel shows "Zoom in for more detailed metrics" when zoom < 10, and "Highly detailed view" when zoom > 16.

### Statistical Calculations

**Standard Deviation** measures how spread out the data is:
- Low Std Dev: Consistent pollution levels
- High Std Dev: Highly variable pollution levels

**Average (Mean)** calculation:
```
Average = Sum of all PM2.5 values / Number of sensors
```

**Risk Distribution Percentage**:
```
Percentage = (Count of sensors in category / Total visible sensors) × 100
```

## Technical Details

### Data Processing

1. **CSV Loading**: The map automatically loads `MASTER_DATASET.csv`
2. **Coordinate Validation**: Only valid coordinates are processed
3. **Real-time Filtering**: Data is filtered by visible map bounds
4. **Statistical Calculation**: Metrics are calculated on-the-fly

### Performance

- CSV loads asynchronously (doesn't block the map)
- Metrics update within 500ms of zoom/pan completion
- Handles datasets with 100K+ records efficiently
- Optimized JavaScript for smooth updates

### Browser Compatibility

✅ Works in all modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Metrics Panel Not Showing

**Problem**: Panel is not visible on the right side

**Solutions**:
1. Refresh the page (F5)
2. Check browser console for errors (F12)
3. Ensure `MASTER_DATASET.csv` is in the same directory
4. Zoom in to activate data loading

### Metrics Show "Loading..."

**Problem**: Metrics stay in loading state

**Solutions**:
1. Wait 2-3 seconds for CSV to load
2. Check internet connection (needed for some map tiles)
3. Check browser console for network errors
4. Verify CSV file is valid

### No Data Points in Area

**Problem**: "Zoom in to view metrics for this area" message

**Solutions**:
1. Your view area has no sensor data
2. Try zooming to a different region
3. Pan to city centers (Dehradun, Haridwar, Rishikesh)
4. Check zoom level is 10+ for better data visibility

### Metrics Are Incorrect

**Problem**: Statistics don't look right

**Solutions**:
1. Check that all CSV columns are present and properly named
2. Verify data types (numbers not text)
3. Ensure coordinates are valid (-90 to 90, -180 to 180)
4. Check for and remove duplicate rows in CSV

## Examples

### Example 1: Finding Polluted Zones
1. Open the map
2. Zoom to level 12-13
3. Look for high percentages in RED (HIGH) risk
4. Click on markers for detailed sensor information

### Example 2: Comparing Two Areas
1. Pan to first area
2. Note the metrics (Average PM2.5, Risk %)
3. Pan to second area
4. Compare with first area's metrics

### Example 3: Understanding Weather Impact
1. Look at Climate section (Temperature, Humidity)
2. High temp + High humidity = Worse air quality
3. Low wind = PM2.5 accumulation
4. Understand cause of pollution events

## Data Columns Used

The metrics panel uses the following columns from your CSV:

**Required:**
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `pm25`: PM2.5 concentration

**Optional (for enhanced metrics):**
- `sensor_name`: Sensor identifier
- `city`: City name
- `zone_type`: Zone classification
- `temperature_c`: Temperature
- `humidity_pct`: Humidity
- `wind_speed_kmh`: Wind speed

## Customization

### Changing Update Frequency

Edit `gis_pipeline.py` and modify:
```python
setTimeout(() => { updateMetricsOnMapChange(); }, 500);  # in milliseconds
```

### Adjusting Risk Thresholds

Edit the risk classification in `gis_pipeline.py`:
```python
if pm25 > 150:  # Change threshold here
    risk = "HIGH"
```

### Modifying Panel Size

Edit the CSS in `gis_pipeline.py` metrics_style:
```css
.metrics-panel {
    max-width: 380px;  # Change width
    max-height: 500px; # Change height
}
```

## Performance Optimization

For very large datasets (>500K records):

1. **Filter by date range** before generating the map
2. **Reduce CSV size** if possible
3. **Zoom to regions** for better performance
4. **Use browser dev tools** to monitor performance (F12)

## API Reference

### JavaScript Functions

**loadCSVData()**
- Loads the CSV file asynchronously
- Parses data and populates csvData array
- Called automatically on page load

**updateMetricsOnMapChange()**
- Triggered on zoom/pan events
- Calculates visible metrics
- Updates panel with new data

**getMapObject()**
- Finds the Leaflet map instance
- Works with Folium-generated maps
- Returns map object for event binding

## Support and Feedback

If you encounter issues or have suggestions:

1. Check the troubleshooting section
2. Review console logs (F12 → Console tab)
3. Verify CSV format and data
4. Test with sample data first

## Version History

- **v2.0** (Latest)
  - Added dynamic metrics panel
  - Real-time zoom and pan updates
  - Statistical calculations
  - Climate data integration
  - Enhanced error handling

- **v1.0**
  - Basic map functionality
  - Static legend
  - Heatmap visualization

---

**Last Updated:** May 28, 2026
