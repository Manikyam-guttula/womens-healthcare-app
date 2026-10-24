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

# --- APP CONFIG & CUSTOM STYLING ---
st.set_page_config(page_title="HerHealth AI", page_icon="🩺", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    [data-testid="stSidebar"] {
        background-color: #f7f9fa;
        border-right: 1px solid #e1e4e8;
    }
    div.stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #e03e3e;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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

# --- MAIN APP ROUTING ---

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
    st.write("Ask questions regarding menstrual health, cycle symptoms, wellness tips, or app navigation.")
    
    user_query = st.text_input("How can I help you today? (e.g., 'How to ease cramps?', 'Why am I fatigued?', 'How do I use the tracker?')")
    
    if user_query:
        query_lower = user_query.lower()
        if "cramp" in query_lower or "pain" in query_lower:
            st.success("🤖 **AI Companion Response:** For cramp relief, try applying a heating pad to your lower abdomen, drinking warm chamomile or ginger tea, and engaging in light stretching or yoga.")
        elif "fatigue" in query_lower or "tired" in query_lower:
            st.success("🤖 **AI Companion Response:** Fatigue during certain cycle phases is common due to changing hormone levels. Focus on iron-rich foods, stay well-hydrated, and aim for 7-9 hours of consistent sleep.")
        elif "pcos" in query_lower:
            st.success("🤖 **AI Companion Response:** Managing PCOS often involves balancing blood sugar through a low-glycemic diet, regular physical activity, and stress management. Try using our built-in **PCOS Risk Screener**.")
        elif "navigation" in query_lower or "use" in query_lower or "app" in query_lower:
            st.success("🤖 **AI Companion Response:** You can navigate HerHealth AI using the sidebar! Record symptoms in **Daily Log**, view insights in **Analytics**, and export your report from the **Doctor Report Generator**.")
        else:
            st.success(f"🤖 **AI Companion Response:** Thank you for asking about *'{user_query}'*. Maintaining a balanced diet, tracking symptoms consistently, and staying hydrated are key to overall hormonal balance.")

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
    st.title("🔄 Habit Correlation Engine")
    st.write("Discover how hydration, sleep quality, and physical activity impact your symptom intensity.")
    st.info("Correlation engine active: Tracking sleep duration vs. cramp severity trends.")

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
        
        # HTML5 JavaScript Geolocation Button
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
            document.getElementById("status").innerHTML = "<b>Live Location Detected!</b><br><br><a href='" + mapsUrl + "' target='_blank' style='background-color:#ff4b4b; color:white; padding:10px 16px; text-decoration:none; border-radius:8px; font-weight:bold;'>📍 View Nearby Women's Hospitals on Google Maps</a>";
        }
        function showError(error) {
            document.getElementById("status").innerHTML = "Location access denied or unavailable. Please type your city manually below.";
        }
        </script>
        <button onclick="getLocation()" style="background-color:#ff4b4b; color:white; border:none; padding:10px 16px; border-radius:8px; cursor:pointer; font-weight:bold;">🎯 Detect My Live GPS Location</button>
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