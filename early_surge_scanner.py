
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

def get_data(ticker="AAPL", interval="5m", period="1d"):
    df = yf.download(ticker, interval=interval, period=period)
    df.dropna(inplace=True)
    return df

def add_indicators(df):
    df['VWMA'] = ta.volume.VolumeWeightedAveragePrice(
        high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']
    ).volume_weighted_average_price()
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_diff'] = macd.macd_diff()
    return df

def check_early_surge(df):
    recent = df.tail(6)
    price_jump = recent['Close'].pct_change().sum()
    macd_trending = recent['MACD_diff'].iloc[-1] > 0
    if price_jump > 0.015 and macd_trending:
        return "ENTRY"
    elif price_jump < -0.01 and recent['MACD_diff'].iloc[-1] < 0:
        return "EXIT"
    return "HOLD"
