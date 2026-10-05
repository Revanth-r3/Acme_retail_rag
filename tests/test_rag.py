from services.rag_service import RAGService


def run_test(rag, question, expected_keywords, should_answer=True):
    print("\n" + "=" * 70)
    print(f"QUESTION: {question}")

    result = rag.answer(question)

    answer = result["answer"]
    sources = result["sources"]

    print(f"ANSWER: {answer}")
    print(f"SOURCES: {sources}")

    if should_answer:
        answer_lower = answer.lower()

        passed = all(
            keyword.lower() in answer_lower
            for keyword in expected_keywords
        )

        print(f"RESULT: {'PASS' if passed else 'FAIL'}")

        return passed

    else:
        expected_message = (
            "I cannot answer this based on the provided documents."
        )

        passed = (
            expected_message.lower() in answer.lower()
            and len(sources) == 0
        )

        print(f"RESULT: {'PASS' if passed else 'FAIL'}")

        return passed


def main():

    rag = RAGService(top_k=3)

    tests = [

        {
            "question": "What was the revenue of the South region?",
            "expected_keywords": ["4.2"],
            "should_answer": True
        },

        {
            "question": "Which product generated the highest revenue?",
            "expected_keywords": ["Laptop"],
            "should_answer": True
        },

        {
            "question": "What was the customer growth during Q1?",
            "expected_keywords": ["12%"],
            "should_answer": True
        },

        {
            "question": (
                "What was the South region revenue and "
                "how much of the target did it achieve?"
            ),
            "expected_keywords": ["4.2", "105%"],
            "should_answer": True
        },

        {
            "question": "What was the employee attrition rate?",
            "expected_keywords": [],
            "should_answer": False
        },

        {
            "question": "What was the Q1 profit margin?",
            "expected_keywords": [],
            "should_answer": False
        }
    ]

    passed = 0

    for test in tests:

        result = run_test(
            rag=rag,
            question=test["question"],
            expected_keywords=test["expected_keywords"],
            should_answer=test["should_answer"]
        )

        if result:
            passed += 1

    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed}/{len(tests)} tests passed")


if __name__ == "__main__":
    main()