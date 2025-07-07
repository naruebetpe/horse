import streamlit as st
import numpy as np
import pandas as pd

st.title("คำนวณแทงม้าแบบถัวเฉลี่ยน้ำหนักตามส่วนแบ่ง (Inverse Proportional Betting)")

# ใส่จำนวนม้า
num_horses = st.number_input("จำนวนม้าที่จะแทง", min_value=1, max_value=50, value=14, step=1)

# สร้าง input ช่องกรอกราคาต่อรองแต่ละม้า
st.write(f"กรอกราคาต่อรอง (ส่วนแบ่งรางวัล) ของแต่ละม้า จำนวน {num_horses} ตัว")

odds = []
for i in range(num_horses):
    val = st.number_input(f"ราคาต่อรอง ม้าหมายเลข {i+1}", min_value=0.01, value=100.0, step=1.0, format="%.2f", key=f"odds_{i}")
    odds.append(val)

budget = st.number_input("งบแทงรวม (บาท)", min_value=1, value=1000, step=100)

if st.button("คำนวณเงินแทงแต่ละม้า"):
    try:
        shares = np.array(odds)
        if any(shares <= 0):
            st.error("ราคาต่อรองต้องมากกว่า 0 ทุกตัว")
        else:
            inv = 1 / shares
            weights = inv / inv.sum()
            bets = weights * budget

            df = pd.DataFrame({
                "ม้าหมายเลข": np.arange(1, num_horses + 1),
                "ราคาต่อรอง (ส่วนแบ่งรางวัล)": shares,
                "น้ำหนักแทง (%)": (weights * 100).round(2),
                "แทง (บาท)": bets.round(2)
            })

            st.write("ผลลัพธ์การคำนวณเงินแทงแต่ละม้า")
            st.dataframe(df)

            st.success("คำนวณเสร็จแล้ว! สามารถนำเงินแทงแต่ละม้าไปใช้เดิมพันได้ตามนี้ครับ")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")


