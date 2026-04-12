def build_llm_context(datasets):

    context = {
        "datasets": []
    }

    for d in datasets:
        if d is None:
            continue

        context["datasets"].append({
            "dataset_id": d["dataset_id"],
            "columns": d["columns"],
            "sample_rows": d["rows"][:20]
        })

    return context