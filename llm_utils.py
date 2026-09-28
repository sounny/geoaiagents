import time
import logging
import json
import hashlib

_llm_cache = {}

def call_llm_with_retry(client, max_retries=3, **kwargs):
    """
    Call the LLM with retry logic for timeouts and malformed responses.
    """
    cache_key = None
    try:
        # Create a deterministic hash of the client and kwargs
        # Use default=str to handle objects that can't be easily JSON serialized
        serialized_kwargs = json.dumps(kwargs, sort_keys=True, default=str)
        # We include id(client) to avoid cache pollution across different test mocks or client instances
        cache_data = f"{id(client)}:{serialized_kwargs}"
        cache_key = hashlib.sha256(cache_data.encode('utf-8')).hexdigest()

        if cache_key in _llm_cache:
            logging.debug("LLM cache hit")
            return _llm_cache[cache_key]
    except Exception as e:
        # If serialization fails for any reason, skip caching
        logging.debug(f"Failed to create cache key: {e}")
        pass

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            if not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Malformed response: 'choices' missing or empty")

            # Cache the successful response
            if cache_key:
                _llm_cache[cache_key] = response

            return response
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"LLM call failed after {max_retries} attempts: {e}")
                raise ValueError(f"LLM call failed after {max_retries} attempts: {e}") from e
            logging.warning(f"LLM call failed on attempt {attempt + 1}: {e}. Retrying...")
            time.sleep(1)

    raise ValueError(f"LLM call failed after {max_retries} attempts")
