from pipeline.retrieval import Retriever
from pipeline.generation import Generator


class RAGService:

    def __init__(self, top_k=3, embedding_model=None):

        self.retriever = Retriever(
            top_k=top_k,
            embedding_model=embedding_model
        )

        self.generator = Generator()

    def answer(self, query):

        retrieved_chunks = self.retriever.search(query)

        # No relevant context
        if not retrieved_chunks:
            return {
                "answer": "I cannot answer this based on the provided documents.",
                "sources": []
            }

        # Generate answer using retrieved context
        answer = self.generator.generate(
            query=query,
            context_chunks=retrieved_chunks
        )

        no_answer_message = (
            "I cannot answer this based on the provided documents."
        )

        # Handle no-answer response
        no_answer_indicators = [
            "cannot answer",
            "cannot calculate",
            "cannot determine",
            "not enough information",
            "insufficient information",
            "provided information is not enough",
            "provided documents do not contain"
        ]

        if any(
            indicator in answer.lower()
            for indicator in no_answer_indicators
        ):
            return {
                "answer": no_answer_message,
                "sources": []
            }

        # -------------------------------------------------
        # Build source metadata from retrieved chunks
        # -------------------------------------------------

        sources = []

        for chunk in retrieved_chunks:

            metadata = chunk["metadata"]

            source_info = {
                "source": metadata.get("source"),
                "file_type": metadata.get("file_type")
            }

            if metadata.get("sheet"):
                source_info["sheet"] = metadata["sheet"]

            if metadata.get("row"):
                source_info["row"] = metadata["row"]

            if metadata.get("slide"):
                source_info["slide"] = metadata["slide"]

            if metadata.get("title"):
                source_info["title"] = metadata["title"]

            sources.append(source_info)

        return {
            "answer": answer.strip(),
            "sources": sources
        }