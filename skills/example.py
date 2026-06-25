"""Example skill domain — demonstrates the skill registration pattern.

Skills:
- echo       : returns whatever input is passed in
- word_count : counts words and characters in a text string

No external dependencies — works out of the box with no API keys.
Copy this file, rename it, and replace these skills with your own.
"""

from typing import Any, Dict

from registry import SkillResult, get_registry


async def echo(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Echo the input back as-is. Useful for testing connectivity."""
    return SkillResult(success=True, output={"echo": input})


async def word_count(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Count words and characters in the provided text.

    Input: { "text": "string to analyse" }
    """
    text = input.get("text", "")
    if not isinstance(text, str):
        return SkillResult(success=False, output={}, error="'text' must be a string")

    words = text.split()
    return SkillResult(success=True, output={
        "word_count": len(words),
        "char_count": len(text),
        "char_count_no_spaces": len(text.replace(" ", "")),
    })


def register_all() -> None:
    registry = get_registry()

    registry.register(
        "example",
        "echo",
        echo,
        schema={
            "type": "object",
            "additionalProperties": True,
            "description": "Any JSON object — it will be echoed back.",
        },
    )

    registry.register(
        "example",
        "word_count",
        word_count,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "The text to analyse."},
            },
        },
    )
