from pipeline.ingestion import parse_document
from pipeline.embeddings import EmbeddingModel
from pipeline.vectorstore import VectorStore
from pipeline.document_tracker import DocumentTracker


def index_document(
    file_path,
    embedding_model,
    vector_store,
    tracker
):
    print(f"\nIndexing: {file_path}")

    try:

        # Check whether the document has already been indexed
        if tracker.is_unchanged(file_path):
            print("Document unchanged. Skipping re-indexing.")
            return

        # If the document was previously indexed but changed,
        # remove the old chunks before adding the new version.
        if tracker.is_indexed(file_path):
            print("Document changed. Removing old indexed chunks.")
            vector_store.delete_document(file_path)

        # 1. Parse document
        chunks = parse_document(file_path)

        print(f"Extracted chunks: {len(chunks)}")

        if not chunks:
            print("No content found.")
            return

        # 2. Create embeddings
        texts = [chunk.text for chunk in chunks]

        embeddings = embedding_model.encode(texts)

        print(f"Generated embeddings: {embeddings.shape}")

        # 3. Store in ChromaDB
        vector_store.add_documents(
            chunks,
            embeddings
        )

        # 4. Save the current file hash
        tracker.mark_indexed(file_path)

        print(
            f"Stored documents: {vector_store.count()}"
        )

    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")

    except ValueError as e:
        print(f"ERROR: Invalid or unsupported document: {e}")

    except Exception as e:
        print(
            f"ERROR: Failed to index {file_path}: {type(e).__name__}: {e}"
        )


if __name__ == "__main__":

    embedding_model = EmbeddingModel()
    vector_store = VectorStore()
    tracker = DocumentTracker()

    files = [
        "data/sales_q1.xlsx",
        "data/customer_sales.csv",
        "data/q1_business_review.pptx"
    ]

    for file_path in files:
        index_document(
            file_path=file_path,
            embedding_model=embedding_model,
            vector_store=vector_store,
            tracker=tracker
        )