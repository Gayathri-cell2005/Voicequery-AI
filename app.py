import streamlit as st
import sqlite3
import speech_recognition as sr
import pyttsx3
import pandas as pd
import tempfile
import os

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
conn = sqlite3.connect('voicequery.db')
cursor = conn.cursor()

# -----------------------------
# SPEECH RECOGNITION SETUP
# -----------------------------
recognizer = sr.Recognizer()

# -----------------------------
# SAFE TEXT-TO-SPEECH FUNCTION
# -----------------------------
def speak(text):
    """Convert text to speech safely without file permission errors."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_path = tmpfile.name
    tmpfile.close()  # Close file before writing

    engine.save_to_file(text, temp_path)
    engine.runAndWait()
    engine.stop()

    # Play audio safely
    with open(temp_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/wav")

    os.remove(temp_path)

# -----------------------------
# CONVERT VOICE TEXT → SQL
# -----------------------------
def text_to_sql(query):
    query = query.lower()

    if "all employees" in query or "list employees" in query:
        return "SELECT * FROM employees;"
    elif "salary" in query and "developer" in query:
        return "SELECT name, salary FROM employees WHERE position='Developer';"
    elif "salary" in query:
        return "SELECT name, salary FROM employees;"
    elif "position" in query:
        return "SELECT name, position FROM employees;"
    elif "manager" in query:
        return "SELECT * FROM employees WHERE position='Manager';"
    elif "analyst" in query:
        return "SELECT * FROM employees WHERE position='Analyst';"
    else:
        return None

# -----------------------------
# CAPTURE VOICE INPUT
# -----------------------------
def listen_and_query():
    with sr.Microphone() as source:
        st.write("🎤 Listening... please speak your query clearly.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query_text = recognizer.recognize_google(audio)
        st.success(f"🗣 You said: {query_text}")
        speak(f"You said: {query_text}")
        return query_text
    except sr.UnknownValueError:
        st.warning("Sorry, I couldn't understand your voice.")
        speak("Sorry, I could not understand your voice.")
        return None
    except sr.RequestError:
        st.error("Speech recognition service unavailable.")
        speak("Speech recognition service unavailable.")
        return None

# -----------------------------
# STREAMLIT APP UI
# -----------------------------
st.set_page_config(page_title="VoiceQuery AI", page_icon="🎙", layout="centered")
st.title("🎙 VoiceQuery AI")
st.write("Ask questions about your employee database using only your voice!")

if st.button("🎤 Speak and Query Database"):
    query_text = listen_and_query()
    if query_text:
        sql_query = text_to_sql(query_text)
        if sql_query:
            st.info(f"🧠 SQL Query Generated:\nsql\n{sql_query}\n")  # Show query clearly
            speak("Executing your query now.")
            try:
                cursor.execute(sql_query)
                results = cursor.fetchall()
                if results:
                    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
                    st.success("✅ Query results:")
                    st.dataframe(df)
                    speak("Here are your results.")
                else:
                    st.warning("No data found.")
                    speak("No matching data found.")
            except Exception as e:
                st.error(f"Error executing query: {e}")
                speak("There was an error running your query.")
        else:
            st.warning("Query not recognized.")
            speak("Sorry, I didn’t understand your question.")