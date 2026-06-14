# src/generator/orchestrator.py
import os
import trafilatura
from google import genai
from google.genai import types

class MultiInputReporterEngine:
    def __init__(self):
        # Initializing the modern Google GenAI Client
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        # Pull the fresh variable directly from Python's active environment memory
        api_token = os.getenv("GEMINI_API_KEY")
        
        # 🔴 ACCELERATOR PASS: Pass the verified token straight into the Client initialization parameter
        if api_token:
            print("🔑 Successfully loaded active GEMINI_API_KEY from environment memory.")
            self.client = genai.Client(api_key=api_token)
        else:
            print("⚠️ Warning: GEMINI_API_KEY environment string is empty. Defaulting to automatic detection...")
            self.client = genai.Client()

    def _extract_url_text(self, url: str) -> str:
        """Downloads a target webpage and extracts the structural body text."""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
                return text if text else f"[Error: Could not extract text content from {url}]"
            return f"[Error: Failed to fetch data from link {url}]"
        except Exception as e:
            return f"[Exception occurred processing URL: {str(e)}]"

    def assemble_and_generate_news(self, web_urls: list, uploaded_files: list, raw_text_inputs: list) -> str:
        """
        Gathers mixed inputs (URLs, PDFs, Images, raw text strings), 
        translates cross-lingual materials, and structures a cohesive news story.
        """
        # 1. Initialize the contents array for the Gemini API call
        contents = []
        
        # 2. Add structural system instructions directly into the dynamic prompt context
        prompt_directive = """
        तपाईं एक कुशल अनुसन्धानकर्ता र व्यावसायिक नेपाली पत्रकार हुनुहुन्छ । 
        तपाईंलाई विभिन्न स्रोतहरूबाट (वेब लिङ्क, कागजात, तस्विर वा विभिन्न भाषाहरूमा लेखिएका सामाग्री) डेटा दिइएको छ।
        
        तपाईंको मुख्य जिम्मेवारी:
        १. सबै स्रोतहरू अध्ययन गरी जानकारीहरूलाई आपसमा मिलाउनुहोस् (Synthesize data) ।
        २. यदि कुनै सामाग्री अंग्रेजीमा छ भने, त्यसको अर्थपूर्ण, प्राकृतिक र सही नेपाली अनुवाद गर्दै मूल मर्मलाई समेट्नुहोस् (मशीनी अनुवाद जस्तो नदेखियोस्) ।
        ३. सबै विवरणहरू समेटेर एक पूर्ण र व्यावसायिक नेपाली समाचार तयार पार्नुहोस् ।
        
        समाचारको संरचना निम्न बमोजिम हुनुपर्दछ:
        - मुख्य आकर्षक हेडलाइन (Headline)
        - पृष्ठभूमि र मुख्य बुँदाहरू (Key points/Summary)
        - बिस्तृत समाचार विवरण (Detailed body paragraph)
        - स्रोतहरूको संक्षिप्त सन्दर्भ (References/Sources linked)
        """
        contents.append(prompt_directive)

        # 3. Process URL Web Scraping
        if web_urls:
            contents.append("\n--- START OF WEB SOURCE ARTICLES ---")
            for url in web_urls:
                if url.strip():
                    scraped_content = self._extract_url_text(url)
                    contents.append(f"\nSource URL: {url}\nContent:\n{scraped_content}")
            contents.append("--- END OF WEB SOURCE ARTICLES ---\n")

        # 4. Attach Manual Text Inputs (English or Nepali text fields)
        if raw_text_inputs:
            contents.append("\n--- START OF MANUAL TEXT INPUTS ---")
            for text in raw_text_inputs:
                if text.strip():
                    contents.append(text)
            contents.append("--- END OF MANUAL TEXT INPUTS ---\n")

        # 5. Attach Uploaded Multimodal Media Objects (Images, Scanned PDFs)
        if uploaded_files:
            for file_bytes, mime_type in uploaded_files:
                # Convert raw memory buffers into explicit API parts objects natively
                file_part = types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type
                )
                contents.append(file_part)

        # 6. Execute Multimodal Synthesis API Request
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents
        )
        return response.text