# streamlit_app/app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import date
import pydeck as pdk

# ---------------------------
# Database connection
# ---------------------------
DB_URL = "postgresql+psycopg2://postgres:root@localhost:5433/oceandb"
engine = create_engine(DB_URL)

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="Ocean Float Data Explorer", layout="wide")
st.title("🌊 Ocean Float Data Explorer")

# Sidebar controls
st.sidebar.header("Filters")

# Variable selector
variable = st.sidebar.selectbox("Choose variable", ["TEMP", "PSAL"])

# Depth slider
depth_limit = st.sidebar.slider("Max depth (m)", 0, 2000, 10, step=10)

# Date range
start_date = st.sidebar.date_input("Start date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End date", date.today())

# ---------------------------
# SQL query for time-series
# ---------------------------
query = f"""
SELECT date_trunc('day', obs_time) AS day, AVG(value) AS avg_val
FROM observations
WHERE variable = '{variable}'
  AND depth < {depth_limit}
  AND obs_time BETWEEN '{start_date}' AND '{end_date}'
GROUP BY day
ORDER BY day;
"""

df = pd.read_sql(query, engine)

# ---------------------------
# Show line chart
# ---------------------------
st.subheader(f"📈 Daily Average {variable} (Depth < {depth_limit}m)")
if df.empty:
    st.warning("No data available for selected filters.")
else:
    st.line_chart(df.set_index("day"))

# ---------------------------
# SQL query for spatial data
# ---------------------------
map_query = f"""
SELECT lon, lat, AVG(value) as val
FROM observations
WHERE variable = '{variable}'
  AND depth < {depth_limit}
  AND obs_time BETWEEN '{start_date}' AND '{end_date}'
GROUP BY lon, lat
LIMIT 2000;
"""

map_df = pd.read_sql(map_query, engine)

# ---------------------------
# Show map
# ---------------------------
st.subheader(f"🗺️ Spatial Distribution of {variable}")
if map_df.empty:
    st.warning("No spatial data available for selected filters.")
else:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v9",
        initial_view_state=pdk.ViewState(
            latitude=20, longitude=80, zoom=3, pitch=0
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=30000,
                pickable=True,
            ),
        ],
        tooltip={"text": f"{variable}: {{val}}"}
    ))
