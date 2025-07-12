from query_data import query_rag
import ollama

EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Is the actual response close enough to the expected response? 
"""


def test_bee_movie_questions():
    assert query_and_validate(
        question="Who is the main character of the Bee Movie?",
        expected_response="Barry B Benson",
    )


def test_rocky_questions():
    assert query_and_validate(
        question="Who does Rocky fight?",
        expected_response="Apollo Creed",
    )


def query_and_validate(question: str, expected_response: str):
    response_text = query_rag(question)
    prompt = EVAL_PROMPT.format(
        expected_response=expected_response, actual_response=response_text
    )

    client = ollama.Client()
    model = "gemma3"
    response = client.generate(model=model, prompt=prompt)
    response_text = response.response
    response_stripped = response_text.strip().lower()

    print(prompt)

    if "true" in response_stripped:
        # Print response in Green if it is correct.
        print("\033[92m" + f"Response: {response_stripped}" + "\033[0m")
        return True
    elif "false" in response_stripped:
        # Print response in Red if it is incorrect.
        print("\033[91m" + f"Response: {response_stripped}" + "\033[0m")
        return False
    else:
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false'."
        )