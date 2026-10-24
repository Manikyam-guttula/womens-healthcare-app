import streamlit as st
import pandas as pd
from fpdf import FPDF
from database import init_db, add_log, get_logs, verify_pin, set_pin

# Initialize database
init_db()

st.set_page_config(page_title="HerHealth AI - Women's Health Platform", layout="wide")

# ---------------------------------------------------------
# FEATURE 4: Privacy Vault Lock Screen
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.sidebar.title("🔐 Security & Navigation")

pin_status = verify_pin("0000")  # Checks if any PIN is saved in the database

if not st.session_state.authenticated:
    if pin_status is None:
        # First time setup
        st.sidebar.subheader("Set Up Your Master PIN")
        new_pin = st.sidebar.text_input("Create 4-Digit PIN", type="password", key="create_pin")
        if st.sidebar.button("Set PIN & Unlock"):
            if len(new_pin) >= 4:
                set_pin(new_pin)
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.sidebar.error("PIN must be at least 4 digits.")
    else:
        # Subsequent logins
        st.sidebar.subheader("Privacy Vault Authentication")
        input_pin = st.sidebar.text_input("Enter Your 4-Digit PIN", type="password", key="login_pin")
        if st.sidebar.button("Unlock Vault"):
            if verify_pin(input_pin):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect PIN! Access Denied.")

    st.title("🔒 HerHealth Vault is Locked")
    st.info("Please set or enter your PIN in the sidebar to unlock your medical records.")
    st.stop()

# ---------------------------------------------------------
# Authenticated App Content
# ---------------------------------------------------------
st.sidebar.success("Vault Unlocked ✅")
page = st.sidebar.radio("Go to", [
    "Daily Log & Phase Tracker", 
    "AI Insights & Analytics", 
    "Doctor Report Generator",
    "AI Health Companion"
])

def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "HerHealth AI - Medical Summary Report", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Logged Symptoms Summary:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", size=10)
    for idx, row in df.iterrows():
        text = f"Date: {row['date']} | Day {row['cycle_day']} | Symptom: {row['symptom']} | Severity: {row['severity']}/10 | Mood: {row['mood']}"
        pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        if row['notes']:
            pdf.cell(0, 6, f"   Notes: {row['notes']}", new_x="LMARGIN", new_y="NEXT")
    
    return pdf.output()

# PAGE 1: Daily Log & Cycle Phase Tracker
if page == "Daily Log & Phase Tracker":
    st.title("🩺 Daily Health & Cycle Tracker")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("symptom_form"):
            cycle_day = st.number_input("Current Cycle Day (e.g., Day 1 to 28)", min_value=1, max_value=45, value=1)
            symptom = st.selectbox("Primary Symptom", [
                "Cramps/Pelvic Pain", "Irregular Bleeding", "Severe Fatigue", 
                "Mood Swings/Anxiety", "Headache/Migraine", "Bloating", "None"
            ])
            severity = st.slider("Severity Level (1-10)", 1, 10, 3)
            mood = st.selectbox("Mood", ["Happy", "Calm", "Anxious", "Stressed", "Tired", "Irritated"])
            notes = st.text_area("Notes (Triggers, sleep hours, diet, etc.)")
            
            submitted = st.form_submit_button("Save Log")
            if submitted:
                add_log(cycle_day, symptom, severity, mood, notes)
                st.success("Log saved to encrypted vault!")

    with col2:
        st.subheader("🌙 Hormonal Phase Info")
        if 1 <= cycle_day <= 5:
            st.error("**Menstrual Phase**")
            st.write("• Energy: Low\n• Focus: Rest, hydration, light stretching.")
        elif 6 <= cycle_day <= 11:
            st.info("**Follicular Phase**")
            st.write("• Energy: Rising\n• Focus: Estrogen increases; great time for high productivity.")
        elif 12 <= cycle_day <= 16:
            st.success("**Ovulatory Phase**")
            st.write("• Energy: Peak\n• Focus: High stamina, social engagement.")
        else:
            st.warning("**Luteal Phase**")
            st.write("• Energy: Decreasing\n• Focus: Progesterone rises; prioritize sleep and stress management.")

# PAGE 2: AI Insights & Analytics
elif page == "AI Insights & Analytics":
    st.title("📊 AI Health Analytics & Risk Engine")
    df = get_logs()
    
    if df.empty:
        st.warning("No logs found. Please record daily symptoms first!")
    else:
        st.subheader("Log History")
        st.dataframe(df, use_container_width=True)

        st.subheader("🤖 AI Correlation Risk Analysis")
        
        cramps = len(df[(df['symptom'] == "Cramps/Pelvic Pain") & (df['severity'] >= 6)])
        fatigue = len(df[df['symptom'] == "Severe Fatigue"])
        
        if cramps >= 2:
            st.error("⚠️ **Risk Indicator:** Multiple episodes of high-severity pelvic pain logged. Pattern correlates with clinical markers of Endometriosis or severe dysmenorrhea. Consider discussing this report with a doctor.")
        elif fatigue >= 3:
            st.warning("⚠️ **Risk Indicator:** Persistent fatigue detected. Correlates with hormonal shifts, thyroid imbalance, or iron deficiency.")
        else:
            st.success("✅ **Status:** Symptom trends remain within nominal baseline ranges.")

        st.subheader("Severity Trend Over Time")
        st.line_chart(df.set_index('date')['severity'])

# PAGE 3: Doctor Report Generator
elif page == "Doctor Report Generator":
    st.title("📄 Clinical Summary Report Exporter")
    st.write("Export an aggregated, privacy-focused medical summary report to share with your healthcare provider.")
    
    df = get_logs()
    if df.empty:
        st.warning("No logs available to generate report.")
    else:
        st.dataframe(df[['date', 'cycle_day', 'symptom', 'severity', 'mood']])
        
        pdf_bytes = generate_pdf(df)
        st.download_button(
            label="📥 Download Clinical PDF Report",
            data=bytes(pdf_bytes),
            file_name="HerHealth_Medical_Report.pdf",
            mime="application/pdf"
        )

# PAGE 4: GenAI Conversational Companion
elif page == "AI Health Companion":
    st.title("💬 HerHealth GenAI Assistant")
    st.write("Ask educational questions about symptoms, hormones, or wellness recommendations.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_query = st.chat_input("Ask a health question...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)

        bot_response = f"**Educational Insight:** Regarding '{user_query}'—symptoms often correlate with cyclic hormonal shifts. If symptoms persist or cause severe distress, please share your exported PDF report with a healthcare specialist."
        
        with st.chat_message("assistant"):
            st.write(bot_response)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})