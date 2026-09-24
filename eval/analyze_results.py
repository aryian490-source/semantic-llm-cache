import csv
import os

def load_results(filename="simulation_results.csv"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)
    with open(full_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze(results):
    total = len(results)
    hits = [r for r in results if r["source"] == "HIT"]
    misses = [r for r in results if r["source"] == "MISS"]

    hit_rate = len(hits) / total

    miss_latencies = [float(r["latency"]) for r in misses]
    avg_miss_latency = sum(miss_latencies) / len(miss_latencies)

    total_tokens_used = sum(float(r["tokens"]) for r in misses)
    # agar cache na hota, to har query ke liye LLM call lagti (average tokens ke hisaab se)
    avg_tokens_per_call = total_tokens_used / len(misses)
    tokens_without_cache = avg_tokens_per_call * total
    tokens_saved = tokens_without_cache - total_tokens_used

    print(f"Total queries: {total}")
    print(f"HIT: {len(hits)}  MISS: {len(misses)}")
    print(f"Hit rate: {hit_rate*100:.1f}%")
    print(f"Avg MISS latency: {avg_miss_latency:.2f} sec")
    print(f"Avg HIT latency: 0 sec (no API call)")
    print(f"Total tokens used (with cache): {total_tokens_used:.0f}")
    print(f"Estimated tokens without cache: {tokens_without_cache:.0f}")
    print(f"Tokens saved: {tokens_saved:.0f} ({(tokens_saved/tokens_without_cache)*100:.1f}%)")

if __name__ == "__main__":
    results = load_results()
    analyze(results)