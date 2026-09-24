import random
import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache.semantic_cache import wrapper, reset_cache, query_embeddings, query_answer
from eval.threshold_sweep import load_test_data


def run_simulation(num_queries=300):
    reset_cache(query_embeddings, query_answer)
    test_data = load_test_data()

    results = []
    for i in range(num_queries):
        query, true_intent = random.choice(test_data)
        result = wrapper(query)
        results.append({
            "query": query,
            "true_intent": true_intent,
            "source": result["source"],
            "latency": result["latency"],
            "tokens": result["tokens"]
        })
        print(f"[{i+1}/{num_queries}] {result['source']} — {query[:40]}")

    return results


def save_to_csv(results, filename="simulation_results.csv"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)
    with open(full_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "true_intent", "source", "latency", "tokens"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved to {full_path}")

if __name__ == "__main__":
    results = run_simulation(num_queries=300)
    save_to_csv(results)