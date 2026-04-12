# core/retriever.py

from config.domain_keywords import DOMAIN_KEYWORDS
from core.embedder import Embedder
from core.hf_search import search_huggingface_datasets
from core.similarity import compute_similarity
from utils.schema_utils import schema_to_text


def retrieve(schema, threshold=0.35, top_k=5):

    domain = schema.get("domain")

    if domain not in DOMAIN_KEYWORDS:
        raise ValueError("Unsupported domain")

    keywords = DOMAIN_KEYWORDS[domain]

    print(f"Searching HF using keywords: {keywords}")

    # Step 1: Metadata search
    candidates = search_huggingface_datasets(keywords)

    if not candidates:
        print("No candidates found.")
        return []

    print(f"Found {len(candidates)} candidate datasets")

    # Step 2: Embedding
    embedder = Embedder()

    schema_text = schema_to_text(schema)
    schema_embedding = embedder.embed([schema_text])[0]

    dataset_texts = [
        c["metadata_text"]   # ✅ FIXED HERE
        for c in candidates
    ]

    dataset_embeddings = embedder.embed(dataset_texts)

    # Step 3: Similarity scoring
    scores = compute_similarity(schema_embedding, dataset_embeddings)

    results = []

    # for dataset, score in zip(candidates, scores):
    #     if score >= threshold:
    #         results.append({
    #             "dataset_id": dataset["name"],
    #             "similarity": float(score)
    #         })

    for dataset, score in zip(candidates, scores):
        results.append({
            "dataset_id": dataset["name"],
            "similarity": float(score)
    })


    results.sort(key=lambda x: x["similarity"], reverse=True)

    return results[:top_k]
