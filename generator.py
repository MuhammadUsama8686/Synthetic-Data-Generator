import json
import random
from typing import List
import asyncio
from openai import AsyncOpenAI
from loguru import logger
from models import DatasetEntry, DatasetType
from prompts import (
    KEYWORD_SYSTEM_PROMPT,
    KEYWORD_USER_PROMPT,
    ENTRY_RAW_DATASET_SYSTEM_PROMPT,
    ENTRY_RAW_DATASET_USER_PROMPT,
    ENTRY_INSTRUCT_SYSTEM_PROMPT,
    ENTRY_INSTRUCT_USER_PROMPT,
    ENTRY_PREFERENCE_SYSTEM_PROMPT,
    ENTRY_PREFERENCE_USER_PROMPT,
    ENTRY_SUMMARIZATION_SYSTEM_PROMPT,
    ENTRY_SUMMARIZATION_USER_PROMPT,
    ENTRY_SENTIMENT_SYSTEM_PROMPT,
    ENTRY_SENTIMENT_USER_PROMPT,
    ENTRY_CLASSIFICATION_SYSTEM_PROMPT,
    ENTRY_CLASSIFICATION_USER_PROMPT,
    LABELS_SYSTEM_PROMPT,
    LABELS_USER_PROMPT,
)
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_keywords(topic: str, language: str, num_samples: int, additional_description: str, domains: str) -> List[str]:
    prompt = KEYWORD_USER_PROMPT.format(
        num_keywords=num_samples,
        topic=topic,
        language=language,
        domains=domains,
        additional_description=additional_description
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": KEYWORD_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    return data["keywords"]

async def generate_entry(
    keyword: str, topic: str, language: str, dataset_type: DatasetType, additional_description: str, domains: str
) -> dict:
    prompts_map = {
        DatasetType.RAW: (ENTRY_RAW_DATASET_SYSTEM_PROMPT, ENTRY_RAW_DATASET_USER_PROMPT),
        DatasetType.INSTRUCTION: (ENTRY_INSTRUCT_SYSTEM_PROMPT, ENTRY_INSTRUCT_USER_PROMPT),
        DatasetType.PREFERENCE: (ENTRY_PREFERENCE_SYSTEM_PROMPT, ENTRY_PREFERENCE_USER_PROMPT),
        DatasetType.SUMMARIZATION: (ENTRY_SUMMARIZATION_SYSTEM_PROMPT, ENTRY_SUMMARIZATION_USER_PROMPT),
        DatasetType.SENTIMENT: (ENTRY_SENTIMENT_SYSTEM_PROMPT, ENTRY_SENTIMENT_USER_PROMPT),
        DatasetType.TEXT_CLASSIFICATION: (ENTRY_CLASSIFICATION_SYSTEM_PROMPT, ENTRY_CLASSIFICATION_USER_PROMPT),
    }
    system_prompt, user_prompt_template = prompts_map[dataset_type]

    extra_kwargs = {}
    if dataset_type == DatasetType.SENTIMENT:
        extra_kwargs["sentiment"] = random.choice(["positive", "negative", "neutral"])
    elif dataset_type == DatasetType.TEXT_CLASSIFICATION:
        labels = await generate_labels(topic, language, 3, additional_description, domains)  # Pass domains
        extra_kwargs["label"] = random.choice(labels)

    user_prompt = user_prompt_template.format(
        keyword=keyword,
        topic=topic,
        language=language,
        additional_description=additional_description,
        **extra_kwargs
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    try:
        entry = json.loads(content)
        DatasetEntry(**entry)  # Validate structure
        return entry
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Invalid JSON response for keyword {keyword}: {e}")
        return None

async def generate_labels(topic: str, language: str, num_labels: int, additional_description: str, domains: str) -> List[str]:
    prompt = LABELS_USER_PROMPT.format(
        num_labels=num_labels,
        topic=topic,
        language=language,
        domains=domains,  # Add domains
        additional_description=additional_description
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": LABELS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    return data["labels"]

async def generate_dataset(
    dataset_type: DatasetType,
    topic: str,
    language: str,
    num_samples: int,
    additional_description: str,
    domains: str
) -> List[dict]:
    logger.info(f"Generating {dataset_type} with {num_samples} samples")
    keywords = await generate_keywords(topic, language, num_samples, additional_description, domains)
    tasks = [
        generate_entry(keyword, topic, language, dataset_type, additional_description, domains)  # Pass domains
        for keyword in keywords
    ]
    entries = await asyncio.gather(*tasks)
    return [entry for entry in entries if entry is not None]