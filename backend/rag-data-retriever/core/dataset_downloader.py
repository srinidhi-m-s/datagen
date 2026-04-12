from datasets import load_dataset


def download_dataset(dataset_id):

    try:
        dataset = load_dataset(dataset_id)

        # Convert first split to list of rows
        split = list(dataset.keys())[0]

        data = dataset[split]

        # limit rows for LLM context
        rows = data.select(range(min(200, len(data))))

        return {
            "dataset_id": dataset_id,
            "columns": data.column_names,
            "rows": rows.to_list()
        }

    except Exception as e:
        print(f"Failed to load {dataset_id}: {e}")
        return None