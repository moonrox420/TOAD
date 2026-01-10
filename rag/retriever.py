"""
RAG retrieval module for querying the vector index.

Provides high-level retrieval functionality with result formatting
for integration with the code generation agent.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

import numpy as np

from .config import (
    RAGConfig,
    get_config,
    RAG_CONTEXT_TEMPLATE,
    EXAMPLE_TEMPLATE,
)
from .embedder import CodeEmbedder
from .indexer import RAGIndexBuilder, load_rag_index

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """
    A single retrieval result from the RAG index.
    
    Attributes:
        text: The full chunk text
        score: Similarity score (higher is better)
        rank: Rank in result list (1-indexed)
        source: Dataset source name
        instruction: Extracted instruction/task
        response: Extracted response/solution
    """
    text: str
    score: float
    rank: int
    source: str = ""
    instruction: str = ""
    response: str = ""
    
    def __post_init__(self):
        """Parse text to extract structured fields."""
        if self.text and not self.source:
            self._parse_chunk()
    
    def _parse_chunk(self) -> None:
        """Parse the chunk text to extract structured fields."""
        lines = self.text.split("\n")
        
        for i, line in enumerate(lines):
            if line.startswith("Source:"):
                self.source = line[7:].strip()
            elif line.startswith("Task:"):
                self.instruction = line[5:].strip()
            elif line.startswith("Elite Solution & Reasoning:"):
                # Everything after this is the response
                self.response = "\n".join(lines[i + 1:]).strip()
                break
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "score": self.score,
            "rank": self.rank,
            "source": self.source,
            "instruction": self.instruction,
            "response": self.response,
        }


class RAGRetriever:
    """
    High-level RAG retrieval interface.
    
    Provides functionality to query the FAISS index and format
    results for use in code generation.
    
    Example:
        >>> retriever = RAGRetriever()
        >>> results = retriever.retrieve("Create a REST API", top_k=5)
        >>> context = retriever.format_context(results)
    """
    
    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        index_builder: Optional[RAGIndexBuilder] = None,
        embedder: Optional[CodeEmbedder] = None,
    ):
        """
        Initialize the retriever.
        
        Args:
            config: RAG configuration. If None, uses global config.
            index_builder: Pre-loaded index builder. If None, loads from disk.
            embedder: Embedder for queries. If None, creates one.
        """
        self.config = config or get_config()
        self._index_builder = index_builder
        self._embedder = embedder
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        """Ensure the retriever is initialized with loaded index."""
        if self._initialized:
            return
        
        if self._index_builder is None:
            if not self.config.paths.index_path.exists():
                raise FileNotFoundError(
                    f"RAG index not found at {self.config.paths.index_path}. "
                    "Run 'python cli.py rag build' first."
                )
            self._index_builder = load_rag_index(self.config)
        
        if self._embedder is None:
            self._embedder = self._index_builder.embedder
        
        self._initialized = True
        logger.info("RAG retriever initialized")
    
    @property
    def index_builder(self) -> RAGIndexBuilder:
        """Get the index builder, initializing if needed."""
        self._ensure_initialized()
        return self._index_builder
    
    @property
    def embedder(self) -> CodeEmbedder:
        """Get the embedder, initializing if needed."""
        self._ensure_initialized()
        return self._embedder
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant coding examples for a query.
        
        Args:
            query: The search query (usually requirements text)
            top_k: Number of results to return. If None, uses config.
            min_score: Minimum similarity score. If None, uses config.
            
        Returns:
            List of RetrievalResult objects, sorted by score descending
        """
        self._ensure_initialized()
        
        top_k = top_k or self.config.retrieval.top_k
        min_score = min_score or self.config.retrieval.min_score
        
        logger.debug(f"Retrieving for query: {query[:100]}...")
        
        # Encode query
        query_embedding = self.embedder.encode_query(query)
        
        # Search index
        scores, indices, texts = self.index_builder.search(query_embedding, k=top_k)
        
        # Build results
        results = []
        for rank, (score, idx, text) in enumerate(zip(scores, indices, texts), start=1):
            if score >= min_score and text:
                results.append(RetrievalResult(
                    text=text,
                    score=float(score),
                    rank=rank,
                ))
        
        logger.info(f"Retrieved {len(results)} results for query")
        return results
    
    def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
    ) -> List[List[RetrievalResult]]:
        """
        Retrieve for multiple queries.
        
        Args:
            queries: List of query strings
            top_k: Number of results per query
            
        Returns:
            List of result lists, one per query
        """
        return [self.retrieve(q, top_k=top_k) for q in queries]
    
    def format_context(
        self,
        results: List[RetrievalResult],
        max_examples: Optional[int] = None,
    ) -> str:
        """
        Format retrieval results as context for code generation.
        
        Args:
            results: List of retrieval results
            max_examples: Maximum examples to include. If None, include all.
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        if max_examples:
            results = results[:max_examples]
        
        examples = []
        for result in results:
            example = EXAMPLE_TEMPLATE.format(
                rank=result.rank,
                score=result.score,
                source=result.source or "Unknown",
                task=result.instruction[:500] if result.instruction else "N/A",
                solution=result.response[:2000] if result.response else result.text[:2000],
            )
            examples.append(example)
        
        context = RAG_CONTEXT_TEMPLATE.format(
            examples="\n".join(examples)
        )
        
        return context
    
    def get_relevant_patterns(
        self,
        results: List[RetrievalResult],
    ) -> List[str]:
        """
        Extract relevant code patterns from retrieval results.
        
        Analyzes the retrieved solutions to identify common patterns
        that can inform code generation.
        
        Args:
            results: List of retrieval results
            
        Returns:
            List of detected pattern names
        """
        patterns = set()
        
        pattern_indicators = {
            "api": ["fastapi", "flask", "django", "@app.route", "@router"],
            "async": ["async def", "await", "asyncio"],
            "database": ["sqlalchemy", "session", "query", "model", "orm"],
            "testing": ["pytest", "unittest", "test_", "assert"],
            "error_handling": ["try:", "except", "raise", "Exception"],
            "logging": ["logging", "logger", "log."],
            "type_hints": ["-> ", ": str", ": int", ": List", ": Dict", "Optional["],
            "dataclass": ["@dataclass", "dataclasses"],
            "pydantic": ["BaseModel", "pydantic", "validator"],
            "authentication": ["jwt", "token", "auth", "password", "login"],
            "caching": ["cache", "redis", "lru_cache", "@cached"],
            "ml": ["sklearn", "tensorflow", "pytorch", "model.fit", "model.predict"],
        }
        
        for result in results:
            text = result.text.lower()
            for pattern, indicators in pattern_indicators.items():
                if any(ind.lower() in text for ind in indicators):
                    patterns.add(pattern)
        
        return list(patterns)
    
    def is_available(self) -> bool:
        """
        Check if the RAG index is available for retrieval.
        
        Returns:
            True if index exists and can be loaded
        """
        try:
            return self.config.paths.index_path.exists()
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get retriever statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.is_available():
            return {"available": False, "total_vectors": 0}
        
        try:
            self._ensure_initialized()
            stats = self.index_builder.get_stats()
            stats["available"] = True
            return stats
        except Exception as e:
            return {"available": False, "error": str(e)}


def create_retriever(config: Optional[RAGConfig] = None) -> RAGRetriever:
    """
    Factory function to create a RAGRetriever.
    
    Args:
        config: RAG configuration. If None, uses global config.
        
    Returns:
        Configured RAGRetriever instance
    """
    return RAGRetriever(config=config)


def retrieve_for_query(
    query: str,
    top_k: int = 5,
    config: Optional[RAGConfig] = None,
) -> List[RetrievalResult]:
    """
    Convenience function to retrieve results for a single query.
    
    Args:
        query: The search query
        top_k: Number of results
        config: RAG configuration
        
    Returns:
        List of retrieval results
    """
    retriever = RAGRetriever(config=config)
    return retriever.retrieve(query, top_k=top_k)
