import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide", page_title="NYPD Complaint Dashboard")

# Sidebar
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Crime Locations",
        "Borough & Precincts",
        "Time-Based Trends",
        "Complaint Explorer",
        "Missing Data",
    ],
)

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    # Direct download URL for your shared Google Drive CSV
    url = "https://drive.google.com/file/d/1oLtYA2XcakCf5EV9-8_fa2v27d-ylSm0/view?usp=drive_link"

    try:
        df = pd.read_csv(url)
    except Exception as e:
        st.error(
            "❌ Failed to load the dataset from Google Drive.\n\n"
            "Make sure the file is shared with 'Anyone with link'.\n"
            f"Details: {e}"
        )
        st.stop()

    # Convert dates/times
    df["CMPLNT_FR_DT"] = pd.to_datetime(df["CMPLNT_FR_DT"], errors="coerce")
    df["CMPLNT_FR_HOUR"] = pd.to_datetime(
        df["CMPLNT_FR_TM"], errors="coerce"
    ).dt.hour
    df["DayOfWeek"] = df["CMPLNT_FR_DT"].dt.day_name()

    # Drop rows without coordinates
    df = df.dropna(subset=["Latitude", "Longitude"])

    return df


df = load_data()

# -------------------- SECTIONS --------------------
if section == "Overview":
    st.title("🚔 NYPD Complaint Data - Overview")
    st.write(f"Dataset shape: {df.shape}")
    st.dataframe(df.head())

    st.subheader("Top Complaint Types")
    st.bar_chart(df["OFNS_DESC"].value_counts().head(10))

elif section == "Crime Locations":
    st.title("📍 Crime Locations Map")
    map_df = df[["Latitude", "Longitude"]].rename(
        columns={"Latitude": "latitude", "Longitude": "longitude"}
    )
    st.map(map_df)

elif section == "Borough & Precincts":
    st.title("🏙️ Borough and Precinct Analysis")

    borough_counts = df["BORO_NM"].value_counts()
    fig1 = px.bar(
        x=borough_counts.index,
        y=borough_counts.values,
        labels={"x": "Borough", "y": "Complaints"},
        title="Complaints by Borough",
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 Precincts")
    top_precincts = df["ADDR_PCT_CD"].value_counts().head(10)
    fig2 = px.bar(
        x=top_precincts.index.astype(str),
        y=top_precincts.values,
        labels={"x": "Precinct", "y": "Complaints"},
        title="Top Precincts by Complaints",
    )
    st.plotly_chart(fig2, use_container_width=True)

elif section == "Time-Based Trends":
    st.title("⏰ Time-Based Crime Trends")

    hourly = df["CMPLNT_FR_HOUR"].value_counts().sort_index()
    fig3 = px.line(
        x=hourly.index,
        y=hourly.values,
        labels={"x": "Hour of Day", "y": "Number of Complaints"},
        title="Complaints by Hour",
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📆 Heatmap of Complaints by Day and Hour")
    heat_df = df.groupby(["DayOfWeek", "CMPLNT_FR_HOUR"]).size().unstack()
    heat_df = heat_df.reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )

    fig4, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heat_df.fillna(0), cmap="YlOrRd", ax=ax)
    st.pyplot(fig4)

elif section == "Complaint Explorer":
    st.title("🔍 Complaint Type Explorer")

    selected_type = st.selectbox(
        "Select Complaint Type",
        sorted(df["OFNS_DESC"].dropna().unique()),
    )

    filtered = df[df["OFNS_DESC"] == selected_type]
    st.write(f"Total complaints of type **{selected_type}**: {len(filtered)}")

    fig5 = px.scatter_mapbox(
        filtered,
        lat="Latitude",
        lon="Longitude",
        hover_data=["CMPLNT_FR_DT", "BORO_NM"],
        zoom=10,
        height=500,
    )
    fig5.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig5, use_container_width=True)

elif section == "Missing Data":
    st.title("🧼 Missing Data Overview")
    st.dataframe(df.isnull().sum())
