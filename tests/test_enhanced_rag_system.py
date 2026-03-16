"""
Tests for enhanced_rag_system.py

Covers:
  - Backend selection logic (GGUFBackend vs TransformersBackend)
  - GGUFBackend error handling (missing package, missing file)
  - TransformersBackend error handling (missing package)
  - EnhancedRAGSystem public API surface (mocked backends)
  - Streaming / callback wiring
  - Environment-variable-driven backend resolution
"""

import os
import sys
import types
import threading
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock, call
import pytest

# Ensure repo root is on sys.path so we can import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dummy_gguf_file(tmp_path: Path) -> Path:
    """Create a dummy (empty) .gguf file for path-validation tests."""
    f = tmp_path / "model.gguf"
    f.write_bytes(b"")
    return f


# ---------------------------------------------------------------------------
# GGUFBackend tests
# ---------------------------------------------------------------------------

class TestGGUFBackend:
    """Tests for the GGUFBackend class."""

    def test_raises_import_error_when_llama_cpp_missing(self, tmp_path):
        """GGUFBackend raises ImportError when llama_cpp is not installed."""
        import enhanced_rag_system as ers

        original = ers._LLAMA_CPP_AVAILABLE
        try:
            ers._LLAMA_CPP_AVAILABLE = False
            with pytest.raises(ImportError, match="llama-cpp-python"):
                ers.GGUFBackend(str(_dummy_gguf_file(tmp_path)))
        finally:
            ers._LLAMA_CPP_AVAILABLE = original

    def test_raises_file_not_found_for_missing_path(self, tmp_path):
        """GGUFBackend raises FileNotFoundError when path does not exist."""
        import enhanced_rag_system as ers

        # Simulate llama_cpp available
        original = ers._LLAMA_CPP_AVAILABLE
        try:
            ers._LLAMA_CPP_AVAILABLE = True
            missing = str(tmp_path / "does_not_exist.gguf")
            with pytest.raises(FileNotFoundError, match="not found"):
                ers.GGUFBackend(missing)
        finally:
            ers._LLAMA_CPP_AVAILABLE = original

    def test_generate_calls_model_correctly(self, tmp_path):
        """GGUFBackend.generate delegates to the llama_cpp.Llama model."""
        import enhanced_rag_system as ers

        gguf_file = _dummy_gguf_file(tmp_path)
        mock_llama_cls = MagicMock()
        mock_model_instance = MagicMock()
        mock_llama_cls.return_value = mock_model_instance
        mock_model_instance.return_value = {
            "choices": [{"text": "hello world"}]
        }

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)

        try:
            ers._LLAMA_CPP_AVAILABLE = True
            # Inject a fake llama_cpp module
            fake_llama_cpp = types.ModuleType("llama_cpp")
            fake_llama_cpp.Llama = mock_llama_cls
            ers.llama_cpp = fake_llama_cpp

            backend = ers.GGUFBackend(str(gguf_file))
            result = backend.generate("test prompt")
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

        assert result == "hello world"

    def test_generate_stream_yields_tokens(self, tmp_path):
        """GGUFBackend.generate_stream yields token strings."""
        import enhanced_rag_system as ers

        gguf_file = _dummy_gguf_file(tmp_path)
        mock_llama_cls = MagicMock()
        mock_model_instance = MagicMock()
        mock_llama_cls.return_value = mock_model_instance

        token_chunks = [
            {"choices": [{"text": "tok1"}]},
            {"choices": [{"text": "tok2"}]},
            {"choices": [{"text": ""}]},   # empty token should be skipped
            {"choices": [{"text": "tok3"}]},
        ]
        mock_model_instance.return_value = iter(token_chunks)

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)

        try:
            ers._LLAMA_CPP_AVAILABLE = True
            fake_llama_cpp = types.ModuleType("llama_cpp")
            fake_llama_cpp.Llama = mock_llama_cls
            ers.llama_cpp = fake_llama_cpp

            backend = ers.GGUFBackend(str(gguf_file))
            tokens = list(backend.generate_stream("prompt"))
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

        # Empty tokens must be filtered
        assert tokens == ["tok1", "tok2", "tok3"]

    def test_generate_with_callback_invokes_callback(self, tmp_path):
        """GGUFBackend.generate_with_callback calls on_token for each token."""
        import enhanced_rag_system as ers

        gguf_file = _dummy_gguf_file(tmp_path)
        mock_llama_cls = MagicMock()
        mock_model_instance = MagicMock()
        mock_llama_cls.return_value = mock_model_instance

        chunks = [
            {"choices": [{"text": "A"}]},
            {"choices": [{"text": "B"}]},
            {"choices": [{"text": "C"}]},
        ]
        mock_model_instance.return_value = iter(chunks)

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)

        received: list = []
        try:
            ers._LLAMA_CPP_AVAILABLE = True
            fake_llama_cpp = types.ModuleType("llama_cpp")
            fake_llama_cpp.Llama = mock_llama_cls
            ers.llama_cpp = fake_llama_cpp

            backend = ers.GGUFBackend(str(gguf_file))
            result = backend.generate_with_callback("p", on_token=received.append)
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

        assert received == ["A", "B", "C"]
        assert result == "ABC"

    def test_env_vars_for_n_threads_and_gpu_layers(self, tmp_path, monkeypatch):
        """GGUF_N_THREADS and GGUF_N_GPU_LAYERS env vars are respected."""
        import enhanced_rag_system as ers

        monkeypatch.setenv("GGUF_N_THREADS", "8")
        monkeypatch.setenv("GGUF_N_GPU_LAYERS", "16")

        gguf_file = _dummy_gguf_file(tmp_path)
        mock_llama_cls = MagicMock()
        mock_llama_cls.return_value = MagicMock()

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)

        try:
            ers._LLAMA_CPP_AVAILABLE = True
            fake_llama_cpp = types.ModuleType("llama_cpp")
            fake_llama_cpp.Llama = mock_llama_cls
            ers.llama_cpp = fake_llama_cpp

            ers.GGUFBackend(str(gguf_file))
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

        _, kwargs = mock_llama_cls.call_args
        assert kwargs["n_threads"] == 8
        assert kwargs["n_gpu_layers"] == 16


