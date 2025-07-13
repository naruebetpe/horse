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
        odds = st.number_input(f"📈 ราคาต่อรอง ม้า {i+1}", min_value=1.0, value=10.0, step=1.0, key=f"odds_{i}")
    with col2:
        price = st.number_input(f"🎫 ราคาตั๋ว ม้า {i+1}", min_value=1.0, value=50.0, step=1.0, key=f"price_{i}")
    with col3:
        name = st.text_input(f"🐴 ชื่อม้า {i+1}", value=f"ม้า {i+1}", key=f"name_{i}")
    data.append({"number": i+1, "name": name, "odds": odds, "price": price})

df = pd.DataFrame(data)

if st.button("🚀 วิเคราะห์และวางแผนแทง"):
    df["approx_prob"] = 1 / df["odds"]
    df = df.sort_values(by="approx_prob", ascending=False)

    selected = []
    total_prob = 0.0
    for _, row in df.iterrows():
        if total_prob >= 0.6:
            break
        selected.append(row)
        total_prob += row["approx_prob"]

    if total_prob < 0.6:
        st.error("⚠️ ไม่สามารถรวมความน่าจะเป็น ≥ 60% จากข้อมูลที่กรอกได้")
    else:
        invest_df = pd.DataFrame(selected)

        # กระจายเงินให้ถูกตัวไหนก็คุ้มทุนหรือขาดทุนน้อยที่สุด
        # สูตรเฉลี่ยตาม prob / (odds - 1)
        invest_df["weight"] = invest_df["approx_prob"] / (invest_df["odds"] - 1)
        invest_df["weight"] /= invest_df["weight"].sum()

        invest_df["money_alloc"] = invest_df["weight"] * budget
        invest_df["tickets"] = np.floor(invest_df["money_alloc"] / invest_df["price"])
        invest_df["used"] = invest_df["tickets"] * invest_df["price"]
        invest_df["revenue"] = invest_df["tickets"] * invest_df["price"] * invest_df["odds"]
        used = invest_df["used"].sum()
        remain = budget - used

        st.markdown("## ✅ แผนแทง: โอกาสรวม ≥ 60% พร้อมกระจายเพื่อคืนทุน")
        st.dataframe(invest_df[["number", "name", "odds", "price", "approx_prob", "tickets", "used", "revenue"]])
        st.success(f"💸 ใช้ไปแล้ว {used:.2f} บาท / คงเหลือ {remain:.2f} บาท")

        # วิเคราะห์ผลลัพธ์
        winner = invest_df[invest_df["number"] == winning_number]
        if not winner.empty:
            gain = float(winner["tickets"]) * float(winner["price"]) * float(winner["odds"])
            st.success(f"🏆 แทงถูกม้าเบอร์ {winning_number}! ได้เงิน {gain:.2f} บาท")
        else:
            gain = 0
            st.error("😢 ไม่ได้แทงม้าที่ชนะ")

        profit = gain - used
        if profit >= 0:
            st.success(f"💰 กำไรสุทธิ: {profit:.2f} บาท")
        else:
            st.warning(f"📉 ขาดทุนสุทธิ: {-profit:.2f} บาท")

        max_loss_pct = (used - min(invest_df["revenue"])) / budget * 100
        if max_loss_pct <= 20:
            st.info(f"✅ แผนนี้ขาดทุนสูงสุดไม่เกิน {max_loss_pct:.2f}% ตามเงื่อนไขที่ตั้งไว้")
        el

