# Import required libraries
import streamlit as st
from gtts import gTTS  # For converting text to speech
import speech_recognition as sr  # For converting voice to text
from langchain_google_genai import GoogleGenerativeAI  # For using Google Gemini LLM
from langchain.chains import LLMChain  # To create a chain using LLM and prompt
from langchain.prompts import PromptTemplate  # To define prompt templates
from textblob import TextBlob  # For sentiment analysis
import requests  # For making HTTP requests (News API)
from fpdf import FPDF  # For creating PDFs
import time  # For managing time in sleep(1)
import os  # For managing files such as s_a.mp3, img 


# Set Google Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDQi1McNz68AfVUDvUU4No6kE1RzOzVZ2g"

# News API key
NEWS_API_KEY = "927581b4ea30409d908d03aa03c7778f"

# LLM model name
LLM_MODEL_NAME = "gemini-1.5-flash-latest"


# Initialize the LLM model
try:
    llm = GoogleGenerativeAI(model=LLM_MODEL_NAME)
except Exception as e:
    st.error(f"Error initializing LLM. Please check your API key and model name: {e}")
    llm = None


# Function to convert summary text to speech and play it
def speak_summary_gtts(text, filename="summary_audio.mp3"):
    """
    Converts the given summary text to speech using gTTS and plays the audio.
    """
    if not text:
        st.warning("No text provided to speak.")
        return
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        st.audio(filename)
    except Exception as e:
        st.error(f"Error generating or playing speech: {e}")


# Function to take voice input from user and convert it to text
def take_command():
    """
    Captures user's voice using microphone and converts it to text using Google Speech Recognition.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎧 Listening...")
        try:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, phrase_time_limit=7)
            st.success("✅ Voice Received. Processing...")
            query = r.recognize_google(audio)
            return query
        except sr.WaitTimeoutError:
            st.warning("⚠️ No speech detected within the time limit.")
            return ""
        except sr.UnknownValueError:
            st.error("⚠️ Google Speech Recognition could not understand audio.")
            return ""
        except sr.RequestError as e:
            st.error(f"⚠️ Could not request results from Google Speech Recognition service; {e}")
            return ""
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred during voice recognition: {e}")
            return ""

# Function to generate PDF
def save_summary_as_pdf(summary_text, filename="News_Summary.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf.output(filename)
    return filename

# Function to search for news articles based on a topic
def search_topic(topic):
    """
    Uses NewsAPI to fetch relevant articles for the given topic and returns combined content.
    """
    st.info(f"Searching for '{topic}' using NewsAPI...")
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=relevancy&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            if articles:
                combined_content = ""
                for article in articles[:3]:
                    content = article.get("content") or article.get("description") or ""
                    combined_content += content + "\n\n"
                return combined_content.strip()
            else:
                st.warning(f"No relevant news articles found for topic '{topic}'.")
                return None
        else:
            st.error(f"NewsAPI request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching topic '{topic}' from NewsAPI: {e}")
        return None


# Function to analyze sentiment and subjectivity of a given text
def analyze_sentiment(text):
    """
    Analyzes the sentiment (positive, negative, neutral) and subjectivity (fact/opinion) of the text.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.3:
        sentiment_label = "😊 Positive"
    elif polarity < -0.3:
        sentiment_label = "😠 Negative"
    else:
        sentiment_label = "😐 Neutral"

    if subjectivity > 0.6:
        subjectivity_label = "🗣️ Subjective (opinionated)"
    elif subjectivity < 0.4:
        subjectivity_label = "📊 Objective (fact-based)"
    else:
        subjectivity_label = "🔍 Mixed (some opinion and some fact)"

    return sentiment_label, subjectivity_label


# Function to fetch live top headlines frogory='general'):
def fetch_live_news(api_key,category='general'):
    url = f'https://newsapi.org/v2/everything?q={category}&language=en&sortBy=publishedAt&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        return news_data['articles']
    else:
        st.error(f"Failed to fetch news: {response.status_code} - {response.text}")
        return []


# Set page configuration for Streamlit app
st.set_page_config(page_title="NewsGenius", layout="centered", page_icon="📰")

 
# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "topic_from_voice" not in st.session_state:
    st.session_state.topic_from_voice = ""

IMAGE_PATH = "c:\\Users\\HIMAND\\Downloads\\ChatGPT Image May 2, 2025, 05_26_14 PM.png"


# Function to display app header image
def display_header_image():
    '''
    Displays the header image at the top of the app.
    '''
    try:
        st.image(IMAGE_PATH, use_container_width=True)
    except FileNotFoundError:
        st.warning(f"Header image not found at {IMAGE_PATH}. Please check the path.")
    except Exception as e:
        st.warning(f"Could not load header image: {e}")


