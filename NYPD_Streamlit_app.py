import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import os

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
    file_id = "1IKme2tIvwZOhFUxwVBEMwItx2-coVNVY"
    output = "nypd_data.csv"

    if not os.path.exists(output):
        with st.spinner("📥 Downloading dataset from Google Drive..."):
            url = "https://drive.google.com/file/d/1jTZvPE1jhk-pde0Q1ywYY0Detd_IeXGU/view?usp=sharing"
            session = requests.Session()
            response = session.get(url, params={"id": file_id}, stream=True)

            # Handle Google Drive confirmation token
            for key, value in response.cookies.items():
                if key.startswith("download_warning"):
                    response = session.get(
                        url,
                        params={"id": file_id, "confirm": value},
                        stream=True,
                    )

            with open(output, "wb") as f:
                for chunk in response.iter_content(32768):
                    if chunk:
                        f.write(chunk)

    df = pd.read_csv(output, low_memory=False)

    df["CMPLNT_FR_DT"] = pd.to_datetime(df["CMPLNT_FR_DT"], errors="coerce")
    df["CMPLNT_FR_HOUR"] = pd.to_datetime(
        df["CMPLNT_FR_TM"], errors="coerce"
    ).dt.hour
    df["DayOfWeek"] = df["CMPLNT_FR_DT"].dt.day_name()

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
        labels={"x": "H
