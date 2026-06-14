# app.py
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
from src.generator.orchestrator import MultiInputReporterEngine
from src.byakaran.checker import AdvancedNepaliByakaranEngine

st.set_page_config(page_title="SmartReporter AI Dashboard", page_icon="📰", layout="wide")

st.title("📰 SmartReporter AI Studio")
st.subheader("Multi-Source Ingestion, Synthesis, & Grammar Check Pipeline")

@st.cache_resource
def init_engines():
    return MultiInputReporterEngine(), AdvancedNepaliByakaranEngine()

try:
    engine, checker = init_engines()
except Exception as e:
    st.error("Engine failure: Verify that your GEMINI_API_KEY environment variable is configured.")
    st.stop()

# 🧠 MEMORY MANAGEMENT: Initialize session storage fields if they don't exist yet
if "final_story_text" not in st.session_state:
    st.session_state["final_story_text"] = ""
if "corrections_made" not in st.session_state:
    st.session_state["corrections_made"] = []

# Build functional workspaces
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📥 Input Panel (Multiple Ingestion Streams)")
    
    st.markdown("**1. Web Scraper URLs (Nepali or International News Sites)**")
    url_input = st.text_area(
        "Enter URLs (One web link per line):",
        height=80,
        placeholder="https://ekantipur.com/example-news\nhttps://bbc.com/world-news-article"
    )
    urls = [u.strip() for u in url_input.split("\n") if u.strip()]

    st.markdown("**2. Copy-Pasted Context (English or Nepali text feeds)**")
    text_input = st.text_area(
        "Paste any updates, text drafts, or raw details directly:",
        height=100,
        placeholder="Type or paste supplementary details here..."
    )

    st.markdown("**3. Multimodal Uploads (Images, Scanned Notices, text/image PDFs)**")
    uploaded_files = st.file_uploader(
        "Upload target assets directly for processing:",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    prepared_files = []
    if uploaded_files:
        for f in uploaded_files:
            file_bytes = f.read()
            mime_type = f.type
            prepared_files.append((file_bytes, mime_type))

    process_btn = st.button("Synthesize All Channels & Write Story", type="primary")

    # When the generation button is clicked, compute the data and lock it into system memory
    if process_btn:
        has_url = len(urls) > 0
        has_text = len(text_input.strip()) > 0
        has_file = len(prepared_files) > 0
        
        if not (has_url or has_text or has_file):
            st.warning("Please supply at least one source stream (URL, text, or file target) to process.")
        else:
            with st.spinner("Parsing sources, translating contexts, and running Byakaran validations..."):
                generated_news_draft = engine.assemble_and_generate_news(
                    web_urls=urls,
                    raw_text_inputs=[text_input] if has_text else [],
                    uploaded_files=prepared_files
                )
                
                # pipeline_output = checker.process_article(generated_news_draft)
                # Change this parameter inside your active execution flow block:
                pipeline_output = checker.analyze_document(generated_news_draft)
                
                # Save data to state parameters instead of standard variables
                st.session_state["final_story_text"] = pipeline_output
                st.session_state["corrections_made"] = pipeline_output["diagnostic_logs"]

with col2:
    st.markdown("### 📄 Polished Editorial Output")
    
    # Render information if the user session state contains data
    if st.session_state["final_story_text"]:
        # Grab the content structure fields
        story_data = st.session_state["final_story_text"]
        
        # 1. Title Formatting Display
        st.subheader(f"📌 {story_data.get('title', 'समाचार')}")
        
        # 2. Highlighted Text Layout Section (Using native warning blocks for prominence)
        st.markdown("#### 🔍 मुख्य हाइलाइटहरू (Highlights)")
        for bullet in story_data.get("highlights", []):
            st.markdown(f"• **{bullet}**")
        
        st.markdown("---")
        
        # 3. Editorial Description Layout Paragraphs
        st.markdown("#### 📝 विस्तृत विवरण (Description)")
        st.write(story_data.get("description", ""))
        
        # 📥 Compile the complete output structure for a downloadable plain txt format file
        compiled_downloadable_string = (
            f"शीर्षक: {story_data.get('title')}\n"
            f"=========================================\n"
            f"मुख्य हाइलाइटहरू:\n" + "\n".join([f"- {b}" for b in story_data.get('highlights')]) + "\n"
            f"=========================================\n"
            f"विवरण:\n{story_data.get('description')}"
        )
        
        st.download_button(
            label="📥 Download Structured Report (.txt)",
            data=compiled_downloadable_string,
            file_name="smart_reporter_structured.txt",
            mime="text/plain"
        )
        
        # Display the custom diagnostic metrics
        if st.session_state["corrections_made"]:
            with st.expander("🛠️ Gorkhapatra Standards & Grammar Logs"):
                for item in st.session_state["corrections_made"]:
                    st.info(item)