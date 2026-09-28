import time
import logging

MAX_PROMPT_LENGTH = 1000000

def call_llm_with_retry(client, max_retries=3, **kwargs):
    """
    Call the LLM with retry logic for timeouts and malformed responses.
    """
    messages = kwargs.get("messages")
    if not messages:
        raise ValueError("Prompt cannot be empty or None")

    total_length = 0
    has_content = False
    for msg in messages:
        c = msg.get("content")
        if c:
            has_content = True
            total_length += len(str(c))

    if not has_content:
        raise ValueError("Prompt cannot be empty or None")

    if total_length > MAX_PROMPT_LENGTH:
        raise ValueError("Prompt is oversized")

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            if not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Malformed response: 'choices' missing or empty")
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"LLM call failed after {max_retries} attempts: {e}")
                raise ValueError(f"LLM call failed after {max_retries} attempts: {e}") from e
            logging.warning(f"LLM call failed on attempt {attempt + 1}: {e}. Retrying...")
            time.sleep(1)

    raise ValueError(f"LLM call failed after {max_retries} attempts")
