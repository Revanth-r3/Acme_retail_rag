import ollama
import time


class Generator:

    def __init__(self, model_name="llama3.2:latest"):
        self.model_name = model_name

    def generate(self, query, context_chunks):

        context_parts = []

        for i, chunk in enumerate(context_chunks, start=1):

            context_parts.append(
                f"[SOURCE_{i}]\n"
                f"{chunk['text']}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are an Acme Retail document question-answering assistant.

Answer the user's question ONLY using the provided context.

Strict rules:

1. Use only information explicitly present in the context.
2. Do not use outside knowledge.
3. Do not make assumptions.
4. Do not invent facts.
5. Give a concise answer.
6. Do not mention source numbers.
7. Do not write SOURCE_1, SOURCE_2, or any other source labels.
8. Do not write ANSWER: or SOURCES:.
9. If the context does not contain enough information to answer the question,
   respond with exactly:

I cannot answer this based on the provided documents.

Context:

{context}

Question:

{query}
"""

        try:

            start_time = time.time()

            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            generation_time = time.time() - start_time

            print(
                f"Generation time: {generation_time:.3f} seconds"
            )

            return response["message"]["content"].strip()

        except Exception as e:

            print(
                f"ERROR: LLM generation failed: "
                f"{type(e).__name__}: {e}"
            )

            return (
                "I cannot answer this based on the provided documents."
            )