import streamlit as st
import numpy as np
import pandas as pd

st.title("คำนวณแทงม้าแบบถัวเฉลี่ยน้ำหนักตามส่วนแบ่ง (Inverse Proportional Betting)")

st.write("กรอกข้อมูลส่วนแบ่งรางวัลของแต่ละม้า (คั่นด้วย , ) เช่น 29,191,7376,1147,...")

# รับข้อมูลส่วนแบ่งรางวัล
shares_input = st.text_input("ส่วนแบ่งรางวัลของแต่ละม้า", "29,191,7376,1147,10326,16,31,448,61,12908,4302,2458,164,87")

# รับงบแทงรวม
budget = st.number_input("งบแทงรวม (บาท)", min_value=1, value=1000, step=100)

if st.button("คำนวณเงินแทงแต่ละม้า"):
    try:
        # แปลง input เป็น numpy array
        shares = np.array([float(x.strip()) for x in shares_input.split(",") if x.strip() != ''])
        if len(shares) == 0:
            st.error("กรุณากรอกข้อมูลส่วนแบ่งรางวัลให้ถูกต้อง")
        else:
            # คำนวณ inverse weights
            inv = 1 / shares
            weights = inv / inv.sum()
            bets = weights * budget

            # สร้าง DataFrame แสดงผล
            df = pd.DataFrame({
                "ม้าหมายเลข": np.arange(1, len(shares) + 1),
                "ส่วนแบ่งรางวัล": shares,
                "น้ำหนักแทง (%)": weights * 100,
                "แทง (บาท)": bets.round(2)
            })

            st.write("ผลลัพธ์การคำนวณเงินแทงแต่ละม้า")
            st.dataframe(df)

            st.success("คำนวณเสร็จแล้ว! สามารถนำเงินแทงแต่ละม้าไปใช้เดิมพันได้ตามนี้ครับ")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
