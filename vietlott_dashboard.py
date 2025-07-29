import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# --- Crawl dữ liệu ---
@st.cache_data
def crawl_vietlott_results():
    url = "https://www.vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    rows = soup.select(".result-item")[:30]  # lấy 1 tháng (~30 kỳ)
    for row in rows:
        date = row.select_one(".result-date").text.strip()
        numbers = [int(num.text) for num in row.select(".number")]
        if len(numbers) >= 6:
            data.append([date] + numbers[:6])

    df = pd.DataFrame(data, columns=["Ngày quay", "S1", "S2", "S3", "S4", "S5", "S6"])
    return df

# --- Phân tích & dự đoán ---
def analyze_and_predict(df):
    all_numbers = df[["S1","S2","S3","S4","S5","S6"]].values.flatten()
    freq = pd.Series(all_numbers).value_counts()

    hot_numbers = freq.head(3).index.tolist()
    cold_numbers = freq.tail(3).index.tolist()

    prediction = sorted(hot_numbers + cold_numbers)[:6]
    return freq, prediction

# --- Giao diện ---
st.title("🎯 Vietlott Prediction Dashboard")
st.write("Phân tích kết quả 1 tháng qua và dự đoán kỳ quay tới")

df = crawl_vietlott_results()
freq, prediction = analyze_and_predict(df)

st.subheader("📊 Dữ liệu 1 tháng gần nhất")
st.dataframe(df)

st.subheader("🔥 Biểu đồ tần suất xuất hiện")
fig = px.bar(freq, x=freq.index, y=freq.values, labels={'x':'Số', 'y':'Số lần xuất hiện'})
st.plotly_chart(fig)

st.subheader("🎯 Dãy số dự đoán cho kỳ tới")
st.success(prediction)
