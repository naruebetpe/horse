import streamlit as st
import pandas as pd

st.title("เว็บวิเคราะห์แทงม้า (Horse Betting Analyzer)")

st.markdown("""
กรอกข้อมูลม้าต่าง ๆ เพื่อคำนวณความน่าจะเป็นที่ปรับแล้ว, EV, และ % เดิมพันด้วย Kelly Criterion
""")

# จำนวนม้าที่จะวิเคราะห์
num_horses = st.number_input("จำนวนม้าที่ต้องการวิเคราะห์", min_value=1, max_value=10, value=3, step=1)

def calc_implied_prob(odds):
    if odds <= 0:
        return 0
    return 1 / odds

def adjust_probability(base_prob, form_pct, weight, track_condition):
    prob = base_prob
    prob += (form_pct - 50) * 0.002
    if weight > 55:
        prob -= (weight - 55) * 0.01
    elif weight < 50:
        prob += (50 - weight) * 0.005
    if track_condition == "ดี":
        prob += 0.02
    elif track_condition == "แย่":
        prob -= 0.02
    prob = max(0, min(prob, 1))
    return prob

def calc_ev(prob, odds, stake=1):
    payout = odds * stake
    ev = prob * payout - (1 - prob) * stake
    return ev

def calc_kelly(prob, odds):
    b = odds - 1
    q = 1 - prob
    numerator = b * prob - q
    if numerator <= 0:
        return 0
    return numerator / b

horses = []

for i in range(num_horses):
    st.markdown(f"### ม้าตัวที่ {i+1}")
    name = st.text_input(f"ชื่อม้า {i+1}", key=f"name_{i}")
    odds = st.number_input(f"ราคาต่อรอง (Odds) ของม้า {i+1}", min_value=1.0, step=0.1, format="%.2f", key=f"odds_{i}")
    form_pct = st.slider(f"ฟอร์มย้อนหลัง (%) ของม้า {i+1}", min_value=0, max_value=100, value=50, key=f"form_{i}")
    weight = st.number_input(f"น้ำหนักที่แบก (กก.) ของม้า {i+1}", min_value=40.0, max_value=70.0, step=0.5, value=55.0, key=f"weight_{i}")
    track_condition = st.selectbox(f"สภาพสนามสำหรับม้า {i+1}", ["ดี", "กลาง", "แย่"], key=f"track_{i}")

    base_prob = calc_implied_prob(odds)
    adjusted_prob = adjust_probability(base_prob, form_pct, weight, track_condition)
    ev = calc_ev(adjusted_prob, odds)
    kelly_fraction = calc_kelly(adjusted_prob, odds)

    horses.append({
        "ชื่อม้า": name,
        "Odds": odds,
        "ฟอร์ม (%)": form_pct,
        "น้ำหนัก (กก.)": weight,
        "สภาพสนาม": track_condition,
        "ความน่าจะเป็นพื้นฐาน": round(base_prob, 4),
        "ความน่าจะเป็นปรับแล้ว": round(adjusted_prob, 4),
        "EV ต่อ 1 บาท": round(ev, 4),
        "Kelly (%)": round(kelly_fraction * 100, 2)
    })

df = pd.DataFrame(horses)
st.markdown("## ผลการวิเคราะห์ม้าแต่ละตัว")
st.dataframe(df)

st.markdown("""
### คำแนะนำ
- เลือกแทงม้าที่ EV > 0  
- Kelly (%) คือ % ของทุนที่ควรแทง (เช่น 5 หมายถึง แทง 5% ของเงินทุนทั้งหมด)  
- อย่าลงเงินเกิน Kelly เพื่อควบคุมความเสี่ยง
""")
