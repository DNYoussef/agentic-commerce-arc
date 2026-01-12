"""
Pre-warm script for Replicate models.

Runs a lightweight image generation to warm caches before demos.
"""

import asyncio
import logging
import os

from tools.replicate import ReplicateClient, DEFAULT_MODEL

logger = logging.getLogger(__name__)

PROMPTS = [
    "a minimalist arc logo on a white background",
    "a sleek futuristic sneaker on a studio backdrop",
]


async def pre_warm():
    client = ReplicateClient()
    await client.initialize()

    if not client._initialized:
        logger.warning("Replicate client not initialized; skipping pre-warm.")
        return

    model = os.getenv("REPLICATE_WARM_MODEL", DEFAULT_MODEL)
    for prompt in PROMPTS:
        logger.info("Warming model %s with prompt: %s", model, prompt)
        await client.generate_image(prompt=prompt, style="minimalist", aspect_ratio="1:1", model=model)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(pre_warm())
