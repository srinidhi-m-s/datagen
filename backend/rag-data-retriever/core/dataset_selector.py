def select_top_datasets(results, min_similarity=0.25, top_k=5):
    filtered = [
        r for r in results if r["similarity"] >= min_similarity
    ]

    filtered.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return filtered[:top_k]