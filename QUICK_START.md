# Quick Start: Zoom Metrics Feature 🚀

## What's New?

When you zoom and pan the map, you'll now see **real-time metrics** for that specific area!

## How to Use It

### 1. Generate the Map
```bash
python gis_pipeline.py
```

This creates `city_map.html` with the enhanced metrics feature.

### 2. Open in Browser
- Double-click `city_map.html` or drag it to your browser
- Wait for the map to load (takes 2-3 seconds)

### 3. Zoom to See Metrics
```
🔍 Use your mouse wheel to zoom in/out
👆 Click and drag to pan around
📊 Watch the metrics panel on the right update automatically!
```

## What You'll See

### Metrics Panel (Right Side)
```
┌─────────────────────────────┐
│ 📊 Area Metrics             │
├─────────────────────────────┤
│ Zoom Level: 12 | Points: 45 │
├─────────────────────────────┤
│ PM2.5 LEVELS (µg/m³)        │
│ Average:      45.32         │
│ Maximum:      125.50        │
│ Minimum:       8.20         │
├─────────────────────────────┤
│ RISK DISTRIBUTION           │
│ 🔴 High (>150):   0 (0%)    │
│ 🟠 Medium:        8 (17%)   │
│ 🟢 Low (≤80):    37 (83%)   │
├─────────────────────────────┤
│ 🌡️ CLIMATE                 │
│ Avg Temperature: 22.5°C     │
│ Avg Humidity:    55.0%      │
└─────────────────────────────┘
```

## 5 Key Metrics Explained

### 1. **PM2.5 Average** 
The typical pollution level in this area
- Low: Good air quality
- High: Poor air quality

### 2. **PM2.5 Maximum** 
Highest pollution recorded
- Shows worst-case scenario
- Red color = HIGH risk

### 3. **PM2.5 Minimum**
Lowest pollution recorded
- Shows best-case scenario
- Green color = LOW risk

### 4. **Risk Distribution**
What percentage of sensors show each risk level
- High % means many areas are problematic
- Low % means area is generally safe

### 5. **Climate Conditions**
Temperature, humidity, wind speed
- Affects how pollutants disperse
- High temp + low wind = more pollution

## Color Guide 🎨

| Color | Meaning | Risk Level |
|-------|---------|-----------|
| 🟢 Green | Safe | Low (≤80 µg/m³) |
| 🟠 Orange | Caution | Medium (81-150 µg/m³) |
| 🔴 Red | Danger | High (>150 µg/m³) |

## Pro Tips 💡

### Tip 1: Find Worst Polluted Areas
1. Zoom to city level (zoom 12)
2. Look for RED color in the risk distribution
3. Click those red markers for details

### Tip 2: Compare Two Areas
1. Pan to Area A and note the "Average PM2.5"
2. Pan to Area B and compare
3. Which has better air quality?

### Tip 3: Understand Pollution Patterns
1. Look at Climate Conditions
2. High temperature + High humidity + LOW wind = WORST air quality
3. Use this to predict bad air days

### Tip 4: Track Sensor Coverage
- "Points: X" tells you how many sensors are visible
- Zoom in more to see individual points
- Fewer points = less data for that area

## Example Workflows

### Workflow 1: Daily Air Quality Check
```
1. Open map
2. Zoom to your city (zoom 12)
3. Check "Average PM2.5"
4. Look at "Risk Distribution"
5. Check if it's safe to go outside
```

### Workflow 2: Compare Cities
```
1. Zoom to Dehradun → Note Average PM2.5
2. Zoom to Haridwar → Note Average PM2.5
3. Zoom to Rishikesh → Note Average PM2.5
4. Compare which city has best air quality
```

### Workflow 3: Understand a Pollution Event
```
1. Find area with High (red) risk zones
2. Check Temperature and Humidity
3. If high temp + high humidity = Pollution trapped
4. Check wind speed - if low = Pollution won't disperse
5. This explains why that area is polluted!
```

## Troubleshooting

### ❌ Metrics showing "Loading..."?
- Wait 2-3 seconds for CSV to load
- Check that `MASTER_DATASET.csv` exists

### ❌ Panel says "Zoom in to view metrics"?
- Your current view has no sensor data
- Try zooming to city centers:
  - Dehradun: [30.16, 78.13]
  - Haridwar: [29.96, 78.14]
  - Rishikesh: [30.11, 78.30]

### ❌ Numbers look wrong?
- Refresh the page (F5)
- Check that CSV file is in the same folder

## Technical Details

- **Update Speed**: Updates instantly after zoom/pan completes
- **Data Source**: MASTER_DATASET.csv
- **Calculation**: Real-time, on visible data points only
- **Performance**: Handles 100K+ records efficiently

## Files You Need

```
gis-project/
├── gis_pipeline.py           ← Run this to generate map
├── city_map.html            ← Open this in browser
├── MASTER_DATASET.csv       ← Data source (must exist)
└── METRICS_FEATURE.md       ← Detailed documentation
```

## Keyboard Shortcuts (in browser)

| Key | Action |
|-----|--------|
| `F5` | Refresh page |
| `F12` | Open developer console (for debugging) |
| `+/-` | Zoom in/out |
| `Scroll` | Zoom in/out (on map) |

## Next Steps

1. **Run the pipeline**: `python gis_pipeline.py`
2. **Open the map**: Open `city_map.html`
3. **Explore the data**: Zoom and pan around
4. **Check metrics**: Watch the panel update in real-time
5. **Analyze**: Use the data to understand air quality patterns

## Need Help?

See `METRICS_FEATURE.md` for detailed documentation including:
- Advanced features
- Statistical explanations
- Customization options
- Performance optimization
- API reference

---

**Quick Tip**: Start at zoom level 12 for the best overview! 📍
