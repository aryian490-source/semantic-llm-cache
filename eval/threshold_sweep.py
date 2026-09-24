import json
import os
import sys
from cache.semantic_cache import eval_wrapper, reset_cache, query_embeddings, query_answer



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



def load_test_data(faq_path="../bot/faq.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", "bot", "faq.json")

    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_data = []
    for item in data["intents"]:
        intent_id = item["intent_id"]
        for paraphrase in item["paraphrases"]:
            test_data.append((paraphrase, intent_id))

    return test_data


def run_sweep(test_data, thresholds):
    results = []

    for threshold in thresholds:
        reset_cache(query_embeddings, query_answer)   # Step 1: cache khaali karo

        correct_hits = 0
        false_hits = 0
        total_miss = 0

        for query, true_intent in test_data:           # Step 2: har query bhejo
            outcome, matched_intent = eval_wrapper(query, true_intent, threshold)

            if outcome == "HIT" and matched_intent == true_intent:
                correct_hits += 1                       # Step 4a
            elif outcome == "HIT" and matched_intent != true_intent:
                false_hits += 1                          # Step 4b
            else:
                total_miss += 1                          # Step 4c

        total_queries = len(test_data)
        hit_rate = correct_hits / total_queries          # Step 5
        false_hit_rate = false_hits / total_queries

        results.append({
            "threshold": threshold,
            "hit_rate": hit_rate,
            "false_hit_rate": false_hit_rate
        })                                                 # Step 6

    return results

    
if __name__ == "__main__":
    test_data = load_test_data()
    thresholds_to_test = [0.65, 0.70, 0.75, 0.78, 0.80, 0.82, 0.85, 0.88, 0.90, 0.95]
    sweep_results = run_sweep(test_data, thresholds_to_test)
    for r in sweep_results:
        print(r)





