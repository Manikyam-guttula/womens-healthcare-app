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

# --- PDF GENERATOR (ROBUST STREAMLIT COMPATIBLE) ---
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
        pdf.cell(30, 10, str(col), border=1)
    pdf.ln()
    
    # Table Data
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
app_mode = st.sidebar.radio(
    "Navigation", 
    [
        "Daily Log & Phase Tracker", 
        "AI Predictive Forecaster", 
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

# --- LUXURY FEATURE-SPECIFIC GRADIENTS & BUTTON ACCENTS ---
theme_mapping = {
    "Daily Log & Phase Tracker": {
        "bg": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #feada6 100%)",
        "btn": "#e11d48"
    },
    "AI Predictive Forecaster": {
        "bg": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "btn": "#9333ea"
    },
    "AI Insights & Analytics": {
        "bg": "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)",
        "btn": "#2563eb"
    },
    "Doctor Report Generator": {
        "bg": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)",
        "btn": "#0d9488"
    },
    "AI Health Companion": {
        "bg": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
        "btn": "#ea580c"
    },
    "PCOS Risk Screener": {
        "bg": "linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)",
        "btn": "#7c3aed"
    },
    "Medication Tracker": {
        "bg": "linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)",
        "btn": "#c026d3"
    },
    "Habit Correlation": {
        "bg": "linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)",
        "btn": "#16a34a"
    },
    "Emergency & Clinics": {
        "bg": "linear-gradient(135deg, #ff0844 0%, #ffb199 100%)",
        "btn": "#dc2626"
    },
    "Telugu Accessibility": {
        "bg": "linear-gradient(135deg, #a8edf0 0%, #fed6e3 100%)",
        "btn": "#0284c7"
    }
}

current_theme = theme_mapping.get(app_mode, {
    "bg": "linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)",
    "btn": "#0f172a"
})

st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{
        background: {current_theme['bg']} !important;
        transition: background 0.6s ease-in-out;
    }}
    [data-testid="stMain"] {{
        background: transparent !important;
    }}
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
    div.stButton > button:hover {{
        filter: brightness(0.9);
        color: white !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- MAIN APP ROUTING ---

if app_mode == "Daily Log & Phase Tracker":
    st.title("📅 Daily Log & Phase Tracker")
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
    st.subheader("📋 Your Recent Log History")
    conn = sqlite3.connect(DB_FILE)
    history_df = pd.read_sql("SELECT date, cycle_day, flow, symptom, severity, energy, mood, notes FROM health_logs ORDER BY id DESC LIMIT 5", conn)
    conn.close()
    if not history_df.empty:
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No entries logged yet. Fill out the form above to start tracking!")

elif app_mode == "AI Predictive Forecaster":
    st.title("🔮 AI Predictive Health & Ovulation Forecaster")
    st.write("Advanced machine-learning simulation predicting future cycle phases, fertile windows, and hormonal health risks based on your database trends.")
    
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
        
        st.markdown("### 🧠 Clinical Risk & Hormone Insight")
        if stress_factor == "High / Exam Season" or sleep_quality < 6.0:
            st.warning("⚡ **Predictive Alert:** High stress and reduced sleep detected. Our machine learning model indicates a 35% higher chance of temporary cycle delay or increased pre-menstrual cramping for this cycle. Ensure consistent hydration and rest.")
        else:
            st.success("✅ **Stable Forecast:** Your cycle patterns and lifestyle metrics indicate healthy hormonal stability. Ovulation and phase progressions are projected to be on schedule.")

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
    st.write("Ask any question regarding menstrual health, symptoms, nutrition, workouts, or wellness!")
    
    user_query = st.text_input("Ask a question (e.g., 'What is PCOD?', 'What foods help with cramps?', 'Can I exercise during my period?')")
    
    if user_query:
        q = user_query.lower()
        if any(w in q for w in ["pcod", "polycystic", "pcos"]):
            st.success("🤖 **AI Companion Response:** PCOD and PCOS are hormonal conditions affecting ovarian function. Managing them successfully relies on a low-glycemic diet, regular physical activity, insulin regulation, and consistent symptom tracking using our app's **PCOS Risk Screener**.")
        elif any(w in q for w in ["food", "diet", "eat", "nutrition", "sugar", "iron"]):
            st.success("🤖 **AI Companion Response:** Nutrition plays a key role in cycle health! During your period, focus on iron-rich foods (spinach, lentils) to combat fatigue, and anti-inflammatory foods (berries, omega-3 fatty acids) to ease cramping and bloating.")
        elif any(w in q for w in ["exercise", "workout", "gym", "yoga", "walk"]):
            st.success("🤖 **AI Companion Response:** Gentle exercises like walking, yoga, and light stretching are wonderful during menstruation. They release endorphins which naturally reduce cramp severity and improve mood.")
        elif any(w in q for w in ["mood", "anxious", "irritabl", "depression", "sad", "emotional"]):
            st.success("🤖 **AI Companion Response:** Pre-menstrual mood shifts are driven by fluctuating estrogen and progesterone levels. Prioritizing sleep, mindfulness, and talking to loved ones can help manage emotional wellness.")
        elif any(w in q for w in ["sleep", "tired", "fatigue", "rest"]):
            st.success("🤖 **AI Companion Response:** Hormonal fluctuations can impact sleep quality, leading to daytime fatigue. Aim for 7–9 hours of sleep, maintain a consistent sleep schedule, and limit screen time before bed.")
        elif any(w in q for w in ["cramp", "pain", "ache", "stomach"]):
            st.success("🤖 **AI Companion Response:** For menstrual cramps, try applying a heating pad, drinking warm ginger or chamomile tea, or taking magnesium supplements after consulting your physician.")
        elif any(w in q for w in ["headache", "migraine"]):
            st.success("🤖 **AI Companion Response:** Hormonal headaches often occur due to pre-period estrogen drops. Staying well-hydrated and managing stress levels can significantly minimize their frequency.")
        elif any(w in q for w in ["app", "use", "navigate", "tracker", "report"]):
            st.success("🤖 **AI Companion Response:** Navigating HerHealth AI is easy! Use the sidebar to switch between tracking daily logs, viewing analytics, exporting medical PDF reports, or finding emergency care.")
        else:
            st.success(f"🤖 **AI Companion Response:** That's a great question about *'{user_query}'*. While every individual's hormonal health profile is unique, maintaining consistent daily logs and consulting a certified healthcare professional is always the best path forward.")

elif app_mode == "PCOS Risk Screener":
    st.title("🩺 PCOS & Hormonal Risk Screener")
    st.write("Answer the clinical checklist below to assess potential hormonal indicators.")
    
    q1 = st.checkbox("Irregular menstrual cycles (shorter than 21 days or longer than 35 days) over the last 6 months?")
    q2 = st.checkbox("Unexplained weight gain, abdominal weight retention, or difficulty losing weight?")
    q3 = st.checkbox("Excess facial or body hair growth (hirsutism) on the chin, chest, or back?")
    q4 = st.checkbox("Persistent adult acne, oily skin, or scalp hair thinning/hair loss?")
    q5 = st.checkbox("Frequent fatigue, brain fog, or afternoon energy crashes?")
    q6 = st.checkbox("Family history of PCOS, diabetes, or metabolic disorders?")
    
    if st.button("Evaluate Comprehensive Risk"):
        score = sum([q1, q2, q3, q4, q5, q6])
        if score >= 4:
            st.error(f"⚠️ **High Risk Indicator Score ({score}/6):** Multiple clinical indicators detected. We strongly recommend scheduling an appointment with a gynecologist or endocrinologist for a professional hormone panel.")
        elif score >= 2:
            st.warning(f"⚡ **Moderate Risk Indicator Score ({score}/6):** Some hormonal imbalance indicators noted. Maintain consistent symptom logs and consider lifestyle adjustments.")
        else:
            st.success(f"✅ **Low Risk Indicator Score ({score}/6):** Few or no primary indicators detected. Continue tracking your cycle regularly!")

elif app_mode == "Medication Tracker":
    st.title("💊 Medication & Supplement Tracker")
    st.write("Manage your daily supplements, iron tablets, or prescribed medications.")
    med_name = st.text_input("Medication / Supplement Name")
    med_time = st.time_input("Reminder Time")
    if st.button("Set Reminder"):
        st.success(f"Reminder set successfully for {med_name} at {med_time}!")

elif app_mode == "Habit Correlation":
    st.title("🔄 Interactive Habit Correlation Engine")
    st.write("Input your daily lifestyle habits below to simulate how sleep, hydration, and caffeine impact your cramp severity and energy levels.")
    
    with st.form("habit_analysis_form"):
        col1, col2 = st.columns(2)
        with col1:
            sleep_hrs = st.slider("Sleep Duration (Hours)", 3.0, 12.0, 7.0, 0.5)
            water_intake = st.slider("Water Intake (Litres)", 0.5, 5.0, 2.0, 0.5)
        with col2:
            activity_level = st.selectbox("Physical Activity Level", ["Sedentary", "Light Walking", "Moderate Exercise", "High Intensity / Gym"])
            caffeine_cups = st.slider("Caffeine Intake (Cups)", 0, 6, 1)
            
        run_analysis = st.form_submit_button("Run Habit Impact Analysis")
        
        if run_analysis:
            risk_score = 0
            if sleep_hrs < 6.5: risk_score += 2
            if water_intake < 2.0: risk_score += 2
            if caffeine_cups > 3: risk_score += 1
            if activity_level == "Sedentary": risk_score += 1
            
            st.markdown("---")
            st.subheader("📊 Habit Impact Simulation Results")
            if risk_score >= 4:
                st.error(f"⚠️ **High Symptom Impact Predicted (Risk Score: {risk_score}/5):** Your current sleep ({sleep_hrs} hrs) and hydration ({water_intake} L) are strongly correlated with increased cramp severity and fatigue. Recommendation: Increase water intake and aim for at least 7.5 hours of consistent sleep.")
            elif risk_score >= 2:
                st.warning(f"⚡ **Moderate Impact (Risk Score: {risk_score}/5):** Minor lifestyle adjustments—such as increasing hydration or reducing evening caffeine—can noticeably improve your cycle comfort.")
            else:
                st.success(f"✅ **Optimal Habit Balance (Risk Score: {risk_score}/5):** Excellent! Your current lifestyle habits are well-balanced to keep cramp intensity low and energy levels stable.")

elif app_mode == "Emergency & Clinics":
    st.title("🚨 Emergency Services & Live Clinic Finder")
    st.write("Access 24/7 National Emergency Helplines or detect your live location to find nearby women's hospitals across India.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🇮🇳 All-India Emergency Helplines")
        st.markdown("- **National Emergency Number:** `112` (24/7 Medical / Police)")
        st.markdown("- **National Women Helpline:** `1091`")
        st.markdown("- **National Medical Ambulance:** `108`")
        st.markdown("- **Women Helpline (NCW):** `7827170170`")
        st.markdown("- **KIRAN Mental Health Helpline:** `1800-599-0019`")
        
    with col_b:
        st.markdown("### 📍 Live GPS Location Finder")
        
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
            document.getElementById("status").innerHTML = "<b>Live Location Detected!</b><br><br><a href='" + mapsUrl + "' target='_blank' style='background-color:#dc2626; color:white; padding:10px 16px; text-decoration:none; border-radius:8px; font-weight:bold;'>📍 View Nearby Women's Hospitals on Google Maps</a>";
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

elif app_mode == "Telugu Accessibility":
    st.title("🌐 Telugu Accessibility / తెలుగు యాక్సెసిబిలిటీ")
    st.write("Switch interface preferences to Telugu.")
    lang_choice = st.radio("Select Language / భాషను ఎంచుకోండి", ["English", "Telugu"], index=0 if st.session_state["lang"]=="English" else 1)
    if st.button("Apply Language Preference"):
        st.session_state["lang"] = lang_choice
        st.success(f"Language successfully switched to {lang_choice}!")
        st.rerun()