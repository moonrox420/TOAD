"""
Tests for RAG configuration module.
"""

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import (
    RAGConfig,
    EmbeddingConfig,
    DatasetConfig,
    IndexConfig,
    RetrievalConfig,
    PathConfig,
    get_config,
    reset_config,
    get_default_datasets,
)


class TestRAGConfig:
    """Tests for RAGConfig class."""
    
    def test_default_config_creation(self):
        """Test creating a config with defaults."""
        config = RAGConfig()
        
        assert config.embedding.model_name == "sentence-transformers/all-mpnet-base-v2"
        assert config.embedding.dimension == 768
        assert config.embedding.normalize is True
        assert config.embedding.batch_size == 32
    
    def test_default_datasets(self):
        """Test that default datasets are loaded."""
        config = RAGConfig()
        
        assert len(config.datasets) > 0
        assert any("Elite_GOD_Coder" in ds.name for ds in config.datasets)
    
    def test_get_enabled_datasets(self):
        """Test filtering enabled datasets."""
        config = RAGConfig()
        config.datasets[0].enabled = False
        
        enabled = config.get_enabled_datasets()
        
        assert len(enabled) == len(config.datasets) - 1
        assert config.datasets[0] not in enabled
    
    def test_ensure_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RAGConfig()
            config.paths.data_dir = Path(tmpdir) / "rag_data"
            config.paths.cache_dir = config.paths.data_dir / "cache"
            config.paths.index_dir = config.paths.data_dir / "index"
            
            config.ensure_directories()
            
            assert config.paths.data_dir.exists()
            assert config.paths.cache_dir.exists()
            assert config.paths.index_dir.exists()
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = RAGConfig()
        d = config.to_dict()
        
        assert "embedding" in d
        assert "datasets" in d
        assert "index" in d
        assert "retrieval" in d
        assert "paths" in d
        
        assert d["embedding"]["model"] == config.embedding.model_name
    
    def test_config_save_and_load(self):
        """Test saving and loading config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RAGConfig()
            config.paths.data_dir = Path(tmpdir)
            
            save_path = Path(tmpdir) / "test_config.yaml"
            config.save(save_path)
            
            assert save_path.exists()
            
            loaded = RAGConfig.load(save_path)
            
            assert loaded.embedding.model_name == config.embedding.model_name
            assert loaded.retrieval.top_k == config.retrieval.top_k
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "embedding": {
                "model": "test-model",
                "dimension": 512,
            },
            "retrieval": {
                "top_k": 10,
            },
        }
        
        config = RAGConfig.from_dict(data)
        
        assert config.embedding.model_name == "test-model"
        assert config.embedding.dimension == 512
        assert config.retrieval.top_k == 10


class TestEmbeddingConfig:
    """Tests for EmbeddingConfig."""
    
    def test_default_values(self):
        """Test default embedding config values."""
        config = EmbeddingConfig()
        
        assert config.model_name == "sentence-transformers/all-mpnet-base-v2"
        assert config.dimension == 768
        assert config.normalize is True
        assert config.batch_size == 32
    
    def test_custom_values(self):
        """Test custom embedding config values."""
        config = EmbeddingConfig(
            model_name="test-model",
            dimension=512,
            batch_size=64,
        )
        
        assert config.model_name == "test-model"
        assert config.dimension == 512
        assert config.batch_size == 64


class TestDatasetConfig:
    """Tests for DatasetConfig."""
    
    def test_default_values(self):
        """Test default dataset config values."""
        config = DatasetConfig(name="test/dataset")
        
        assert config.name == "test/dataset"
        assert config.enabled is True
        assert config.requires_auth is False
        assert config.split == "train"
    
    def test_custom_values(self):
        """Test custom dataset config values."""
        config = DatasetConfig(
            name="test/dataset",
            enabled=False,
            requires_auth=True,
            split="validation",
            max_samples=1000,
        )
        
        assert config.enabled is False
        assert config.requires_auth is True
        assert config.split == "validation"
        assert config.max_samples == 1000


class TestPathConfig:
    """Tests for PathConfig."""
    
    def test_index_path_property(self):
        """Test index_path property."""
        config = PathConfig()
        
        assert config.index_path == config.index_dir / config.index_file
    
    def test_metadata_path_property(self):
        """Test metadata_path property."""
        config = PathConfig()
        
        assert config.metadata_path == config.index_dir / config.metadata_file


class TestGlobalConfig:
    """Tests for global config functions."""
    
    def teardown_method(self):
        """Reset config after each test."""
        reset_config()
    
    def test_get_config_singleton(self):
        """Test that get_config returns singleton."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_get_config_reload(self):
        """Test that reload creates new config."""
        config1 = get_config()
        config2 = get_config(reload=True)
        
        assert config1 is not config2
    
    def test_reset_config(self):
        """Test resetting global config."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        
        assert config1 is not config2


class TestGetDefaultDatasets:
    """Tests for get_default_datasets function."""
    
    def test_returns_list(self):
        """Test that function returns a list."""
        datasets = get_default_datasets()
        
        assert isinstance(datasets, list)
        assert len(datasets) > 0
    
    def test_all_dataset_configs(self):
        """Test that all items are DatasetConfig."""
        datasets = get_default_datasets()
        
        for ds in datasets:
            assert isinstance(ds, DatasetConfig)
    
    def test_expected_datasets(self):
        """Test expected datasets are present."""
        datasets = get_default_datasets()
        names = [ds.name for ds in datasets]
        
        assert any("Elite_GOD_Coder" in n for n in names)
        assert any("dolphin-coder" in n for n in names)
