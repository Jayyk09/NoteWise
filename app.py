import streamlit as st
import google.generativeai as genai
import time
import firebase_admin
from firebase_admin import credentials, firestore
import webbrowser
import urllib.parse

st.title("Notewise")

# Configure the API key
genai_api_key = st.secrets["GEMINI_API"]

genai.configure(api_key=genai_api_key)

model = "models/gemini-1.5-flash-8b"

# Firebase authentication

cred = credentials.Certificate("firebase-credentials.json")

# cache the Firebase initialization to avoid reinitializing the app. 
# subsequent calls will return the cached Firestore client.
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
        prompt = "write lecture notes for this video with specific time stamps. "
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-8b")
        print("Making LLM inference request...")
        response = model.generate_content(
            [video_file, prompt], request_options={"timeout": 600} # Increase timeout to 10 minutes 
        )
        return response.text
    
    except Exception as e:
        return f"Error analyzing video: {e}"
    
def generate_latex_code(analysis_result):
    """
    Sends the analysis result to Gemini to generate LaTeX code.

    Args:
        analysis_result: The text content of the analysis.

    Returns:
        A string containing the generated LaTeX code.
    """
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-8b")
        response = model.generate_content([
            f"Generate LaTeX code for the following analysis:\n\n{analysis_result}. Don't write anything else" 
        ])  # Specify response format here
        return response.text
    except Exception as e:
        return f"Error generating LaTeX code: {e}"

if username:
    # Show the list of videos with the video name that the user has uploaded
    videos_ref = db.collection("users").document(username).collection("videos")
    videos = [doc.id for doc in videos_ref.stream()]
    if videos:
        st.write("Uploaded videos:")
        for video in videos:
            if st.button(video):  # Create a button for each video
                st.session_state.video_to_show = video  # Store the selected video in session state
                st.rerun()  # Rerun the app to go to the new page

    # Check if a video has been selected
    if "video_to_show" in st.session_state:
        st.write(f"Showing analysis for: {st.session_state.video_to_show}")
        # Retrieve the full analysis from Firestore
        doc_ref = db.collection("users").document(username).collection("videos").document(st.session_state.video_to_show)
        analysis = doc_ref.get().to_dict().get("analysis")
        latex = doc_ref.get().to_dict().get("latex")
        st.write(analysis)
        st.write(latex)
    else:
        st.write("No videos uploaded yet")

    uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

    if uploaded_file is not None:
        # Display the uploaded video
        st.video(uploaded_file)

        # Analyze the video
        with st.spinner("Analyzing video..."):
            analysis_result = analyze_video(uploaded_file, uploaded_file.name)
            # upload to firestore for the user -> video title -> analysis
            doc_ref = db.collection("users").document(username).collection("videos").document(uploaded_file.name)
            doc_ref.set({"analysis": analysis_result})
            

        # Display the analysis
        st.header("Analysis Results")
        #st.write(analysis_result)
        #call from firestore
        doc = db.collection("users").document(username).get()
        st.write(doc.to_dict()["analysis"])

        #have buttons for additional analysis
        if st.button("Turn into PDF"):
            analysis = doc.to_dict()["analysis"]
            latex_code = generate_latex_code(analysis)
            doc_ref.update({"latex": latex_code})
            # print the latex code
            st.write(latex_code)