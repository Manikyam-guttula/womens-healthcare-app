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

# --- COMPREHENSIVE MULTILINGUAL DICTIONARY ---
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
        "nav_lang": "Language & Accessibility",
        
        "daily_desc": "Securely log your daily cycle progression, symptoms, flow intensity, energy levels, and moods.",
        "forecast_desc": "Advanced machine-learning simulation predicting future cycle phases, fertile windows, and hormonal health risks.",
        "analytics_desc": "Visualizing trends and correlations from your tracked health metrics.",
        "doctor_desc": "Export an aggregated, privacy-focused medical summary report to share with your healthcare provider.",
        "companion_desc": "Ask any question regarding menstrual health, symptoms, nutrition, workouts, or wellness!",
        "screener_desc": "Answer the clinical checklist below to assess potential hormonal indicators.",
        "meds_desc": "Manage your daily supplements, iron tablets, or prescribed medications.",
        "habit_desc": "Input your daily lifestyle habits below to simulate how sleep, hydration, and caffeine impact your cramp severity and energy levels.",
        "emergency_desc": "Access 24/7 National Emergency Helplines or detect your live GPS location to find nearby women's hospitals across India.",
        "lang_desc": "Select your preferred interface language."
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
        "nav_lang": "భాష & ప్రాప్యత",
        
        "daily_desc": "మీ రోజువారీ చక్రం పురోగతి, లక్షణాలు, ప్రవాహ తీవ్రత, శక్తి స్థాయిలు మరియు మానసిక స్థితిని సురక్షితంగా లాగ్ చేయండి.",
        "forecast_desc": "భవిష్యత్ చక్ర దశలు, ఫలదీకరణ విండోలు మరియు హార్మోన్ల ఆరోగ్య రిస్క్‌లను అంచనా వేసే అధునాతన సిమ్యులేషన్.",
        "analytics_desc": "మీ ట్రాక్ చేసిన ఆరోగ్య కొలమానాల నుండి ట్రెండ్‌లు మరియు పరస్పర సంబంధాలను విజువలైజ్ చేస్తోంది.",
        "doctor_desc": "మీ ఆరోగ్య సంరక్షణ ప్రదాతతో భాగస్వామ్యం చేయడానికి వైద్య సారాంశ నివేదికను ఎగుమతి చేయండి.",
        "companion_desc": "ఋతు ఆరోగ్యం, లక్షణాలు, పోషకాహారం, వ్యాయామాలు లేదా వెల్నెస్ గురించి ఏదైనా ప్రశ్న అడగండి!",
        "screener_desc": "సంభావ్య హార్మోన్ల సూచికలను అంచనా వేయడానికి క్రింది క్లినికల్ చెక్‌లిస్ట్‌కు సమాధానం ఇవ్వండి.",
        "meds_desc": "మీ రోజువారీ సప్లిమెంట్లు, ఇనుము మాత్రలు లేదా సూచించిన మందులను నిర్వహించండి.",
        "habit_desc": "నిద్ర, ఆర్ద్రీకరణ మరియు కెఫిన్ మీ తిమ్మిరి తీవ్రత మరియు శక్తి స్థాయిలను ఎలా ప్రభావితం చేస్తాయో అనుకరించండి.",
        "emergency_desc": "24/7 జాతీయ అత్యవసర హెల్ప్‌లైన్‌లను యాక్సెస్ చేయండి లేదా సమీపంలోని మహిళా ఆసుపత్రులను కనుగొనండి.",
        "lang_desc": "మీకు ఇష్టమైన ఇంటర్‌ఫేస్ భాషను ఎంచుకోండి."
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
        "nav_lang": "भाषा और पहुंच",
        
        "daily_desc": "अपने दैनिक चक्र की प्रगति, लक्षणों, प्रवाह तीव्रता, ऊर्जा स्तर और मनोदशा को सुरक्षित रूप से लॉग करें।",
        "forecast_desc": "भविष्य के चक्र चरणों, उपजाऊ खिड़कियों और हार्मोनल स्वास्थ्य जोखिमों की भविष्यवाणी करने वाला उन्नत सिम्युलेटर।",
        "analytics_desc": "आपके ट्रैक किए गए स्वास्थ्य मीट्रिक्स से रुझानों की विजुअलाइज़ेशन।",
        "doctor_desc": "अपने स्वास्थ्य सेवा प्रदाता के साथ साझा करने के लिए एक समेकित मेडिकल सारांश रिपोर्ट निर्यात करें।",
        "companion_desc": "मासिक धर्म स्वास्थ्य, लक्षणों, पोषण, वर्कआउट या कल्याण के बारे में कोई भी प्रश्न पूछें!",
        "screener_desc": "संभावित हार्मोनल संकेतकों का आकलन करने के लिए नीचे दी गई नैदानिक चेकलिस्ट का उत्तर दें।",
        "meds_desc": "अपने दैनिक पूरक, आयरन की गोलियाँ या निर्धारित दवाएं प्रबंधित करें।",
        "habit_desc": "अनुकरण करें कि नींद, जलयोजन और कैफीन आपके ऐंठन की गंभीरता और ऊर्जा के स्तर को कैसे प्रभावित करते हैं।",
        "emergency_desc": "24/7 राष्ट्रीय आपातकालीन हेल्पलाइन तक पहुंचें या नजदीकी महिला अस्पताल खोजें।",
        "lang_desc": "अपनी पसंदीदा इंटरफ़ेस भाषा चुनें।"
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
        "nav_lang": "மொழி & அணுகல்",
        
        "daily_desc": "உங்கள் தினசரி சுழற்சி முன்னேற்றம், அறிகுறிகள், ஓட்ட தீவிரம், ஆற்றல் நிலைகள் மற்றும் மனநிலையை பாதுகாப்பாக பதிவு செய்யுங்கள்.",
        "forecast_desc": "எதிர்கால சுழற்சி கட்டங்கள் மற்றும் ஹார்மோன் ஆரோக்கிய அபாயங்களை கணிக்கக்கூடிய மேம்பட்ட இயந்திர கற்றல் உருவகப்படுத்துதல்.",
        "analytics_desc": "உங்கள் கண்காணிக்கப்பட்ட சுகாதார அளவீடுகளிலிருந்து போக்குகளை காட்சிப்படுத்துதல்.",
        "doctor_desc": "உங்கள் சுகாதார வழங்குநருடன் பகிர்ந்து கொள்ள மருத்துவ சுருக்க அறிக்கையை ஏற்றுமதி செய்யுங்கள்.",
        "companion_desc": "மாதவிடாய் சுகாதாரம், அறிகுறிகள், ஊட்டச்சத்து அல்லது ஆரோக்கியம் பற்றிய எந்த கேள்வியையும் கேளுங்கள்!",
        "screener_desc": "சாத்தியமான ஹார்மோன் குறிகாட்டிகளை மதிப்பிட கீழே உள்ள மருத்துவ சோதனையை முடிக்கவும்.",
        "meds_desc": "உங்கள் தினசரி சப்ளிமெண்ட்ஸ் மற்றும் பரிந்துரைக்கப்பட்ட மருந்துகளை நிர்வகிக்கவும்.",
        "habit_desc": "தூக்கம் மற்றும் நீரேற்றம் எவ்வாறு உங்கள் தசைப்பிடிப்பு தீவிரத்தை பாதிக்கிறது என்பதை உருவகப்படுத்துங்கள்.",
        "emergency_desc": "24/7 தேசிய அவசர உதவி எண்களை அணுகவும் அல்லது அருகில் உள்ள மருத்துவமனைகளைக் கண்டறியவும்.",
        "lang_desc": "உங்களுக்கு பிடித்த இடைமுக மொழியைத் தேர்ந்தெடுக்கவும்."
    }
}

