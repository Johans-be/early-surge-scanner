
import streamlit as st
import plotly.graph_objs as go
from early_surge_scanner import get_data, add_indicators, check_early_surge

st.set_page_config(layout="wide")
st.title("📈 Early Surge Scanner")

ticker = st.sidebar.text_input("Enter Ticker", value="AAPL")
df = get_data(ticker)
df = add_indicators(df)
signal = check_early_surge(df)

st.subheader(f"Signal: {signal}")

fig = go.Figure(data=[
    go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Candlestick'),
    go.Scatter(
        x=df.index, y=df['VWMA'], line=dict(color='orange', width=2), name='VWMA')
])
st.plotly_chart(fig, use_container_width=True)

fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')))
fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], name='Signal', line=dict(color='red')))
fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_diff'], name='MACD Diff', marker_color='green'))
fig_macd.update_layout(title='MACD Indicator', height=300)
st.plotly_chart(fig_macd, use_container_width=True)
