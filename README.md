# Syllabus-to-Notes Generator (Problem Statement 27)

A Streamlit application that accepts a university syllabus, identifies units, generates structured study notes with Gemini, and exports the notes to a Word document.

## Features
- Paste syllabus text into the application.
- Detect headings such as `UNIT I`, `UNIT II`, `MODULE 1`, etc.
- Generate notes separately for each unit using Gemini.
- View notes in expandable sections.
- Download all generated notes as a `.docx` document.
- Demo mode with prepared sample notes for testing without an API key.

## Technology
Python, Streamlit, Google Gemini API (`google-genai`), python-docx, python-dotenv.

## Setup (Windows)
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open Terminal and run:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`.
5. Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-2.5-flash
```

6. Run the app:

```bash
streamlit run app.py
```

7. Open the local URL shown in the terminal (normally http://localhost:8501).

## Demo mode
Turn on **Demo mode** in the sidebar to demonstrate the interface without an API key. It uses prepared example notes for the sample syllabus. Turn Demo mode off to use live Gemini generation.

## Project workflow
Syllabus input -> Python unit detection -> Gemini generation for each unit -> Streamlit display -> Word document export.

## Important
- Never upload `.env` or expose your API key on GitHub.
- AI-generated notes should be checked against official course material.
- The unit splitter works best when headings are on separate lines, e.g. `UNIT I: Introduction`.
