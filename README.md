# 📡 Drone Tracking (Real-Time Mock Demo)

This project demonstrates **real-time GPS tracking of a drone** using **Python + Streamlit + Folium**.  
It shows a moving marker on a map, just like how Google Maps shows live movement.  

---

## 🚀 Features
- Displays a **drone moving along GPS coordinates** on a map.  
- Uses **Folium + Leaflet MovingMarker plugin** for smooth animation.  
- Reads coordinates from a CSV file (`drone_path.csv`).  
- **API Ready** → can be connected to a live GPS feed (e.g., Raspberry Pi + GPS module).  

---

## 📂 Project Structure
Drone tracking/
│── drone_tracking.py # Main Streamlit app
│── drone_path.csv # Mock GPS path (lat, lon)
│── README.md # Project documentation
│── .streamlit/ # Streamlit config files

yaml
Copy code

---

## 🔧 Installation

1. **Clone or copy the folder**  
   Place `drone_tracking.py` and `drone_path.csv` inside the same directory.

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   source venv/bin/activate  # On Mac/Linux
Install dependencies:

bash
Copy code
pip install streamlit folium streamlit-folium pandas
▶️ Running the App
Inside the project folder (Drone tracking):

bash
Copy code
python -m streamlit run drone_tracking.py
This will open the app in your browser at:
👉 http://localhost:8501

📊 CSV File Format (drone_path.csv)
The CSV contains latitude and longitude coordinates:

csv
Copy code
lat,lon
19.428,72.824
19.429,72.825
19.430,72.826
19.431,72.827
Each row = one GPS position.

The script animates movement along these points.

🌍 Switching to Live API
Currently, coordinates are loaded from drone_path.csv.
To use real-time GPS data from an API:

Replace this line in drone_tracking.py:

python
Copy code
df = pd.read_csv("drone_path.csv")
with:

python
Copy code
import requests
response = requests.get("http://your-api-url/drone")
latest_data = response.json()
lat, lon = latest_data["lat"], latest_data["lon"]
Append new coordinates into the list (or DataFrame).

The marker will automatically update position in real-time.

✅ Next Steps
Integrate with your drone’s GPS + Raspberry Pi API.

Use WebSocket streaming instead of polling for smoother real-time tracking.

Add UI features like speed control, pause/resume, and historical path playback.

🛠️ Tech Stack
Python 3.9+

Streamlit (web interface)

Folium + Leaflet (map rendering & animation)

Pandas (CSV handling)

