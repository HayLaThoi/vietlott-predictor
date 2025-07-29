import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- Lấy dữ liệu từ API Vietlott ---
@st.cache_data
def fetch_vietlott_results():
    url = "https://api.vietlott.vn/v1/ketqua?game=power655&limit=30"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        
        results = []
        for item in data.get("data", []):
            date = item.get("openDate")
            numbers = item.get("winningNumbers", [])
            if len(numbers) >= 6:
                results.append([date] + numbers[:6])
        
        if not results:
            raise ValueError("Không có dữ liệu trả về.")
        
        df = pd.DataFrame(results, columns=["Ngày quay", "S1", "S2", "S3", "S4", "S5", "S6"])
        return df
    except Exception as e:
        st.warning(f"⚠️ Không thể lấy dữ liệu API ({e}). Sử dụng dữ liệu mẫu.")
        sample = [
            ["2025-07-01", 5, 12, 24, 33, 45, 51],
            ["2025-07-03", 7, 14, 26, 35, 40, 48],
            ["2025-07-05", 3, 18, 21, 30, 41, 55],
        ]
        return pd.DataFrame(sample, columns=["Ngày quay", "S1", "S2", "S3", "S4", "S5", "S6"])

# --- Phân tích & dự đoán ---
def analyze_and_predict(df):
    all_numbers = df[["S1","S2","S3","S4","S5","S6"]].values.flatten()
    freq = pd.Series(all_numbers).value_counts()
    hot_numbers = freq.head(3).index.tolist()
    cold_numbers = freq.tail(3).index.tolist()
    prediction = sorted(hot_numbers + cold_numbers)[:6]
    return freq, prediction

# --- Giao diện ---
st.title("🎯 Vietlott Prediction Dashboard (API JSON)")
st.write("Phân tích kết quả Power 6/55 trong 1 tháng qua và dự đoán kỳ quay tới")

df = fetch_vietlott_results()
freq, prediction = analyze_and_predict(df)

st.subheader("📊 Dữ liệu 1 tháng gần nhất")
st.dataframe(df)

st.subheader("🔥 Biểu đồ tần suất xuất hiện")
fig = px.bar(freq, x=freq.index, y=freq.values, labels={'x':'Số', 'y':'Số lần xuất hiện'})
st.plotly_chart(fig)

st.subheader("🎯 Dãy số dự đoán cho kỳ tới")
st.success(prediction)