# ---------------------------------------------------------------------------
# TransformersBackend tests
# ---------------------------------------------------------------------------

class TestTransformersBackend:
    """Tests for the TransformersBackend class."""

    def test_raises_import_error_when_transformers_missing(self):
        """TransformersBackend raises ImportError when transformers not installed."""
        import enhanced_rag_system as ers

        original = ers._TRANSFORMERS_AVAILABLE
        try:
            ers._TRANSFORMERS_AVAILABLE = False
            with pytest.raises(ImportError, match="transformers"):
                ers.TransformersBackend()
        finally:
            ers._TRANSFORMERS_AVAILABLE = original


# ---------------------------------------------------------------------------
# _resolve_backend tests
# ---------------------------------------------------------------------------

class TestResolveBackend:
    """Tests for the backend-factory function."""

    def test_explicit_gguf_path_takes_priority(self, tmp_path, monkeypatch):
        """An explicit local_gguf_path overrides the env var."""
        import enhanced_rag_system as ers

        gguf_file = _dummy_gguf_file(tmp_path)
        # env var points somewhere else – explicit arg should win
        monkeypatch.setenv("LOCAL_GGUF_MODEL", "/nonexistent/path.gguf")

        mock_llama_cls = MagicMock()
        mock_llama_cls.return_value = MagicMock()

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)
        try:
            ers._LLAMA_CPP_AVAILABLE = True
            fake_llama_cpp = types.ModuleType("llama_cpp")
            fake_llama_cpp.Llama = mock_llama_cls
            ers.llama_cpp = fake_llama_cpp

            backend = ers._resolve_backend(str(gguf_file))
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

        assert isinstance(backend, ers.GGUFBackend)

    def test_env_var_triggers_gguf_backend(self, tmp_path, monkeypatch):
        """Setting LOCAL_GGUF_MODEL env var selects GGUFBackend."""
        import enhanced_rag_system as ers

        gguf_file = _dummy_gguf_file(tmp_path)
        monkeypatch.setenv("LOCAL_GGUF_MODEL", str(gguf_file))

        mock_llama_cls = MagicMock()
        mock_llama_cls.return_value = MagicMock()

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)
        try:
            ers._LLAMA_CPP_AVAILABLE = True
            fake_llama_cpp = types.ModuleType("llama_cpp")
            fake_llama_cpp.Llama = mock_llama_cls
            ers.llama_cpp = fake_llama_cpp

            backend = ers._resolve_backend()
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

        assert isinstance(backend, ers.GGUFBackend)

    def test_no_env_var_uses_transformers_backend(self, monkeypatch):
        """Without LOCAL_GGUF_MODEL, TransformersBackend is selected."""
        import enhanced_rag_system as ers

        monkeypatch.delenv("LOCAL_GGUF_MODEL", raising=False)

        original_available = ers._TRANSFORMERS_AVAILABLE
        try:
            ers._TRANSFORMERS_AVAILABLE = False
            with pytest.raises(ImportError, match="transformers"):
                ers._resolve_backend()
        finally:
            ers._TRANSFORMERS_AVAILABLE = original_available


# ---------------------------------------------------------------------------
# EnhancedRAGSystem tests
# ---------------------------------------------------------------------------

