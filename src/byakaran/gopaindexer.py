# src/byakaran/indexer.py
import os
import json

class GorkhapatraRulesIndexer:
    """Manages and loads the pre-compiled Gorkhapatra rules cache to guarantee zero boot overhead."""
    def __init__(self):
        self.rules_database = {}
        self.cache_path = "data/bhasasaili.json"

    def load_pdf_rules(self, pdf_path: str = None):
        """
        Loads rules from the JSON cache. If the file exists, it ensures the core baseline
        rules are present without overwriting your existing scanned content.
        """
        # Define the core fallback rules schema dictionary
        gorkhapatra_master_rules = {
            "suffix": "विभक्ति (ले, लाई, मा, को, बाट, द्वारा, देखि) शब्दहरू अगाडिको पदसँग अनिवार्य रूपमा जोडेर लेख्नुपर्छ (पदयोग)। जस्तै: 'नेपालमा', 'काठमाडौँबाट' ।",
            "postposition": "नामयोगी शब्दहरू (माथि, मुनि, भित्र, बाहिर, सँग, निम्ति, विरूद्ध) अगाडिको पदसँग जोडेर लेख्नुपर्छ। जस्तै: 'टेबुलमाथि', 'घरभित्र', 'उनीसँग' ।",
            "व्याकरण_नाम_र_क्रियापदको_आदरार्थी_तह_सङ्गति": "नाम र क्रियापदको आदरार्थी तह सङ्गति मिल्नुपर्छ। उच्च आदरार्थी पदका लागि सधैं आदरार्थी क्रियापद प्रयोग गर्नुहोस्। जस्तै: 'प्रधानमन्त्रीले भन्नुभयो' (भन्यो वा भने होइन) ।",
            "हिज्जे_नेपाली_शब्दहरूको_गोरखापत्र_शब्दकोश_नियम": "नेपाली शब्दहरूको हिज्जे लेख्दा आधिकारिक गोरखापत्र शब्दकोश बमोजिम ह्रस्व र दीर्घ (इकार/उकार) नियम पालना गर्नुपर्छ। जस्तै: 'नेपाली', 'प्रविधिको' ।",
            "तथ्याङ्क_वा_सरकारी_निर्णयहरू_उल्लेख_gorkhapatra": "तथ्याङ्क वा सरकारी निर्णयहरू उल्लेख गर्दा वाक्यको अन्त्यमा स्पष्ट र व्यावसायिक पत्रकारिता स्तरको क्रियापद हुनुपर्छ। जस्तै: 'घोषणा गरिएको छ' ।",
            "संयुक्ताक्षर_र_हलन्त_अजन्तको_मानक_लेखन_शैली": "संयुक्ताक्षर (जस्तै: द्ध, ट्ट, न्न) र हलन्त/अजन्तको प्रयोग गोरखापत्रको मानक प्रकाशन शैली अनुसार शुद्ध हुनुपर्छ।"
        }

        existing_loaded = False

        # 🚀 Step 1: Check if a valid, populated JSON cache file exists
        if os.path.exists(self.cache_path) and os.path.getsize(self.cache_path) > 10:
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.rules_database = json.load(f)
                
                if self.rules_database and isinstance(self.rules_database, dict):
                    existing_loaded = True
                    print(f"🚀 Base Cache Detected: Loaded {len(self.rules_database)} active entries.")
            except Exception as e:
                print(f"⚠️ Cache read anomaly: {e}. Rebuilding standard dictionary templates...")
                self.rules_database = {}

        # 🚀 Step 2: Smart Merge - Only inject the rule if the key doesn't exist yet
        mutated_flag = False
        
        for key, value in gorkhapatra_master_rules.items():
            if key not in self.rules_database:
                self.rules_database[key] = value
                mutated_flag = True
                print(f"➕ Auto-Injected missing master anchor rule key: [{key}]")

        # 🚀 Step 3: Write changes back to disk cleanly if updates occurred or file was missing
        if not existing_loaded or mutated_flag:
            try:
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                with open(self.cache_path, "w", encoding="utf-8") as f:
                    json.dump(self.rules_database, f, ensure_ascii=False, indent=4)
                print(f"💾 Centralized rule storage updated and synchronized successfully at: {self.cache_path}")
            except Exception as e:
                print(f"❌ Critical error writing synchronized rules database to disk: {e}")
        else:
            print("✨ Perfect Sync: Database already holds all mandatory baseline rules.")