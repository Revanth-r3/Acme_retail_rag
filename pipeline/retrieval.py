from pipeline.embeddings import EmbeddingModel
from pipeline.vectorstore import VectorStore
import time

class Retriever:
    def __init__(
        self,
        top_k=3,
        max_distance=0.8,
        embedding_model=None
    ):
        self.top_k = top_k
        self.max_distance = max_distance

        if embedding_model is not None:
            self.embedding_model = embedding_model
        else:
            self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore()

    def search(self, query):
        start_time = time.time()
        # Convert the user query into an embedding
        query_embedding = self.embedding_model.encode([query])

        # Search ChromaDB
        results = self.vector_store.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=self.top_k
        )

        retrieved_chunks = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        # Keep only sufficiently relevant results
        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            if distance <= self.max_distance:
                retrieved_chunks.append({
                    "text": document,
                    "metadata": metadata,
                    "distance": distance
                })

        retrieval_time = time.time() - start_time
        print(f"Retrieval time: {retrieval_time:.3f} seconds")

        return retrieved_chunks