Here is the complete **`README.md`** text you can copy directly into your file:

# 🩺 Multilingual AI Health Companion & PCOS Screener

An AI-powered health assistant and clinical screening web application built with **Streamlit**. Designed for regional accessibility across South Asia, it supports dynamic translation and intelligent script detection for **Kannada, Telugu, English, Hindi, and Tamil**.

---

## 📌 Project Overview

The **Multilingual AI Health Companion & PCOS Screener** is an interactive web application designed to evaluate preliminary hormonal health indicators and answer general wellness queries.

### Key Features:

* **Dynamic Language Switcher:** Instantly changes the entire interface—including medical questionnaire checklists, headings, and buttons—between 5 major languages (**Kannada, Telugu, English, Hindi, and Tamil**).
* **Clinical PCOS Risk Screener:** Allows users to check off key symptoms (menstrual cycle irregularities, hirsutism, weight fluctuations, fatigue, family history) to calculate potential risk indicators.
* **Auto-Detecting AI Assistant:** Analyzes user input queries in real-time using Unicode script detection and responds in the exact language typed (e.g., Telugu query $\rightarrow$ Telugu answer).

---

## 📦 Dependencies & Requirements

To run this application, ensure you have the following installed:

* **Python**: `3.8` or higher
* **Streamlit**: `1.20.0` or higher
* **Standard Python Libraries**: `re` (Regular Expressions)

---

## 🛠️ Setup Instructions

### Step 1: Install Python & Git

Verify that Python and Git are installed on your machine by running these commands in your terminal or command prompt:

```bash
python --version
git --version

```

### Step 2: Set Up Project Directory

Create a project folder on your computer and navigate into it:

```bash
mkdir pcos-health-screener
cd pcos-health-screener

```

### Step 3: Install Required Dependencies

Install **Streamlit** using Python's package manager (`pip`):

```bash
pip install streamlit

```

---

## 🏃 Steps to Run the Project

1. **Open the Project in VS Code:**
* Open **Visual Studio Code**.
* Go to **File > Open Folder...** and select your `pcos-health-screener` folder.
* Make sure `app.py` and `README.md` are inside this folder.


2. **Open Integrated Terminal:**
* Press `Ctrl + ~` (or select **Terminal > New Terminal** from the top menu).


3. **Launch the Streamlit App:**
Run the following command in the terminal:

```bash
   streamlit run app.py
   

```

4. **Access the App:**
* Streamlit will automatically launch the application in your default web browser at `http://localhost:8501`.



---

## 📁 Project File Structure

```text
pcos-health-screener/
├── app.py          # Main Streamlit application file (UI + Logic)
└── README.md       # Project documentation and setup guide

```

---

## 🌏 Supported Languages & Detection Logic

| Language | UI Language Toggle | Script Detection Range |
| --- | --- | --- |
| **Kannada** (ಕನ್ನಡ) | ✅ | `[\u0C80-\u0CFF]` |
| **Telugu** (తెలుగు) | ✅ | `[\u0C00-\u0C7F]` |
| **English** | ✅ | Default / Latin |
| **Hindi** (हिंदी) | ✅ | `[\u0900-\u097F]` |
| **Tamil** (தமிழ்) | ✅ | `[\u0B80-\u0BFF]` |

---

## ⚠️ Medical Disclaimer

*This application is for informational and screening awareness purposes only. It does not provide formal medical diagnoses. Users should consult a qualified healthcare specialist or endocrinologist for clinical evaluations.*
