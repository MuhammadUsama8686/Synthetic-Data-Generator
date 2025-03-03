from enum import Enum
from typing import List, Literal, Union
from pydantic import BaseModel, Field

class DatasetType(str, Enum):
    RAW = "Raw Dataset"
    INSTRUCTION = "Instruction Dataset"
    PREFERENCE = "Preference Dataset"
    SENTIMENT = "Sentiment Analysis Dataset"
    SUMMARIZATION = "Summarization Dataset"
    TEXT_CLASSIFICATION = "Text Classification Dataset"

class DatasetRequest(BaseModel):
    dataset_type: DatasetType = Field(..., description="Type of dataset to generate")
    topic: str = Field(..., min_length=1, description="Topic of the dataset")
    language: str = Field("English", min_length=1, description="Language of the dataset")
    num_samples: int = Field(..., ge=1, description="Number of samples to generate")
    additional_description: str = Field("", max_length=1000, description="Additional context")
    domains: str = Field(..., min_length=1, description="Comma-separated list of domains (e.g., 'Environmental Science, Renewable Energy')")

# Rest of the file (GeneratedText, InstructMessage, etc.) remains unchanged
class GeneratedText(BaseModel):
    text: str

class InstructMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class GeneratedInstructText(BaseModel):
    messages: List[InstructMessage]

class PreferencePrompt(BaseModel):
    role: Literal["system", "user"]
    content: str

class PreferenceChosen(BaseModel):
    role: Literal["assistant"]
    content: str

class PreferenceRejected(BaseModel):
    role: Literal["assistant"]
    content: str

class GeneratedPreferenceText(BaseModel):
    prompt: List[PreferencePrompt]
    chosen: List[PreferenceChosen]
    rejected: List[PreferenceRejected]

class GeneratedSummaryText(BaseModel):
    text: str
    summary: str

class GeneratedSentimentAnalysis(BaseModel):
    prompt: str
    label: Literal["positive", "negative", "neutral"]

class GeneratedTextClassification(BaseModel):
    prompt: str
    label: str

class DatasetEntry(BaseModel):
    keyword: str
    topic: str
    language: str
    generated_entry: Union[
        GeneratedText,
        GeneratedInstructText,
        GeneratedPreferenceText,
        GeneratedSummaryText,
        GeneratedSentimentAnalysis,
        GeneratedTextClassification,
    ]

class DatasetResponse(BaseModel):
    data: List[DatasetEntry]