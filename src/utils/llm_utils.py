"""LLM utility functions for OpenAI API interactions."""

import os
from typing import List, Optional, Dict, Any
from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient:
    """Wrapper for OpenAI API calls with caching and error handling."""

    def __init__(self):
        """Initialize the LLM client."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            logger.warning("OpenAI API key not set. Please update .env file.")

        self.client = OpenAI(api_key=self.api_key)
        self.gpt4_model = os.getenv("GPT4_MODEL", "gpt-4-turbo-preview")
        self.gpt35_model = os.getenv("GPT35_MODEL", "gpt-3.5-turbo")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))

        # Simple cache for repeated queries
        self.cache: Dict[str, Any] = {}

    def call_gpt4(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call GPT-4 for complex reasoning tasks.

        Args:
            prompt: The user prompt
            system_message: Optional system message
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Model response text
        """
        cache_key = f"gpt4:{system_message}:{prompt}"
        if cache_key in self.cache:
            logger.debug("Returning cached GPT-4 response")
            return self.cache[cache_key]

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.gpt4_model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            result = response.choices[0].message.content
            self.cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"GPT-4 API call failed: {e}")
            raise

    def call_gpt35(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call GPT-3.5 for simpler tasks.

        Args:
            prompt: The user prompt
            system_message: Optional system message
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Model response text
        """
        cache_key = f"gpt35:{system_message}:{prompt}"
        if cache_key in self.cache:
            logger.debug("Returning cached GPT-3.5 response")
            return self.cache[cache_key]

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.gpt35_model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            result = response.choices[0].message.content
            self.cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"GPT-3.5 API call failed: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        cache_key = f"embed:{text[:100]}"
        if cache_key in self.cache:
            logger.debug("Returning cached embedding")
            return self.cache[cache_key]

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            self.cache[cache_key] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Embedding API call failed: {e}")
            raise

    def batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Batch embedding API call failed: {e}")
            raise

    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
        logger.info("LLM cache cleared")
