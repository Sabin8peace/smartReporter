# src/byakaran/indexer.py
import os
import json

class GorkhapatraRulesIndexer:
    """Manages and loads the pre-compiled Gorkhapatra rules cache to guarantee zero boot overhead."""
    def __init__(self):
        self.rules_database = []
        self.cache_path = "data/gorkhapatra_cache.json"

    def load_pdf_rules(self, pdf_path: str = None):
        """
        Reads from the pre-extracted JSON file. 
        If missing or empty, auto-generates the file with production fallback rules.
        """
        # 🚀 Step 1: Check if a valid, populated JSON cache file exists
        if os.path.exists(self.cache_path) and os.path.getsize(self.cache_path) > 10:
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.rules_database = json.load(f)
                
                # Double-check that it successfully parsed an active array list
                if self.rules_database and isinstance(self.rules_database, list):
                    print(f"🚀 Speed Optimization: Loaded {len(self.rules_database)} custom rules directly from cache.")
                    return
            except Exception as e:
                print(f"⚠️ Cache read anomaly: {e}. Rebuilding from master fallback baseline rules...")

        # 📄 Step 2: Master standard Gorkhapatra rules list
        gorkhapatra_master_rules = [
            "विभक्ति (ले, लाई, मा, को, बाट, द्वारा, देखि) शब्दहरू अगाडिको पदसँग अनिवार्य रूपमा जोडेर लेख्नुपर्छ (पदयोग)। जस्तै: 'नेपालमा', 'काठमाडौँबाट' ।",
            "नामयोगी शब्दहरू (माथि, मुनि, भित्र, बाहिर, सँग, निम्ति, विरूद्ध) अगाडिको पदसँग जोडेर लेख्नुपर्छ। जस्तै: 'टेबुलमाथि', 'घरभित्र', 'उनीसँग' ।",
            "नाम र क्रियापदको आदरार्थी तह सङ्गति मिल्नुपर्छ। उच्च आदरार्थी पदका लागि सधैं आदरार्थी क्रियापद प्रयोग गर्नुहोस्। जस्तै: 'प्रधानमन्त्रीले भन्नुभयो' (भन्यो वा भने होइन) ।",
            "नेपाली शब्दहरूको हिज्जे लेख्दा आधिकारिक गोरखापत्र शब्दकोश बमोजिम ह्रस्व र दीर्घ (इकार/उकार) नियम पालना गर्नुपर्छ। जस्तै: 'नेपाली', 'प्रविधिको' ।",
            "तथ्याङ्क वा सरकारी निर्णयहरू उल्लेख गर्दा वाक्यको अन्त्यमा स्पष्ट र व्यावसायिक पत्रकारिता स्तरको क्रियापद हुनुपर्छ। जस्तै: 'घोषणा गरिएको छ' ।",
            "संयुक्ताक्षर (जस्तै: द्ध, ट्ट, न्न) र हलन्त/अजन्तको प्रयोग गोरखापत्रको मानक प्रकाशन शैली अनुसार शुद्ध हुनुपर्छ।"
        ]

        # 💾 Step 3: Auto-create the cache file using safe UTF-8 Devanagari settings
        print("⚠️ Notice: Cache file was empty or missing. Creating a healthy baseline database standard...")
        self.rules_database = gorkhapatra_master_rules
        
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.rules_database, f, ensure_ascii=False, indent=4)
            print(f"💾 Centralized rule storage created successfully at: {self.cache_path}")
        except Exception as e:
            print(f"❌ Critical error writing data structure to disk: {e}")