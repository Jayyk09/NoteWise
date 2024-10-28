import streamlit as st
import google.generativeai as genai
import time
import firebase_admin
from firebase_admin import credentials, firestore

st.title("Notewise")

# Configure the API key
genai_api_key = st.secrets["GEMINI_API"]

genai.configure(api_key=genai_api_key)

# Firebase authentication

cred = credentials.Certificate("firebase-credentials.json")

@st.cache_resource
def init_firebase():
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# Auth with just username for the sake of ease
username = st.text_input("Username")

def analyze_video(uploaded_file, display_name):
    """
    This function analyzes the video content using the Gemini Pro 1.5 model.
    Args:
      video_bytes: The bytes of the video file.
      display_name: The display name for the uploaded file in Gemini.

    Returns:
      A string containing the analysis of the video.
    """
    try:
        # Get file list in Gemini
        file_list = genai.list_files(page_size=100)

        # Check if the file is already uploaded
        video_file = next((f for f in file_list if f.display_name == display_name), None)

        if video_file is None:
            print(f"Uploading file...")
            video_file = genai.upload_file(
                path=uploaded_file, 
                display_name=display_name,
                mime_type="video/mp4",
                resumable=True
            )
            print(f"Completed upload: {video_file.uri}")
        else:
            print(f"File URI: {video_file.uri}")

        # Check the state of the uploaded file
        while video_file.state.name == "PROCESSING":
            print(".", end="")
            time.sleep(10)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)

        # Generate content using the uploaded file
        prompt = "write lecture for this video with specific time stamps. at the end of it, provide summary of the video for review"
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
        print("Making LLM inference request...")
        response = model.generate_content(
            [video_file, prompt], request_options={"timeout": 600} # Increase timeout to 10 minutes 
        )
        return response.text
    
    except Exception as e:
        return f"Error analyzing video: {e}"


if username:
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

    if uploaded_file is not None:
        # Display the uploaded video
        st.video(uploaded_file)

        # Analyze the video
        with st.spinner("Analyzing video..."):
            analysis_result = analyze_video(uploaded_file, uploaded_file.name)

        # Display the analysis
        st.header("Analysis Results")
        st.write(analysis_result)