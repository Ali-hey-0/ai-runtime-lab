import math
from typing import List, Dict, Any


class HybridRAGEngine:
    """موتور بازیابی ترکیبی (Dense + Sparse) با الگوریتم RRF"""

    def __init__(self, corpus: List[str]):
        self.corpus = corpus

    # ۱. شبیه‌ساز Sparse Search (BM25/Keyword Matching)
    def _sparse_search(self, query: str) -> List[int]:
        query_words = set(query.lower().split())
        scores = []
        for idx, doc in enumerate(self.corpus):
            doc_words = doc.lower().split()
            # محاسبه ساده فرکانس کلمات مشترک (Simplified BM25 logic)
            score = sum(1 for word in doc_words if word in query_words)
            scores.append((idx, score))
        # مرتب‌سازی بر اساس بالاترین اسکور
        scores.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, score in scores if score > 0]

    # ۲. شبیه‌ساز Dense Search (Vector Similarity)
    def _dense_search(self, query: str) -> List[int]:
        # در پیاده‌سازی واقعی اینجا Cosine Similarity ایمبدینگ‌ها قرار می‌گیرد
        # شبیه‌سازی: اولویت با اسنادی که تشابه مفهومی دارند
        scores = []
        for idx, doc in enumerate(self.corpus):
            similarity = 0.8 if "architecture" in doc or "system" in doc else 0.2
            scores.append((idx, similarity))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, _ in scores]

    # ۳. ادغام رتبه‌ها با Reciprocal Rank Fusion (RRF)
    def hybrid_retrieve(self, query: str, top_k: int = 2, k_constant: int = 60) -> List[Dict[str, Any]]:
        sparse_ranks = self._sparse_search(query)
        dense_ranks = self._dense_search(query)

        rrf_scores: Dict[int, float] = {}

        # محاسبه RRF برای نتایج Sparse
        for rank, doc_id in enumerate(sparse_ranks):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_constant + rank + 1))

        # محاسبه RRF برای نتایج Dense
        for rank, doc_id in enumerate(dense_ranks):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_constant + rank + 1))

        # مرتب‌سازی نهایی بر اساس اسکور ترکیبی RRF
        sorted_docs = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

        results = []
        for doc_id, score in sorted_docs[:top_k]:
            results.append({
                "doc_id": doc_id,
                "text": self.corpus[doc_id],
                "rrf_score": round(score, 5)
            })

        return results


# --- تست عملکرد Hybrid Retrieval ---
if __name__ == "__main__":
    documents = [
        "System architecture defined with deterministic FSM and durable execution.",
        "Error handling guide: HTTP 429 rate limits and exponential backoff retry.",
        "RAG context window management: combining BM25 sparse search with dense vectors.",
        "Database indexing techniques for high throughput key-value stores."
    ]

    engine = HybridRAGEngine(corpus=documents)
    
    # جستجوی کلیدواژه‌ای دقیق + مفهومی
    search_query = "RAG search architecture 429"
    retrieved = engine.hybrid_retrieve(query=search_query, top_k=2)

    print(f"[HYBRID SEARCH QUERY]: '{search_query}'\n")
    for rank, res in enumerate(retrieved, start=1):
        print(f"Rank {rank} (RRF Score: {res['rrf_score']}):")
        print(f"  Content: \"{res['text']}\"\n")

