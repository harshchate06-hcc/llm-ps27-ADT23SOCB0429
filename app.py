import os
import re
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from docx import Document
from docx.shared import Inches, Pt

load_dotenv()

st.set_page_config(page_title="Syllabus to Notes Generator", page_icon="📚", layout="wide")

SAMPLE_SYLLABUS = """UNIT I: INTRODUCTION TO ARTIFICIAL INTELLIGENCE
Meaning and definition of AI, history and applications of AI, intelligent agents,
problem solving, search strategies and state-space representation.

UNIT II: MACHINE LEARNING FUNDAMENTALS
Meaning of machine learning, supervised and unsupervised learning, classification,
regression, training and testing data, overfitting and model evaluation.

UNIT III: NEURAL NETWORKS
Artificial neurons, perceptron model, activation functions, feed-forward networks,
backpropagation and applications of neural networks."""

DEMO_NOTES = {
    "UNIT I": """## 1. Introduction to Artificial Intelligence

### Meaning of Artificial Intelligence
Artificial Intelligence (AI) is a branch of computer science that develops systems capable of performing tasks that normally require human intelligence. Examples include understanding language, recognising images and making decisions.

### History and Applications
AI has developed from early rule-based programs to modern systems that learn from data. Common applications include virtual assistants, recommendation systems, medical image analysis, fraud detection and autonomous vehicles.

### Intelligent Agents
An intelligent agent observes its environment through sensors and acts through actuators. A rational agent selects actions that help it achieve its defined goal.

### Problem Solving and Search
AI problems can be represented using:
- Initial state: the starting situation.
- Goal state: the desired result.
- Actions: possible moves between states.
- Path cost: the cost of reaching a state.

Search strategies explore possible states to find a solution. Examples include breadth-first search and depth-first search.""",
    "UNIT II": """## 2. Machine Learning Fundamentals

### Meaning of Machine Learning
Machine Learning (ML) is a field of AI in which computers learn patterns from data and use those patterns to make predictions or decisions without being explicitly programmed for every case.

### Types of Machine Learning
- **Supervised learning:** learns from labelled examples. Examples include spam detection and house-price prediction.
- **Unsupervised learning:** finds patterns in unlabelled data. Examples include customer grouping and clustering.

### Classification and Regression
Classification predicts a category, such as spam or not spam. Regression predicts a numerical value, such as temperature or price.

### Training, Testing and Overfitting
Training data is used to fit a model, while testing data checks performance on unseen examples. Overfitting occurs when a model memorises training data and performs poorly on new data.

### Model Evaluation
Evaluation measures how well a model performs. Common measures include accuracy, precision, recall and mean squared error, depending on the task.""",
    "UNIT III": """## 3. Neural Networks

### Artificial Neuron
An artificial neuron receives input values, multiplies them by weights, adds a bias and applies an activation function to produce an output.

### Perceptron Model
A perceptron is a basic neural-network unit used for binary classification. It calculates a weighted sum and applies a threshold or activation function.

### Activation Functions
Activation functions introduce non-linearity into a network. Common examples include sigmoid, tanh and ReLU.

### Feed-Forward Networks
In a feed-forward network, information moves from the input layer through hidden layers to the output layer. There are no feedback connections in the basic architecture.

### Backpropagation
Backpropagation calculates how much each network weight contributes to prediction error. The weights are then adjusted, commonly using gradient descent, to reduce the error.

### Applications
Neural networks are used in image recognition, speech processing, language applications, forecasting and recommendation systems."""
}

def split_into_units(text):
    """Split text at headings such as UNIT I, Unit 1, or Module 1."""
    pattern = re.compile(
        r"(?im)^\s*((?:UNIT|MODULE)\s*(?:[IVXLC]+|\d+)\b[^\n]*)\s*$"
    )
    matches = list(pattern.finditer(text))
    if not matches:
        cleaned = text.strip()
        return [("General Syllabus", cleaned)] if cleaned else []
    units = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip(" \n:-")
        units.append((match.group(1).strip(), content))
    return [(title, content) for title, content in units if content]


