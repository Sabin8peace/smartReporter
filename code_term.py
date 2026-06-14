# extract_image.py
import os
import json
import easyocr

print("📥 Initializing Local OCR Engine (Devanagari + English)...")
# Initialize EasyOCR for native language recognition
reader_ocr = easyocr.Reader(['ne', 'en'])

def append_image_rules_to_cache(image_path, cache_path="data/gorkhapatra_cache.json"):
    if not os.path.exists(image_path):
        print(f"❌ Error: Target image file not found at '{image_path}'")
        return

    print(f"\n📸 Target Image Identified: {image_path}")
    print("--- Running Local Visual OCR Extraction (EasyOCR) ---")
    
    try:
        # Run visual character recognition directly on the image file
        ocr_results = reader_ocr.readtext(image_path, detail=0)
        page_text = " ".join(ocr_results)
        
        extracted_rules = []
        if page_text.strip():
            # Parse text blocks into individual rule items using 'नियम' as the boundary
            for block in page_text.split("नियम"):
                if block.strip():
                    extracted_rules.append(f"नियम {block.strip()}")
                    
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return

    if not extracted_rules:
        print("⚠️ Warning: No readable Devanagari text or grammar rules found in this image.")
        return

    # 💾 MEMORY LAYER: Handle incremental append logic safely
    existing_rules = []
    
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 10:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                existing_rules = json.load(f)
            print(f"📂 Found existing cache file with {len(existing_rules)} rules. Preparing to append...")
        except Exception as e:
            print(f"⚠️ Problem reading existing JSON cache ({e}). Creating a fresh file structure instead.")

    # Merge fresh entries with legacy database, stripping duplicates along the way
    for rule in extracted_rules:
        if rule not in existing_rules:
            existing_rules.append(rule)

    # Write out the combined dataset using clean UTF-8 formatting parameters
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(existing_rules, f, ensure_ascii=False, indent=4)
        
        print(f"✨ SUCCESS! Processed {len(extracted_rules)} rules from your image.")
        print(f"💾 Total collection in cache now stands at: {len(existing_rules)} rules inside '{cache_path}'")
    except Exception as e:
        print(f"❌ Failed to update the centralized storage file: {e}")

if __name__ == "__main__":
    # Put your snapshot rule snapshot image path here to run via terminal
    # Example format: "data/rules_page_snapshot.jpg" or "data/rules_page_snapshot.png"
    target_image = "img/11.png" 
    
    append_image_rules_to_cache(target_image)