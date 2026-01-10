"""
FAISS vector index building and persistence.

Provides functionality to build, save, and load FAISS indexes
for efficient similarity search over coding embeddings.
"""

import logging
import pickle
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import numpy as np

from .config import RAGConfig, get_config
from .embedder import CodeEmbedder
from .datasets import CodingDatasetLoader

logger = logging.getLogger(__name__)


class RAGIndexBuilder:
    """
    Build and manage FAISS vector indexes for RAG retrieval.
    
    This class handles:
    - Creating FAISS indexes from embeddings
    - Adding vectors incrementally
    - Saving and loading index files
    - Index statistics and validation
    
    Example:
        >>> builder = RAGIndexBuilder()
        >>> builder.build_from_datasets()
        >>> builder.save()
    """
    
    def __init__(
        self,
        embedder: Optional[CodeEmbedder] = None,
        config: Optional[RAGConfig] = None,
    ):
        """
        Initialize the index builder.
        
        Args:
            embedder: CodeEmbedder instance. If None, creates one.
            config: RAG configuration. If None, uses global config.
        """
        self.config = config or get_config()
        self.embedder = embedder or CodeEmbedder(config=self.config)
        self._index = None
        self._metadata: List[str] = []  # Stores original texts
        self._faiss = None
    
    @property
    def faiss(self):
        """Lazy import of faiss module."""
        if self._faiss is None:
            try:
                import faiss
                self._faiss = faiss
            except ImportError as e:
                logger.error(
                    "faiss not installed. "
                    "Run: pip install faiss-cpu (or faiss-gpu for GPU support)"
                )
                raise ImportError(
                    "faiss is required for index building"
                ) from e
        return self._faiss
    
    @property
    def index(self):
        """Get or create the FAISS index."""
        if self._index is None:
            self._create_index()
        return self._index
    
    def _create_index(self) -> None:
        """Create a new FAISS index based on configuration."""
        dimension = self.embedder.get_dimension()
        index_type = self.config.index.index_type
        
        logger.info(f"Creating {index_type} index with dimension {dimension}")
        
        if index_type == "IndexFlatIP":
            # Exact search with inner product (cosine for normalized vectors)
            self._index = self.faiss.IndexFlatIP(dimension)
            
        elif index_type == "IndexFlatL2":
            # Exact search with L2 distance
            self._index = self.faiss.IndexFlatL2(dimension)
            
        elif index_type == "IndexIVFFlat":
            # Approximate search with inverted file
            quantizer = self.faiss.IndexFlatIP(dimension)
            self._index = self.faiss.IndexIVFFlat(
                quantizer,
                dimension,
                self.config.index.nlist,
                self.faiss.METRIC_INNER_PRODUCT,
            )
            
        elif index_type == "IndexHNSW":
            # Hierarchical Navigable Small World graph
            self._index = self.faiss.IndexHNSWFlat(dimension, 32)
            
        else:
            logger.warning(f"Unknown index type {index_type}, using IndexFlatIP")
            self._index = self.faiss.IndexFlatIP(dimension)
    
    def add_vectors(self, embeddings: np.ndarray, texts: List[str]) -> None:
        """
        Add vectors to the index.
        
        Args:
            embeddings: Numpy array of embeddings, shape (n, dimension)
            texts: List of original texts corresponding to embeddings
        """
        if len(embeddings) != len(texts):
            raise ValueError(
                f"Embeddings ({len(embeddings)}) and texts ({len(texts)}) "
                "must have the same length"
            )
        
        # Ensure float32 for FAISS
        embeddings = np.array(embeddings).astype("float32")
        
        # Train IVF index if needed
        if hasattr(self.index, "is_trained") and not self.index.is_trained:
            logger.info("Training IVF index...")
            self.index.train(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        self._metadata.extend(texts)
        
        logger.info(f"Added {len(embeddings)} vectors to index (total: {self.index.ntotal})")
    
    def build_from_texts(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
    ) -> None:
        """
        Build index from a list of texts.
        
        Args:
            texts: List of texts to index
            batch_size: Batch size for embedding. If None, uses config.
        """
        if not texts:
            logger.warning("No texts provided for indexing")
            return
        
        batch_size = batch_size or self.config.embedding.batch_size
        
        logger.info(f"Building index from {len(texts)} texts...")
        
        # Generate embeddings
        embeddings = self.embedder.encode(
            texts,
            batch_size=batch_size,
            show_progress=True,
        )
        
        # Add to index
        self.add_vectors(embeddings, texts)
    
    def build_from_datasets(
        self,
        max_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build index from configured HuggingFace datasets.
        
        Args:
            max_chunks: Maximum number of chunks to index. If None, index all.
            
        Returns:
            Statistics dictionary with loading and indexing info
        """
        self.config.ensure_directories()
        
        logger.info("Loading datasets for indexing...")
        loader = CodingDatasetLoader(config=self.config)
        
        texts = []
        for chunk in loader.load_all_chunks():
            texts.append(chunk.text)
            
            if max_chunks and len(texts) >= max_chunks:
                logger.info(f"Reached max_chunks limit: {max_chunks}")
                break
        
        stats = loader.get_statistics()
        
        if texts:
            self.build_from_texts(texts)
            stats["vectors_indexed"] = self.index.ntotal
        else:
            logger.warning("No chunks loaded from datasets")
            stats["vectors_indexed"] = 0
        
        return stats
    
    def save(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ) -> None:
        """
        Save index and metadata to files.
        
        Args:
            index_path: Path for index file. If None, uses config.
            metadata_path: Path for metadata file. If None, uses config.
        """
        index_path = index_path or self.config.paths.index_path
        metadata_path = metadata_path or self.config.paths.metadata_path
        
        # Ensure directories exist
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        self.faiss.write_index(self.index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save metadata
        with open(metadata_path, "wb") as f:
            pickle.dump(self._metadata, f)
        logger.info(f"Saved metadata ({len(self._metadata)} entries) to {metadata_path}")
    
    def load(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
    ) -> None:
        """
        Load index and metadata from files.
        
        Args:
            index_path: Path to index file. If None, uses config.
            metadata_path: Path to metadata file. If None, uses config.
        """
        index_path = index_path or self.config.paths.index_path
        metadata_path = metadata_path or self.config.paths.metadata_path
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        # Load FAISS index
        self._index = self.faiss.read_index(str(index_path))
        logger.info(f"Loaded FAISS index from {index_path} ({self._index.ntotal} vectors)")
        
        # Load metadata
        with open(metadata_path, "rb") as f:
            self._metadata = pickle.load(f)
        logger.info(f"Loaded metadata ({len(self._metadata)} entries) from {metadata_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            "total_vectors": self.index.ntotal if self._index else 0,
            "dimension": self.embedder.get_dimension(),
            "index_type": self.config.index.index_type,
            "metadata_count": len(self._metadata),
            "is_trained": getattr(self.index, "is_trained", True) if self._index else False,
        }
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Search the index for similar vectors.
        
        Args:
            query_embedding: Query vector of shape (dimension,) or (1, dimension)
            k: Number of results to return
            
        Returns:
            Tuple of (scores, indices, texts)
        """
        # Ensure 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Ensure float32
        query_embedding = query_embedding.astype("float32")
        
        # Search
        scores, indices = self.index.search(query_embedding, k)
        
        # Get corresponding texts
        texts = []
        for idx in indices[0]:
            if 0 <= idx < len(self._metadata):
                texts.append(self._metadata[idx])
            else:
                texts.append("")
        
        return scores[0], indices[0], texts


def build_rag_index(
    config: Optional[RAGConfig] = None,
    max_chunks: Optional[int] = None,
    save: bool = True,
) -> Dict[str, Any]:
    """
    Build the RAG index from configured datasets.
    
    This is the main entry point for building the index.
    
    Args:
        config: RAG configuration. If None, uses global config.
        max_chunks: Maximum chunks to index. If None, index all.
        save: Whether to save the index after building.
        
    Returns:
        Statistics dictionary
    """
    config = config or get_config()
    config.ensure_directories()
    
    print("\n" + "=" * 60)
    print("RAG INDEX BUILDER")
    print("=" * 60)
    print(f"Embedding model: {config.embedding.model_name}")
    print(f"Index type: {config.index.index_type}")
    print(f"Datasets: {len(config.get_enabled_datasets())} enabled")
    print("=" * 60 + "\n")
    
    builder = RAGIndexBuilder(config=config)
    stats = builder.build_from_datasets(max_chunks=max_chunks)
    
    if save and stats.get("vectors_indexed", 0) > 0:
        builder.save()
        config.save()
    
    print("\n" + "=" * 60)
    print("INDEX BUILD COMPLETE")
    print("=" * 60)
    print(f"Datasets loaded: {stats.get('datasets_loaded', 0)}")
    print(f"Datasets failed: {stats.get('datasets_failed', 0)}")
    print(f"Chunks created: {stats.get('chunks_created', 0)}")
    print(f"Vectors indexed: {stats.get('vectors_indexed', 0)}")
    print(f"Index saved to: {config.paths.index_path}")
    print("=" * 60 + "\n")
    
    return stats


def load_rag_index(
    config: Optional[RAGConfig] = None,
) -> RAGIndexBuilder:
    """
    Load an existing RAG index.
    
    Args:
        config: RAG configuration. If None, uses global config.
        
    Returns:
        RAGIndexBuilder with loaded index
    """
    config = config or get_config()
    builder = RAGIndexBuilder(config=config)
    builder.load()
    return builder
