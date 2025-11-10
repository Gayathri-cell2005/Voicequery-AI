import sqlite3
import speech_recognition as sr
import pyttsx3

# Step 1: Create and connect to SQLite database
conn = sqlite3.connect('voicequery.db')
cursor = conn.cursor()

# Step 2: Create example table
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    position TEXT,
    salary REAL
)
''')

# Insert sample data if table is empty
cursor.execute('SELECT COUNT(*) FROM employees')
if cursor.fetchone()[0] == 0:
    cursor.executemany('INSERT INTO employees (name, position, salary) VALUES (?, ?, ?)', [
        ('Alice', 'Developer', 70000),
        ('Bob', 'Manager', 85000),
        ('Charlie', 'Analyst', 65000)
    ])
    conn.commit()

# Step 3: Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Step 4: Simple text-to-SQL converter for demo purposes
def text_to_sql(text):
    text = text.lower()
    if "all employees" in text or "list employees" in text:
        return "SELECT * FROM employees;"
    elif "salary" in text:
        return "SELECT name, salary FROM employees;"
    elif "position" in text:
        return "SELECT name, position FROM employees;"
    else:
        return "SELECT * FROM employees;"  # fallback query

# Step 5: Capture and process voice input
def listen_and_query():
    with sr.Microphone() as source:
        speak("Please say your query about employees.")
        audio = recognizer.listen(source)

    try:
        query_text = recognizer.recognize_google(audio)
        speak(f"You asked: {query_text}")
    except sr.UnknownValueError:
        speak("Sorry, I could not understand your speech.")
        return
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return

    sql_query = text_to_sql(query_text)
    speak(f"Executing query: {sql_query}")

    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if results:
            for row in results:
                speak(", ".join(str(item) for item in row))
        else:
            speak("No results found.")
    except Exception as e:
        speak(f"Error executing query: {e}")

if __name__ == "__main__":
    listen_and_query()
    conn.close()