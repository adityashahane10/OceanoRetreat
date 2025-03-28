import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# File to store user data
csv_file = "user_data.csv"
csv_path = Path(csv_file)

# Initialize session state
if "selected_discount" not in st.session_state:
    st.session_state.selected_discount = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Function to get IST time
def get_ist_time():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

# Streamlit UI
st.title("🍽️ Welcome to Oceano Retreat")
st.subheader("Fill in your details:")

# Show Date & Time
current_datetime = get_ist_time()
st.write(f"📅 Date & Time: {current_datetime}")

# Load existing data
existing_df = pd.read_csv(csv_path) if csv_path.exists() else pd.DataFrame(columns=[
    "Date & Time", "Name", "Discount Applied", "Mobile Number", "Aadhar Card Number",
    "Age", "Nationality", "Address", "Check-in Date", "Check-out Date",
    "Room Number", "Room Type", "Room Rent", "Total Stay", "Total Bill"
])

# Special Offers
st.subheader("🎉 Special Offers")
discount_options = ["5% Discount", "10% Discount", "15% Discount", "Free Drink", "Free Dessert", "VIP Lounge Access"]
st.session_state.selected_discount = st.radio(
    "Select your reward:", discount_options,
    index=discount_options.index(st.session_state.selected_discount) if st.session_state.selected_discount in discount_options else 0
)
st.write(f"✅ Selected Discount: **{st.session_state.selected_discount}**")
st.session_state.user_data["Discount Applied"] = st.session_state.selected_discount

if st.button("Save Special Offer"):
    st.success("Special offer saved!")

# User details form
st.session_state.user_data["Date & Time"] = current_datetime

with st.expander("👤 Personal Details"):
    for field in ["Name", "Mobile Number", "Aadhar Card Number", "Age", "Nationality", "Address"]:
        st.session_state.user_data[field] = st.text_input(field, value=st.session_state.user_data.get(field, ""))
    
    if st.button("Save Personal Details"):
        st.success("Personal details saved!")

with st.expander("🏨 Stay Details"):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user_data["Check-in Date"] = st.date_input("Check-in Date", value=st.session_state.user_data.get("Check-in Date", datetime.today()))
        st.session_state.user_data["Room Number"] = st.text_input("Room Number", value=st.session_state.user_data.get("Room Number", ""))
    with col2:
        st.session_state.user_data["Check-out Date"] = st.date_input("Check-out Date", value=st.session_state.user_data.get("Check-out Date", datetime.today()))
        st.session_state.user_data["Room Type"] = st.selectbox("Room Type", ["Single", "Double", "Suite"], index=["Single", "Double", "Suite"].index(st.session_state.user_data.get("Room Type", "Single")))

    st.session_state.user_data["Room Rent"] = st.number_input("Room Rent (per night)", min_value=0.0, step=0.1, value=st.session_state.user_data.get("Room Rent", 0.0))
    st.session_state.user_data["Total Stay"] = (st.session_state.user_data["Check-out Date"] - st.session_state.user_data["Check-in Date"]).days
    discount_factor = {"5% Discount": 0.95, "10% Discount": 0.90, "15% Discount": 0.85}.get(st.session_state.selected_discount, 1.0)
    st.session_state.user_data["Total Bill"] = st.session_state.user_data["Total Stay"] * st.session_state.user_data["Room Rent"] * discount_factor

    st.write(f"📌 Total Stay Duration: {st.session_state.user_data['Total Stay']} nights")
    st.write(f"💰 Final Bill: ₹{st.session_state.user_data['Total Bill']:.2f}")

    if st.button("Save Stay Details"):
        st.success("Stay details saved!")

# Save to CSV
if st.button("Save All Details"):
    df = pd.DataFrame([st.session_state.user_data])
    df.to_csv(csv_path, mode='a', header=not csv_path.exists(), index=False)
    st.success(f"✅ Details saved successfully!")

st.write("📂 Your details are securely stored in `user_data.csv`.")
