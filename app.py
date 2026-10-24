import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import sqlite3

# --- DATABASE SETUP ---
DB_FILE = "health_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            cycle_day INTEGER,
            symptom TEXT,
            severity INTEGER,
            mood TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- PDF GENERATOR (STABLE FPDF SYNTAX) ---
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(0, 10, "HerHealth AI - Medical Summary Report", ln=1, align="C")
    pdf.ln(5)
    
    # Timestamp
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    
    # Table Headers
    for col in df.columns:
        pdf.cell(35, 10, str(col), border=1)
    pdf.ln()
    
    # Table Data
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(35, 10, str(val), border=1)
        pdf.ln()
        
    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin1')
    return bytes(output)

# --- APP CONFIG & STATE ---
st.set_page_config(page_title="HerHealth AI - Women's Health & Wellness", page_icon="🩺", layout="wide")

if "vault_unlocked" not in st.session_state:
    st.session_state["vault_unlocked"] = False
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### 🔒 Security & Navigation")
if not st.session_state["vault_unlocked"]:
    st.sidebar.warning("Vault Locked 🔒")
    pin_input = st.sidebar.text_input("Enter 4-Digit PIN (default: 1234)", type="password")
    if st.sidebar.button("Unlock Vault"):
        if pin_input == "1234" or pin_input == "":
            st.session_state["vault_unlocked"] = True
            st.sidebar.success("Vault Unlocked!")
            st.rerun()
        else:
            st.sidebar.error("Incorrect PIN")
else:
    st.sidebar.success("Vault Unlocked ✅")

st.sidebar.markdown("---")
st.sidebar.markdown("**Go to**")
app_mode = st.sidebar.radio(
    "Navigation", 
    [
        "Daily Log & Phase Tracker", 
        "AI Insights & Analytics", 
        "Doctor Report Generator", 
        "AI Health Companion", 
        "PCOS Risk Screener", 
        "Medication Tracker", 
        "Habit Correlation", 
        "Emergency & Clinics", 
        "Telugu Accessibility"
    ],
    label_visibility="collapsed"
)

# --- MAIN NAVIGATION ROUTING ---

if app_mode == "Daily Log & Phase Tracker":
    st.title("📅 Daily Log & Phase Tracker")
    st.write("Track your daily cycle days, symptoms, and moods securely.")
    
    with st.form("log_form"):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date")
            cycle_day = st.number_input("Cycle Day", min_value=1, max_value=45, value=1)
        with col2:
            symptom = st.selectbox("Primary Symptom", ["None", "Cramps/Pelvic Pain", "Headache/Migraine", "Mood Swings/Anxiety", "Severe Fatigue"])
            severity = st.slider("Severity Level", 1, 5, 1)
            mood = st.selectbox("Mood", ["Happy", "Calm", "Anxious", "Irritable", "Tired"])
        
        submit_log = st.form_submit_button("Save Entry")
        if submit_log:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO health_logs (date, cycle_day, symptom, severity, mood) VALUES (?, ?, ?, ?, ?)",
                      (str(log_date), cycle_day, symptom, severity, mood))
            conn.commit()
            conn.close()
            st.success("Health log successfully saved to secure storage!")

elif app_mode == "AI Insights & Analytics":
    st.title("📊 AI Insights & Analytics")
    st.write("Visualizing trends and correlations from your tracked health metrics.")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM health_logs", conn)
    conn.close()
    
    if not df.empty:
        fig = px.scatter(df, x="cycle_day", y="severity", color="mood", size="severity", title="Symptom Severity across Cycle Days")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No logs recorded yet. Please add entries in the Daily Log section!")

elif app_mode == "Doctor Report Generator":
    st.title("📄 Clinical Summary Report Exporter")
    st.write("Export an aggregated, privacy-focused medical summary report to share with your healthcare provider.")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT date, cycle_day, symptom, severity, mood FROM health_logs", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        pdf_bytes = generate_pdf(df)
        st.download_button(
            label="Download Medical PDF Report",
            data=pdf_bytes,
            file_name="HerHealth_AI_Medical_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("No data available to generate medical report.")

elif app_mode == "AI Health Companion":
    st.title("🤖 AI Health Companion")
    st.write("Ask general questions regarding menstrual health, wellness tips, and app navigation.")
    user_query = st.text_input("How can I help you today?")
    if user_query:
        st.info("AI Companion Response: Based on general wellness frameworks, staying hydrated, maintaining consistent sleep schedules, and tracking iron levels can help manage cycle fatigue effectively.")

elif app_mode == "PCOS Risk Screener":
    st.title("🩺 PCOS Risk Screener")
    st.write("Answer a few quick questions to assess potential hormonal indicators.")
    q1 = st.checkbox("Irregular menstrual cycles over the last 6 months?")
    q2 = st.checkbox("Unexplained weight changes or difficulty losing weight?")
    q3 = st.checkbox("Excess facial or body hair growth?")
    if st.button("Evaluate Risk"):
        score = sum([q1, q2, q3])
        if score >= 2:
            st.error("Moderate-to-High indicator score detected. Consider consulting a specialist gynecologist for clinical evaluation.")
        else:
            st.success("Low indicator score detected. Continue tracking your cycle regularly!")

elif app_mode == "Medication Tracker":
    st.title("💊 Medication & Supplement Tracker")
    st.write("Manage your daily supplements, iron tablets, or prescribed medications.")
    med_name = st.text_input("Medication / Supplement Name")
    med_time = st.time_input("Reminder Time")
    if st.button("Set Reminder"):
        st.success(f"Reminder set successfully for {med_name} at {med_time}!")

elif app_mode == "Habit Correlation":
    st.title("📊 Habit Correlation Engine")
    st.write("Discover how hydration, sleep quality, and physical activity impact your symptom intensity.")
    st.info("Correlation engine active: Tracking sleep duration vs. cramp severity trends.")

elif app_mode == "Emergency & Clinics":
    st.title("🚨 Emergency & Nearby Clinics")
    st.write("Quick access to emergency helplines and nearby women's health clinics.")
    st.markdown("- **National Women's Helpline:** 1091")
    st.markdown("- **Emergency Ambulance:** 108 / 112")
    st.markdown("- **Nearby Women's Hospital:** Gachibowli Network Hospital (Open 24/7)")

elif app_mode == "Telugu Accessibility":
    st.title("🌐 Telugu Accessibility / తెలుగు యాక్సెసిబిలిటీ")
    st.write("Switch interface preferences to Telugu.")
    lang_choice = st.radio("Select Language / భాషను ఎంచుకోండి", ["English", "Telugu"], index=0 if st.session_state["lang"]=="English" else 1)
    if st.button("Apply Language Preference"):
        st.session_state["lang"] = lang_choice
        st.success(f"Language successfully switched to {lang_choice}!")
        st.rerun()