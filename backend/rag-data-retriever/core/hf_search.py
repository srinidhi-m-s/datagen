# core/hf_search.py

from huggingface_hub import HfApi

api = HfApi()

def search_huggingface_datasets(keywords, max_per_keyword=10):
    """
    Search Hugging Face datasets using keywords.
    Returns metadata only (NO dataset downloads).
    """

    results = []
    seen = set()

    for keyword in keywords:
        try:
            datasets = api.list_datasets(search=keyword, limit=max_per_keyword)

            for ds in datasets:
                if ds.id in seen:
                    continue

                seen.add(ds.id)

                metadata_text = f"""
                {ds.id}
                {ds.description if ds.description else ""}
                {' '.join(ds.tags) if ds.tags else ""}
                """

                results.append({
                    "name": ds.id,
                    "metadata_text": metadata_text.strip()
                })

        except Exception:
            continue

    return results
