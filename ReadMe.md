# Notewise

Notewise is a Streamlit web application that leverages the power of Google's Gemini AI model to analyze educational videos and provide users with comprehensive lecture notes, summaries, and even LaTeX code for generating PDF documents.

## Features

- **Video Upload and Analysis:** Users can upload educational videos, which are then analyzed by the Gemini Pro 1.5 model to extract key information and generate lecture notes with timestamps.
- **Interactive Summary:** The app provides a concise summary of the video content, allowing users to quickly grasp the main points.
- **Firebase Integration:** User data and analysis results are stored in Firebase for persistence and easy retrieval.

## How it Works

1. **Video Upload:** Users upload an MP4 video file through the Streamlit interface.
2. **Gemini Analysis:** The video is sent to the Gemini Pro 1.5 model, which analyzes the content and generates lecture notes with timestamps.
3. **Firebase Storage:** User data, analysis results, and LaTeX code are stored in Firebase.

The latex code can be used to generate pdf using pdflatex or this can be pasted in overleaf.

## Technologies Used

- **Streamlit:** For building the interactive web application.
- **Google Gemini:** For powerful AI video analysis and content generation.
- **Firebase:** For user authentication, data storage, and backend management.

## Getting Started

1. **Clone the repository:** `git clone https://github.com/your-username/notewise.git`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Set up Firebase:**
   - Create a Firebase project and obtain your credentials file (`firebase-credentials.json`).
   - Replace `"path/to/your/firebase-credentials.json"` in the code with the actual path to your credentials file.
4. **Configure Gemini API key:**
   - Obtain a Gemini API key from Google Cloud.
   - Create a `secrets.toml` file in the `.streamlit` directory and add your API key:
     ```toml
     [secrets]
     GEMINI_API = "your_actual_api_key_here"
     ```
5. **Run the app:** `streamlit run notewise.py`

## Future Enhancements

- **User Authentication:** Implement a robust user authentication system using Firebase Authentication.
- **Quiz Generation:** Add functionality to generate quizzes from the video content.
- **Improved PDF Generation:** Explore more advanced LaTeX templating and PDF generation options.
- **Multi-language Support:** Add support for analyzing and generating notes in different languages.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License