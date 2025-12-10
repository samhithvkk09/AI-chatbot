import logging
import streamlit as st
from agent import run_conversation

# Configure basic logging so exceptions are recorded in logs
logging.basicConfig(level=logging.INFO)

try:
    import speech_recognition as sr
    import soundfile as sf
    voice_enabled = True
except ImportError:
    voice_enabled = False

def main():
    st.title("JARVIS Chatbot")
    st.write("Type your message to interact with JARVIS.")

    # Text input section
    user_input = st.text_input("Enter your message here:")

    if st.button("Send"):
        if user_input.strip() != "":
            st.write("You: " + user_input)
            with st.spinner("Processing..."):
                try:
                    response = run_conversation(user_input)
                    st.write("JARVIS: " + response)
                except Exception as e:
                    # Friendly message for users + detailed exception for debugging/logs
                    st.error("An error occurred while processing your request. The full error has been logged.")
                    st.exception(e)
                    logging.exception("Error in run_conversation for user input: %s", user_input)
        else:
            st.warning("Please enter a message before sending.")

    # Voice input section
    if voice_enabled:
        if st.button("Start Listening"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                st.write("Recognizing...")
                try:
                    transcript = recognizer.recognize_google(audio)
                    st.write("You: " + transcript)
                    with st.spinner("Processing..."):
                        try:
                            response = run_conversation(transcript)
                            st.write("JARVIS: " + response)
                        except Exception as e:
                            st.error("An error occurred while processing your voice input. The full error has been logged.")
                            st.exception(e)
                            logging.exception("Error in run_conversation for voice transcript: %s", transcript)
                except sr.UnknownValueError:
                    st.write("Sorry, I could not understand the audio.")
                except sr.RequestError as e:
                    st.write(f"Could not request results; {e}")
    else:
        st.write("Voice recognition is not available.")

if __name__ == "__main__":
    main()
