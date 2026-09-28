import time
import logging

def call_llm_with_retry(client, max_retries=3, **kwargs):
    """
    Call the LLM with retry logic for timeouts and malformed responses.
    """
    messages = kwargs.get('messages')
    if messages is None:
        raise ValueError("Prompt cannot be None")
    if not messages:
        raise ValueError("Prompt cannot be empty")

    if len(str(messages)) > 1000000:
        raise ValueError("Prompt is oversized (length > 1,000,000 characters)")

    is_whitespace_only = True
    for msg in messages:
        content = msg.get('content', '')
        if content is None:
            continue
        if isinstance(content, str):
            if content.strip() != '':
                is_whitespace_only = False
                break
        else:
            is_whitespace_only = False
            break

    if is_whitespace_only:
        raise ValueError("Prompt cannot be whitespace-only")
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
