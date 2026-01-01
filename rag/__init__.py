"""
RAG (Retrieval-Augmented Generation) Module for TOAD Code Generation Agent.

This module provides functionality to build and query a vector index of elite
coding examples from HuggingFace datasets, enhancing code generation with
relevant context from proven solutions.

Components:
    - config: Configuration management for RAG settings
    - datasets: HuggingFace dataset loading and processing
    - embedder: Sentence-transformer embedding generation
    - indexer: FAISS vector index building and persistence
    - retriever: Query and retrieval logic
    - integration: CodeGenerationAgent integration

Usage:
    from rag import RAGEnhancedAgent, build_rag_index
    
    # Build index (one-time)
    build_rag_index()
    
    # Use enhanced agent
    agent = RAGEnhancedAgent()
    code = agent.generate_code("Create a REST API with authentication")
"""

from .config import RAGConfig, get_config
from .datasets import CodingDatasetLoader
from .embedder import CodeEmbedder
from .indexer import RAGIndexBuilder, build_rag_index
from .retriever import RAGRetriever, RetrievalResult
from .integration import RAGEnhancedAgent

__all__ = [
    "RAGConfig",
    "get_config",
    "CodingDatasetLoader",
    "CodeEmbedder",
    "RAGIndexBuilder",
    "build_rag_index",
    "RAGRetriever",
    "RetrievalResult",
    "RAGEnhancedAgent",
]

__version__ = "1.0.0"
