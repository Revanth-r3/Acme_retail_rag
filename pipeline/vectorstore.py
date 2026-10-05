import chromadb


class VectorStore:
    def __init__(self, path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)

        self.collection = self.client.get_or_create_collection(
            name="acme_documents"
        )

    def add_documents(self, chunks, embeddings):
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            source = chunk.metadata.get("source", "unknown")

            safe_source = source.replace("\\", "/").replace("/", "_")

            chunk_id = f"{safe_source}_chunk_{i}"

            ids.append(chunk_id)
            documents.append(chunk.text)
            metadatas.append(chunk.metadata)

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    def delete_document(self, file_path):
        """
        Delete all indexed chunks belonging to a specific source file.
        """

        self.collection.delete(
            where={
                "source": file_path
            }
        )

    def count(self):
        return self.collection.count()