import re
from transformers import pipeline

# load a small open-source model (Qwen, Mistral, etc.)
# you can swap with "meta-llama/Llama-3-8b-instruct" if you have GPU
llm = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", device_map="auto")

def parse_constraints(user_input: str):
    # simple regex for numbers
    budget_match = re.search(r"(\d+)\s*(?:usd|dollars|\$)", user_input.lower())
    days_match = re.search(r"(\d+)\s*(?:days|day)", user_input.lower())

    budget = int(budget_match.group(1)) if budget_match else None
    days = int(days_match.group(1)) if days_match else None

    # let LLM try to detect required cities
    prompt = f"Extract cities mentioned from this text: {user_input}. Return as a Python list."
    cities_text = llm(prompt, max_new_tokens=50)[0]["generated_text"]
    
    must_include = []
    if "[" in cities_text and "]" in cities_text:
        try:
            must_include = eval(cities_text[cities_text.index("["):cities_text.index("]")+1])
        except:
            must_include = []

    return {
        "budget": budget,
        "days": days,
        "must_include": must_include
    }
