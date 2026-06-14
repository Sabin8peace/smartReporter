# extractor_app.py
import os
import json
import streamlit as st
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="Gorkhapatra Rules Ingestion", page_icon="📝", layout="centered")

st.title("📝 Gorkhapatra Rules Ingestion UI")
st.write("Upload an image snippet to extract and append rules to your local database JSON cache cleanly.")

# 🧠 Cache the EasyOCR reader load sequence so it doesn't re-initialize on every UI change
@st.cache_resource
def load_ocr_engine():
    st.info("📥 Initializing Local OCR Engine (Devanagari + English)...")
    return easyocr.Reader(['ne', 'en'])

reader_ocr = load_ocr_engine()
CACHE_PATH = "data/gorkhapatra_cache.json"

# File Uploader component field
uploaded_file = st.file_uploader("Choose a grammar screenshot image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Open and display the uploaded image to the user interface
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Grammar Sheet Perspective", width="stretch")
    
    # Trigger active process loop execution button
    if st.button("Extract text & append to JSON", type="primary"):
        with st.spinner("--- Running Local Visual OCR Extraction (EasyOCR) ---"):
            try:
                # Convert uploaded PIL stream target into an open array layout matrix
                img_array = np.array(image)
                
                # --- YOUR EXACT EXTRACTION LOGIC ---
                ocr_results = reader_ocr.readtext(img_array, detail=0)
                page_text = " ".join(ocr_results)
                
                extracted_rules = []
                if page_text.strip():
                    # Parse text blocks into individual rule items using 'नियम' as the boundary
                    for block in page_text.split("नियम"):
                        if block.strip():
                            extracted_rules.append(f"नियम {block.strip()}")
                
                if not extracted_rules:
                    st.warning("⚠️ Warning: No readable Devanagari text or grammar rules found in this image.")
                else:
                    # --- YOUR EXACT MEMORY LAYER LOGIC ---
                    existing_rules = []
                    
                    if os.path.exists(CACHE_PATH) and os.path.getsize(CACHE_PATH) > 10:
                        try:
                            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                                existing_rules = json.load(f)
                            st.write(f"📂 Found existing cache file with {len(existing_rules)} rules. Preparing to append...")
                        except Exception as e:
                            st.error(f"⚠️ Problem reading existing JSON cache ({e}). Creating a fresh file structure instead.")

                    # Merge fresh entries with legacy database, stripping duplicates along the way
                    new_additions = 0
                    for rule in extracted_rules:
                        if rule not in existing_rules:
                            existing_rules.append(rule)
                            new_additions += 1

                    # --- YOUR EXACT WRITE OUT SYSTEM ---
                    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
                    with open(CACHE_PATH, "w", encoding="utf-8") as f:
                        json.dump(existing_rules, f, ensure_ascii=False, indent=4)
                    
                    st.success(f"✨ SUCCESS! Processed {len(extracted_rules)} rules from your image.")
                    st.info(f"💾 Total collection in cache now stands at: **{len(existing_rules)}** rules inside '{CACHE_PATH}' ({new_additions} new rules added)")
                    
                    # Optional expander preview block to double check your data on screen
                    with st.expander("👁️ View Extracted Content Rows"):
                        for r in extracted_rules:
                            st.text(r)
                            
            except Exception as e:
                st.error(f"❌ Extraction failed: {e}")