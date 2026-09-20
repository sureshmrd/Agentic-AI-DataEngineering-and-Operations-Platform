from rag.retrieval import search_knowledge_base


TEST_CASES = [
    {
        "query": "What does gross_revenue mean?",
        "expect_results": True,
    },
    {
        "query": "What should an operator check when a pipeline fails?",
        "expect_results": True,
    },
    {
        "query": "What is the stock price of Microsoft today?",
        "expect_results": False,
    },
    {
        "query": "What is the CEO of Olist?",
        "expect_results": False,
    },
]


def run_tests():
    passed = 0

    for test in TEST_CASES:
        result = search_knowledge_base(
            test["query"],
            top_k=5,
        )

        has_results = (
            result["result_count"] > 0
            and not result["low_confidence"]
        )

        expected = test["expect_results"]

        success = has_results == expected

        status = "PASS" if success else "FAIL"

        print(
            f"{status} | {test['query']}"
        )

        if success:
            passed += 1

    print()
    print(
        f"{passed}/{len(TEST_CASES)} retrieval tests passed."
    )


if __name__ == "__main__":
    run_tests()


#run : python -m rag.evaluate - for grp of test cases running.