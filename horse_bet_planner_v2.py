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

    # 1. เลือกม้าจน prob รวม ≥ 60%
    selected = []
    total_prob = 0.0
    for _, row in df.iterrows():
        if total_prob >= 0.6:
            break
        selected.append(row)
        total_prob += row["approx_prob"]

    if total_prob < 0.6:
        st.warning("⚠️ รวมความน่าจะเป็นยังไม่ถึง 60%")
    else:
        invest_df = pd.DataFrame(selected)

        # 2. คำนวณจำนวนตั๋วเพื่อให้ถูกตัวไหนก็ได้เงินคืน ≈ งบ
        invest_df["tickets"] = np.floor(budget / (invest_df["odds"] * invest_df["price"]))
        invest_df["used"] = invest_df["tickets"] * invest_df["price"]
        invest_df["revenue_if_win"] = invest_df["tickets"] * invest_df["price"] * invest_df["odds"]
        used = invest_df["used"].sum()
        remain = budget - used

        st.markdown("## ✅ แผนกระจายแบบคืนทุนทุกตัวที่แทง")
        st.dataframe(invest_df[["number", "name", "odds", "price", "approx_prob", "tickets", "used", "revenue_if_win"]])
        st.success(f"💸 ใช้ไปแล้ว {used:.2f} บาท / คงเหลือ {remain:.2f} บาท")

        # ตรวจผล
        winner = invest_df[invest_df["number"] == winning_number]
        if not winner.empty:
            gain = float(winner["tickets"]) * float(winner["price"]) * float(winner["odds"])
            st.success(f"🏆 แทงถูกม้าเบอร์ {winning_number}! ได้รับเงิน {gain:.2f} บาท")
        else:
            gain = 0
            st.error("😢 ไม่ได้แทงม้าที่ชนะ")

        profit = gain - used
        if profit >= 0:
            st.success(f"💰 กำไรสุทธิ: {profit:.2f} บาท")
        else:
            st.warning(f"📉 ขาดทุนสุทธิ: {-profit:.2f} บาท")

        if used > 0:
            loss_pct = max(0, -profit / used * 100)
            if loss_pct <= 20:
                st.info(f"✅ ขาดทุนสูงสุดไม่เกิน 20% ({loss_pct:.2f}%)")
            else:
                st.warning(f"⚠️ ขาดทุนสูงสุดอาจเกิน 20% ({loss_pct:.2f}%)")