def generate_with_gemini(unit_title, unit_content, detail_level):
    """Generate notes using Gemini with bounded retries."""
    import time
    from google import genai
    from google.genai import errors

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing. Check your .env file.")

    client = genai.Client(api_key=api_key)

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    prompt = f"""
You are an educational notes assistant. Create accurate,
student-friendly study notes using ONLY the syllabus topics supplied.
Provide headings, simple explanations, important points and examples.

UNIT: {unit_title}
SYLLABUS CONTENT:
{unit_content}

Notes detail: {detail_level}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text or "The model returned an empty response."

        except errors.ServerError as exc:
            if attempt == 2 or "503" not in str(exc):
                raise
            time.sleep(3 * (attempt + 1))


def create_docx(notes_by_unit):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    title = doc.add_heading("Syllabus-Based Study Notes", 0)
    title.alignment = 1
    p = doc.add_paragraph("Generated using the Syllabus-to-Notes Generator")
    p.alignment = 1
    for unit_title, note_text in notes_by_unit:
        doc.add_heading(unit_title, level=1)
        for line in note_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("### "):
                doc.add_heading(line[4:], level=2)
            elif line.startswith("## "):
                doc.add_heading(line[3:], level=2)
            elif line.startswith("- ") or line.startswith("* "):
                doc.add_paragraph(line[2:], style="List Bullet")
            else:
                doc.add_paragraph(line)
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.title("📚 Syllabus-to-Notes Generator")
st.caption("Turn a university syllabus into organised, unit-wise study notes.")
with st.sidebar:
    st.header("Generation settings")
    detail = st.selectbox("Notes detail", ["concise", "moderate", "detailed"], index=1)
    demo_mode = st.toggle("Demo mode (works without an API key)", value=not bool(os.getenv("GEMINI_API_KEY")))
    st.markdown("---")
    st.caption("Live generation requires a Gemini API key in the project's .env file.")
    st.caption("Demo mode uses prepared sample notes for demonstration.")

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("1. Enter your syllabus")
    syllabus = st.text_area(
        "Paste syllabus text below",
        value=SAMPLE_SYLLABUS,
        height=300,
        placeholder="Paste syllabus containing headings such as UNIT I, UNIT II...",
        label_visibility="collapsed",
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Load sample syllabus", use_container_width=True):
            st.session_state["syllabus_reset"] = True
            st.rerun()
    with c2:
        generate = st.button("✨ Generate notes", type="primary", use_container_width=True)

with right:
    st.subheader("2. How it works")
    st.markdown(
        "1. Python identifies unit headings.\\n"
        "2. Each unit is processed separately.\\n"
        "3. Gemini generates structured notes (live mode).\\n"
        "4. Notes are combined into a Word document."
    )
    st.info("Tip: Use clear headings such as UNIT I, UNIT II or MODULE 1 for best unit detection.")

if generate:
    if not syllabus.strip():
        st.error("Please paste a syllabus before generating notes.")
    else:
        units = split_into_units(syllabus)
        if not units:
            st.error("No syllabus content was found.")
        else:
            st.session_state["generated_notes"] = []
            st.session_state["unit_count"] = len(units)
            progress = st.progress(0, text="Preparing units...")
            results = []
            for index, (unit_title, unit_content) in enumerate(units):
                try:
                    if demo_mode:
                        key = re.match(r"UNIT\s+[IVXLC]+", unit_title, re.I)
                        demo_key = key.group(0).upper() if key else ""
                        note = DEMO_NOTES.get(demo_key)
                        if not note:
                            note = (
                                f"## {unit_title}\\n\\n"
                                "### Overview\\n"
                                f"This unit covers: {unit_content}\\n\\n"
                                "### Key study points\\n"
                                "- Review each listed concept and understand its definition.\\n"
                                "- Prepare examples and compare related concepts.\\n"
                                "- Revise important terminology from the syllabus."
                            )
                    else:
                        note = generate_with_gemini(unit_title, unit_content, detail)
                    results.append((unit_title, note))
                    progress.progress((index + 1) / len(units), text=f"Generated {index + 1} of {len(units)} units")
                except Exception as exc:
                    st.error(f"Could not generate notes for {unit_title}: {exc}")
                    break
            else:
                st.session_state["generated_notes"] = results
                st.success(f"Successfully prepared notes for {len(results)} unit(s).")

if st.session_state.get("generated_notes"):
    notes = st.session_state["generated_notes"]
    st.markdown("---")
    st.subheader("3. Generated study notes")
    for title, content in notes:
        with st.expander(title, expanded=True):
            st.markdown(content)
    docx_file = create_docx(notes)
    st.download_button(
        "⬇️ Download notes as Word document",
        data=docx_file,
        file_name="syllabus_study_notes.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )
    st.caption("Review AI-generated notes against your official syllabus and learning material.")
