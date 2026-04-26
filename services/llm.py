import os
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 500,
    model: str = "claude-sonnet-4-0"
) -> str:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else "You are a helpful AI assistant.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # safer parsing
        if response.content and len(response.content) > 0:
            return response.content[0].text.strip()

        return "No response generated."

    except Exception as e:
        print(f"[LLM ERROR]: {str(e)}")
        return "LLM failed. Please try again."