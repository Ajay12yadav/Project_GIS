"""
Configuration Guide for GIS PM2.5 Project
==========================================

This file contains additional configuration options and setup instructions.
"""

# =====================================================================
# INSTALLATION GUIDE
# =====================================================================

"""
Step 1: Create a Python Virtual Environment (Recommended)
---------------------------------------------------------
python -m venv venv

# Activate virtual environment:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
"""

"""
Step 2: Install Dependencies
-----------------------------
pip install -r requirements.txt

# Optional: Install additional packages for enhanced functionality
pip install matplotlib seaborn tqdm jupyter

# Verify installation:
python -c "import pandas, folium, numpy; print('All packages installed successfully!')"
"""

# =====================================================================
# ENVIRONMENT VARIABLES (Optional)
# =====================================================================

"""
Create a .env file in the project root for configuration:

CSV_FILE_PATH=./MASTER_DATASET.csv
OUTPUT_MAP_PATH=./city_map.html
OUTPUT_ANALYSIS_PATH=./zone_analysis.csv
LOG_LEVEL=INFO
MAP_ZOOM_LEVEL=12
MAP_CENTER_LAT=30.16315
MAP_CENTER_LON=78.131
"""

# =====================================================================
# RUNNING THE PIPELINE
# =====================================================================

"""
Basic Usage:
-----------
python gis_pipeline.py

Expected Output:
- Console logs showing progress
- zone_analysis.csv (generated statistics)
- city_map.html (interactive map)

Troubleshooting:
---------------
1. If CSV not found: Ensure MASTER_DATASET.csv is in the same directory
2. If import errors: Run 'pip install -r requirements.txt' again
3. If map won't load: Check internet connection (needed for map tiles)
4. If no data points: Verify CSV format and coordinate columns
"""

# =====================================================================
# DATA FORMAT SPECIFICATIONS
# =====================================================================

"""
MASTER_DATASET.csv Requirements:
--------------------------------

Required Columns (case-insensitive):
- latitude or lat: Geographic latitude (-90 to 90)
- longitude or lon: Geographic longitude (-180 to 180)
- pm25 or pm2.5: PM2.5 concentration in µg/m³
- sensor_name: Sensor identifier
- city: City name
- zone_type: Type of zone (residential, industrial, school_zone, hospital_zone, market, highway)

Optional but Recommended:
- date: Date of measurement
- temperature_c: Temperature in Celsius
- humidity_pct: Humidity percentage
- weather: Weather condition
- aerosol_index: Aerosol optical depth
- traffic_level: Traffic congestion level
- aqi_category: AQI category classification
- urgency_score: Risk urgency score
- wind_speed_kmh: Wind speed
- is_raining: Boolean for rain condition

Data Quality Guidelines:
- No missing values for latitude, longitude, or pm25
- Coordinates must be valid (lat: -90 to 90, lon: -180 to 180)
- PM2.5 values should be non-negative
- Dates should be in YYYY-MM-DD format
"""

# =====================================================================
# CUSTOMIZATION OPTIONS
# =====================================================================

"""
Color Scheme Customization:
--------------------------
In gis_pipeline.py, modify calculate_risk_metrics() function:

Example: Change HIGH risk color from red (#ff0000) to purple:
    'color': '#9c27b0',  # PURPLE
    
Available colors:
    Low:     #00cc44 (green)
    Medium:  #ff9900 (orange)
    High:    #ff0000 (red)
    Custom:  Use any hex color code

Heatmap Gradient:
-----------------
In create_map() function, modify HeatMap gradient:
    gradient={
        0.0: '#00ff00',   # Green at 0%
        0.5: '#ffff00',   # Yellow at 50%
        1.0: '#ff0000'    # Red at 100%
    }

Map Center and Zoom:
-------------------
Change these constants at the top of gis_pipeline.py:
    MAP_CENTER = [latitude, longitude]
    MAP_ZOOM = zoom_level (2-20, higher = closer)
"""

# =====================================================================
# ADVANCED FEATURES
# =====================================================================

"""
1. Custom Risk Thresholds:
--------------------------
Modify calculate_risk_metrics() to use different PM2.5 thresholds:
    if avg_pm25 > 100:  # Changed from 150
        risk = "HIGH"
    elif avg_pm25 > 50:  # Changed from 80
        risk = "MEDIUM"

2. Filter Data by Zone Type:
---------------------------
Add in main() before create_map():
    df_filtered = df[df['zone_type'] == 'industrial']
    create_map(df_filtered)

3. Export Analysis to Multiple Formats:
--------------------------------------
In generate_zone_analysis():
    zone_stats.to_excel('zone_analysis.xlsx')  # Requires: pip install openpyxl
    zone_stats.to_json('zone_analysis.json')
    zone_stats.to_html('zone_analysis.html')

4. Add Time-Based Analysis:
---------------------------
df['date'] = pd.to_datetime(df['date'])
daily_stats = df.groupby(df['date'].dt.date)['pm25'].agg(['mean', 'max', 'min'])

5. Generate Additional Visualizations:
-------------------------------------
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
df.groupby('zone_type')['pm25'].mean().plot(kind='bar', color=['#00cc44', '#ff9900', '#ff0000'])
plt.title('Average PM2.5 by Zone Type')
plt.ylabel('PM2.5 (µg/m³)')
plt.savefig('zone_pm25_comparison.png')
"""

