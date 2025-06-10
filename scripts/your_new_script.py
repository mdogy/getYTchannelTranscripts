import os
from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    """
    Retrieves the LLM API key from the environment variables.

    Raises:
        ValueError: If the LLM_API_KEY environment variable is not set.

    Returns:
        str: The LLM API key.
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError(
            "LLM_API_KEY environment variable not set. "
            "Please create a .env file and add your API key."
        )
    return api_key


if __name__ == "__main__":
    try:
        key = get_api_key()
        print("Successfully retrieved API key.")
    except ValueError as e:
        print(e)
