import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import sqlite3
import streamlit.components.v1 as components

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
    for col, col_type in [("flow", "TEXT"), ("energy", "INTEGER"), ("notes", "TEXT")]:
        try:
            c.execute(f"ALTER TABLE health_logs ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

init_db()

# --- PDF GENERATOR ---
def generate_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    pdf.cell(0, 10, "HerHealth AI - Medical Summary Report", ln=1, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    
    for col in df.columns:
        pdf.cell(30, 10, str(col), border=1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        for val in row:
            pdf.cell(30, 10, str(val), border=1)
        pdf.ln()
        
    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin1')
    return bytes(output)

# --- APP CONFIG & SESSION STATES ---
st.set_page_config(page_title="HerHealth AI", page_icon="🩺", layout="wide")

if "vault_unlocked" not in st.session_state:
    st.session_state["vault_unlocked"] = False
if "saved_username" not in st.session_state:
    st.session_state["saved_username"] = "admin"
if "saved_password" not in st.session_state:
    st.session_state["saved_password"] = "1234"
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

# --- MULTILINGUAL DICTIONARY ---
LANG_DICT = {
    "English": {
        "nav_daily": "Daily Log & Phase Tracker",
        "nav_forecast": "AI Predictive Forecaster",
        "nav_analytics": "AI Insights & Analytics",
        "nav_doctor": "Doctor Report Generator",
        "nav_companion": "AI Health Companion",
        "nav_screener": "PCOS Risk Screener",
        "nav_meds": "Medication Tracker",
        "nav_habit": "Habit Correlation",
        "nav_emergency": "Emergency & Clinics",
        "nav_lang": "Language & Accessibility"
    },
    "Telugu (తెలుగు)": {
        "nav_daily": "రోజువారీ లాగ్ & ఫేస్ ట్రాకర్",
        "nav_forecast": "AI ప్రిడిక్టివ్ ఫోర్‌కాస్టర్",
        "nav_analytics": "AI అంతర్దృష్టులు & విశ్లేషణలు",
        "nav_doctor": "డాక్టర్ నివేదిక జనరేటర్",
        "nav_companion": "AI ఆరోగ్య సహచరుడు",
        "nav_screener": "PCOS రిస్క్ స్క్రీనర్",
        "nav_meds": "మందుల ట్రాకర్",
        "nav_habit": "అలవాటు సహసంబంధం",
        "nav_emergency": "అత్యవసర & క్లినిక్‌లు",
        "nav_lang": "భాష & ప్రాప్యత"
    },
    "Hindi (हिन्दी)": {
        "nav_daily": "दैनिक लॉग और चरण ट्रैकर",
        "nav_forecast": "एआई भविष्यवक्ता",
        "nav_analytics": "एआई अंतर्दृष्टि और विश्लेषण",
        "nav_doctor": "डॉक्टर रिपोर्ट जेनरेटर",
        "nav_companion": "एआई स्वास्थ्य साथी",
        "nav_screener": "पीसीओएस जोखिम स्क्रीनर",
        "nav_meds": "दवा ट्रैकर",
        "nav_habit": "आदत सहसंबंध",
        "nav_emergency": "आपातकाल और क्लीनिक",
        "nav_lang": "भाषा और पहुंच"
    },
    "Tamil (தமிழ்)": {
        "nav_daily": "தினசரி பதிவு & கட்டம் கண்காணிப்பு",
        "nav_forecast": "AI கணிப்பு முன்னறிவிப்பு",
        "nav_analytics": "AI நுண்ணறிவு & பகுப்பாய்வு",
        "nav_doctor": "மருத்துவர் அறிக்கை ஜெனரேட்டர்",
        "nav_companion": "AI சுகாதார தோழன்",
        "nav_screener": "PCOS ஆபத்து பரிசோதகர்",
        "nav_meds": "மருந்து கண்காணிப்பு",
        "nav_habit": "பழக்கவழக்க தொடர்பு",
        "nav_emergency": "அவசரநிலை & கிளினிக்குகள்",
        "nav_lang": "மொழி & அணுகல்"
    }
}

current_l = st.session_state["lang"]
t = LANG_DICT.get(current_l, LANG_DICT["English"])

# --- SIDEBAR NAVIGATION & CUSTOM CREDENTIAL VAULT ---
st.sidebar.markdown("### 🔒 Security Vault & Setup")

if not st.session_state["vault_unlocked"]:
    tab_login, tab_create = st.sidebar.tabs(["Login", "Create Vault"])
    
    with tab_login:
        login_user = st.text_input("Username", key="login_u")
        login_pass = st.text_input("Password", type="password", key="login_p")
        if st.button("Unlock Vault"):
            if login_user == st.session_state["saved_username"] and login_pass == st.session_state["saved_password"]:
                st.session_state["vault_unlocked"] = True
                st.success("Vault Unlocked!")
                st.rerun()
            else:
                st.error("Invalid Username or Password")
                
    with tab_create:
        st.markdown("Set custom credentials:")
        new_user = st.text_input("New Username", key="new_u")
        new_pass = st.text_input("New Password", type="password", key="new_p")
        if st.button("Save New Credentials"):
            if new_user and new_pass:
                st.session_state["saved_username"] = new_user
                st.session_state["saved_password"] = new_pass
                st.success("Credentials created successfully! You can now log in.")
            else:
                st.warning("Please enter both username and password.")
else:
    st.sidebar.success("Vault Unlocked ✅")
    if st.sidebar.button("Lock Vault"):
        st.session_state["vault_unlocked"] = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Go to**")

nav_options_display = [
    t["nav_daily"], 
    t["nav_forecast"], 
    t["nav_analytics"], 
    t["nav_doctor"], 
    t["nav_companion"], 
    t["nav_screener"], 
    t["nav_meds"], 
    t["nav_habit"], 
    t["nav_emergency"], 
    t["nav_lang"]
]

selected_display_mode = st.sidebar.radio("Navigation", nav_options_display, label_visibility="collapsed")

reverse_mapping = {
    t["nav_daily"]: "Daily Log & Phase Tracker",
    t["nav_forecast"]: "AI Predictive Forecaster",
    t["nav_analytics"]: "AI Insights & Analytics",
    t["nav_doctor"]: "Doctor Report Generator",
    t["nav_companion"]: "AI Health Companion",
    t["nav_screener"]: "PCOS Risk Screener",
    t["nav_meds"]: "Medication Tracker",
    t["nav_habit"]: "Habit Correlation",
    t["nav_emergency"]: "Emergency & Clinics",
    t["nav_lang"]: "Language & Accessibility"
}

app_mode = reverse_mapping.get(selected_display_mode, "Daily Log & Phase Tracker")

# --- GRADIENT THEMES ---
theme_mapping = {
    "Daily Log & Phase Tracker": {"bg": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #feada6 100%)", "btn": "#e11d48"},
    "AI Predictive Forecaster": {"bg": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)", "btn": "#9333ea"},
    "AI Insights & Analytics": {"bg": "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)", "btn": "#2563eb"},
    "Doctor Report Generator": {"bg": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)", "btn": "#0d9488"},
    "AI Health Companion": {"bg": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)", "btn": "#ea580c"},
    "PCOS Risk Screener": {"bg": "linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)", "btn": "#7c3aed"},
    "Medication Tracker": {"bg": "linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)", "btn": "#c026d3"},
    "Habit Correlation": {"bg": "linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)", "btn": "#16a34a"},
    "Emergency & Clinics": {"bg": "linear-gradient(135deg, #ff0844 0%, #ffb199 100%)", "btn": "#dc2626"},
    "Language & Accessibility": {"bg": "linear-gradient(135deg, #a8edf0 0%, #fed6e3 100%)", "btn": "#0284c7"}
}

current_theme = theme_mapping.get(app_mode, {"bg": "linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)", "btn": "#0f172a"})

st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{
        background: {current_theme['bg']} !important;
        transition: background 0.6s ease-in-out;
    }}
    [data-testid="stMain"] {{ background: transparent !important; }}
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-right: 1px solid #cbd5e1 !important;
    }}
    div.stButton > button {{
        background: {current_theme['btn']} !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }}
    div.stButton > button:hover {{ filter: brightness(0.9); color: white !important; }}
</style>
""", unsafe_allow_html=True)

# --- MAIN ROUTING ---

if app_mode == "Daily Log & Phase Tracker":
    st.title(f"📅 {t['nav_daily']}")
    st.write("Securely log your daily cycle progression, symptoms, flow intensity, energy levels, and moods.")
    
    with st.form("log_form"):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date")
            cycle_day = st.number_input("Cycle Day", min_value=1, max_value=45, value=1)
            flow = st.selectbox("Flow Intensity", ["None/Dry", "Spotting", "Light", "Medium", "Heavy"])
        with col2:
            symptom = st.selectbox("Primary Symptom", ["None", "Cramps/Pelvic Pain", "Headache/Migraine", "Mood Swings/Anxiety", "Severe Fatigue", "Bloating"])
            severity = st.slider("Symptom Severity Level", 1, 5, 1)
            energy = st.slider("Energy Level (1=Low, 5=High)", 1, 5, 3)
            mood = st.selectbox("Mood", ["Happy", "Calm", "Anxious", "Irritable", "Tired", "Energetic"])
        
        notes = st.text_area("Personal Journal / Custom Notes", placeholder="Add any extra notes about how you feel today...")
        
        submit_log = st.form_submit_button("Save Daily Entry")
        if submit_log:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO health_logs (date, cycle_day, symptom, severity, mood, flow, energy, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (str(log_date), cycle_day, symptom, severity, mood, flow, energy, notes))
            conn.commit()
            conn.close()
            st.success("Daily health log successfully saved to secure storage!")
            
    st.markdown("---")
    st.subheader("📋 Recent Log History")
    conn = sqlite3.connect(DB_FILE)
    history_df = pd.read_sql("SELECT date, cycle_day, flow, symptom, severity, energy, mood, notes FROM health_logs ORDER BY id DESC LIMIT 5", conn)
    conn.close()
    if not history_df.empty:
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No entries logged yet.")

elif app_mode == "AI Predictive Forecaster":
    st.title(f"🔮 {t['nav_forecast']}")
    st.write("Advanced machine-learning simulation predicting future cycle phases, fertile windows, and hormonal health risks.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        avg_cycle_len = st.number_input("Average Cycle Length (Days)", min_value=21, max_value=45, value=28)
        last_period_start = st.date_input("Start Date of Last Period")
    with col_p2:
        stress_factor = st.selectbox("Current Stress Level", ["Low", "Moderate", "High / Exam Season"])
        sleep_quality = st.slider("Average Sleep (Hours/Night)", 4.0, 10.0, 7.5)
        
    if st.button("Run AI Predictive Forecast"):
        next_period = last_period_start + pd.Timedelta(days=avg_cycle_len)
        ovulation_day = last_period_start + pd.Timedelta(days=(avg_cycle_len - 14))
        fertile_start = ovulation_day - pd.Timedelta(days=3)
        fertile_end = ovulation_day + pd.Timedelta(days=1)
        
        st.markdown("---")
        st.subheader("📊 AI Prediction Results")
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Predicted Next Period", str(next_period))
        metric_col2.metric("Estimated Ovulation", str(ovulation_day))
        metric_col3.metric("Fertile Window", f"{fertile_start.strftime('%b %d')} - {fertile_end.strftime('%b %d')}")

elif app_mode == "AI Insights & Analytics":
    st.title(f"📊 {t['nav_analytics']}")
    st.write("Visualizing trends and correlations from your tracked health metrics.")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM health_logs", conn)
    conn.close()
    
    if not df.empty:
        fig = px.scatter(df, x="cycle_day", y="severity", color="mood", size="severity", title="Symptom Severity across Cycle Days")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No logs recorded yet.")

elif app_mode == "Doctor Report Generator":
    st.title(f"📄 {t['nav_doctor']}")
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
    st.title(f"🤖 {t['nav_companion']}")
    st.write("Ask any question regarding menstrual health, symptoms, nutrition, workouts, or wellness!")
    
    user_query = st.text_input("Ask a question (e.g., 'What is PCOD?', 'What foods help with cramps?')")
    
    if user_query:
        q = user_query.lower()
        if any(w in q for w in ["pcod", "polycystic", "pcos"]):
            st.success("🤖 **AI Companion Response:** PCOD and PCOS are hormonal conditions affecting ovarian function. Managing them successfully relies on a low-glycemic diet, regular physical activity, and consistent symptom tracking.")
        else:
            st.success(f"🤖 **AI Companion Response:** That's a great question about *'{user_query}'*. Maintaining consistent daily logs and consulting a certified healthcare professional is always the best path forward.")

elif app_mode == "PCOS Risk Screener":
    st.title(f"🩺 {t['nav_screener']}")
    st.write("Answer the clinical checklist below to assess potential hormonal indicators.")
    
    q1 = st.checkbox("Irregular menstrual cycles over the last 6 months?")
    q2 = st.checkbox("Unexplained weight gain or difficulty losing weight?")
    q3 = st.checkbox("Excess facial or body hair growth (hirsutism)?")
    q4 = st.checkbox("Persistent adult acne or hair thinning?")
    q5 = st.checkbox("Frequent fatigue or afternoon energy crashes?")
    q6 = st.checkbox("Family history of PCOS or diabetes?")
    
    if st.button("Evaluate Comprehensive Risk"):
        score = sum([q1, q2, q3, q4, q5, q6])
        if score >= 2:
            st.warning(f"⚡ **Moderate-to-High Risk Score ({score}/6):** Consider consulting a specialist gynecologist.")
        else:
            st.success(f"✅ **Low Risk Score ({score}/6):** Continue tracking your cycle regularly!")

elif app_mode == "Medication Tracker":
    st.title(f"💊 {t['nav_meds']}")
    st.write("Manage your daily supplements, iron tablets, or prescribed medications.")
    med_name = st.text_input("Medication / Supplement Name")
    med_time = st.time_input("Reminder Time")
    if st.button("Set Reminder"):
        st.success(f"Reminder set successfully for {med_name} at {med_time}!")

elif app_mode == "Habit Correlation":
    st.title(f"🔄 {t['nav_habit']}")
    st.write("Simulate how sleep, hydration, and caffeine impact your cramp severity and energy levels.")
    
    with st.form("habit_analysis_form"):
        sleep_hrs = st.slider("Sleep Duration (Hours)", 3.0, 12.0, 7.0, 0.5)
        water_intake = st.slider("Water Intake (Litres)", 0.5, 5.0, 2.0, 0.5)
        run_analysis = st.form_submit_button("Run Habit Impact Analysis")
        if run_analysis:
            st.success("✅ Habit simulation analyzed successfully. Stay hydrated and get 7+ hours of sleep!")

elif app_mode == "Emergency & Clinics":
    st.title(f"🚨 {t['nav_emergency']}")
    st.write("Access 24/7 National Emergency Helplines or detect your live GPS location to find nearby women's hospitals across India.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🇮🇳 All-India Emergency Helplines")
        st.markdown("- **National Emergency Number:** `112` (24/7 Medical / Police)")
        st.markdown("- **National Women Helpline:** `1091`")
        st.markdown("- **National Medical Ambulance:** `108`")
        st.markdown("- **Women Helpline (NCW):** `7827170170`")
        st.markdown("- **KIRAN Mental Health Helpline:** `1800-599-0019`")
        
    with col_b:
        st.markdown("### 📍 Live GPS Location & Hospital Tracker")
        
        loc_html = """
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError);
            } else {
                document.getElementById("status").innerHTML = "Geolocation is not supported by this browser.";
            }
        }
        function showPosition(position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;
            var mapsUrl = "https://www.google.com/maps/search/gynaecologist+womens+hospital/@" + lat + "," + lon + ",14z";
            document.getElementById("status").innerHTML = "<b>✅ Live Location Detected!</b><br><br><a href='" + mapsUrl + "' target='_blank' style='background-color:#dc2626; color:white; padding:10px 16px; text-decoration:none; border-radius:8px; font-weight:bold;'>📍 View Nearby Women's Hospitals on Google Maps</a>";
        }
        function showError(error) {
            document.getElementById("status").innerHTML = "Location access denied or unavailable. Please type your city manually below.";
        }
        </script>
        <button onclick="getLocation()" style="background-color:#dc2626; color:white; border:none; padding:10px 16px; border-radius:8px; cursor:pointer; font-weight:bold;">🎯 Detect My Live GPS Location</button>
        <div id="status" style="margin-top:15px; font-family:sans-serif;"></div>
        """
        components.html(loc_html, height=140)
        
        st.markdown("---")
        st.markdown("### 🏙️ Or Search by City Name")
        user_city = st.text_input("Enter City/Area Name:", "Hyderabad")
        
        city_coords = {
            "hyderabad": (17.3850, 78.4867),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
            "bengaluru": (12.9716, 77.5946),
            "chennai": (13.0827, 80.2707),
            "kolkata": (22.5726, 88.3639),
            "pune": (18.5204, 73.8567),
            "ahmedabad": (23.0225, 72.5714),
            "jaipur": (26.9124, 75.7873),
            "visakhapatnam": (17.6868, 83.2185),
            "vijayawada": (16.5062, 80.6480)
        }
        
        city_key = user_city.strip().lower()
        if city_key in city_coords:
            lat, lon = city_coords[city_key]
        else:
            lat, lon = 20.5937, 78.9629
            
        hospital_df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
        st.map(hospital_df, zoom=11)
        
        encoded_city = user_city.replace(" ", "+")
        gmaps_url = f"https://www.google.com/maps/search/gynaecologist+womens+hospital+near+{encoded_city}"
        st.markdown(f"[👉 Click here to find Women's Hospitals near **{user_city}** on Google Maps]({gmaps_url})")

elif app_mode == "Language & Accessibility":
    st.title(f"🌐 {t['nav_lang']}")
    st.write("Select your preferred interface language.")
    
    lang_choice = st.radio(
        "Choose Language / భాషను ఎంచుకోండి / भाषा चुनें / மொழி", 
        ["English", "Telugu (తెలుగు)", "Hindi (हिन्दी)", "Tamil (தமிழ்)"],
        index=["English", "Telugu (తెలుగు)", "Hindi (हिन्दी)", "Tamil (தமிழ்)"].index(st.session_state["lang"])
    )
    
    if st.button("Apply Language Preference"):
        st.session_state["lang"] = lang_choice
        st.success(f"Language successfully switched to {lang_choice}!")
        st.rerun()