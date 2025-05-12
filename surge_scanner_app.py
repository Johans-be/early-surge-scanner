
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import datetime
import time
import os
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Early Surge Stock Scanner", layout="wide")
st.title("📈 Early Surge Stock Scanner")

# 🔄 Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="refresh")

# 🔧 User inputs
watchlist_input = st.text_input("Enter stock symbols separated by commas", "AAPL,TSLA,AMD")
symbols = [s.strip().upper() for s in watchlist_input.split(",")]

enable_sound = st.checkbox("🔊 Enable sound alert", value=False)
enable_email = st.checkbox("📧 Enable email alert", value=False)

email_address = ""
email_password = ""
receiver_email = ""

if enable_email:
    with st.expander("🔐 Email Settings (Gmail App Passwords Recommended)"):
        email_address = st.text_input("Sender Email", type="default")
        email_password = st.text_input("App Password", type="password")
        receiver_email = st.text_input("Recipient Email", type="default")

# 📅 Time window for surge scan
now = datetime.datetime.now()
start_time = (now - datetime.timedelta(minutes=60)).strftime('%Y-%m-%d %H:%M:%S')
end_time = now.strftime('%Y-%m-%d %H:%M:%S')

# 📩 Email alert function
def send_email_alert(stock, change):
    try:
        msg = EmailMessage()
        msg.set_content(f"{stock} is surging: {change:.2f}% up")
        msg["Subject"] = f"Stock Alert: {stock} 🚀"
        msg["From"] = email_address
        msg["To"] = receiver_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
        st.success(f"📨 Email sent for {stock}!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# 🔊 Sound alert (only works locally)
def play_sound():
    try:
        if os.name == 'nt':  # Windows
            import winsound
            winsound.Beep(1000, 500)
        else:
            print('\a')  # Unix/mac
    except:
        pass

# 📈 Fetch & scan stocks
def fetch_data(ticker):
    data = yf.download(ticker, interval="1m", start=start_time, end=end_time, progress=False)
    return data

for stock in symbols:
    df = fetch_data(stock)
    if df.empty:
        st.warning(f"No data for {stock}")
        continue

    open_price = df['Open'].iloc[0]
    latest_price = df['Close'].iloc[-1]
    percent_change = ((latest_price - open_price) / open_price) * 100

    average_volume = df['Volume'].mean()
    latest_volume = df['Volume'].iloc[-1]

    col = st.container()
    col.subheader(f"📊 {stock}")
    col.line_chart(df['Close'])

    if percent_change > 1.5 and latest_volume > average_volume * 1.5:
        col.success(f"🚀 {stock} is surging! {percent_change:.2f}% up")
        col.info(f"📈 Volume spike: {latest_volume:,} vs average {int(average_volume):,}")

        if enable_sound:
            play_sound()
        if enable_email and email_address and receiver_email and email_password:
            send_email_alert(stock, percent_change)
    else:
        col.info(f"{stock} is calm. {percent_change:.2f}% change.")
