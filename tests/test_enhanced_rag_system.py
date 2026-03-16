"""
Tests for enhanced_rag_system.py – local GGUF model support.

These tests exercise the public API without requiring llama-cpp-python or a
real .gguf file to be present on the test machine.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import LLMConfig, RAGConfig, get_config, reset_config, DEFAULT_HF_MODEL_NAME
from enhanced_rag_system import (
    EnhancedRAGSystem,
    HFHostedModel,
    LocalGGUFModel,
    create_enhanced_rag_system,
)


# ---------------------------------------------------------------------------
# LLMConfig tests
# ---------------------------------------------------------------------------

class TestLLMConfig:
    """Tests for the new LLMConfig dataclass in rag/config.py."""

    def test_default_values(self):
        cfg = LLMConfig()
        assert cfg.local_model_path is None
        assert cfg.hf_model_name == DEFAULT_HF_MODEL_NAME
        assert cfg.n_ctx == 4096
        assert cfg.n_gpu_layers == 0
        assert cfg.max_tokens == 2048
        assert cfg.temperature == 0.2

    def test_custom_local_path(self):
        cfg = LLMConfig(local_model_path="/tmp/model.gguf")
        assert cfg.local_model_path == "/tmp/model.gguf"

    def test_rag_config_includes_llm(self):
        config = RAGConfig()
        assert hasattr(config, "llm")
        assert isinstance(config.llm, LLMConfig)

    def test_rag_config_to_dict_includes_llm(self):
        config = RAGConfig()
        d = config.to_dict()
        assert "llm" in d
        assert "local_model_path" in d["llm"]
        assert "hf_model_name" in d["llm"]

    def test_rag_config_from_dict_with_llm(self):
        data = {
            "llm": {
                "local_model_path": "/tmp/test.gguf",
                "n_ctx": 2048,
                "temperature": 0.5,
            }
        }
        config = RAGConfig.from_dict(data)
        assert config.llm.local_model_path == "/tmp/test.gguf"
        assert config.llm.n_ctx == 2048
        assert config.llm.temperature == 0.5

    def test_rag_config_save_load_roundtrip_with_llm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RAGConfig()
            config.llm.local_model_path = "/tmp/my_model.gguf"
            config.llm.n_ctx = 8192

            save_path = Path(tmpdir) / "config.yaml"
            config.save(save_path)

            loaded = RAGConfig.load(save_path)
            assert loaded.llm.local_model_path == "/tmp/my_model.gguf"
            assert loaded.llm.n_ctx == 8192


class TestLocalModelPathEnvVar:
    """Tests for LOCAL_MODEL_PATH environment variable support."""

    def teardown_method(self):
        reset_config()
        os.environ.pop("LOCAL_MODEL_PATH", None)

    def test_env_var_sets_local_model_path(self):
        os.environ["LOCAL_MODEL_PATH"] = "/tmp/env_model.gguf"
        config = get_config(reload=True)
        assert config.llm.local_model_path == "/tmp/env_model.gguf"

    def test_no_env_var_leaves_path_none(self):
        os.environ.pop("LOCAL_MODEL_PATH", None)
        config = get_config(reload=True)
        assert config.llm.local_model_path is None


# ---------------------------------------------------------------------------
# HFHostedModel tests
# ---------------------------------------------------------------------------

class TestHFHostedModel:
    """Tests for the HFHostedModel stub."""

    def test_generate_returns_empty_string(self):
        cfg = LLMConfig()
        model = HFHostedModel(cfg)
        assert model.generate("hello") == ""

    def test_is_local_is_false(self):
        cfg = LLMConfig()
        model = HFHostedModel(cfg)
        assert model.is_local is False


# ---------------------------------------------------------------------------
# LocalGGUFModel tests
# ---------------------------------------------------------------------------

class TestLocalGGUFModel:
    """Tests for LocalGGUFModel."""

    def test_raises_value_error_when_no_path_set(self):
        cfg = LLMConfig(local_model_path=None)
        with pytest.raises(ValueError, match="local_model_path is not set"):
            LocalGGUFModel(cfg)

    def test_raises_file_not_found_for_missing_file(self):
        cfg = LLMConfig(local_model_path="/nonexistent/path/model.gguf")
        with pytest.raises(FileNotFoundError):
            LocalGGUFModel(cfg)

    def test_raises_import_error_when_llama_cpp_missing(self):
        with tempfile.NamedTemporaryFile(suffix=".gguf") as f:
            cfg = LLMConfig(local_model_path=f.name)
            with patch.dict("sys.modules", {"llama_cpp": None}):
                with pytest.raises(ImportError, match="llama-cpp-python"):
                    LocalGGUFModel(cfg)

    def test_generate_calls_llama_and_returns_text(self):
        with tempfile.NamedTemporaryFile(suffix=".gguf") as f:
            cfg = LLMConfig(local_model_path=f.name)

            mock_llama_instance = MagicMock()
            mock_llama_instance.return_value = {
                "choices": [{"text": "  generated text  "}]
            }
            mock_llama_cls = MagicMock(return_value=mock_llama_instance)

            mock_module = MagicMock()
            mock_module.Llama = mock_llama_cls

            with patch.dict("sys.modules", {"llama_cpp": mock_module}):
                model = LocalGGUFModel(cfg)
                # Calling the instance of Llama (stored as _llm) should return text
                result = model.generate("test prompt")

            assert result == "generated text"

    def test_is_local_is_true(self):
        with tempfile.NamedTemporaryFile(suffix=".gguf") as f:
            cfg = LLMConfig(local_model_path=f.name)
            mock_module = MagicMock()
            mock_module.Llama = MagicMock(return_value=MagicMock())
            with patch.dict("sys.modules", {"llama_cpp": mock_module}):
                model = LocalGGUFModel(cfg)
            assert model.is_local is True


# ---------------------------------------------------------------------------
# EnhancedRAGSystem tests
# ---------------------------------------------------------------------------

class TestEnhancedRAGSystem:
    """Tests for EnhancedRAGSystem."""

    def test_uses_hf_backend_when_no_local_path(self):
        config = RAGConfig()
        config.llm.local_model_path = None
        system = EnhancedRAGSystem(config=config)
        assert system.llm_backend == "hf_hosted"

    def test_uses_hf_backend_when_path_missing(self):
        config = RAGConfig()
        config.llm.local_model_path = "/nonexistent/model.gguf"
        system = EnhancedRAGSystem(config=config)
        assert system.llm_backend == "hf_hosted"

    def test_uses_local_backend_when_file_exists_and_llama_available(self):
        with tempfile.NamedTemporaryFile(suffix=".gguf") as f:
            config = RAGConfig()
            config.llm.local_model_path = f.name

            mock_module = MagicMock()
            mock_module.Llama = MagicMock(return_value=MagicMock())
            with patch.dict("sys.modules", {"llama_cpp": mock_module}):
                system = EnhancedRAGSystem(config=config)

            assert system.llm_backend == "local"

    def test_generate_returns_empty_with_hf_stub(self):
        config = RAGConfig()
        config.llm.local_model_path = None
        system = EnhancedRAGSystem(config=config)
        # RAG index not built → retrieval is skipped
        result = system.generate("test query", use_rag=False)
        assert result == ""

    def test_generate_returns_empty_without_rag_index(self):
        config = RAGConfig()
        config.llm.local_model_path = None
        system = EnhancedRAGSystem(config=config)
        result = system.generate("test query", use_rag=True)
        assert result == ""

    def test_generate_with_details_structure(self):
        config = RAGConfig()
        config.llm.local_model_path = None
        system = EnhancedRAGSystem(config=config)
        details = system.generate_with_details("test query", use_rag=False)

        assert "response" in details
        assert "rag_results" in details
        assert "rag_context" in details
        assert "llm_backend" in details
        assert "local_model_path" in details
        assert details["llm_backend"] == "hf_hosted"
        assert details["local_model_path"] is None

    def test_retrieve_returns_empty_without_index(self):
        config = RAGConfig()
        system = EnhancedRAGSystem(config=config)
        results = system.retrieve("some query")
        assert results == []

    def test_llm_backend_property_local(self):
        with tempfile.NamedTemporaryFile(suffix=".gguf") as f:
            config = RAGConfig()
            config.llm.local_model_path = f.name
            mock_module = MagicMock()
            mock_module.Llama = MagicMock(return_value=MagicMock())
            with patch.dict("sys.modules", {"llama_cpp": mock_module}):
                system = EnhancedRAGSystem(config=config)
            assert system.llm_backend == "local"

    def test_falls_back_to_hf_when_llama_cpp_missing(self):
        with tempfile.NamedTemporaryFile(suffix=".gguf") as f:
            config = RAGConfig()
            config.llm.local_model_path = f.name
            with patch.dict("sys.modules", {"llama_cpp": None}):
                system = EnhancedRAGSystem(config=config)
            assert system.llm_backend == "hf_hosted"


# ---------------------------------------------------------------------------
# create_enhanced_rag_system factory tests
# ---------------------------------------------------------------------------

class TestCreateEnhancedRAGSystem:
    """Tests for the create_enhanced_rag_system factory function."""

    def test_factory_with_explicit_path(self):
        system = create_enhanced_rag_system(local_model_path="/nonexistent/model.gguf")
        # File doesn't exist → falls back to hf_hosted
        assert system.llm_backend == "hf_hosted"
        assert system.config.llm.local_model_path == "/nonexistent/model.gguf"

    def test_factory_without_path(self):
        system = create_enhanced_rag_system()
        assert system.llm_backend == "hf_hosted"

    def test_factory_explicit_path_overrides_config(self):
        config = RAGConfig()
        config.llm.local_model_path = "/original/path.gguf"
        system = create_enhanced_rag_system(
            local_model_path="/override/path.gguf",
            config=config,
        )
        assert system.config.llm.local_model_path == "/override/path.gguf"
