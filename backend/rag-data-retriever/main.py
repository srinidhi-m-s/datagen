import json

from core.retriever import retrieve
from core.dataset_selector import select_top_datasets
from core.dataset_downloader import download_dataset
from core.context_builder import build_llm_context

# load schema
with open("schemas/sample_schema.json") as f:
    schema = json.load(f)

# step 1 retrieve datasets
results = retrieve(schema)

# step 2 select best
top_datasets = select_top_datasets(results)

# step 3 download
downloaded = [
    download_dataset(d["dataset_id"])
    for d in top_datasets
]

# step 4 build llm context
llm_context = build_llm_context(downloaded)

# save
with open("storage/llm_context.json", "w") as f:
    json.dump(llm_context, f, indent=2)

print("Datasets ready for LLM")