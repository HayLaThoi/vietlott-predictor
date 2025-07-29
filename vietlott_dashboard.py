import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# --- Hàm crawl dữ liệu ---
@st.cache_data
def crawl_vietlott_results():
    url = "https://www.vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    rows = soup.select("div.item.result")
    
    for row in rows[:30]:  # lấy 1 tháng (30 kỳ)
        date_tag = row.select_one("div.result__date")
        number_tags = row.select("span.result__number")
        
        if date_tag and len(number_tags) >= 6:
            date = date_tag.text.strip()
            numbers = [int(n.text) for n in number_tags[:6]]
            data.append([date] + numbers)

    if not data:
        raise ValueError("Không lấy được dữ liệu thực tế từ website Vietlott")

    return pd.DataFrame(data, columns=["Ngày quay", "S1", "S2", "S3", "S4", "S5", "S6"])

# --- Phân tích dữ liệu ---
def analyze_and_predict(df):
    all_numbers = df[["S1","S2","S3","S4","S5","S6"]].values.flatten()
    freq = pd.Series(all_numbers).value_counts()
    hot_numbers = freq.head(3).index.tolist()
    cold_numbers = freq.tail(3).index.tolist()
    prediction = sorted(hot_numbers + cold_numbers)[:6]
    return freq, prediction

# --- Giao diện Streamlit ---
st.title("🎯 Vietlott Prediction Dashboard (HTML)")
st.write("Phân tích kết quả xổ số Vietlott 6/45 trong 1 tháng và dự đoán kỳ quay tới")

try:
    df = crawl_vietlott_results()
    freq, prediction = analyze_and_predict(df)

    st.subheader("📊 Dữ liệu 1 tháng gần nhất")
    st.dataframe(df)

    st.subheader("🔥 Biểu đồ tần suất xuất hiện")
    fig = px.bar(freq, x=freq.index, y=freq.values, labels={'x':'Số', 'y':'Số lần xuất hiện'})
    st.plotly_chart(fig)

    st.subheader("🎯 Dãy số dự đoán cho kỳ tới")
    st.success(prediction)

except Exception as e:
    st.error(f"❌ Lỗi: {e}")