class TestEnhancedRAGSystem:
    """Integration-level tests for EnhancedRAGSystem."""

    def _make_mock_gguf_backend(self, tmp_path, ers):
        """Return a GGUFBackend with a mocked llama model."""
        gguf_file = _dummy_gguf_file(tmp_path)
        mock_llama_cls = MagicMock()
        mock_model = MagicMock()
        mock_llama_cls.return_value = mock_model
        mock_model.return_value = {"choices": [{"text": "result"}]}

        ers._LLAMA_CPP_AVAILABLE = True
        fake_llama_cpp = types.ModuleType("llama_cpp")
        fake_llama_cpp.Llama = mock_llama_cls
        ers.llama_cpp = fake_llama_cpp

        return ers.GGUFBackend(str(gguf_file)), mock_model

    def test_backend_type_property_gguf(self, tmp_path):
        """backend_type returns 'gguf' when GGUF backend is active."""
        import enhanced_rag_system as ers

        original_available = ers._LLAMA_CPP_AVAILABLE
        original_module = getattr(ers, "llama_cpp", None)
        try:
            backend, _ = self._make_mock_gguf_backend(tmp_path, ers)
            system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
            system._backend = backend
            system._rag_agent = None
            assert system.backend_type == "gguf"
        finally:
            ers._LLAMA_CPP_AVAILABLE = original_available
            if original_module is None:
                if hasattr(ers, "llama_cpp"):
                    del ers.llama_cpp
            else:
                ers.llama_cpp = original_module

    def test_backend_type_property_transformers(self):
        """backend_type returns 'transformers' when Transformers backend is used."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock(spec=ers.TransformersBackend)
        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = None
        assert system.backend_type == "transformers"

    def test_generate_delegates_to_backend(self):
        """EnhancedRAGSystem.generate delegates to the backend."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock()
        mock_backend.generate.return_value = "generated code"

        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = None
        system.max_new_tokens = 512
        system.temperature = 0.7
        system.top_p = 0.95

        result = system.generate("write a function")

        assert result == "generated code"
        mock_backend.generate.assert_called_once()

    def test_generate_stream_delegates_to_backend(self):
        """EnhancedRAGSystem.generate_stream delegates to the backend."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock()
        mock_backend.generate_stream.return_value = iter(["tok1", "tok2"])

        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = None
        system.max_new_tokens = 512
        system.temperature = 0.7
        system.top_p = 0.95

        tokens = list(system.generate_stream("write a function"))

        assert tokens == ["tok1", "tok2"]
        mock_backend.generate_stream.assert_called_once()

    def test_generate_with_callback_delegates(self):
        """EnhancedRAGSystem.generate_with_callback delegates to backend."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock()
        mock_backend.generate_with_callback.return_value = "output"

        received = []

        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = None
        system.max_new_tokens = 512
        system.temperature = 0.7
        system.top_p = 0.95

        result = system.generate_with_callback("request", on_token=received.append)

        assert result == "output"
        mock_backend.generate_with_callback.assert_called_once()

    def test_rag_context_prepended_to_prompt(self):
        """When RAG returns context, it is prepended to the generated prompt."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock()
        mock_backend.generate.return_value = "answer"

        mock_rag = MagicMock()
        mock_rag.rag_available = True
        mock_rag._get_rag_context.return_value = "=== RAG CONTEXT ==="

        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = mock_rag
        system.max_new_tokens = 512
        system.temperature = 0.7
        system.top_p = 0.95

        system.generate("my request")

        # The prompt passed to the backend should contain RAG context
        prompt_arg = mock_backend.generate.call_args[0][0]
        assert "=== RAG CONTEXT ===" in prompt_arg
        assert "my request" in prompt_arg

    def test_rag_unavailable_prompt_has_no_context(self):
        """When RAG is unavailable, the prompt has no extra context block."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock()
        mock_backend.generate.return_value = "answer"

        mock_rag = MagicMock()
        mock_rag.rag_available = False

        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = mock_rag
        system.max_new_tokens = 512
        system.temperature = 0.7
        system.top_p = 0.95

        system.generate("my request")

        prompt_arg = mock_backend.generate.call_args[0][0]
        # No RAG context separator should appear
        assert "=== RAG CONTEXT ===" not in prompt_arg
        assert "my request" in prompt_arg

    def test_parameter_overrides_respected(self):
        """Per-call temperature/top_p/max_new_tokens override instance defaults."""
        import enhanced_rag_system as ers

        mock_backend = MagicMock()
        mock_backend.generate.return_value = "ok"

        system = ers.EnhancedRAGSystem.__new__(ers.EnhancedRAGSystem)
        system._backend = mock_backend
        system._rag_agent = None
        system.max_new_tokens = 512
        system.temperature = 0.7
        system.top_p = 0.95

        system.generate("req", max_new_tokens=128, temperature=0.1, top_p=0.5)

        _, kwargs = mock_backend.generate.call_args
        assert kwargs["max_new_tokens"] == 128
        assert kwargs["temperature"] == 0.1
        assert kwargs["top_p"] == 0.5
