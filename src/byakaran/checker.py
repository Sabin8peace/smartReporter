# src/byakaran/checker.py
import os
import re
import jellyfish
import json
from indicnlp.tokenize import indic_tokenize
from google import genai
from dotenv import load_dotenv

from src.byakaran.gopaindexer import GorkhapatraRulesIndexer

load_dotenv()

class AdvancedNepaliByakaranEngine:
    def __init__(self):
        self.vocabulary = [
            "नेपाल", "नेपाली", "काठमाडौँ", "समाचार", "पत्रकार", "सरकार", "संविधान",
            "विकास", "आर्थिक", "बजेट", "घोषणा", "गरेका", "भएका", "छन्", "थिए", "गर्छन्"
        ]
        self.nepali_suffixes = ["ले", "लाई", "का", "की", "को", "मा", "बाट", "देखि", "हरू"]
        
        api_token = os.getenv("GEMINI_API_KEY")
        # Explicit pass here as well to force the fresh token swap
        self.client = genai.Client(api_key=api_token)
        
        # self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        self.indexer = GorkhapatraRulesIndexer()
        self.indexer.load_pdf_rules("data/gorkhapatra_rules.pdf")

    def _levenshtein_suggest(self, word: str) -> str:
        if word in self.vocabulary or len(word) <= 2:
            return word
        best_match = word
        highest_similarity = 0.0
        for valid_word in self.vocabulary:
            similarity = jellyfish.jaro_winkler_similarity(word, valid_word)
            if similarity > 0.82 and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = valid_word
        return best_match

    def fix_padyog_padbiyog(self, text: str) -> tuple[str, list]:
        flags = []
        modified_text = text
        for suffix in self.nepali_suffixes:
            pattern = rf"(\b\w+)\s+({suffix})\b"
            matches = re.findall(pattern, modified_text)
            if matches:
                for word, suff in matches:
                    flags.append(f"पदयोग नियम: '{word} {suff}' लाई जोडेर '{word}{suff}' बनाइयो ।")
                modified_text = re.sub(pattern, r"\1\2", modified_text)
        return modified_text, flags

    def context_spell_check(self, text: str) -> tuple[str, list]:
        flags = []
        tokens = indic_tokenize.trivial_tokenize(text)
        corrected_tokens = []
        for token in tokens:
            if re.match(r'^[\u0900-\u097F]+$', token):
                suggested = self._levenshtein_suggest(token)
                if suggested != token:
                    flags.append(f"हिज्जे सुधार (Base): '{token}' -> '{suggested}'")
                    corrected_tokens.append(suggested)
                else:
                    corrected_tokens.append(token)
            else:
                corrected_tokens.append(token)
        return " ".join(corrected_tokens), flags

    def _gorkhapatra_ai_pass(self, text: str) -> dict:
        """Validates text structure and breaks it into Title, Highlights, and Description fields."""
        extracted_guidelines = "\n".join([f"- {rule}" for rule in self.indexer.rules_database])

        gorkhapatra_prompt = f"""
        तपाईं गोरखापत्र (Gorkhapatra) को वरिष्ठ भाषा सम्पादक (Copy Editor) हुनुहुन्छ। 
        तल दिइएको नेपाली समाचार पाठलाई गोरखापत्रको आधिकारिक व्याकरण, हिज्जे र शैली पुस्तिका बमोजिम शुद्ध गर्नुहोस्।

        तपाईंले अनिवार्य रूपमा पालना गर्नुपर्ने गोरखापत्रका आन्तरिक नियमहरू:
        {extracted_guidelines}

        तपाईंको जवाफ मात्र निम्न JSON ढाँचामा हुनुपर्छ, अरू केही पनि नलेख्नुहोस्:
        {{
            "title": "समाचारको छोटो र आकर्षक शीर्षक (Title)",
            "highlights": [
                "मुख्य समाचारको मुख्य अंश वा हाइलाइट बुँदा १",
                "मुख्य समाचारको मुख्य अंश वा हाइलाइट बुँदा २"
            ],
            "description": "गोरखापत्रको स्तरमा पूर्ण रूपमा शुद्ध गरिएको विस्तृत समाचार विवरण (Full Editorial Content)",
            "logs": ["परिवर्तन गरिएको व्याकरण नियम विविरण १", "परिवर्तन गरिएको व्याकरण नियम विविरण २"]
        }}

        समाचार पाठ:
        {text}
        """

        # Set up a safe structured fallback dict if things crash
        fallback = {
            "title": "ताजा समाचार रिपोर्ट",
            "highlights": ["स्रोत सामग्रीहरू प्रशोधन गरियो।"],
            "description": text,
            "logs": ["गोरखापत्र एजेन्ट पार्सिङ त्रुटि।"]
        }

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=gorkhapatra_prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            fallback["logs"] = [f"त्रुटि: {str(e)}"]
            return fallback

    def analyze_document(self, raw_text: str) -> dict:
        all_logs = []
        
        step1_text = re.sub(r'\s*।\s*', ' । ', raw_text).strip()
        step2_text, padyog_logs = self.fix_padyog_padbiyog(step1_text)
        all_logs.extend(padyog_logs)
        
        step3_text, spelling_logs = self.context_spell_check(step2_text)
        all_logs.extend(spelling_logs)
        
        cleaned_base_text = re.sub(r'\s+([।,.?])', r'\1', step3_text)
        
        # Run AI pass to get the structured dictionary object
        ai_structured_result = self._gorkhapatra_ai_pass(cleaned_base_text)
        
        # Combine local regex correction summaries with AI editing logs
        all_logs.extend(ai_structured_result.get("logs", []))
        
        return {
            "title": ai_structured_result.get("title", "समाचार"),
            "highlights": ai_structured_result.get("highlights", []),
            "description": ai_structured_result.get("description", ""),
            "diagnostic_logs": all_logs
        }