# Login Page (if not already logged in)
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #6a1b9a;'>🕉️ Hare Krishna</h1>", unsafe_allow_html=True)
    display_header_image()
    st.markdown("<h2 style='text-align: center; color: #1e88e5;'>Welcome to <span style='color:#e91e63'>NewsGenius</span> !!</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>A Perfect Friend for the Geniuses</h4>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("🔐 Login to Continue")
    with st.form("login_form"):
        username_input = st.text_input("Username", placeholder="Enter your username")
        password_input = st.text_input("Password", placeholder="Enter your password", type="password")
        login_button = st.form_submit_button("Login", use_container_width=True)

        if login_button:
            if username_input == "admin" and password_input == "1234":
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.success("Login successful! 🎉")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials. Try again.")


# Main App (after successful login)
else:
    display_header_image()
    st.markdown("<h1 style='text-align: center; color: #6a1b9a;'>🕉️ Hare Krishna</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1e88e5;'>Welcome to <span style='color:#e91e63'>NewsGenius</span> !!</h2>", unsafe_allow_html=True)

    st.sidebar.header("🧑‍💼 User Panel")
    st.sidebar.write(f"✅ Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logged_in = False
        st.rerun()

    st.markdown("---")
    category = st.selectbox("📚 Choose News Category", ["Sports", "Bollywood", "Geopolitics", "Trending", "Spirituality"], key="news_category")

    topic_option = st.radio("🗣️ How do you want to input the topic?", ("Type Topic", "Voice Input"), key="topic_input_option")

    typed_topic = ""
    voice_topic_editable = ""

    if topic_option == "Type Topic":
        typed_topic = st.text_input("📝 Enter Topic", placeholder="e.g. Operation Sindoor", key="typed_topic_input_field")
    else:
        if st.button("🎧 Speak Now", key="speak_now_button"):
            recognized_speech = take_command()
            st.session_state.topic_from_voice = recognized_speech if recognized_speech else ""
        voice_topic_editable = st.text_input("🎤 Recognized/Edit Topic", value=st.session_state.topic_from_voice, key="voice_top" \
        "c_input_field")

    st.markdown("#### 📰 Or Paste Full News Article Below")
    full_article_pasted = st.text_area("Paste News Article Here", height=200, key="full_article_input_field")

    if st.button("🔎 Summarize", key="summarize_action_button"):
        current_typed_topic = st.session_state.get("typed_topic_input_field", "")
        current_voice_topic = st.session_state.get("voice_topic_input_field", "")
        current_article_content = st.session_state.get("full_article_input_field", "")

        final_topic_to_use = current_typed_topic if topic_option == "Type Topic" else current_voice_topic
        st.session_state.summary = ""

        if llm is None:
            st.error("LLM is not initialized. Cannot summarize.")

        elif current_article_content.strip():
            with st.spinner("Summarizing pasted article..."):
                prompt = PromptTemplate(
                    input_variables=["content"],
                    template="You are a news assistant. Summarize the following article in simple language, within 150 words:\n\n{content}\n\nSummary:"
                )
                chain = LLMChain(llm=llm, prompt=prompt)

                try:
                    st.session_state.summary = chain.run(content=current_article_content)
                except Exception as e:
                    st.error(f"Error during summarization: {e}")

        elif final_topic_to_use.strip():
            with st.spinner(f"Fetching and summarizing topic: '{final_topic_to_use}'..."):
                fetched_data = search_topic(final_topic_to_use)
                if fetched_data:
                    prompt = PromptTemplate(
                        input_variables=["content"],
                        template="You are a news assistant. Based on the following information, provide a concise summary for the topic in simple language, within 150 words:\n\n{content}\n\nSummary:"
                    )

                    chain = LLMChain(llm=llm, prompt=prompt)
                    try:
                        st.session_state.summary = chain.run(content=fetched_data)
                    except Exception as e:
                        st.error(f"Error during summarization: {e}")
                else:
                    st.warning(f"No data found for topic '{final_topic_to_use}', so no summary can be generated.")

        else:
            st.warning("⚠️ Please enter/speak a topic, or paste an article first.")

    if st.session_state.get("summary"):
        st.subheader("🧠 Summary:")
        st.success(st.session_state.summary)

        sentiment, subjectivity = analyze_sentiment(st.session_state.summary)
        st.info(f"🧽 Sentiment: {sentiment}")
        st.info(f"📌 Subjectivity: {subjectivity}")

        if st.button("🔊 Speak Summary", key="speak_summary_action_button"):
            with st.spinner("Generating audio..."):
                speak_summary_gtts(st.session_state.summary)

        if st.button("📄 Download Summary as PDF", key="download_pdf_button"):
            with st.spinner("Creating PDF..."):
                pdf_file = save_summary_as_pdf(st.session_state.summary)
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="⬇️ Click to Download PDF",
                        data=file,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )
    
    st.markdown("---")
    st.subheader("📰 Live News Feed")
    news_articles = fetch_live_news(NEWS_API_KEY, category=category.lower())

    if news_articles:
        for article in news_articles[:5]:
            st.markdown(f"**{article['title']}**")
            st.markdown(f"*{article['source']['name']}*")
            st.markdown(f"{article['description']}")
            st.markdown(f"[Read more]({article['url']})")
            st.markdown("---")
            
    else:
        st.write("No news articles available at the moment.")

    st.markdown("<p style='text-align: center; font-size: 14px; color: gray;'>Made with lots of Effort </p>", unsafe_allow_html=True)