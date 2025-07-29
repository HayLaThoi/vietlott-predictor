import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# Crawl dữ liệu an toàn hơn
@st.cache_data
def crawl_vietlott_results():
    url = "https://www.vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    rows = soup.find_all("div", class_="result-item")
    
    if not rows:
        st.warning("⚠️ Không lấy được dữ liệu trực tiếp. Đang sử dụng dữ liệu mẫu.")
        # Dữ liệu mẫu để dashboard không bị lỗi
        sample = [
            ["2025-07-01", 5, 12, 24, 33, 45, 51],
            ["2025-07-03", 7, 14, 26, 35, 40, 48],
            ["2025-07-05", 3, 18, 21, 30, 41, 55],
        ]
        return pd.DataFrame(sample, columns=["Ngày quay", "S1", "S2", "S3", "S4", "S5", "S6"])

    for row in rows[:30]:  # lấy 1 tháng
        date_tag = row.find(class_="result-date")
        numbers_tag = row.find_all(class_="number")
        if date_tag and len(numbers_tag) >= 6:
            date = date_tag.text.strip()
            numbers = [int(num.text) for num in numbers_tag[:6]]
            data.append([date] + numbers)

    return pd.DataFrame(data, columns=["Ngày quay", "S1", "S2", "S3", "S4", "S5", "S6"])

def analyze_and_predict(df):
    numbers = df[["S1", "S2", "S3", "S4", "S5", "S6"]].values.flatten()
    freq = pd.Series(numbers).value_counts()
    hot_numbers = freq.head(3).index.tolist()
    cold_numbers = freq.tail(3).index.tolist()
    prediction = sorted(hot_numbers + cold_numbers)[:6]
    return freq, prediction

st.title("🎯 Vietlott Prediction Dashboard")
df = crawl_vietlott_results()
freq, prediction = analyze_and_predict(df)

st.subheader("📊 Dữ liệu 1 tháng gần nhất")
st.dataframe(df)

st.subheader("🔥 Biểu đồ tần suất xuất hiện")
fig = px.bar(freq, x=freq.index, y=freq.values, labels={'x': 'Số', 'y': 'Số lần xuất hiện'})
st.plotly_chart(fig)

st.subheader("🎯 Dãy số dự đoán cho kỳ tới")
st.success(prediction)
