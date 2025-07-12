import streamlit as st
import pandas as pd
import numpy as np

st.title("🐎 แอปวิเคราะห์แทงม้าอัจฉริยะ (พร้อมคำนวณกำไร/ขาดทุน)")

st.markdown("### ➤ กำหนดจำนวนม้าและงบประมาณ")
num_horses = st.number_input("จำนวนม้า", min_value=2, max_value=50, value=10)
budget = st.number_input("งบประมาณรวม (บาท)", min_value=1.0, value=500.0, step=10.0)
winning_number = st.number_input("กรอกเบอร์ม้าที่ชนะ (ถ้ามี)", min_value=1, max_value=50, value=1, step=1)

st.markdown("### ➤ กรอกข้อมูลม้าแต่ละตัว")
data = []
for i in range(num_horses):
    col1, col2, col3 = st.columns(3)
    with col1:
        odds = st.number_input(f"📈 ราคาต่อรอง ม้า {i+1}", min_value=1.0, value=50.0, step=1.0, key=f"odds_{i}")
    with col2:
        price = st.number_input(f"🎫 ราคาตั๋ว ม้า {i+1}", min_value=1.0, value=20.0, step=1.0, key=f"price_{i}")
    with col3:
        name = st.text_input(f"🐴 ชื่อม้า {i+1}", value=f"ม้า {i+1}", key=f"name_{i}")
    data.append({"number": i+1, "name": name, "odds": odds, "price": price})

df = pd.DataFrame(data)

if st.button("🚀 วิเคราะห์และวางแผนแทง"):
    df["approx_prob"] = 1 / df["odds"]
    df["approx_prob"] /= df["approx_prob"].sum()
    df["expected_return"] = df["approx_prob"] * df["odds"] * df["price"]

    invest_df = df[df["approx_prob"] >= 0.03].copy()
    other_df = df[df["approx_prob"] < 0.03].copy()

    st.markdown("## ✅ แผนลงทุนหลัก (โอกาสชนะ ≥ 3%)")
    if not invest_df.empty:
        weights = invest_df["expected_return"] / invest_df["expected_return"].sum()
        invest_df["money_alloc"] = weights * budget
        invest_df["tickets"] = np.floor(invest_df["money_alloc"] / invest_df["price"])
        invest_df["used"] = invest_df["tickets"] * invest_df["price"]
        used = invest_df["used"].sum()
        invest_df["revenue"] = invest_df["used"] * df["odds"]
        remain = budget - used

        st.dataframe(invest_df[["number", "name", "odds", "price", "approx_prob", "tickets", "used", "revenue"]])
        st.success(f"💸 ใช้ไปแล้ว {used:.2f} บาท / งบคงเหลือ: {remain:.2f} บาท")

        if not other_df.empty and remain >= other_df["price"].min():
            st.markdown("## 🎯 แทงม้าเสี่ยงดวง (งบที่เหลือ)")
            other_df = other_df.sort_values(by="expected_return", ascending=False)
            other_df["tickets"] = np.floor(remain / other_df["price"])
            other_df = other_df[other_df["tickets"] > 0]
            other_df["used"] = other_df["tickets"] * other_df["price"]
            other_df["revenue"] = other_df["used"] * df["odds"]
            st.dataframe(other_df[["number", "name", "odds", "price", "approx_prob", "tickets", "used", "revenue"]])
            st.info(f"🎁 ใช้งบสำหรับเสี่ยงดวง: {other_df['used'].sum():.2f} บาท")
            used += other_df['used'].sum()

        all_bets = pd.concat([invest_df, other_df], ignore_index=True)
        winner = all_bets[all_bets["number"] == winning_number]

        if not winner.empty:
            gain = float(winner["tickets"]) * float(winner["price"]) * float(winner["odds"])
            st.success(f"🏆 คุณแทงถูกม้าเบอร์ {winning_number}! ได้รับเงินรางวัล {gain:.2f} บาท")
        else:
            gain = 0
            st.error("😢 คุณไม่ได้แทงม้าที่ชนะ")

        profit = gain - used
        if profit >= 0:
            st.success(f"💰 กำไรสุทธิ: {profit:.2f} บาท")
        else:
            st.warning(f"📉 ขาดทุนสุทธิ: {-profit:.2f} บาท")
    else:
        st.warning("ไม่มีม้าที่เข้าเกณฑ์ลงทุนจริง (โอกาสชนะ ≥ 3%)")
