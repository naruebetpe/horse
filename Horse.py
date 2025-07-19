import streamlit as st
import pandas as pd
import numpy as np

st.title("🐎 โปรแกรมวิเคราะห์ความเสี่ยงแทงม้า (Risk Calculator)")

# ส่วนกำหนดจำนวนม้า
st.header("1️⃣ กำหนดจำนวนม้าและงบลงทุน")
num_horses = st.number_input("จำนวนม้า (5-20 ตัว)", min_value=5, max_value=20, value=10)
budget = st.number_input("งบประมาณรวม (บาท)", min_value=100.0, value=1000.0, step=50.0)

# กรอกข้อมูลม้าแต่ละตัว
st.header("2️⃣ กรอกข้อมูลม้าแต่ละตัว")
data = []
for i in range(num_horses):
    st.subheader(f"🐴 ม้า {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        odds = st.number_input(f"ราคาต่อรอง (odds) ม้า {i+1}", min_value=1.1, value=10.0, step=0.1, key=f"odds_{i}")
    with col2:
        ticket_price = st.number_input(f"ราคาตั๋ว ม้า {i+1} (บาท)", min_value=10.0, value=50.0, step=5.0, key=f"price_{i}")
    with col3:
        form_score = st.slider(f"คะแนนฟอร์ม (1-10) ม้า {i+1}", min_value=1, max_value=10, value=5, key=f"form_{i}")
    data.append({"number": i+1, "odds": odds, "ticket_price": ticket_price, "form_score": form_score})

df = pd.DataFrame(data)

# ปุ่มวิเคราะห์
if st.button("🚀 วิเคราะห์ความเสี่ยงและแผนการลงทุน"):

    # คำนวณโอกาสโดยประมาณจาก 1/odds + ฟอร์ม
    df["approx_prob"] = (1 / df["odds"]) * (df["form_score"] / 5)
    df["approx_prob"] /= df["approx_prob"].sum()  # ปรับให้น้ำหนักรวมเป็น 1

    # คำนวณ expected return
    df["expected_return"] = df["approx_prob"] * df["odds"] * df["ticket_price"]

    # แนะนำแผนการลงทุน
    safe_df = df[df["approx_prob"] >= 0.03].copy()  # คัดตัวที่โอกาสไม่น้อยเกินไป
    weights = safe_df["expected_return"] / safe_df["expected_return"].sum()
    safe_df["budget_alloc"] = weights * budget
    safe_df["tickets"] = np.floor(safe_df["budget_alloc"] / safe_df["ticket_price"])
    safe_df["used_money"] = safe_df["tickets"] * safe_df["ticket_price"]
    used_total = safe_df["used_money"].sum()

    # คำนวณว่าถ้าแทงถูกจะได้เงินเท่าไหร่
    safe_df["payout"] = safe_df["tickets"] * safe_df["ticket_price"] * safe_df["odds"]

    # คำนวณโอกาสถูกอย่างน้อย 1 ตัว
    win_prob = safe_df["approx_prob"].sum()

    # แสดงผล
    st.subheader("📊 แผนการลงทุน")
    st.dataframe(safe_df[["number", "odds", "ticket_price", "approx_prob", "tickets", "used_money", "payout"]])

    st.success(f"✅ ใช้งบลงทุนไปทั้งหมด: {used_total:.2f} บาท")
    st.info(f"🎯 โอกาสถูกรวม: {win_prob*100:.2f}%")

    # วิเคราะห์ความเสี่ยง
    st.subheader("⚠️ วิเคราะห์ความเสี่ยงโดยรวม")
    if win_prob < 0.5:
        st.error("❌ ความเสี่ยงสูงมาก (โอกาสถูกน้อยกว่า 50%) — ควรหลีกเลี่ยงเล่นรอบนี้")
    elif win_prob < 0.6:
        st.warning("⚠️ ความเสี่ยงค่อนข้างสูง (โอกาสถูก 50–60%) — แทงได้ถ้ารับความเสี่ยงได้")
    else:
        st.success("✅ โอกาสถูกเกิน 60% — รอบนี้น่าเล่น (ถ้ามีทุนพอ)")

    # ประเมินผลตอบแทน
    exp_profit = (safe_df["payout"] * safe_df["approx_prob"]).sum() - used_total
    st.markdown(f"**💰 ผลตอบแทนคาดหวัง (เฉลี่ยต่อรอบ): {exp_profit:.2f} บาท**")

    if exp_profit < 0:
        st.error("📉 ระบบนี้มีโอกาสขาดทุนในระยะยาว — เล่นเพื่อฝึกหรือสนุกจะเหมาะกว่า")
    else:
        st.success("💸 ระบบนี้น่าจะมีกำไรเฉลี่ยระยะยาว — ถ้าแทงตามแผนนี้")
