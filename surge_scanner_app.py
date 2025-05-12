
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import datetime
import os
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Early Surge Stock Scanner", layout="wide")
st.title("📈 Enhanced Early Surge Stock Scanner")

# 🔄 Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="refresh")

# 🔧 User inputs
watchlist_input = st.text_input("Enter stock symbols separated by commas", "ASST,AAPL,TSLA,AMD")
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

# 📩 Email alert function
def send_email_alert(stock, message):
    try:
        msg = EmailMessage()
        msg.set_content(message)
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
    try:
        data = yf.download(ticker, interval="1m", period="1d", progress=False)
        return data
    except:
        return pd.DataFrame()
    
for stock in symbols:
    df = fetch_data(stock)
    if df.empty or 'Close' not in df.columns:
        st.warning(f"{stock} skipped due to insufficient intraday data.")
    continue

# Calculate VWMA and MACD
    df['VWMA'] = calculate_vwma(df, 20)
    df['MACD'], df['Signal'] = calculate_macd(df)

# Display
    col = st.container()
    col.subheader(f"📊 {stock}")

    latest_close = df['Close'].iloc[-1]
    latest_volume = df['Volume'].iloc[-1]
    average_volume = df['Volume'].mean()
    percent_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100

    col.metric("Price", f"${latest_close:.2f}")
    col.metric("Volume", f"{int(latest_volume)}")
    col.metric("Change", f"{percent_change:.2f}%")

# Chart safely
    if 'Close' in df.columns and 'VWMA' in df.columns:
        col.line_chart(df[['Close', 'VWMA']].dropna())
    else:
        col.warning(f"⚠️ Not enough data to chart {stock}.")



    last_vwma = df['VWMA'].iloc[-1]
    last_macd = df['MACD'].iloc[-1]
    last_signal = df['Signal'].iloc[-1]

    # Trigger alerts if all strategy conditions match
    if (
        latest_price > last_vwma and
        last_macd > last_signal and
        latest_volume > average_volume * 1.5
    ):
        col.success(f"🚨 {stock} Alert: Strong surge! 📈")
        col.info(f"Price > VWMA ({latest_price:.2f} > {last_vwma:.2f})")
        col.info(f"MACD Bullish Crossover ({last_macd:.2f} > {last_signal:.2f})")
        col.info(f"Volume Surge: {latest_volume:,} vs avg {int(average_volume):,}")

        if enable_sound:
            play_sound()
        if enable_email and email_address and receiver_email and email_password:
            send_email_alert(
                stock,
                f"{stock} is surging!\nPrice: {latest_price:.2f}\nVWMA: {last_vwma:.2f}\nMACD: {last_macd:.2f}\nSignal: {last_signal:.2f}\nVolume: {latest_volume:,}"
            )
    else:
        col.info(f"{stock} status: {percent_change:.2f}% | Calm or building.")
