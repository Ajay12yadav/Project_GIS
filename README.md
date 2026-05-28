# GIS PM2.5 Air Quality Analysis Project

A comprehensive Geographic Information System (GIS) application for analyzing and visualizing PM2.5 air quality data across multiple cities and zones.

## 📊 Overview

This project combines satellite data with geospatial analysis to create interactive heat maps and risk assessments for air quality monitoring. It processes multi-source sensor data and generates visual representations for better understanding of pollution patterns.

**Key Cities Covered:**
- Dehradun
- Haridwar
- Rishikesh

**Zone Types Analyzed:**
- Residential
- Industrial
- School Zones
- Hospital Zones
- Markets
- Highways

## 🚀 Features

### Data Processing
- **CSV Data Loading**: Robust data import with error handling
- **Data Validation**: Automatic column detection and validation
- **Risk Classification**: PM2.5 levels classified as HIGH (>150), MEDIUM (81-150), LOW (≤80)
- **Zone Analytics**: Statistical analysis by zone type

### Visualization
- **Interactive Maps**: Leaflet.js powered maps with multiple layers
- **Heat Maps**: Visual representation of pollution concentration
- **Risk Indicators**: Color-coded markers (Red/Orange/Green)
- **Layer Control**: Toggle between map types and data layers
- **Fullscreen Mode**: Immersive viewing experience

### Technical Features
- Type hints and documentation
- Comprehensive error handling and logging
- Efficient data processing with Pandas & NumPy
- Responsive HTML interface

## 📁 Project Structure

```
gis-project/
├── gis_pipeline.py           # Main Python pipeline
├── city_map.html            # Interactive web map
├── MASTER_DATASET.csv       # Raw sensor data
├── zone_analysis.csv        # Generated zone statistics
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd gis-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Running the Pipeline

```bash
python gis_pipeline.py
```

This will:
1. Load data from `MASTER_DATASET.csv`
2. Validate the data structure
3. Generate zone-wise analysis and save to `zone_analysis.csv`
4. Create an interactive map and save to `city_map.html`
5. Log progress and any warnings to console

### Viewing the Map

Open `city_map.html` in any modern web browser to explore the interactive map.

**Map Features:**
- Pan and zoom to explore different areas
- Click on markers to see detailed sensor information
- Toggle heat map and marker layers on/off
- Switch between Light, Dark, and Satellite map backgrounds
- Use fullscreen mode for better viewing

## 📊 Data Structure

### Input: MASTER_DATASET.csv

Required columns:
- `date` - Date of measurement
- `latitude` - Geographic latitude
- `longitude` - Geographic longitude
- `pm25` - PM2.5 concentration (µg/m³)
- `sensor_name` - Sensor identifier
- `city` - City name
- `zone_type` - Type of zone (residential, industrial, etc.)
- Additional fields (temperature, humidity, weather, etc.)

### Output: zone_analysis.csv

Generated statistics by zone:
- `avg_pm25` - Average PM2.5 level
- `max_pm25` - Maximum recorded PM2.5
- `min_pm25` - Minimum recorded PM2.5
- `readings` - Number of observations
- `unique_sensors` - Count of unique sensors
- `unique_cities` - Count of cities in zone
- `risk_level` - Overall risk classification

## ⚙️ Configuration

Edit the following in `gis_pipeline.py` to customize:

```python
CSV_FILE = 'MASTER_DATASET.csv'          # Input data file
OUTPUT_MAP_FILE = 'city_map.html'        # Output map file
OUTPUT_ANALYSIS_FILE = 'zone_analysis.csv' # Output analysis file
MAP_CENTER = [30.16315, 78.131]          # Default map center
MAP_ZOOM = 12                             # Default zoom level
```

## 📈 Risk Classification

| Risk Level | PM2.5 Range | Color | Interpretation |
|-----------|------------|-------|-----------------|
| HIGH | > 150 µg/m³ | 🔴 Red | Unhealthy - Everyone at risk |
| MEDIUM | 81-150 µg/m³ | 🟠 Orange | Unhealthy for Sensitive Groups |
| LOW | ≤ 80 µg/m³ | 🟢 Green | Acceptable Air Quality |

## 🐛 Error Handling

The application includes comprehensive error handling for:
- Missing or corrupted CSV files
- Invalid coordinate data
- Missing required columns
- Data type conversion errors
- File I/O operations

All errors are logged with descriptive messages for debugging.

## 📝 Logging

Logs are displayed in the console with the following format:
```
YYYY-MM-DD HH:MM:SS - LEVEL - Message
```

**Log Levels:**
- `INFO`: General operation information
- `WARNING`: Non-fatal issues (e.g., invalid coordinates)
- `ERROR`: Failures that may stop execution

## 🔧 Technologies Used

### Python Libraries
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **folium** - Interactive map generation
- **scikit-learn** - Machine learning utilities

### Frontend
- **Leaflet.js** - Interactive mapping
- **Leaflet HeatMap Plugin** - Heat map visualization
- **CartoDB** - Base map tiles

## 📋 Requirements

See [requirements.txt](requirements.txt) for detailed package versions.

Core dependencies:
- pandas >= 2.0.0
- numpy >= 1.24.0
- folium >= 0.14.0
- scikit-learn >= 1.3.0

## 🤝 Contributing

To improve this project:

1. **Data Quality**: Ensure input CSV has all required columns
2. **Code Style**: Follow PEP 8 conventions
3. **Documentation**: Add docstrings to new functions
4. **Testing**: Validate with sample data

## 📄 License

This project analyzes publicly available air quality data from SENTINEL5P satellite imagery.

## 🔗 Data Source

- **Satellite Data**: SENTINEL5P (European Space Agency)
- **Collection Method**: GEE (Google Earth Engine)
- **Coverage**: Real-time air quality monitoring
- **Time Period**: 2019-Present

## 🚨 Important Notes

- **Data Accuracy**: Results depend on input data quality
- **Coordinate Validation**: Invalid coordinates are automatically skipped
- **Performance**: Large datasets (>100K records) may take time to process
- **Browser Compatibility**: Use modern browsers (Chrome, Firefox, Safari, Edge)

## ❓ Troubleshooting

### Map won't load
- Verify `MASTER_DATASET.csv` exists in the project directory
- Check browser console for JavaScript errors
- Ensure internet connection for map tiles

### No data points showing
- Check CSV file is in correct format
- Verify coordinate columns are named correctly
- Look for error messages in console output

### Python errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8 or higher
- Check file permissions on CSV files

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the console logs for error messages
3. Verify data format matches requirements

## ✨ Future Enhancements

Planned improvements:
- Time-series analysis and forecasting
- Advanced statistical models
- Comparison between zones and cities
- Mobile-responsive interface
- Real-time data integration
- Export analysis as PDF reports

---

**Last Updated:** May 2026
**Version:** 1.0
