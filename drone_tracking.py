# drone_tracking.py
# Single-file Streamlit app that reads drone_path.csv and shows a smooth animation in-browser.
# Requirements:
#   pip install streamlit streamlit-folium folium pandas

import streamlit as st
import pandas as pd
import math
import json
from streamlit.components.v1 import html as components_html

st.set_page_config(page_title="Drone Tracker (CSV → Smooth animation)", layout="wide")
st.title("Drone Tracker — Smooth mock live animation (from CSV)")

CSV_PATH = "drone_path.csv"

# Load CSV
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Failed to read '{CSV_PATH}': {e}")
    st.stop()

if df.shape[0] < 2:
    st.error("CSV must contain at least two rows (lat,lon). Example:\nlat,lon\n18.9220,72.8347\n...")
    st.stop()

# Convert to float and prepare points as list of [lat, lon]
df = df[['lat', 'lon']].astype(float)
points = df.values.tolist()  # [[lat, lon], ...]

# Sidebar controls
speed_m_s = st.sidebar.slider("Playback speed (meters / second)", min_value=1, max_value=50, value=8)
min_segment_ms = st.sidebar.number_input("Minimum time per segment (ms)", min_value=100, max_value=10000, value=400, step=50)
auto_play = st.sidebar.checkbox("Auto play on load", value=True)
loop = st.sidebar.checkbox("Loop animation", value=False)

# Haversine distance (meters)
def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*(math.sin(dlambda/2.0)**2)
    return 2 * R * math.asin(math.sqrt(a))

# Compute per-segment durations (ms) proportional to distance and speed
durations = []
for i in range(len(points) - 1):
    d = haversine_m(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    ms = max(min_segment_ms, int(d / max(0.0001, speed_m_s) * 1000.0))
    durations.append(ms)

# Convert to JSON to embed into HTML/JS
points_json = json.dumps(points)       # [[lat, lon], ...]
durations_json = json.dumps(durations) # [ms, ms, ...]

# Build HTML with Leaflet + JS animation (requestAnimationFrame interpolation)
html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>Drone mock animation</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
  html, body, #map {{ height:100%; margin:0; padding:0; }}
  #map {{ width:100%; height:650px; }}
  .leaflet-top {{ z-index:1000; }}
</style>
</head>
<body>
<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const points = {points_json};  // [ [lat, lon], ... ]
const durations = {durations_json}; // ms per segment
const autoPlay = {str(auto_play).lower()};
const doLoop = {str(loop).lower()};

const map = L.map('map', {{zoomControl:true}}).setView(points[0], 17);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}}).addTo(map);

// draw full route
const fullLine = L.polyline(points, {{color:'blue', weight:4, opacity:0.6}}).addTo(map);

// trail (the path covered so far)
const trail = L.polyline([points[0]], {{color:'#00c9ff', weight:4}}).addTo(map);

// drone icon
const droneIcon = L.icon({{
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/744/744465.png',
  iconSize: [34,34],
  iconAnchor: [17,17]
}});

// marker starting position
const marker = L.marker(points[0], {{icon: droneIcon}}).addTo(map);

// interpolation animation per segment
function animateSegment(from, to, durationMs) {{
  return new Promise(resolve => {{
    const startTime = performance.now();
    function step(now) {{
      const t = Math.min(1, (now - startTime) / durationMs);
      const lat = from[0] + (to[0] - from[0]) * t;
      const lon = from[1] + (to[1] - from[1]) * t;
      marker.setLatLng([lat, lon]);
      // update trail by adding interpolated point (keeps trail smooth)
      const last = trail.getLatLngs();
      const lastLat = last.length ? last[last.length-1].lat : null;
      if (lastLat === null || Math.abs(last[last.length-1].lat - lat) > 1e-8 || Math.abs(last[last.length-1].lng - lon) > 1e-8) {{
        trail.addLatLng([lat, lon]);
      }}
      if (t < 1) requestAnimationFrame(step);
      else resolve();
    }}
    requestAnimationFrame(step);
  }});
}}

// main animation loop
async function runAnimation() {{
  do {{
    trail.setLatLngs([points[0]]);
    marker.setLatLng(points[0]);
    for (let i=0;i<points.length-1;i++) {{
      await animateSegment(points[i], points[i+1], durations[i]);
    }}
  }} while (doLoop);
}}

// start automatically if requested
if (autoPlay) {{
  runAnimation();
}} else {{
  // show a start button overlay if not auto play
  const btn = L.control({{position:'topleft'}});
  btn.onAdd = function() {{
    var div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
    div.style.background = 'white';
    div.style.padding = '6px';
    div.style.cursor = 'pointer';
    div.innerHTML = '<b>Start</b>';
    L.DomEvent.on(div, 'click', function() {{
      runAnimation();
      div.style.display='none';
    }});
    return div;
  }};
  btn.addTo(map);
}}
</script>
</body>
</html>
"""

# Render the HTML block (single iframe). The animation runs in browser JS -> no blinking.
components_html(html, height=700)
