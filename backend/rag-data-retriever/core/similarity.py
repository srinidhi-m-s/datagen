from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(query_embedding, dataset_embeddings):
    return cosine_similarity([query_embedding], dataset_embeddings)[0]
