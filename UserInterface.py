import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# Set custom page title and favicon
st.set_page_config(page_title="Oceano Retreat", page_icon="🏨", layout="centered")

# Google Drive Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)

# Open Google Sheet
sheet = client.open("Oceano_Retreat_Data").sheet1  # Change to your sheet name

# Initialize session state
if "selected_discount" not in st.session_state:
    st.session_state.selected_discount = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Get current IST time
current_datetime = datetime.utcnow() + timedelta(hours=5, minutes=30)
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

# Streamlit UI
st.title("🍽️ Welcome to Oceano Retreat")
st.subheader("Fill in your details:")

# Show Date & Time
st.write(f"📅 Date & Time: {formatted_datetime} (IST)")

# Load existing data
existing_data = sheet.get_all_records()
existing_df = pd.DataFrame(existing_data)

# Special Offers
st.subheader("🎉 Special Offers")
discount_options = ["5% Discount", "10% Discount", "15% Discount", "Free Drink", "Free Dessert", "VIP Lounge Access"]
st.session_state.selected_discount = st.radio("Select your reward:", discount_options)
st.write(f"✅ Selected Discount: **{st.session_state.selected_discount}**")
st.session_state.user_data["Discount Applied"] = st.session_state.selected_discount

if st.button("Save Special Offer"):
    st.success("Special offer saved!")

# User details form
st.session_state.user_data["Date & Time"] = formatted_datetime

with st.expander("👤 Personal Details"):
    for field in ["Name", "Mobile Number", "Aadhar Card Number", "Age", "Nationality", "Address"]:
        st.session_state.user_data[field] = st.text_input(field, value=st.session_state.user_data.get(field, ""))

    if st.button("Save Personal Details"):
        st.success("Personal details saved!")

with st.expander("🏨 Stay Details"):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user_data["Check-in Date"] = st.date_input("Check-in Date", value=datetime.today())
        st.session_state.user_data["Room Number"] = st.text_input("Room Number", value=st.session_state.user_data.get("Room Number", ""))
    with col2:
        st.session_state.user_data["Check-out Date"] = st.date_input("Check-out Date", value=datetime.today())
        st.session_state.user_data["Room Type"] = st.selectbox("Room Type", ["Single", "Double", "Suite"], index=0)

    st.session_state.user_data["Room Rent"] = st.number_input("Room Rent (per night)", min_value=0.0, step=0.1)
    st.session_state.user_data["Total Stay"] = (st.session_state.user_data["Check-out Date"] - st.session_state.user_data["Check-in Date"]).days
    discount_factor = {"5% Discount": 0.95, "10% Discount": 0.90, "15% Discount": 0.85}.get(st.session_state.selected_discount, 1.0)
    st.session_state.user_data["Total Bill"] = st.session_state.user_data["Total Stay"] * st.session_state.user_data["Room Rent"] * discount_factor

    st.write(f"📌 Total Stay Duration: {st.session_state.user_data['Total Stay']} nights")
    st.write(f"💰 Final Bill: ₹{st.session_state.user_data['Total Bill']:.2f}")

    if st.button("Save Stay Details"):
        st.success("Stay details saved!")

# Save to Google Sheets
if st.button("Save All Details"):
    row_data = list(st.session_state.user_data.values())
    sheet.append_row(row_data)
    st.success(f"✅ Details saved successfully to Google Drive!")
