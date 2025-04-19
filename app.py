import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

# Default prompt for detailed exam preparation
DEFAULT_PROMPT = ('''You are an expert tutor. I will provide you a PDF.
Your task is to read and understand the entire PDF carefully, and then give me a complete, detailed, and well-organized explanation of all the content in a single response.

Format your output properly in **Markdown** (using headings, subheadings, bold text, bullet points, numbered lists, etc.), so it can be saved as a Markdown report if needed.

Instructions:
- Explain every topic thoroughly in simple, short and clear language.
- Use similar words as present in the PDF for better understanding.
- Define important terms when first introduced.
- Cover all sections equally; do not skip anything.
- If any formulas are present, include them properly, explain each variable clearly.
- Add short examples wherever helpful.
- I need Nice Short and Simple explanations for each topic.
- Structure the response logically with proper Markdown formatting.
- Make it detailed, clean, and simple (suitable for exam preparation).
- Give the full explanation in **one continuous Markdown-formatted response** — no step-by-step or broken replies.
''')

def generate_response_with_pdf(pdf_data: bytes, user_prompt: str) -> str | None:
    """
    Generates a response from the Gemini model using the content of a PDF.

    Args:
        pdf_data (bytes): The bytes of the PDF file.
        user_prompt (str): The prompt or question you want to ask about the PDF.

    Returns:
        str or None: The generated response text, or None if an error occurs.
    """
    try:
        contents = [
            {"mime_type": "application/pdf", "data": pdf_data},
            user_prompt,
        ]
        response = model.generate_content(contents)
        response.resolve()
        return response.text
    except Exception as e:
        st.error(f"An error occurred while generating the response: {e}")
        return None

def create_pdf_from_markdown(markdown_text: str) -> BytesIO:
    """Converts Markdown text to a PDF file in memory."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for line in markdown_text.split('\n'):
        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['h1']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['h2']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['h3']))
        elif line.startswith('- '):
            story.append(Paragraph(line[2:], styles['Bullet']))
        elif line.startswith('* '):
            story.append(Paragraph(line[2:], styles['Bullet']))
        elif line.startswith('**'):
            parts = line.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    story.append(Paragraph(f"<b>{part}</b>", styles['Normal']))
                elif part:
                    story.append(Paragraph(part, styles['Normal']))
        elif line.strip():
            story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Streamlit UI enhancements
st.set_page_config(page_title="Exam PDF Explainer", page_icon="📚")

# Custom CSS for a nicer look
st.markdown(
    """
    <style>
        .reportview-container {
            background: linear-gradient(135deg, #e0f7fa, #cddc39);
        }
        .main .block-container {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00796b;
        }
        .stFileUploader label {
            background-color: #4caf50;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .stTextArea textarea {
            border: 1px solid #00796b;
            border-radius: 5px;
            padding: 0.5rem;
        }
        .stButton button {
            background-color: #00796b;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 5px;
            font-weight: bold;
        }
        .stButton button:hover {
            background-color: #009688;
        }
        .stSuccess {
            color: green;
            font-weight: bold;
            margin-top: 1rem;
        }
        .stSubheader {
            color: #00796b;
            margin-top: 1.5rem;
        }
        .stMarkdown {
            line-height: 1.6;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 Exam PDF Explainer with Gemini Pro")
st.subheader("Your AI-powered study assistant!")

uploaded_file = st.file_uploader("Upload your PDF file 📄", type=["pdf"])

prompt = DEFAULT_PROMPT

if uploaded_file and prompt:
    pdf_data = uploaded_file.read()

    if st.button("Explain PDF for Exam"):
        with st.spinner("Generating a detailed explanation..."):
            response_text = generate_response_with_pdf(pdf_data, prompt)

        if response_text:
            st.success("✅ Explanation generated successfully!")
            st.subheader("📝 Detailed Explanation:")
            st.markdown(response_text+"\n \n Created By H", unsafe_allow_html=True) 

            # Option to download as Markdown
            st.download_button(
                label="Download as Markdown",
                data=response_text,
                file_name="explanation.md",
                mime="text/markdown",
            )

            # Option to download as PDF
            pdf_buffer = create_pdf_from_markdown(response_text)
            st.download_button(
                label="Download as PDF",
                data=pdf_buffer,
                file_name="explanation.pdf",
                mime="application/pdf",
            )