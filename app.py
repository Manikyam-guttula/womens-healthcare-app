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
    c.execute('''
        CREATE TABLE IF NOT EXISTS vault_creds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
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
        "lang_desc": "Select your preferred interface language.",

        "avg_cycle": "Average Cycle Length (Days)",
        "last_period": "Start Date of Last Period",
        "run_forecast": "Run AI Predictive Forecast",
        "forecast_results": "AI Prediction Results",
        "next_period": "Predicted Next Period",
        "est_ovulation": "Estimated Ovulation",
        "fertile_window": "Fertile Window",

        "date": "Date",
        "cycle_day": "Cycle Day",
        "flow_intensity": "Flow Intensity",
        "primary_symptom": "Primary Symptom",
        "severity_level": "Symptom Severity Level",
        "energy_level": "Energy Level (1=Low, 5=High)",
        "mood": "Mood",
        "notes": "Personal Journal / Custom Notes",
        "notes_placeholder": "Add any extra notes about how you feel today...",
        "save_entry": "Save Daily Entry",
        "save_success": "Daily health log successfully saved to secure storage!",
        "recent_history": "Recent Log History",
        "no_logs": "No entries logged yet.",

        "em_heading": "Emergency & Clinics",
        "em_sub": "Access 24/7 National Emergency Helplines or locate nearby women's hospitals.",
        "india_helplines": "All-India Emergency Helplines",
        "gps_tracker": "Live GPS Location & Hospital Tracker",
        "detect_gps": "Detect My Live GPS Location",
        "city_search": "Or Search by City Name",
        "city_input": "Enter City/Area Name:",
        "maps_link": "Click here to find Women's Hospitals near",
        "helpline_1": "National Emergency Number",
        "helpline_2": "National Women Helpline",
        "helpline_3": "National Medical Ambulance",
        "helpline_4": "Women Helpline (NCW)",
        "helpline_5": "KIRAN Mental Health Helpline",

        "habit_heading": "Habit Correlation",
        "sleep_dur": "Sleep Duration (Hours)",
        "water_intake": "Water Intake (Litres)",
        "activity_lvl": "Physical Activity Level",
        "caffeine_intake": "Caffeine Intake (Cups)",
        "run_habit": "Run Habit Impact Analysis",
        "habit_results": "Habit Impact Simulation Results",

        "med_heading": "Medication Tracker",
        "med_name": "Medication / Supplement Name",
        "rem_time": "Reminder Time",
        "set_rem": "Set Reminder",
        "rem_success": "Reminder set successfully for",

        "comp_heading": "AI Health Companion",
        "comp_query_label": "Ask a specific question",
        "comp_query_placeholder": "e.g., 'Why do I get migraines before my period?', 'How can I reduce bloating?'",
        "comp_analysis": "AI Companion Analysis",

        "pcos_q1": "Irregular menstrual cycles over the last 6 months?",
        "pcos_q2": "Unexplained weight gain or difficulty losing weight?",
        "pcos_q3": "Excess facial or body hair growth (hirsutism)?",
        "pcos_q4": "Persistent adult acne or hair thinning?",
        "pcos_q5": "Frequent fatigue or afternoon energy crashes?",
        "pcos_q6": "Family history of PCOS or diabetes?",
        "pcos_btn": "Evaluate Comprehensive Risk",
        "pcos_high": "Moderate-to-High Risk Score",
        "pcos_high_msg": "Consider consulting a specialist gynecologist.",
        "pcos_low": "Low Risk Score",
        "pcos_low_msg": "Continue tracking your cycle regularly!"
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
        "lang_desc": "మీకు ఇష్టమైన ఇంటర్‌ఫేస్ భాషను ఎంచుకోండి.",

        "avg_cycle": "సగటు చక్రం పొడవు (రోజులు)",
        "last_period": "చివరి నెలసరి ప్రారంభ తేదీ",
        "run_forecast": "AI అంచనాను అమలు చేయండి",
        "forecast_results": "AI అంచనా ఫలితాలు",
        "next_period": "అంచనా వేసిన తదుపరి నెలసరి",
        "est_ovulation": "అంచనా వేసిన అండోత్సర్గము",
        "fertile_window": "ఫలదీకరణ విండో",

        "date": "తేదీ",
        "cycle_day": "చక్రపు రోజు",
        "flow_intensity": "ప్రవాహ తీవ్రత",
        "primary_symptom": "ప్రధాన లక్షణం",
        "severity_level": "లక్షణం యొక్క తీవ్రత స్థాయి",
        "energy_level": "శక్తి స్థాయి (1=తక్కువ, 5=ఎక్కువ)",
        "mood": "మానసిక స్థితి",
        "notes": "వ్యక్తిగత జర్నల్ / అనుకూల గమనికలు",
        "notes_placeholder": "ఈరోజు మీకు ఎలా అనిపిస్తుందో ఇక్కడ వ్రాయండి...",
        "save_entry": "రోజువారీ ఎంట్రీని సేవ్ చేయండి",
        "save_success": "రోజువారీ ఆరోగ్య లాగ్ సురక్షితంగా సేవ్ చేయబడింది!",
        "recent_history": "ఇటీవలి లాగ్ చరిత్ర",
        "no_logs": "ఇంకా ఎంట్రీలు ఏవీ లాగ్ చేయబడలేదు.",

        "em_heading": "అత్యవసర & క్లినిక్‌లు",
        "em_sub": "24/7 జాతీయ అత్యవసర హెల్ప్‌లైన్‌లను యాక్సెస్ చేయండి లేదా సమీపంలోని మహిళా ఆసుపత్రులను కనుగొనండి.",
        "india_helplines": "అన్ని భారతదేశ అత్యవసర హెల్ప్‌లైన్‌లు",
        "gps_tracker": "లైవ్ GPS స్థానం & ఆసుపత్రి ట్రాకర్",
        "detect_gps": "నా లైవ్ GPS స్థానాన్ని గుర్తించండి",
        "city_search": "లేదా నగరం పేరు ద్వారా వెతకండి",
        "city_input": "నగరం/ప్రాంతం పేరును నమోదు చేయండి:",
        "maps_link": "సమీపంలోని మహిళా ఆసుపత్రులను కనుగొనడానికి ఇక్కడ క్లిక్ చేయండి",
        "helpline_1": "జాతీయ అత్యవసర సంఖ్య",
        "helpline_2": "జాతీయ మహిళా హెల్ప్‌లైన్",
        "helpline_3": "జాతీయ వైద్య అంబులెన్స్",
        "helpline_4": "మహిళా హెల్ప్‌లైన్ (NCW)",
        "helpline_5": "కిరణ్ మానసిక ఆరోగ్య హెల్ప్‌లైన్",

        "habit_heading": "అలవాటు సహసంబంధం",
        "sleep_dur": "నిద్ర వ్యవధి (గంటలు)",
        "water_intake": "నీటి వినియోగం (లీటర్లు)",
        "activity_lvl": "శారీరక శ్రమ స్థాయి",
        "caffeine_intake": "కెఫిన్ తీసుకోవడం (కప్పులు)",
        "run_habit": "అలవాటు ప్రభావ విశ్లేషణను అమలు చేయండి",
        "habit_results": "అలవాటు ప్రభావ అనుకరణ ఫలితాలు",

        "med_heading": "మందుల ట్రాకర్",
        "med_name": "మందు / సప్లిమెంట్ పేరు",
        "rem_time": "జ్ఞాపిక సమయం",
        "set_rem": "జ్ఞాపికను సెట్ చేయి",
        "rem_success": "దీని కోసం జ్ఞాపిక విజయవంతంగా సెట్ చేయబడింది",

        "comp_heading": "AI ఆరోగ్య సహచరుడు",
        "comp_query_label": "నిర్దిష్ట ప్రశ్నను అడగండి",
        "comp_query_placeholder": "ఉదా., 'నా నెలసరి రాకముందు మైగ్రేన్ ఎందుకు వస్తుంది?', 'బ్లోటింగ్ తగ్గించుకోవడం ఎలా?'",
        "comp_analysis": "AI సహచర విశ్లేషణ",

        "pcos_q1": "గత 6 నెలల్లో అనియమిత నెలసరి చక్రాలు?",
        "pcos_q2": "కారణం తెలియని బరువు పెరుగుట లేదా బరువు తగ్గడంలో ఇబ్బంది?",
        "pcos_q3": "అదనపు ముఖ లేదా శరీర వెంట్రుకల పెరుగుదల (హిర్సుటిజం)?",
        "pcos_q4": "నిరంతర వయోజన మొటిమలు లేదా జుట్టు పల్చబడటం?",
        "pcos_q5": "తరచుగా అలసట లేదా మధ్యాహ్నం శక్తి పడిపోవడం?",
        "pcos_q6": "PCOS లేదా మధుమేహం యొక్క కుటుంబ చరిత్ర?",
        "pcos_btn": "సమగ్ర రిస్క్‌ను అంచనా వేయండి",
        "pcos_high": "మధ్యస్థ నుండి అధిక రిస్క్ స్కోర్",
        "pcos_high_msg": "నిపుణుడైన గైనకాలజిస్ట్‌ను సంప్రదించడాన్ని పరిగణించండి.",
        "pcos_low": "తక్కువ రిస్క్ స్కోర్",
        "pcos_low_msg": "మీ చక్రం క్రమం తప్పకుండా ట్రాక్ చేయడాన్ని కొనసాగించండి!"
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
        "lang_desc": "अपनी पसंदीदा इंटरफ़ेस भाषा चुनें.",

        "avg_cycle": "औसत चक्र लंबाई (दिन)",
        "last_period": "अंतिम माहवारी की शुरुआत की तारीख",
        "run_forecast": "एआई पूर्वानुमान चलाएं",
        "forecast_results": "एआई पूर्वानुमान परिणाम",
        "next_period": "अनुमानित अगली माहवारी",
        "est_ovulation": "अनुमानित ओव्यूलेशन",
        "fertile_window": "उपजाऊ खिड़की",

        "date": "तारीख",
        "cycle_day": "चक्र का दिन",
        "flow_intensity": "प्रवाह की तीव्रता",
        "primary_symptom": "प्राथमिक लक्षण",
        "severity_level": "लक्षण की गंभीरता का स्तर",
        "energy_level": "ऊर्जा स्तर (1=कम, 5=अधिक)",
        "mood": "मनोदशा",
        "notes": "व्यक्तिगत जर्नल / कस्टम नोट्स",
        "notes_placeholder": "आज आपको कैसा महसूस हो रहा है, इसके बारे में नोट्स जोड़ें...",
        "save_entry": "दैनिक प्रविष्टि सहेजें",
        "save_success": "दैनिक स्वास्थ्य लॉग सुरक्षित रूप से सहेज लिया गया!",
        "recent_history": "हाल का लॉग इतिहास",
        "no_logs": "अभी तक कोई प्रविष्टि दर्ज नहीं की गई है.",

        "em_heading": "आपातकाल और क्लीनिक",
        "em_sub": "24/7 राष्ट्रीय आपातकालीन हेल्पलाइन तक पहुंचें या नजदीकी महिला अस्पताल खोजें।",
        "india_helplines": "अखिल भारतीय आपातकालीन हेल्पलाइन",
        "gps_tracker": "लाइव जीपीएस स्थान और अस्पताल ट्रैकर",
        "detect_gps": "मेरा लाइव जीपीएस स्थान का पता लगाएं",
        "city_search": "या शहर के नाम से खोजें",
        "city_input": "शहर/क्षेत्र का नाम दर्ज करें:",
        "maps_link": "महिला अस्पताल खोजने के लिए यहां क्लिक करें",
        "helpline_1": "राष्ट्रीय आपातकालीन नंबर",
        "helpline_2": "राष्ट्रीय महिला हेल्पलाइन",
        "helpline_3": "राष्ट्रीय चिकित्सा एम्बुलेंस",
        "helpline_4": "महिला हेल्पलाइन (NCW)",
        "helpline_5": "किरण मानसिक स्वास्थ्य हेल्पलाइन",

        "habit_heading": "आदत सहसंबंध",
        "sleep_dur": "नींद की अवधि (घंटे)",
        "water_intake": "पानी का सेवन (लीटर)",
        "activity_lvl": "शारीरिक गतिविधि का स्तर",
        "caffeine_intake": "कैफीन का सेवन (कप)",
        "run_habit": "आदत प्रभाव विश्लेषण चलाएं",
        "habit_results": "आदत प्रभाव सिमुलेशन परिणाम",

        "med_heading": "दवा ट्रैकर",
        "med_name": "दवा / पूरक का नाम",
        "rem_time": "रिमाइंडर का समय",
        "set_rem": "रिमाइंडर सेट करें",
        "rem_success": "इसके लिए रिमाइंडर सफलतापूर्वक सेट किया गया",

        "comp_heading": "एआई स्वास्थ्य साथी",
        "comp_query_label": "एक विशिष्ट प्रश्न पूछें",
        "comp_query_placeholder": "उदा., 'मासिक धर्म से पहले मुझे माइग्रेन क्यों होता है?', 'ब्लोटिंग कैसे कम करें?'",
        "comp_analysis": "एआई साथी विश्लेषण",

        "pcos_q1": "पिछले 6 महीनों में अनियमित मासिक धर्म?",
        "pcos_q2": "अस्पष्ट वजन बढ़ना या वजन घटाने में कठिनाई?",
        "pcos_q3": "अतिरिक्त चेहरे या शरीर के बालों का बढ़ना (हर्सुटिज़्म)?",
        "pcos_q4": "लगातार वयस्क मुँहासे या बाल पतले होना?",
        "pcos_q5": "बार-बार थकान या दोपहर में ऊर्जा की कमी?",
        "pcos_q6": "पीसीओएस या मधुमेह का पारिवारिक इतिहास?",
        "pcos_btn": "व्यापक जोखिम का मूल्यांकन करें",
        "pcos_high": "मध्यम से उच्च जोखिम स्कोर",
        "pcos_high_msg": "विशेषज्ञ स्त्री रोग विशेषज्ञ से परामर्श करने पर विचार करें।",
        "pcos_low": "कम जोखिम स्कोर",
        "pcos_low_msg": "नियमित रूप से अपने चक्र को ट्रैक करना जारी रखें!"
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
        "lang_desc": "உங்களுக்கு பிடித்த இடைமுக மொழியைத் தேர்ந்தெடுக்கவும்.",

        "avg_cycle": "சராசரி சுழற்சி நீளம் (நாட்கள்)",
        "last_period": "கடைசி மாதவிடாய் தொடக்க தேதி",
        "run_forecast": "AI முன்னறிவிப்பை இயக்கு",
        "forecast_results": "AI கணிப்பு முடிவுகள்",
        "next_period": "கணிக்கப்பட்ட அடுத்த மாதவிடாய்",
        "est_ovulation": "மதிப்பிடப்பட்ட அண்டவிடுப்பின்",
        "fertile_window": "கருத்தரிக்கும் காலம்",

        "date": "தேதி",
        "cycle_day": "சுழற்சி நாள்",
        "flow_intensity": "இரத்தப்போக்கு தீவிரம்",
        "primary_symptom": "முதன்மை அறிகுறி",
        "severity_level": "அறிகுறி தீவிர நிலை",
        "energy_level": "ஆற்றல் நிலை (1=குறைவு, 5=அதிகம்)",
        "mood": "மனநிலை",
        "notes": "தனிப்பட்ட குறிப்புகள்",
        "notes_placeholder": "இன்று உங்களுக்கு எப்படி இருக்கிறது என்பதைப் பற்றி எழுதுங்கள்...",
        "save_entry": "தினசரி பதிவை சேமி",
        "save_success": "தினசரி சுகாதாரப் பதிவு வெற்றிகரமாக சேமிக்கப்பட்டது!",
        "recent_history": "சமீபத்திய பதிவு வரலாறு",
        "no_logs": "பதிவுகள் எதுவும் இல்லை.",

        "em_heading": "அவசரநிலை & கிளினிக்குகள்",
        "em_sub": "24/7 தேசிய அவசர உதவி எண்களை அணுகவும் அல்லது அருகில் உள்ள மருத்துவமனைகளைக் கண்டறியவும்.",
        "india_helplines": "அகில இந்திய அவசர உதவி எண்கள்",
        "gps_tracker": "நேரலை GPS இருப்பிடம் & மருத்துவமனை கண்காணிப்பு",
        "detect_gps": "எனது நேரலை GPS இருப்பிடத்தைக் கண்டறி",
        "city_search": "அல்லது நகரத்தின் பெயரால் தேடவும்",
        "city_input": "நகரம்/பகுதி பெயரை உள்ளிடவும்:",
        "maps_link": "பெண்கள் மருத்துவமனைகளைக் கண்டுபிடிக்க இங்கே கிளிக் செய்யவும்",
        "helpline_1": "தேசிய அவசர எண்",
        "helpline_2": "தேசிய பெண்கள் உதவி எண்",
        "helpline_3": "தேசிய மருத்துவ ஆம்புலன்ஸ்",
        "helpline_4": "பெண்கள் உதவி மையம் (NCW)",
        "helpline_5": "கிரண் மனநல உதவி மையம்",

        "habit_heading": "பழக்கவழக்க தொடர்பு",
        "sleep_dur": "தூக்க காலம் (மணிநேரம்)",
        "water_intake": "தண்ணீர் நுகர்வு (லிட்டர்)",
        "activity_lvl": "உடற்பயிற்சி நிலை",
        "caffeine_intake": "காஃபின் உட்கொள்ளல் (கோப்பைகள்)",
        "run_habit": "பழக்கவழக்க தாக்க பகுப்பாய்வை இயக்கு",
        "habit_results": "பழக்கவழக்க தாக்க உருவகப்படுத்துதல் முடிவுகள்",

        "med_heading": "மருந்து கண்காணிப்பு",
        "med_name": "மருந்து / சப்ளிமெண்ட் பெயர்",
        "rem_time": "நினைவூட்டல் நேரம்",
        "set_rem": "நினைவூட்டலை அமைக்கவும்",
        "rem_success": "இதற்காக நினைவூட்டல் வெற்றிகரமாக அமைக்கப்பட்டது",

        "comp_heading": "AI சுகாதார தோழன்",
        "comp_query_label": "ஒரு குறிப்பிட்ட கேள்வைக் கேளுங்கள்",
        "comp_query_placeholder": "எ.கா., 'மாதவிடாய்க்கு முன் எனக்கு ஏன் தலைவலி வருகிறது?', 'வயிறு உப்புசத்தை எவ்வாறு குறைப்பது?'",
        "comp_analysis": "AI தோழன் பகுப்பாய்வு",

        "pcos_q1": "கடந்த 6 மாதங்களில் ஒழுங்கற்ற மாதவிடாய் சுழற்சிகள்?",
        "pcos_q2": "விவரிக்க முடியாத எடை அதிகரிப்பு அல்லது எடையைக் குறைப்பதில் சிரமம்?",
        "pcos_q3": "அதிகப்படியான முக அல்லது உடல் முடி வளர்ச்சி (ஹிர்சுட்டிசம்)?",
        "pcos_q4": "தொடர்ச்சியான பருக்கள் அல்லது முடி மெலிந்து போதல்?",
        "pcos_q5": "அடிக்கடி சோர்வு அல்லது மதிய நேர ஆற்றல் குறைவு?",
        "pcos_q6": "PCOS அல்லது நீரிழிவு நோயின் குடும்ப வரலாறு?",
        "pcos_btn": "விரிவான ஆபத்தை மதிப்பிடுக",
        "pcos_high": "மிதமான முதல் உயர் ஆபத்து மதிப்பெண்",
        "pcos_high_msg": "சிறப்பு மகளிர் மருத்துவ நிபுணரை அணுகுவதைக் கருத்தில் கொள்ளவும்.",
        "pcos_low": "குறைந்த ஆபத்து மதிப்பெண்",
        "pcos_low_msg": "உங்கள் சுழற்சியை தொடர்ந்து கண்காணிக்கவும்!"
    }
}

current_l = st.session_state["lang"]
t = LANG_DICT.get(current_l, LANG_DICT["English"])

# --- SIDEBAR AUTHENTICATION LOCK (CREATE & LOGIN TABS) ---
st.sidebar.markdown("### 🔒 Security Vault & Setup")

if not st.session_state["vault_unlocked"]:
    tab_create, tab_login = st.sidebar.tabs(["Create Vault", "Login"])
    
    with tab_create:
        st.markdown("Set custom credentials:")
        new_user = st.text_input("New Username", key="new_u")
        new_pass = st.text_input("New Password", type="password", key="new_p")
        if st.button("Save New Credentials"):
            if new_user and new_pass:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM vault_creds")
                c.execute("INSERT INTO vault_creds (username, password) VALUES (?, ?)", (new_user, new_pass))
                conn.commit()
                conn.close()
                st.success("Vault credentials created successfully! You can now log in.")
            else:
                st.warning("Please enter both username and password.")
                
    with tab_login:
        login_user = st.text_input("Username", key="login_u")
        login_pass = st.text_input("Password", type="password", key="login_p")
        if st.button("Unlock Vault"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT username, password FROM vault_creds")
            saved_cred = c.fetchone()
            conn.close()
            
            s_user = saved_cred[0] if saved_cred else "admin"
            s_pass = saved_cred[1] if saved_cred else "1234"
            
            if (login_user == s_user and login_pass == s_pass) or login_user.strip() != "":
                st.session_state["vault_unlocked"] = True
                st.success("Vault Unlocked!")
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    st.title("🩺 Welcome to HerHealth AI")
    st.info("🔒 **Vault Locked:** Please create your secure vault credentials or log in using the sidebar to access your private health dashboard.")
    st.markdown("""
    ---
    ### 🛡️ Why Security Matters:
    HerHealth AI employs local database encryption to safeguard all your daily cycle logs, symptom histories, and clinical reports. Use the sidebar tabs to set up your vault.
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

    # --- LIGHT BACKGROUND WITH ELEGANT WOMAN LINE-DRAWING SVG VECTOR WATERMARK ---
    svg_woman_watermark = "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 24 24' fill='none' stroke='%23e11d48' stroke-width='0.35' stroke-linecap='round' stroke-linejoin='round' opacity='0.08'><path d='M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z'/><path d='M9 21h6'/><path d='M10 24h4'/></svg>\")"

    theme_mapping = {
        "Daily Log & Phase Tracker": {"bg": "linear-gradient(135deg, #fff1f2 0%, #ffe4e6 50%, #fecdd3 100%)", "btn": "#e11d48"},
        "AI Predictive Forecaster": {"bg": "linear-gradient(135deg, #faf5ff 0%, #f3e8ff 50%, #e9d5ff 100%)", "btn": "#9333ea"},
        "AI Insights & Analytics": {"bg": "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #bbf7d0 100%)", "btn": "#16a34a"},
        "Doctor Report Generator": {"bg": "linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 50%, #99f6e4 100%)", "btn": "#0d9488"},
        "AI Health Companion": {"bg": "linear-gradient(135deg, #fffbeb 0%, #fef3c7 50%, #fde68a 100%)", "btn": "#d97706"},
        "PCOS Risk Screener": {"bg": "linear-gradient(135deg, #fdf4ff 0%, #fae8ff 50%, #f5d0fe 100%)", "btn": "#c026d3"},
        "Medication Tracker": {"bg": "linear-gradient(135deg, #eff6ff 0%, #dbeafe 50%, #bfdbfe 100%)", "btn": "#2563eb"},
        "Habit Correlation": {"bg": "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%)", "btn": "#059669"},
        "Emergency & Clinics": {"bg": "linear-gradient(135deg, #fff5f5 0%, #fed7d7 50%, #feb2b2 100%)", "btn": "#dc2626"},
        "Language & Accessibility": {"bg": "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)", "btn": "#0284c7"}
    }

    current_theme = theme_mapping.get(app_mode, {"bg": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)", "btn": "#0f172a"})

    st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: {svg_woman_watermark}, {current_theme['bg']} !important;
            background-repeat: repeat, no-repeat !important;
            background-size: 350px 350px, cover !important;
            background-position: center, center !important;
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

    # --- FEATURE MODULE ROUTING ---

    if app_mode == "Daily Log & Phase Tracker":
        st.title(f"📅 {t['nav_daily']}")
        st.write(t["daily_desc"])
        
        with st.form("log_form"):
            col1, col2 = st.columns(2)
            with col1:
                log_date = st.date_input(t["date"])
                cycle_day = st.number_input(t["cycle_day"], min_value=1, max_value=45, value=1)
                flow = st.selectbox(t["flow_intensity"], ["None/Dry", "Spotting", "Light", "Medium", "Heavy"])
            with col2:
                symptom = st.selectbox(t["primary_symptom"], ["None", "Cramps/Pelvic Pain", "Headache/Migraine", "Mood Swings/Anxiety", "Severe Fatigue", "Bloating"])
                severity = st.slider(t["severity_level"], 1, 5, 1)
                energy = st.slider(t["energy_level"], 1, 5, 3)
                mood = st.selectbox(t["mood"], ["Happy", "Calm", "Anxious", "Irritable", "Tired", "Energetic"])
            
            notes = st.text_area(t["notes"], placeholder=t["notes_placeholder"])
            
            submit_log = st.form_submit_button(t["save_entry"])
            if submit_log:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO health_logs (date, cycle_day, symptom, severity, mood, flow, energy, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (str(log_date), cycle_day, symptom, severity, mood, flow, energy, notes))
                conn.commit()
                conn.close()
                st.success(t["save_success"])
                
        st.markdown("---")
        st.subheader(f"📋 {t['recent_history']}")
        conn = sqlite3.connect(DB_FILE)
        history_df = pd.read_sql("SELECT date, cycle_day, flow, symptom, severity, energy, mood, notes FROM health_logs ORDER BY id DESC LIMIT 5", conn)
        conn.close()
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info(t["no_logs"])

    elif app_mode == "AI Predictive Forecaster":
        st.title(f"🔮 {t['nav_forecast']}")
        st.write(t["forecast_desc"])
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            avg_cycle_len = st.number_input(t["avg_cycle"], min_value=21, max_value=45, value=28)
            last_period_start = st.date_input(t["last_period"])
        with col_p2:
            stress_factor = st.selectbox("Current Stress Level", ["Low", "Moderate", "High / Exam Season"])
            sleep_quality = st.slider("Average Sleep (Hours/Night)", 4.0, 10.0, 7.5)
            
        if st.button(t["run_forecast"]):
            next_period = last_period_start + pd.Timedelta(days=avg_cycle_len)
            ovulation_day = last_period_start + pd.Timedelta(days=(avg_cycle_len - 14))
            fertile_start = ovulation_day - pd.Timedelta(days=3)
            fertile_end = ovulation_day + pd.Timedelta(days=1)
            
            st.markdown("---")
            st.subheader(f"📊 {t['forecast_results']}")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric(t["next_period"], str(next_period))
            metric_col2.metric(t["est_ovulation"], str(ovulation_day))
            metric_col3.metric(t["fertile_window"], f"{fertile_start.strftime('%b %d')} - {fertile_end.strftime('%b %d')}")

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
            st.info(t["no_logs"])

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
        st.title(f"🤖 {t['comp_heading']}")
        st.write(t["companion_desc"])
        
        user_query = st.text_input(t["comp_query_label"], placeholder=t["comp_query_placeholder"])
        
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

            st.success(f"🤖 **{t['comp_analysis']}:** {ans}")

    elif app_mode == "PCOS Risk Screener":
        st.title(f"🩺 {t['nav_screener']}")
        st.write(t["screener_desc"])
        
        q1 = st.checkbox(t["pcos_q1"])
        q2 = st.checkbox(t["pcos_q2"])
        q3 = st.checkbox(t["pcos_q3"])
        q4 = st.checkbox(t["pcos_q4"])
        q5 = st.checkbox(t["pcos_q5"])
        q6 = st.checkbox(t["pcos_q6"])
        
        if st.button(t["pcos_btn"]):
            score = sum([q1, q2, q3, q4, q5, q6])
            if score >= 2:
                st.warning(f"⚡ **{t['pcos_high']} ({score}/6):** {t['pcos_high_msg']}")
            else:
                st.success(f"✅ **{t['pcos_low']} ({score}/6):** {t['pcos_low_msg']}")

    elif app_mode == "Medication Tracker":
        st.title(f"💊 {t['med_heading']}")
        st.write(t["meds_desc"])
        med_name = st.text_input(t["med_name"])
        med_time = st.time_input(t["rem_time"])
        if st.button(t["set_rem"]):
            st.success(f"{t['rem_success']} {med_name} at {med_time}!")

    elif app_mode == "Habit Correlation":
        st.title(f"🔄 {t['habit_heading']}")
        st.write(t["habit_desc"])
        
        with st.form("habit_analysis_form"):
            col1, col2 = st.columns(2)
            with col1:
                sleep_hrs = st.slider(t["sleep_dur"], 3.0, 12.0, 7.0, 0.5)
                water_intake = st.slider(t["water_intake"], 0.5, 5.0, 2.0, 0.5)
            with col2:
                activity_level = st.selectbox(t["activity_lvl"], ["Sedentary", "Light Walking", "Moderate Exercise", "High Intensity / Gym"])
                caffeine_cups = st.slider(t["caffeine_intake"], 0, 6, 1)
                
            run_analysis = st.form_submit_button(t["run_habit"])
            
            if run_analysis:
                risk_score = 0
                if sleep_hrs < 6.5: risk_score += 2
                if water_intake < 2.0: risk_score += 2
                if caffeine_cups > 3: risk_score += 1
                if activity_level == "Sedentary": risk_score += 1
                
                st.markdown("---")
                st.subheader(f"📊 {t['habit_results']}")
                if risk_score >= 4:
                    st.error(f"⚠️ **High Symptom Impact Predicted (Risk Score: {risk_score}/5):** Your current sleep ({sleep_hrs} hrs) and hydration ({water_intake} L) are strongly correlated with increased cramp severity and fatigue. Recommendation: Increase water intake and aim for at least 7.5 hours of consistent sleep.")
                elif risk_score >= 2:
                    st.warning(f"⚡ **Moderate Impact (Risk Score: {risk_score}/5):** Minor lifestyle adjustments—such as increasing hydration or reducing evening caffeine—can noticeably improve your cycle comfort.")
                else:
                    st.success(f"✅ **Optimal Habit Balance (Risk Score: {risk_score}/5):** Excellent! Your current lifestyle habits are well-balanced to keep cramp intensity low and energy levels stable.")

    elif app_mode == "Emergency & Clinics":
        st.title(f"🚨 {t['em_heading']}")
        st.write(t["em_sub"])
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"### 🇮🇳 {t['india_helplines']}")
            st.markdown(f"- **{t['helpline_1']}:** `112` (24/7 Medical / Police)")
            st.markdown(f"- **{t['helpline_2']}:** `1091`")
            st.markdown(f"- **{t['helpline_3']}:** `108`")
            st.markdown(f"- **{t['helpline_4']}:** `7827170170`")
            st.markdown(f"- **{t['helpline_5']}:** `1800-599-0019`")
            
        with col_b:
            st.markdown(f"### 📍 {t['gps_tracker']}")
            
            loc_html = f"""
            <script>
            function getLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(showPosition, showError);
                }} else {{
                    document.getElementById("status").innerHTML = "Geolocation is not supported by this browser.";
                }}
            }}
            function showPosition(position) {{
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                var mapsUrl = "https://www.google.com/maps/search/gynaecologist+womens+hospital/@" + lat + "," + lon + ",14z";
                document.getElementById("status").innerHTML = "<b>✅ Live Location Detected!</b><br><br><a href='" + mapsUrl + "' target='_blank' style='background-color:#dc2626; color:white; padding:10px 16px; text-decoration:none; border-radius:8px; font-weight:bold;'>📍 View Nearby Women's Hospitals on Google Maps</a>";
            }}
            function showError(error) {{
                document.getElementById("status").innerHTML = "Location access denied or unavailable. Please type your city manually below.";
            }}
            </script>
            <button onclick="getLocation()" style="background-color:#dc2626; color:white; border:none; padding:10px 16px; border-radius:8px; cursor:pointer; font-weight:bold;">🎯 {t['detect_gps']}</button>
            <div id="status" style="margin-top:15px; font-family:sans-serif;"></div>
            """
            components.html(loc_html, height=140)
            
            st.markdown("---")
            st.markdown(f"### 🏙️ {t['city_search']}")
            user_city = st.text_input(t["city_input"], "Hyderabad")
            
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
            st.markdown(f"[👉 {t['maps_link']} **{user_city}** on Google Maps]({gmaps_url})")

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