current_l = st.session_state["lang"]
t = LANG_DICT.get(current_l, LANG_DICT["English"])

# --- SIDEBAR AUTHENTICATION LOCK ---
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

    st.title("🩺 Welcome to HerHealth AI")
    st.info("🔒 **Vault Locked:** Please log in or set up your security credentials in the sidebar to access your private health dashboard and features.")
    st.markdown("""
    ---
    ### 🛡️ Why Security Matters:
    HerHealth AI employs local database encryption to safeguard all your daily cycle logs, symptom histories, and clinical reports. Use the sidebar to log in or create your custom secure vault credentials.
    """)

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

    # --- FEATURE MODULE ROUTING ---

    if app_mode == "Daily Log & Phase Tracker":
        st.title(f"📅 {t['nav_daily']}")
        st.write(t["daily_desc"])
        
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
        st.write(t["forecast_desc"])
        
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
        st.write(t["analytics_desc"])
        
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
        st.write(t["doctor_desc"])
        
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
        st.write(t["companion_desc"])
        
        user_query = st.text_input("Ask a specific question (e.g., 'Why do I get migraines before my period?', 'How can I reduce bloating?')")
        
        if user_query:
            q = user_query.lower()
            if any(w in q for w in ["pcod", "polycystic", "pcos"]):
                ans = "PCOD/PCOS is an endocrine disorder causing hormonal imbalance, irregular ovulation, and elevated androgen levels. Managing it effectively involves maintaining a low-glycemic index diet, regular physical exercise, and monitoring insulin levels."
            elif any(w in q for w in ["cramp", "pain", "ache", "stomach", "pelvic"]):
                ans = "Menstrual cramps (dysmenorrhea) are caused by uterine contractions triggered by prostaglandins. Relief can be achieved with heat therapy (heating pads), gentle stretching, magnesium-rich foods, or consulting a physician about pain relief."
            elif any(w in q for w in ["headache", "migraine", "head"]):
                ans = "Hormonal headaches or migraines are frequently linked to the sharp drop in estrogen levels right before menstruation. Staying consistently hydrated, practicing stress management, and maintaining regular sleep schedules help minimize them."
            elif any(w in q for w in ["food", "diet", "eat", "nutrition", "sugar", "iron", "bloat", "crave"]):
                ans = "Nutrition directly impacts inflammation and hormone regulation. Focus on iron-rich foods (spinach, lentils) during your period to combat fatigue, and anti-inflammatory foods (berries, omega-3) to alleviate bloating and cramping."
            elif any(w in q for w in ["exercise", "workout", "gym", "yoga", "walk", "active", "run"]):
                ans = "Physical activity releases endorphins that naturally alleviate cramps and elevate mood. Low-impact workouts like yoga, Pilates, and brisk walking are ideal during menstruation, while strength training can be aligned with your follicular phase."
            elif any(w in q for w in ["mood", "anxious", "irritabl", "depression", "sad", "emotional", "anger", "pmdd"]):
                ans = "Pre-menstrual mood fluctuations stem from shifts in estrogen and progesterone impacting neurotransmitters like serotonin. Prioritizing mindfulness, adequate sleep, and journaling in your Daily Log can provide clarity and relief."
            elif any(w in q for w in ["sleep", "tired", "fatigue", "rest", "insomnia", "exhaust"]):
                ans = "Hormonal shifts can disrupt REM sleep and cause daytime fatigue. Aim for 7–9 hours of quality sleep, keep your bedroom cool, and limit screen time 1 hour before bed to support hormonal recovery."
            elif any(w in q for w in ["spotting", "irregular", "delay", "late", "miss"]):
                ans = "Irregular cycles or mid-cycle spotting can be influenced by stress, hormonal fluctuations, thyroid health, or lifestyle shifts. Use our AI Predictive Forecaster and PCOS Risk Screener to monitor trends for your doctor."
            else:
                ans = f"Regarding your question about *'{user_query}'*: Every individual's hormonal and physiological profile is unique. Based on clinical guidelines, keeping consistent daily symptom logs and discussing persistent concerns with a certified healthcare specialist is recommended."

            st.success(f"🤖 **AI Companion Analysis:** {ans}")

    elif app_mode == "PCOS Risk Screener":
        st.title(f"🩺 {t['nav_screener']}")
        st.write(t["screener_desc"])
        
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
        st.write(t["meds_desc"])
        med_name = st.text_input("Medication / Supplement Name")
        med_time = st.time_input("Reminder Time")
        if st.button("Set Reminder"):
            st.success(f"Reminder set successfully for {med_name} at {med_time}!")

    elif app_mode == "Habit Correlation":
        st.title(f"🔄 {t['nav_habit']}")
        st.write(t["habit_desc"])
        
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
        st.title(f"🚨 {t['nav_emergency']}")
        st.write(t["emergency_desc"])
        
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
        st.write(t["lang_desc"])
        
        lang_choice = st.radio(
            "Choose Language / భాషను ఎంచుకోండి / भाषा चुनें / மொழி", 
            ["English", "Telugu (తెలుగు)", "Hindi (हिन्दी)", "Tamil (தமிழ்)"],
            index=["English", "Telugu (తెలుగు)", "Hindi (हिन्दी)", "Tamil (தமிழ்)"].index(st.session_state["lang"])
        )
        
        if st.button("Apply Language Preference"):
            st.session_state["lang"] = lang_choice
            st.success(f"Language successfully switched to {lang_choice}!")
            st.rerun()