import requests

r = requests.post("http://10.10.183.205:11434/api/generate", json={
    "model": "llama3:8b",
    "prompt": "Classify this question's Bloom's Taxonomy level (Remember/Understand/Apply/Analyze/Evaluate/Create). Respond with JSON only, format: {\"bloom_level\": \"...\", \"confidence\": ...}\n\nQuestion: Design an experiment to test soil erosion mitigation strategies.",
    "format": "json",
    "stream": False,
    "options": {
        "num_predict": 150,
        "temperature": 0.1
    }
})
print(r.json()["response"])
