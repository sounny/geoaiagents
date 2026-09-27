import time
import logging

def call_llm_with_retry(client, max_retries=3, **kwargs):
    """
    Call the LLM with retry logic for timeouts and malformed responses.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            if not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Malformed response: 'choices' missing or empty")
            if not hasattr(response.choices[0], 'message') or not response.choices[0].message:
                raise ValueError("Malformed response: 'message' missing or empty")
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                logging.exception(f"LLM call failed after {max_retries} attempts: {e}")
                raise
            logging.warning(f"LLM call failed on attempt {attempt + 1}: {e}. Retrying...", exc_info=True)
            time.sleep(1)

    raise ValueError(f"LLM call failed after {max_retries} attempts")
