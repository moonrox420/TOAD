"""
Configuration management for the RAG system.

Provides centralized configuration for embedding models, datasets,
index settings, and file paths. Supports environment variable overrides.
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

import yaml

logger = logging.getLogger(__name__)

# Base directory for RAG data (relative to TOAD directory)
BASE_DIR = Path(__file__).parent.parent
RAG_DATA_DIR = BASE_DIR / "rag_data"


@dataclass
class DatasetConfig:
    """Configuration for a single dataset."""
    name: str
    enabled: bool = True
    requires_auth: bool = False
    split: str = "train"
    max_samples: Optional[int] = None


@dataclass
class EmbeddingConfig:
    """Configuration for the embedding model."""
    model_name: str = "sentence-transformers/all-mpnet-base-v2"
    dimension: int = 768
    normalize: bool = True
    batch_size: int = 32
    show_progress: bool = True
    device: Optional[str] = None  # Auto-detect if None


@dataclass
class IndexConfig:
    """Configuration for the FAISS index."""
    index_type: str = "IndexFlatIP"  # Inner product for normalized embeddings
    metric: str = "inner_product"
    nlist: int = 100  # For IVF indexes
    nprobe: int = 10  # For IVF indexes


@dataclass
class RetrievalConfig:
    """Configuration for retrieval settings."""
    top_k: int = 5
    min_score: float = 0.3
    include_metadata: bool = True


@dataclass
class PathConfig:
    """Configuration for file paths."""
    data_dir: Path = field(default_factory=lambda: RAG_DATA_DIR)
    cache_dir: Path = field(default_factory=lambda: RAG_DATA_DIR / "cache")
    index_dir: Path = field(default_factory=lambda: RAG_DATA_DIR / "index")
    index_file: str = "faiss_index.bin"
    metadata_file: str = "metadata.pkl"
    config_file: str = "config.yaml"
    
    @property
    def index_path(self) -> Path:
        return self.index_dir / self.index_file
    
    @property
    def metadata_path(self) -> Path:
        return self.index_dir / self.metadata_file
    
    @property
    def config_path(self) -> Path:
        return self.data_dir / self.config_file


@dataclass
class RAGConfig:
    """
    Main configuration class for the RAG system.
    
    Attributes:
        embedding: Embedding model configuration
        datasets: List of dataset configurations
        index: FAISS index configuration
        retrieval: Retrieval settings
        paths: File path configuration
    """
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    datasets: List[DatasetConfig] = field(default_factory=list)
    index: IndexConfig = field(default_factory=IndexConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    
    def __post_init__(self):
        """Initialize default datasets if none provided."""
        if not self.datasets:
            self.datasets = get_default_datasets()
    
    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        self.paths.data_dir.mkdir(parents=True, exist_ok=True)
        self.paths.cache_dir.mkdir(parents=True, exist_ok=True)
        self.paths.index_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured RAG directories exist at {self.paths.data_dir}")
    
    def get_enabled_datasets(self) -> List[DatasetConfig]:
        """Return only enabled datasets."""
        return [ds for ds in self.datasets if ds.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            "embedding": {
                "model": self.embedding.model_name,
                "dimension": self.embedding.dimension,
                "normalize": self.embedding.normalize,
                "batch_size": self.embedding.batch_size,
            },
            "datasets": [
                {
                    "name": ds.name,
                    "enabled": ds.enabled,
                    "requires_auth": ds.requires_auth,
                    "split": ds.split,
                    "max_samples": ds.max_samples,
                }
                for ds in self.datasets
            ],
            "index": {
                "type": self.index.index_type,
                "metric": self.index.metric,
            },
            "retrieval": {
                "top_k": self.retrieval.top_k,
                "min_score": self.retrieval.min_score,
            },
            "paths": {
                "data_dir": str(self.paths.data_dir),
                "cache_dir": str(self.paths.cache_dir),
                "index_dir": str(self.paths.index_dir),
            },
        }
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to YAML file."""
        save_path = path or self.paths.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
        logger.info(f"Saved RAG config to {save_path}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RAGConfig":
        """Create config from dictionary."""
        embedding = EmbeddingConfig(
            model_name=data.get("embedding", {}).get("model", "sentence-transformers/all-mpnet-base-v2"),
            dimension=data.get("embedding", {}).get("dimension", 768),
            normalize=data.get("embedding", {}).get("normalize", True),
            batch_size=data.get("embedding", {}).get("batch_size", 32),
        )
        
        datasets = [
            DatasetConfig(
                name=ds["name"],
                enabled=ds.get("enabled", True),
                requires_auth=ds.get("requires_auth", False),
                split=ds.get("split", "train"),
                max_samples=ds.get("max_samples"),
            )
            for ds in data.get("datasets", [])
        ]
        
        index = IndexConfig(
            index_type=data.get("index", {}).get("type", "IndexFlatIP"),
            metric=data.get("index", {}).get("metric", "inner_product"),
        )
        
        retrieval = RetrievalConfig(
            top_k=data.get("retrieval", {}).get("top_k", 5),
            min_score=data.get("retrieval", {}).get("min_score", 0.3),
        )
        
        paths_data = data.get("paths", {})
        paths = PathConfig(
            data_dir=Path(paths_data.get("data_dir", RAG_DATA_DIR)),
            cache_dir=Path(paths_data.get("cache_dir", RAG_DATA_DIR / "cache")),
            index_dir=Path(paths_data.get("index_dir", RAG_DATA_DIR / "index")),
        )
        
        return cls(
            embedding=embedding,
            datasets=datasets,
            index=index,
            retrieval=retrieval,
            paths=paths,
        )
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> "RAGConfig":
        """Load configuration from YAML file."""
        load_path = path or (RAG_DATA_DIR / "config.yaml")
        if load_path.exists():
            with open(load_path, "r") as f:
                data = yaml.safe_load(f)
            logger.info(f"Loaded RAG config from {load_path}")
            return cls.from_dict(data)
        else:
            logger.info(f"No config file found at {load_path}, using defaults")
            return cls()


def get_default_datasets() -> List[DatasetConfig]:
    """
    Return the default list of elite coding datasets.
    
    These datasets contain high-quality coding examples for RAG retrieval.
    """
    return [
        DatasetConfig(
            name="gss1147/Elite_GOD_Coder_100k",
            enabled=True,
            requires_auth=False,
        ),
        DatasetConfig(
            name="QuixiAI/dolphin-coder",
            enabled=True,
            requires_auth=True,  # Gated dataset
        ),
        DatasetConfig(
            name="nvidia/OpenCodeInstruct",
            enabled=True,
            requires_auth=False,
        ),
        DatasetConfig(
            name="HuggingFaceH4/codealpaca_20k",
            enabled=True,
            requires_auth=False,
        ),
    ]


# Global configuration instance
_config: Optional[RAGConfig] = None


def get_config(reload: bool = False) -> RAGConfig:
    """
    Get the global RAG configuration instance.
    
    Args:
        reload: If True, reload config from file even if already loaded
        
    Returns:
        RAGConfig instance
    """
    global _config
    
    if _config is None or reload:
        # Check for environment variable overrides
        config_path = os.environ.get("RAG_CONFIG_PATH")
        if config_path:
            _config = RAGConfig.load(Path(config_path))
        else:
            _config = RAGConfig.load()
        
        # Apply environment variable overrides
        if os.environ.get("RAG_EMBEDDING_MODEL"):
            _config.embedding.model_name = os.environ["RAG_EMBEDDING_MODEL"]
        
        if os.environ.get("RAG_TOP_K"):
            _config.retrieval.top_k = int(os.environ["RAG_TOP_K"])
        
        if os.environ.get("RAG_DATA_DIR"):
            _config.paths.data_dir = Path(os.environ["RAG_DATA_DIR"])
            _config.paths.cache_dir = _config.paths.data_dir / "cache"
            _config.paths.index_dir = _config.paths.data_dir / "index"
    
    return _config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None


# Chunk template for creating indexed documents
CHUNK_TEMPLATE = """ELITE CODING REFERENCE
Source: {source}
Task: {instruction}
Elite Solution & Reasoning: {response}"""

# Context template for RAG-enhanced generation
RAG_CONTEXT_TEMPLATE = """
=== RELEVANT CODING EXAMPLES ===

{examples}

=== END EXAMPLES ===
"""

EXAMPLE_TEMPLATE = """
--- Example {rank} (Relevance: {score:.2f}) ---
Source: {source}
Task: {task}
Solution:
{solution}
"""
