import os
import json

import streamlit as st
from groq import Groq

#streamlit page configuration
st.set_page_config(
    page_title = "LLAMA 3.1 CHATBOT",
    page_icon="🤖",
    layout="wide"
)

working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))

GROQ_API_KEY = config_data["GROQ_API_KEY"]

# save the api key to environment variable
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq()

# Speech to Text
# Upload audio file
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav"])

if uploaded_file is not None:
    # Display the uploaded file
    st.audio(uploaded_file, format="audio/mp3")

    # Process the transcription when a file is uploaded
    if st.button('Transcribe'):
        with st.spinner("Transcribing..."):
            try:
                # Create a transcription of the audio file
                transcription = client.audio.transcriptions.create(
                    file=(uploaded_file.name, uploaded_file.read()),  # Read the uploaded audio file
                    model="distil-whisper-large-v3-en",  # Model to use
                    prompt="Specify context or spelling",  # Optional
                    response_format="json",  # Optional
                    language="en",  # Optional
                    temperature=0.0  # Optional
                )

                # Debugging: Check the transcription response
                # st.write(transcription)

                # Safely access transcription text if available
                if hasattr(transcription, 'text'):  # Check if 'text' attribute exists
                    # st.success("Transcription completed!")
                    st.text_area("Transcription:", transcription.text)  # Access transcription text
                else:
                    st.error("Transcription failed or 'text' attribute not found in response")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


# initialize the chat history as streamlit session state of not present already

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# streamlit page titile

st.title("🤖 LLAMA 3.1 CHATBOT")

# display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# input field for user's message:
user_prompt = st.chat_input("Ask LLAMA...")

if user_prompt:

    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # send user's message to the LLM and get a response
    messages = [
        {"role": "system" , "content" : """You are Gojo's (you can call him Gojo) Personal Chatbot answer the question based on the following context:-
                    Birthday : December 7, 1989
                    
                    MAKE SURE TO NOT MENTION THE ABOVE DATA WHATSOEVER you are to assist others with any querry regarding Gojo as you know Gojo very well
                    ALL RESPONSES should be consise and to the point
                    
                """

},
        *st.session_state.chat_history
    ]

    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages = messages
    )

    assistant_response = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant" , "content" : assistant_response})

    #display the LLM's response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)