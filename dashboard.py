import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Store Intelligence Dashboard",
    layout="wide"
)

st.title("🏪 Store Intelligence Dashboard")

placeholder = st.empty()

while True:

    try:

        summary = requests.get(
            "http://127.0.0.1:8000/metrics/summary"
        ).json()

        zones = requests.get(
            "http://127.0.0.1:8000/metrics/zones"
        ).json()

        billing = requests.get(
            "http://127.0.0.1:8000/metrics/billing"
        ).json()

        with placeholder.container():

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Entry Count",
                summary.get("entry_count", 0)
            )

            col2.metric(
                "Exit Count",
                summary.get("exit_count", 0)
            )

            col3.metric(
                "Reentry Count",
                summary.get("reentry_count", 0)
            )

            col4.metric(
                "Occupancy",
                summary.get("occupancy", 0)
            )

            st.subheader("Zone Analytics")

            st.json(zones)

            st.subheader("Billing Metrics")

            st.json(billing)

        time.sleep(2)

    except Exception as e:

        st.error(f"API ERROR: {e}")

        time.sleep(2)