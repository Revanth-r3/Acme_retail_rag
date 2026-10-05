import json
import math

import ollama

from services.rag_service import RAGService


DATASET_PATH = "evaluation/eval_dataset.json"
JUDGE_MODEL = "llama3.2:latest"


def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def source_matches(expected_source, retrieved_metadata):
    if expected_source["source"] != retrieved_metadata.get("source"):
        return False

    if "slide" in expected_source:
        return expected_source["slide"] == retrieved_metadata.get("slide")

    if "sheet" in expected_source:
        return (
            expected_source["sheet"] == retrieved_metadata.get("sheet")
            and expected_source["row"] == retrieved_metadata.get("row")
        )

    return True


def calculate_context_precision(retrieved_chunks, item):
    acceptable_sources = item["acceptable_sources"]

    if not retrieved_chunks:
        return 0.0

    relevant_count = 0

    for chunk in retrieved_chunks:
        if any(
            source_matches(expected_source, chunk["metadata"])
            for expected_source in acceptable_sources
        ):
            relevant_count += 1

    return relevant_count / len(retrieved_chunks)


def calculate_context_recall(retrieved_chunks, item):
    acceptable_sources = item["acceptable_sources"]

    if not acceptable_sources:
        return None

    matched_sources = 0

    for expected_source in acceptable_sources:
        found = any(
            source_matches(expected_source, chunk["metadata"])
            for chunk in retrieved_chunks
        )

        if found:
            matched_sources += 1

    if item.get("required_all_sources", False):
        return matched_sources / len(acceptable_sources)

    return 1.0 if matched_sources > 0 else 0.0


def calculate_context_relevance(
    question,
    retrieved_chunks,
    embedding_model
):
    if not retrieved_chunks:
        return 0.0

    question_embedding = embedding_model.encode([question])[0]

    similarities = []

    for chunk in retrieved_chunks:
        chunk_embedding = embedding_model.encode([chunk["text"]])[0]

        similarity = cosine_similarity(
            question_embedding,
            chunk_embedding
        )

        similarities.append(similarity)

    return sum(similarities) / len(similarities)


def parse_judge_score(response_text):
    try:
        data = json.loads(response_text)
        score = data.get("score")

        if score in [0, 1]:
            return float(score)

    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    return 0.0