# =====================================================================
# PERFORMANCE OPTIMIZATION
# =====================================================================

"""
For Large Datasets (>100K records):
----------------------------------

1. Reduce marker density - skip every Nth row:
   for idx, row in df.iterrows():
       if idx % 10 != 0:  # Process every 10th row
           continue

2. Use data chunking for processing:
   chunk_size = 5000
   for chunk in pd.read_csv('MASTER_DATASET.csv', chunksize=chunk_size):
       process_chunk(chunk)

3. Pre-filter data before mapping:
   df = df[df['pm25'].notna()]  # Remove null values
   df = df[(df['pm25'] > 0) & (df['pm25'] < 1000)]  # Remove outliers

4. Use simpler base map for faster rendering:
   tiles='CartoDB positron'  # Lighter than OpenStreetMap
"""

# =====================================================================
# TROUBLESHOOTING CHECKLIST
# =====================================================================

"""
Issue: "Module not found" error
Solution:
- Run: pip install -r requirements.txt
- Check Python version: python --version (requires 3.8+)
- Verify virtual environment is activated

Issue: "CSV file not found" error
Solution:
- Ensure MASTER_DATASET.csv is in the project directory
- Check file permissions: chmod +r MASTER_DATASET.csv (Linux/Mac)
- Verify CSV file is not corrupted

Issue: Map won't load in browser
Solution:
- Check internet connection (needed for Leaflet tiles)
- Try a different browser
- Clear browser cache
- Check browser console for JavaScript errors (F12)

Issue: No data points on map
Solution:
- Verify CSV has required columns (latitude, longitude, pm25)
- Check column names match (case-sensitive in some cases)
- Run: python -c "import pandas; df = pd.read_csv('MASTER_DATASET.csv'); print(df.columns)"
- Look for error logs in console output

Issue: Slow performance
Solution:
- Use smaller dataset for testing
- Check system RAM availability
- Reduce number of markers (skip rows)
- Use simpler base map tiles

Issue: Data validation warnings
Solution:
- Check for null/NaN values: df.isnull().sum()
- Check coordinate ranges: df[['latitude', 'longitude']].describe()
- Check PM2.5 value ranges: df['pm25'].describe()
"""

# =====================================================================
# MAINTENANCE
# =====================================================================

"""
Regular Updates:
---------------
1. Update dependencies: pip install --upgrade -r requirements.txt
2. Monitor CSV file size and archive old data
3. Test with new data samples periodically
4. Review console logs for warnings

Backup Strategy:
---------------
1. Keep backup copy of original CSV
2. Version control the pipeline code
3. Export analysis results regularly
4. Save map HTML files periodically

Data Refresh Cycle:
------------------
- Daily: Check for new sensor readings
- Weekly: Regenerate analysis and statistics
- Monthly: Review trends and anomalies
- Quarterly: Update documentation and configurations
"""

# =====================================================================
# DEPENDENCIES AND VERSIONS
# =====================================================================

"""
Core Package Information:
------------------------

pandas (2.0.0+)
- Data manipulation and analysis
- CSV reading and processing
- Group-by operations

folium (0.14.0+)
- Interactive map generation
- Marker and circle rendering
- Custom HTML/JS integration

numpy (1.24.0+)
- Numerical computations
- Array operations
- Data type handling

scikit-learn (1.3.0+)
- Machine learning utilities
- Data preprocessing

Optional Packages:
-----------------
matplotlib (3.7.0+) - Static visualizations
seaborn (0.12.0+) - Advanced statistical plots
jupyter (1.0.0+) - Interactive notebooks
geopy (2.3.0+) - Geocoding and geolocation
tqdm (4.65.0+) - Progress bars
"""

# =====================================================================
# CONTRIBUTING GUIDELINES
# =====================================================================

"""
Code Style:
----------
- Follow PEP 8 style guide
- Use type hints for function parameters
- Write docstrings for all functions
- Keep lines under 100 characters

Testing:
-------
- Test with different data samples
- Verify error handling with edge cases
- Test in different browsers for HTML output
- Check performance with large datasets

Documentation:
--------------
- Update README.md for major changes
- Add inline comments for complex logic
- Document new configuration options
- Include examples in docstrings

Reporting Issues:
-----------------
- Include error messages and logs
- Provide minimal reproducible example
- Specify Python version and OS
- List installed package versions
"""

# =====================================================================
# VERSION HISTORY
# =====================================================================

"""
v1.0 (May 2026)
- Initial release
- Basic mapping and heatmap functionality
- Zone analysis generation
- Comprehensive error handling
- Full documentation
"""

# =====================================================================
# CONTACT AND SUPPORT
# =====================================================================

"""
For additional support or questions:
1. Review the README.md file
2. Check the console logs for error messages
3. Verify data format matches specifications
4. Test with sample data first

Project Resources:
- Documentation: README.md
- Configuration: SETUP.py (this file)
- Main Pipeline: gis_pipeline.py
- Web Interface: city_map.html
"""
