import re
from datetime import datetime

# Rule-Based Category Keywords (Cold-Start Fallback)
CATEGORY_KEYWORDS = {
    "Groceries": ["groceries", "ration", "kitchan", "daal", "aata", "vegetables", "sabzi", "fruit", "supermarket", "store"],
    "Utilities": ["bill", "bijli", "electricity", "gas", "water", "paani", "internet", "wifi", "wapda", "ptcl"],
    "Transportation": ["fuel", "petrol", "diesel", "cng", "car", "bike", "uber", "careem", "indrive", "rickshaw", "fare"],
    "Dining": ["food", "khana", "restaurant", "hotel", "biryani", "tea", "chai", "coffee", "dinner", "lunch"],
    "Health": ["doctor", "medicine", "dawa", "hospital", "clinic", "checkup", "medical"],
    "Housing": ["rent", "kiraya", "maintenance", "house"],
    "Salary": ["salary", "tankhwah", "pay", "income", "freelance", "client"],
    "Committee/Savings": ["committee", "bc", "bisi", "saving"],
    "Udhaar/Credit": ["udhaar", "loan", "borrow", "khata"]
}

TAG_RULES = {
    "utilities": ["#utilities", "#bill"],
    "fuel": ["#fuel", "#transport"],
    "petrol": ["#fuel", "#vehicle"],
    "groceries": ["#groceries", "#food"],
    "salary": ["#salary", "#income"],
    "committee": ["#committee", "#savings"],
    "udhaar": ["#udhaar", "#credit"],
    "rent": ["#rent", "#housing"],
    "medicine": ["#health", "#medical"],
    "doctor": ["#health", "#medical"]
}

def parse_transaction(text: str):
    """
    Hybrid NLP Transaction Parser: Uses ML Classifier if trained, falls back to Rule-Based.
    """
    clean_text = text.lower().strip()
    
    # 1. Extract Amount
    amounts = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', clean_text)
    amount = 0.0
    if amounts:
        parsed_nums = [float(a.replace(',', '')) for a in amounts]
        amount = max(parsed_nums)
        
    # 2. Determine Transaction Type
    income_words = ["salary", "tankhwah", "income", "received", "aaye", "aaya", "mile", "profit", "remittance", "earned"]
    trans_type = "Expense"
    if any(word in clean_text for word in income_words):
        trans_type = "Income"
        
    # 3. Rule-Based Category Detection
    rule_category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in clean_text for kw in keywords):
            rule_category = cat
            break

    # 4. Try Machine Learning Classification (Naive Bayes)
    category = rule_category
    engine_used = "Rule-Based Parser"
    confidence = 0.75
    
    try:
        from src.ml_engine import predict_category_ml
        ml_cat, ml_conf = predict_category_ml(text)
        if ml_cat and ml_conf > 0.35:
            category = ml_cat
            confidence = float(ml_conf)
            engine_used = f"ML Model (Naive Bayes — {int(confidence * 100)}% Conf.)"
        else:
            if amount > 0 and rule_category != "Other":
                confidence = 0.90
    except Exception:
        pass # Fallback to rule engine if ML module not initialized
            
    # 5. Smart Hashtags
    auto_tags = set()
    for word, tags in TAG_RULES.items():
        if word in clean_text:
            auto_tags.update(tags)
            
    if not auto_tags:
        auto_tags.add(f"#{category.lower().replace('/', '_')}")
        
    tags_str = " ".join(sorted(auto_tags))
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": amount,
        "category": category,
        "description": text.strip(),
        "type": trans_type,
        "tags": tags_str,
        "confidence": confidence,
        "engine": engine_used
    }