def judge_faithfulness(question, answer, context):
    prompt = f"""
You are evaluating a RAG system.

Determine whether the answer is fully supported by the provided context.

Question:
{question}

Context:
{context}

Answer:
{answer}

Evaluation rules:

- Score 1 if every factual claim in the answer is supported by the context.
- Score 0 if the answer contains unsupported, invented, or contradictory information.
- If the answer says:
  "I cannot answer this based on the provided documents."
  and the context does not contain the required information, score 1.
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations.

Required format:
{{"score": 1}}

or

{{"score": 0}}
"""

    try:
        response = ollama.chat(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_response = response["message"]["content"].strip()

        return parse_judge_score(raw_response)

    except Exception as e:
        print(f"Faithfulness judge error: {e}")
        return 0.0


def judge_answer_relevancy(question, answer):
    prompt = f"""
You are evaluating a RAG system.

Determine whether the answer directly and appropriately answers the question.

Question:
{question}

Answer:
{answer}

Evaluation rules:

- Score 1 if the answer directly addresses the question.
- Score 0 if the answer is irrelevant or does not address the question.
- If the question cannot be answered from the documents and the answer says:
  "I cannot answer this based on the provided documents."
  score 1.
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations.

Required format:
{{"score": 1}}

or

{{"score": 0}}
"""

    try:
        response = ollama.chat(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_response = response["message"]["content"].strip()

        return parse_judge_score(raw_response)

    except Exception as e:
        print(f"Answer relevancy judge error: {e}")
        return 0.0


def build_context(retrieved_chunks):
    context_parts = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"[SOURCE_{index}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context_parts)


def generate_answer_from_chunks(rag, question, retrieved_chunks):
    if not retrieved_chunks:
        return "I cannot answer this based on the provided documents."

    generated_response = rag.generator.generate(
        query=question,
        context_chunks=retrieved_chunks
    )

    answer = generated_response.strip()

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
        return "I cannot answer this based on the provided documents."

    return answer

def calculate_answer_correctness(answer, item):
    expected_answer = item.get("expected_answer")

    if not item.get("answerable", True):
        expected_fallback = "I cannot answer this based on the provided documents."
        return 1.0 if answer.strip().lower() == expected_fallback.lower() else 0.0

    if not expected_answer:
        return 0.0

    answer_lower = answer.lower()
    expected_lower = expected_answer.lower()

    expected_parts = [
        part.strip()
        for part in expected_lower.replace(" and ", "|").split("|")
        if part.strip()
    ]

    return 1.0 if all(part in answer_lower for part in expected_parts) else 0.0



def main():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    rag = RAGService(top_k=3)
    
    embedding_model = rag.retriever.embedding_model

    results = []

    print("\n" + "=" * 80)
    print("RAG EVALUATION")
    print("=" * 80)

    for item in dataset:
        question = item["question"]

        print("\n" + "-" * 80)
        print(f"ID: {item['id']}")
        print(f"QUESTION: {question}")

        # Retrieve ONCE
        retrieved_chunks = rag.retriever.search(question)

        precision = calculate_context_precision(
            retrieved_chunks,
            item
        )

        recall = calculate_context_recall(retrieved_chunks, item)

        relevance = calculate_context_relevance(
            question,
            retrieved_chunks,
            embedding_model
        )


        answer = generate_answer_from_chunks(rag, question, retrieved_chunks)
        context = build_context(retrieved_chunks)
        answer_correctness = calculate_answer_correctness(answer, item)
        faithfulness = judge_faithfulness(question, answer, context)
        answer_relevancy = judge_answer_relevancy(question, answer)

        result = {
            "id": item["id"],
            "context_precision": precision,
            "context_recall": recall,
            "context_relevance": relevance,
            "answer_correctness": answer_correctness,
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy
        }

        results.append(result)

        print(f"Retrieved chunks: {len(retrieved_chunks)}")
        print(f"Answer: {answer}")
        print(f"Context Precision: {precision:.3f}")

        if recall is None:
            print("Context Recall:    N/A")
        else:
            print(f"Context Recall:    {recall:.3f}")

        print(f"Context Relevance: {relevance:.3f}")
        print(f"Answer Correctness: {answer_correctness:.3f}")
        print(f"Faithfulness:      {faithfulness:.3f}")
        print(f"Answer Relevancy:  {answer_relevancy:.3f}")

    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    avg_precision = sum(
        r["context_precision"]
        for r in results
    ) / len(results)

    recall_values = [
        r["context_recall"]
        for r in results
        if r["context_recall"] is not None
    ]

    avg_recall = (
        sum(recall_values) / len(recall_values)
        if recall_values
        else 0.0
    )

    avg_relevance = sum(
        r["context_relevance"]
        for r in results
    ) / len(results)

    avg_faithfulness = sum(
        r["faithfulness"]
        for r in results
    ) / len(results)

    avg_answer_relevancy = sum(
        r["answer_relevancy"]
        for r in results
    ) / len(results)
    avg_answer_correctness = (
        sum(r["answer_correctness"] for r in results) / len(results)
    )

    print(f"Average Answer Correctness: {avg_answer_correctness:.3f}")

    print(f"Average Context Precision: {avg_precision:.3f}")
    print(f"Average Context Recall:    {avg_recall:.3f}")
    print(f"Average Context Relevance: {avg_relevance:.3f}")
    print(f"Average Faithfulness:      {avg_faithfulness:.3f}")
    print(f"Average Answer Relevancy:  {avg_answer_relevancy:.3f}")


if __name__ == "__main__":
    main()