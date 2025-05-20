# streamlit_app.py

import os
import datetime
import numbers
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────────────────────────────────────
# 1 · CONFIG & CONNECTIONS
# ─────────────────────────────────────────────────────────────────────────────

CSV_FILE = "/Users/adityahemantshahane/Desktop/codes/user_data.csv"

# Pull out the connection info and credentials separately
conn_info      = st.secrets["connections"]["gsheets"]
SPREADSHEET_URL = conn_info["spreadsheet"]
svc_creds       = conn_info["service_account_info"]

@st.cache_resource(show_spinner=False)
def _gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    return gspread.authorize(
        Credentials.from_service_account_info(svc_creds, scopes=scopes)
    )

# Initialize clients
gclient     = _gspread_client()
worksheet   = gclient.open_by_url(SPREADSHEET_URL).sheet1
conn_reader = st.connection("gsheets", type=GSheetsConnection)

# Column order used everywhere
expected_cols = [
    "Date & Time", "Name", "Mobile Number", "Aadhar Card Number", "Age",
    "Nationality", "Address", "Check-in Date", "Check-out Date",
    "Room Number", "Room Type", "Room Rent", "Total Stay", "Total Bill"
]

# If sheet is empty → create header row once
if not worksheet.get_all_values():
    worksheet.append_row(expected_cols)

# ─────────────────────────────────────────────────────────────────────────────
# 2 · SESSION DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# ─────────────────────────────────────────────────────────────────────────────
# 3 · UTILITY – convert cells to JSON-safe values
# ─────────────────────────────────────────────────────────────────────────────

def to_sheet(v):
    if pd.isna(v):
        return ""
    if isinstance(v, (datetime.date, datetime.datetime, pd.Timestamp)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, (numbers.Integral, np.integer)):
        return int(v)
    if isinstance(v, (numbers.Real, np.floating)):
        return float(v)
    return str(v)

# ─────────────────────────────────────────────────────────────────────────────
# 4 · UI
# ─────────────────────────────────────────────────────────────────────────────

st.title("🍽️ Welcome to Oceano Retreat")

now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"📅 **{now_str}**")
st.session_state.user_data["Date & Time"] = now_str

# 👤 Personal details
with st.expander("👤 Personal Details", expanded=True):
    for label, key in [
        ("Name", "Name"),
        ("Mobile Number", "Mobile Number"),
        ("Aadhar Card Number", "Aadhar Card Number"),
        ("Age", "Age"),
        ("Nationality", "Nationality"),
        ("Address", "Address"),
    ]:
        st.session_state.user_data[key] = st.text_input(
            label, st.session_state.user_data.get(key, "")
        )

# 🏨 Stay details
with st.expander("🏨 Stay Details"):
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data["Check-in Date"] = st.date_input(
            "Check-in", st.session_state.user_data.get(
                "Check-in Date", datetime.date.today()
            )
        )
        st.session_state.user_data["Room Number"] = st.text_input(
            "Room Number", st.session_state.user_data.get("Room Number", "")
        )
    with c2:
        st.session_state.user_data["Check-out Date"] = st.date_input(
            "Check-out", st.session_state.user_data.get(
                "Check-out Date", datetime.date.today()
            )
        )
        st.session_state.user_data["Room Type"] = st.selectbox(
            "Room Type", ["Single", "Double", "Suite"],
            index=["Single", "Double", "Suite"].index(
                st.session_state.user_data.get("Room Type", "Single")
            )
        )

    # Fixed room rent
    st.session_state.user_data["Room Rent"] = 1000

    # Stay length & bill
    st.session_state.user_data["Total Stay"] = (
        st.session_state.user_data["Check-out Date"] -
        st.session_state.user_data["Check-in Date"]
    ).days
    st.session_state.user_data["Total Bill"] = (
        st.session_state.user_data["Total Stay"] * 1000
    )

    st.info(
        f"Stay = {st.session_state.user_data['Total Stay']} nights  •  "
        f"Bill = ₹{st.session_state.user_data['Total Bill']:.2f}"
    )

# ─────────────────────────────────────────────────────────────────────────────
# 5 · SAVE BUTTON
# ─────────────────────────────────────────────────────────────────────────────

if st.button("💾 Save All Details"):
    row_df = pd.DataFrame([st.session_state.user_data])

    # Local CSV backup
    if os.path.exists(CSV_FILE):
        pd.concat([pd.read_csv(CSV_FILE), row_df], ignore_index=True) \
          .to_csv(CSV_FILE, index=False)
    else:
        row_df.to_csv(CSV_FILE, index=False)

    # Append one row to the sheet
    try:
        worksheet.append_row(
            [to_sheet(row_df.iloc[0][col]) for col in expected_cols],
            value_input_option="USER_ENTERED"
        )
        st.success("✅ Saved to Google Sheets.")
    except Exception as e:
        st.error(f"❌ Google-Sheet write failed: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# 6 · OPTIONAL PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

with st.expander("📊 View current sheet data"):
    try:
        st.dataframe(conn_reader.read())
    except Exception as e:
        st.warning(f"Could not load sheet: {e}")
