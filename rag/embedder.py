"""
Embedding generation using sentence-transformers.

Provides high-quality embeddings for coding content using the
all-mpnet-base-v2 model (768 dimensions) with optional GPU acceleration.
"""

import logging
from typing import List, Optional, Union
import numpy as np

from .config import RAGConfig, get_config

logger = logging.getLogger(__name__)


class CodeEmbedder:
    """
    Generate embeddings for code content using sentence-transformers.
    
    Uses the all-mpnet-base-v2 model by default, which provides high-quality
    768-dimensional embeddings suitable for semantic search.
    
    Features:
        - Batch encoding with progress bar
        - L2 normalization for cosine similarity via inner product
        - GPU support when available
        - Memory-efficient processing
    
    Example:
        >>> embedder = CodeEmbedder()
        >>> embeddings = embedder.encode(["def hello(): pass", "print('world')"])
        >>> print(embeddings.shape)  # (2, 768)
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        config: Optional[RAGConfig] = None,
    ):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the sentence-transformers model.
                       If None, uses config default.
            device: Device to use ('cuda', 'cpu', or None for auto).
            config: RAG configuration. If None, uses global config.
        """
        self.config = config or get_config()
        self.model_name = model_name or self.config.embedding.model_name
        self._device = device or self.config.embedding.device
        self._model = None
        self._dimension: Optional[int] = None
    
    @property
    def model(self):
        """Lazy load the model on first access."""
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self) -> None:
        """Load the sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Determine device
            device = self._device
            if device is None:
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"
            
            self._model = SentenceTransformer(self.model_name, device=device)
            self._dimension = self._model.get_sentence_embedding_dimension()
            
            logger.info(
                f"Loaded {self.model_name} on {device}, "
                f"dimension: {self._dimension}"
            )
            
        except ImportError as e:
            logger.error(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
            raise ImportError(
                "sentence-transformers is required for embedding generation"
            ) from e
    
    def get_dimension(self) -> int:
        """
        Get the embedding dimension.
        
        Returns:
            The dimension of embeddings produced by this model
        """
        if self._dimension is None:
            # Force model load to get dimension
            _ = self.model
        return self._dimension or self.config.embedding.dimension
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
        normalize: Optional[bool] = None,
        show_progress: Optional[bool] = None,
    ) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding. If None, uses config default.
            normalize: Whether to L2-normalize embeddings. If None, uses config.
            show_progress: Whether to show progress bar. If None, uses config.
            
        Returns:
            Numpy array of embeddings, shape (n_texts, dimension)
        """
        # Handle single text
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([]).reshape(0, self.get_dimension())
        
        # Get parameters from config if not specified
        batch_size = batch_size or self.config.embedding.batch_size
        normalize = normalize if normalize is not None else self.config.embedding.normalize
        show_progress = show_progress if show_progress is not None else self.config.embedding.show_progress
        
        logger.info(f"Encoding {len(texts)} texts with batch_size={batch_size}")
        
        # Encode with the model
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )
        
        # Ensure float32 for FAISS compatibility
        embeddings = np.array(embeddings).astype("float32")
        
        logger.info(f"Generated embeddings shape: {embeddings.shape}")
        return embeddings
    
    def encode_query(
        self,
        query: str,
        normalize: Optional[bool] = None,
    ) -> np.ndarray:
        """
        Encode a single query for retrieval.
        
        Optimized for single query encoding without progress bar.
        
        Args:
            query: The query text to encode
            normalize: Whether to normalize. If None, uses config.
            
        Returns:
            1D numpy array of shape (dimension,)
        """
        embedding = self.encode(
            [query],
            batch_size=1,
            normalize=normalize,
            show_progress=False,
        )
        return embedding[0]
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        """
        Encode a batch of texts with memory-efficient chunking.
        
        For very large datasets, this method processes texts in chunks
        to avoid memory issues.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        batch_size = batch_size or self.config.embedding.batch_size
        
        all_embeddings = []
        total = len(texts)
        
        for i in range(0, total, batch_size):
            chunk = texts[i:i + batch_size]
            chunk_embeddings = self.encode(
                chunk,
                batch_size=batch_size,
                show_progress=False,
            )
            all_embeddings.append(chunk_embeddings)
            
            if (i + batch_size) % (batch_size * 10) == 0:
                logger.info(f"Encoded {min(i + batch_size, total)}/{total} texts")
        
        return np.vstack(all_embeddings)
    
    def similarity(
        self,
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray,
    ) -> np.ndarray:
        """
        Compute similarity scores between query and corpus.
        
        Uses inner product (equivalent to cosine similarity for normalized vectors).
        
        Args:
            query_embedding: Query embedding of shape (dimension,) or (1, dimension)
            corpus_embeddings: Corpus embeddings of shape (n, dimension)
            
        Returns:
            Similarity scores of shape (n,)
        """
        # Ensure 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Inner product for normalized vectors = cosine similarity
        scores = np.dot(corpus_embeddings, query_embedding.T).flatten()
        return scores


def create_embedder(config: Optional[RAGConfig] = None) -> CodeEmbedder:
    """
    Factory function to create a CodeEmbedder instance.
    
    Args:
        config: RAG configuration. If None, uses global config.
        
    Returns:
        Configured CodeEmbedder instance
    """
    return CodeEmbedder(config=config)
