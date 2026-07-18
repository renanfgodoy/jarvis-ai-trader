from __future__ import annotations

from core.prompts.models import PromptMessage, PromptSizeEstimate


def estimate_prompt_size(messages: tuple[PromptMessage, ...], *, characters_per_token: int) -> PromptSizeEstimate:
    text = "\n".join(message.content for message in messages)
    character_count = len(text)
    word_count = len(text.split())
    estimated_tokens = max(1, int((character_count + characters_per_token - 1) / characters_per_token))
    return PromptSizeEstimate(
        character_count=character_count,
        word_count=word_count,
        estimated_tokens=estimated_tokens,
        message_count=len(messages),
    )
