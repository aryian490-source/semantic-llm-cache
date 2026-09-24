from sentence_transformers import SentenceTransformer, util
from bot.mock_llm import mock_llm
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

query_embeddings =[]
query_answer=[]


def store(query_text, answer, intent):
    query_embeddings.append(model.encode(query_text, convert_to_tensor=True))
    query_answer.append([query_text,answer, intent])
    return

def lookup(newquery_text, threshold=0.85):
    newquery_embedding = model.encode(newquery_text, convert_to_tensor=True)
    if len(query_embeddings)==0:
        return None
    results = util.semantic_search(newquery_embedding, query_embeddings)
    best = results[0][0]
    score = best['score']
    idx = best['corpus_id']
    if score>=threshold:
        return {"answer":query_answer[idx][1],  "intent": query_answer[idx][2]}
    else:
        return None

def wrapper(query):
    match = lookup(query)
    if match is not None:
        return{"answer": match["answer"], "source": "HIT", "latency": 0 , "tokens" : 0}
    dictionary = mock_llm(query)
    answer = dictionary.get("answer")
    store(query, answer, intent=None)
    return {"answer": answer, "source": "MISS", "latency" : dictionary.get("latency"), "tokens": dictionary.get("tokens")}

def reset_cache(query_embeddings, query_answer):
    query_embeddings.clear()
    query_answer.clear()
    return query_embeddings, query_answer

def eval_wrapper(query, true_intent, threshold):
    match = lookup(query, threshold=threshold)
    if match is not None:
        return ("HIT", match["intent"])          # match ka intent bhi return karo compare karne ke liye
    else:
        store(query, true_intent, true_intent)      # MISS -> apna khud ka intent hi "answer" bana ke store kar do
        return ("MISS", None)
    
if __name__ == "__main__":
    test_queries = [
        ("hostel fees kitni hai", "hostel_fees"),              # 1. MISS (pehli baar)
        ("hostel ki fees kya hai", "hostel_fees"),              # 2. HIT (same matlab)
        ("how much is the hostel fee", "hostel_fees"),          # 3. HIT (English paraphrase)
        ("hostel ke timings kya hain", "hostel_timings"),       # 4. MISS (naya intent, similar shabd)
        ("hostel gate kab band hota hai", "hostel_timings"),    # 5. HIT (confusable se sahi match hona chahiye)
        ("btech ki fees kitni hai", "btech_fees"),               # 6. MISS (naya intent)
        ("what is the fee for btech", "btech_fees"),             # 7. HIT
        ("mba ki fees kitni hai", "mba_fees"),                   # 8. MISS (confusable se galat match na ho)
        ("mba fee structure kya hai", "mba_fees"),               # 9. HIT
        ("admission kaise lein", "admission_process"),           # 10. MISS
        ("how to apply for admission", "admission_process"),     # 11. HIT
        ("library kitne baje khulti hai", "library_timing"),     # 12. MISS
        ("library ka time batao", "library_timing"),             # 13. HIT
        ("kitni books issue kar sakte hain", "library_book_issue"), # 14. MISS (confusable se sahi hona chahiye)
        ("scholarship kaise milegi", "scholarship_eligibility"), # 15. MISS
        ("am I eligible for scholarship", "scholarship_eligibility"), # 16. HIT
        ("scholarship me kitne paise milte hain", "scholarship_amount"), # 17. MISS
        ("placement process kya hai", "placement_process"),       # 18. MISS
        ("how does placement work here", "placement_process"),    # 19. HIT
        ("average package kitna hai", "placement_average_package"), # 20. MISS
        ("aaj mausam kaisa hai", "unrelated"),                     # 21. Bilkul unrelated - MISS honi chahiye
    ]

    for query, true_intent in test_queries:
        result = wrapper(query)
        print(f"Query: {query}")
        print(f"  → Source: {result['source']}, Answer: {result['answer'][:50]}...")
        print()


