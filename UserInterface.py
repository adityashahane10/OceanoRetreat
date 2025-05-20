import streamlit as st
import pandas as pd
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import datetime
import wavio
import os

# File to store user data
csv_file = "/Users/adityahemantshahane/Desktop/codes/user_data.csv"

# Initialize session state for discount selection
if "selected_discount" not in st.session_state:
    st.session_state.selected_discount = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Function to record and transcribe speech
def record_audio(filename="output.wav", duration=5, samplerate=44100):
    st.write("🎙️ Recording... Speak now!")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    progress_bar = st.progress(0)
    for i in range(100):
        progress_bar.progress(i + 1)
        sd.sleep(int(duration * 10))
    sd.wait()
    wavio.write(filename, audio_data, samplerate, sampwidth=2)
    st.write("✅ Recording Complete!")
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"Recognized Name: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Could not understand the audio.")
        return ""
    except sr.RequestError:
        st.error("Speech recognition service is unavailable.")
        return ""

# Streamlit UI
st.title("🍽️ Welcome to Oceano Retreat")
st.subheader("Fill in your details:")

# Show Date & Time
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"📅 Date & Time: {current_datetime}")

# Load existing data
if os.path.exists(csv_file):
    existing_df = pd.read_csv(csv_file)
else:
    existing_df = pd.DataFrame(columns=["Date & Time", "Name", "Discount Applied", "Mobile Number", "Aadhar Card Number", "Age", "Nationality", "Address", "Check-in Date", "Check-out Date", "Room Number", "Room Type", "Room Rent", "Total Stay", "Total Bill"])

# Ensure necessary columns exist
for col in ["Date & Time", "Name", "Discount Applied", "Mobile Number", "Aadhar Card Number", "Age", "Nationality", "Address", "Check-in Date", "Check-out Date", "Room Number", "Room Type", "Room Rent", "Total Stay", "Total Bill"]:
    if col not in existing_df.columns:
        existing_df[col] = ""

# Special Offers (Discount Selection First)
st.subheader("🎉 Special Offers")
discount_options = ["5% Discount", "10% Discount", "15% Discount", "Free Drink", "Free Dessert", "VIP Lounge Access"]
st.session_state.selected_discount = st.radio("Select your reward:", discount_options, index=discount_options.index(st.session_state.selected_discount) if st.session_state.selected_discount in discount_options else 0)
st.write(f"✅ Selected Discount: **{st.session_state.selected_discount}**")
st.session_state.user_data["Discount Applied"] = st.session_state.selected_discount
if st.button("Save Special Offer"):
    st.success("Special offer saved!")

# User details form
st.session_state.user_data["Date & Time"] = current_datetime

with st.expander("👤 Personal Details"):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.session_state.user_data["Name"] = st.text_input("Enter Name", value=st.session_state.user_data.get("Name", ""))
    with col2:
        if st.button("🎤 Speak Name"):
            st.session_state.user_data["Name"] = record_audio()
    
    fields = ["Mobile Number", "Aadhar Card Number", "Age", "Nationality", "Address"]
    for field in fields:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.session_state.user_data[field] = st.text_input(field, value=st.session_state.user_data.get(field, ""))
        with col2:
            if st.button(f"🎤 Speak {field}"):
                st.session_state.user_data[field] = record_audio()
    if st.button("Save Personal Details"):
        st.success("Personal details saved!")

with st.expander("🏨 Stay Details"):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.user_data["Check-in Date"] = st.date_input("Check-in Date", value=st.session_state.user_data.get("Check-in Date", datetime.date.today()))
        st.session_state.user_data["Room Number"] = st.text_input("Room Number", value=st.session_state.user_data.get("Room Number", ""))
    with col2:
        st.session_state.user_data["Check-out Date"] = st.date_input("Check-out Date", value=st.session_state.user_data.get("Check-out Date", datetime.date.today()))
        st.session_state.user_data["Room Type"] = st.selectbox("Room Type", ["Single", "Double", "Suite"], index=["Single", "Double", "Suite"].index(st.session_state.user_data.get("Room Type", "Single")))
    
    st.session_state.user_data["Room Rent"] = st.number_input("Room Rent (per night)", min_value=0.0, step=0.1, value=st.session_state.user_data.get("Room Rent", 0.0))
    st.session_state.user_data["Total Stay"] = (st.session_state.user_data["Check-out Date"] - st.session_state.user_data["Check-in Date"]).days
    discount_factor = {"5% Discount": 0.95, "10% Discount": 0.90, "15% Discount": 0.85}.get(st.session_state.selected_discount, 1.0)
    st.session_state.user_data["Total Bill"] = st.session_state.user_data["Total Stay"] * st.session_state.user_data["Room Rent"] * discount_factor
    
    st.write(f"📌 Total Stay Duration: {st.session_state.user_data['Total Stay']} nights")
    st.write(f"💰 Final Bill after Discount: ₹{st.session_state.user_data['Total Bill']}")
    if st.button("Save Stay Details"):
        st.success("Stay details saved!")

# Save to CSV
if st.button("Save All Details"):
    df = pd.DataFrame([st.session_state.user_data])
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
    df = pd.concat([existing_df, df], ignore_index=True)
    df.to_csv(csv_file, index=False)
    st.success(f"✅ Details saved successfully! {st.session_state.user_data['Discount Applied']} applied.")

st.write("📂 Your details will be securely stored in `user_data.csv`.")