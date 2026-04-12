def schema_to_text(schema: dict) -> str:
    return " ".join([
        schema.get("domain", ""),
        schema.get("task", ""),
        schema.get("entity", ""),
        " ".join(schema.get("features", []))
    ])
