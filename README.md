# 🧠 Semantic Caching Layer for LLM APIs

A production-style semantic caching system that sits between an application and an LLM API, serving cached responses for **semantically similar queries** instead of hitting the LLM every time — cutting cost, tokens, and latency.

Built on a real Groq LLM-backed college helpdesk chatbot, with a Streamlit demo UI and a full evaluation pipeline (model comparison + threshold tuning + traffic simulation).

---

## 🎯 Why this project

Repeated or paraphrased queries to an LLM ("hostel fees kitni hai" vs "how much is the hostel fee") cost the same tokens and latency as a brand-new query — even though the answer is identical. This project detects semantic similarity between queries using sentence embeddings and short-circuits the LLM call when a close-enough match already exists in cache.

---

## 📊 Results (measured, not estimated)

| Metric | Value |
|---|---|
| Cache hit rate (300-query simulated traffic) | **71.7%** |
| Tokens saved | **159,856 / 223,055 (71.7%)** |
| Avg latency — cache HIT | **~0s (instant)** |
| Avg latency — cache MISS (real LLM call) | **4.92s** |
| False-hit rate at selected threshold | **0%** |

> Simulated on a 300-query workload sampled (with repetition) from a 20-intent, ~120-paraphrase college helpdesk FAQ dataset (Hindi + English + Hinglish), using the real Groq API (`openai/gpt-oss-20b`) for cache misses.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Embed query (multilingual sentence embedding)
    │
    ▼
Compare against cached query embeddings (cosine similarity)
    │
    ├── Similarity ≥ threshold ──► Return cached answer (HIT) — no LLM call
    │
    └── Similarity < threshold ──► Call LLM (MISS)
                                       │
                                       ▼
                              Store new query + embedding + answer in cache
```

**Stack:**
- `sentence-transformers` — local, free multilingual embeddings (no API cost for similarity)
- `Groq API` (`openai/gpt-oss-20b`) — the "real" LLM being cached
- `Streamlit` — interactive demo dashboard
- Pure Python / NumPy-backed vector search (`util.semantic_search`) — no external vector DB needed at this scale

---

## 🔬 Evaluation methodology

Rather than guessing a similarity threshold, it was **derived from data**:

### 1. Model comparison
Three multilingual embedding models were benchmarked on a labeled dataset of paraphrase pairs, confusable pairs (e.g. "MBA fees" vs "BTech fees" — similar wording, different meaning), and unrelated pairs:

| Model | Best hit rate @ 0% false-hit rate | Threshold |
|---|---|---|
| **`paraphrase-multilingual-MiniLM-L12-v2`** ✅ | **11%** | 0.85 |
| `paraphrase-multilingual-mpnet-base-v2` | 7% | 0.90 |
| `sentence-transformers/LaBSE` | 0% | 0.90 |

**MiniLM-L12-v2** was selected — best accuracy *and* lowest latency/size of the three.

### 2. Threshold sweep
Thresholds from 0.65 → 0.95 were swept and scored on:
- **Hit rate** — % of paraphrases correctly matched to cache
- **False-hit rate** — % of queries matched to the *wrong* cached answer (the critical failure mode for a cache — worse than a cache miss)

Selected threshold: **0.85** — the lowest threshold at which false-hit rate reaches exactly **0%**.

### 3. Traffic simulation
300 queries were sampled (with repetition, unweighted) from the FAQ paraphrase set and run end-to-end through the real Groq-backed system to produce the headline hit-rate/latency/token numbers above.

---

## ⚠️ Key design decision: false-hit protection matters more than hit rate

A cache that returns the *wrong* answer is worse than no cache at all — it silently corrupts responses. Early testing at threshold=0.75 produced a false-hit: **"MBA fees" was matched to "BTech fees"** because the sentences are structurally almost identical. This drove the decision to explicitly optimize for **zero false-hits first**, then maximize hit rate — rather than just picking the threshold with the highest raw hit rate.

---

## 📁 Project structure

```
semcache/
├── bot/
│   ├── faq.json          # 20 intents × ~6 paraphrases each (Hindi/English/Hinglish)
│   └── mock_llm.py        # Groq API wrapper (system prompt, latency + token tracking)
├── cache/
│   └── semantic_cache.py  # Core cache: store / lookup / wrapper (HIT-or-call-LLM logic)
├── eval/
│   ├── threshold_sweep.py     # Model comparison + threshold sweep
│   ├── simulate_traffic.py    # 300-query realistic traffic simulation
│   └── analyze_results.py     # Hit rate / latency / tokens-saved reporting
├── app.py                 # Streamlit live demo (chat UI + real-time stats)
└── requirements.txt
```

---

## 🚀 Running it

```bash
pip install -r requirements.txt

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# Run the live demo
streamlit run app.py

# Or reproduce the evaluation
python -m eval.threshold_sweep
python -m eval.simulate_traffic
python -m eval.analyze_results
```

---

## 🧑‍💻 What this project demonstrates

- Semantic search / embeddings applied to a real cost-reduction problem
- Rigorous evaluation methodology (multi-model benchmark + data-driven threshold selection, not guesswork)
- Awareness of failure modes (false-hits) beyond the obvious metric (hit rate)
- End-to-end system: real LLM integration, caching layer, evaluation pipeline, and a usable demo UI
