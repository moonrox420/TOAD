"""
Tests for enhanced_rag_system.py.

Validates that:
- LOCAL_GGUF_MODEL env var routes to the llama.cpp backend and never
  imports/downloads the HuggingFace Transformers model.
- The HF Transformers backend is used by default when the env var is absent.
- dtype (not deprecated torch_dtype) is passed to AutoModelForCausalLM.
- The query() pipeline assembles prompts correctly with and without RAG context.
"""

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# Ensure the repo root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers / constants
# ---------------------------------------------------------------------------

FAKE_GGUF_PATH = "/tmp/fake_model.gguf"


def _make_fake_gguf_file(path: str = FAKE_GGUF_PATH) -> None:
    """Create a zero-byte placeholder so path-existence checks pass."""
    Path(path).touch()


def _remove_fake_gguf_file(path: str = FAKE_GGUF_PATH) -> None:
    p = Path(path)
    if p.exists():
        p.unlink()


# ---------------------------------------------------------------------------
# Tests for _load_llama_cpp_model
# ---------------------------------------------------------------------------


class TestLoadLlamaCppModel:
    """Unit tests for the llama.cpp loader helper."""

    def setup_method(self) -> None:
        _make_fake_gguf_file()

    def teardown_method(self) -> None:
        _remove_fake_gguf_file()

    @patch.dict(os.environ, {}, clear=False)
    def test_raises_import_error_when_llama_cpp_missing(self) -> None:
        """Raises ImportError with helpful message when llama-cpp-python absent."""
        from enhanced_rag_system import _load_llama_cpp_model

        with patch.dict("sys.modules", {"llama_cpp": None}):
            with pytest.raises(ImportError, match="llama-cpp-python"):
                _load_llama_cpp_model(FAKE_GGUF_PATH)

    def test_raises_file_not_found_for_missing_gguf(self) -> None:
        """Raises FileNotFoundError when the GGUF file does not exist."""
        from enhanced_rag_system import _load_llama_cpp_model

        mock_llama_module = MagicMock()

        with patch.dict("sys.modules", {"llama_cpp": mock_llama_module}):
            with pytest.raises(FileNotFoundError, match="GGUF model not found"):
                _load_llama_cpp_model("/nonexistent/path/model.gguf")

    def test_returns_llama_instance_for_valid_path(self) -> None:
        """Returns a Llama instance when the file exists and lib is installed."""
        from enhanced_rag_system import _load_llama_cpp_model

        fake_llm = MagicMock()
        mock_llama_module = MagicMock()
        mock_llama_module.Llama.return_value = fake_llm

        with patch.dict("sys.modules", {"llama_cpp": mock_llama_module}):
            result = _load_llama_cpp_model(FAKE_GGUF_PATH)

        assert result is fake_llm
        mock_llama_module.Llama.assert_called_once()


# ---------------------------------------------------------------------------
# Tests for _load_hf_model
# ---------------------------------------------------------------------------


class TestLoadHFModel:
    """Unit tests for the HuggingFace loader helper."""

    def test_raises_import_error_when_transformers_missing(self) -> None:
        """Raises ImportError when transformers is not installed."""
        from enhanced_rag_system import _load_hf_model

        with patch.dict("sys.modules", {"transformers": None, "torch": None}):
            with pytest.raises(ImportError, match="transformers"):
                _load_hf_model()

    def test_uses_dtype_not_torch_dtype(self) -> None:
        """Verifies that AutoModelForCausalLM.from_pretrained receives 'dtype'
        and NOT the deprecated 'torch_dtype' keyword argument."""
        from enhanced_rag_system import _load_hf_model

        import types

        fake_torch = types.ModuleType("torch")
        fake_torch.float16 = "float16_sentinel"

        fake_model = MagicMock()
        fake_tokenizer = MagicMock()
        fake_transformers = types.ModuleType("transformers")
        fake_transformers.AutoModelForCausalLM = MagicMock()
        fake_transformers.AutoModelForCausalLM.from_pretrained.return_value = fake_model
        fake_transformers.AutoTokenizer = MagicMock()
        fake_transformers.AutoTokenizer.from_pretrained.return_value = fake_tokenizer

        with patch.dict(
            "sys.modules",
            {"torch": fake_torch, "transformers": fake_transformers},
        ):
            model, tokenizer = _load_hf_model("test-model")

        call_kwargs = (
            fake_transformers.AutoModelForCausalLM.from_pretrained.call_args.kwargs
        )
        # 'dtype' MUST be present
        assert "dtype" in call_kwargs, "'dtype' not found in from_pretrained kwargs"
        # 'torch_dtype' MUST NOT be present
        assert "torch_dtype" not in call_kwargs, (
            "'torch_dtype' (deprecated) should not be passed to from_pretrained"
        )

    def test_returns_model_and_tokenizer_tuple(self) -> None:
        """Returns a (model, tokenizer) tuple on success."""
        from enhanced_rag_system import _load_hf_model

        import types

        fake_torch = types.ModuleType("torch")
        fake_torch.float16 = "float16"

        fake_model = MagicMock(name="FakeModel")
        fake_tokenizer = MagicMock(name="FakeTokenizer")
        fake_transformers = types.ModuleType("transformers")
        fake_transformers.AutoModelForCausalLM = MagicMock()
        fake_transformers.AutoModelForCausalLM.from_pretrained.return_value = fake_model
        fake_transformers.AutoTokenizer = MagicMock()
        fake_transformers.AutoTokenizer.from_pretrained.return_value = fake_tokenizer

        with patch.dict(
            "sys.modules",
            {"torch": fake_torch, "transformers": fake_transformers},
        ):
            model, tok = _load_hf_model("test-model")

        assert model is fake_model
        assert tok is fake_tokenizer


# ---------------------------------------------------------------------------
# Tests for EnhancedRAGSystem backend selection
# ---------------------------------------------------------------------------


class TestEnhancedRAGSystemBackendSelection:
    """Ensure the correct backend is picked based on LOCAL_GGUF_MODEL."""

    def setup_method(self) -> None:
        _make_fake_gguf_file()

    def teardown_method(self) -> None:
        _remove_fake_gguf_file()
        os.environ.pop("LOCAL_GGUF_MODEL", None)

    # ── llama.cpp path ───────────────────────────────────────────────────────

    def test_llama_cpp_backend_selected_via_env_var(self) -> None:
        """llama.cpp backend is chosen when LOCAL_GGUF_MODEL env var is set."""
        os.environ["LOCAL_GGUF_MODEL"] = FAKE_GGUF_PATH

        fake_llm = MagicMock()
        mock_llama_module = MagicMock()
        mock_llama_module.Llama.return_value = fake_llm

        with (
            patch.dict("sys.modules", {"llama_cpp": mock_llama_module}),
            patch("enhanced_rag_system.RAGRetriever") as mock_retriever_cls,
        ):
            mock_retriever_cls.return_value.is_available.return_value = False
            from enhanced_rag_system import EnhancedRAGSystem

            system = EnhancedRAGSystem()

        assert system.backend == "llama_cpp"

    def test_hf_backend_never_imported_when_gguf_set(self) -> None:
        """transformers is NOT imported when llama.cpp backend is selected."""
        os.environ["LOCAL_GGUF_MODEL"] = FAKE_GGUF_PATH

        fake_llm = MagicMock()
        mock_llama_module = MagicMock()
        mock_llama_module.Llama.return_value = fake_llm

        # If 'transformers' is imported this mock would record the call;
        # we assert it was NOT called for from_pretrained.
        mock_transformers = MagicMock()

        with (
            patch.dict(
                "sys.modules",
                {"llama_cpp": mock_llama_module, "transformers": mock_transformers},
            ),
            patch("enhanced_rag_system.RAGRetriever") as mock_retriever_cls,
        ):
            mock_retriever_cls.return_value.is_available.return_value = False
            from enhanced_rag_system import EnhancedRAGSystem

            system = EnhancedRAGSystem()

        # AutoModelForCausalLM.from_pretrained must NOT have been called
        mock_transformers.AutoModelForCausalLM.from_pretrained.assert_not_called()

    def test_llama_cpp_backend_selected_via_constructor_arg(self) -> None:
        """llama.cpp backend is chosen when gguf_model_path kwarg is passed."""
        # Ensure env var is absent so we know the arg drives the decision
        os.environ.pop("LOCAL_GGUF_MODEL", None)

        fake_llm = MagicMock()
        mock_llama_module = MagicMock()
        mock_llama_module.Llama.return_value = fake_llm

        with (
            patch.dict("sys.modules", {"llama_cpp": mock_llama_module}),
            patch("enhanced_rag_system.RAGRetriever") as mock_retriever_cls,
        ):
            mock_retriever_cls.return_value.is_available.return_value = False
            from enhanced_rag_system import EnhancedRAGSystem

            system = EnhancedRAGSystem(gguf_model_path=FAKE_GGUF_PATH)

        assert system.backend == "llama_cpp"

    # ── HF Transformers path ─────────────────────────────────────────────────

    def test_hf_backend_selected_when_env_var_absent(self) -> None:
        """HF Transformers backend is the default when LOCAL_GGUF_MODEL is unset."""
        os.environ.pop("LOCAL_GGUF_MODEL", None)

        import types

        fake_torch = types.ModuleType("torch")
        fake_torch.float16 = "float16"

        fake_model = MagicMock()
        fake_tokenizer = MagicMock()
        fake_transformers = types.ModuleType("transformers")
        fake_transformers.AutoModelForCausalLM = MagicMock()
        fake_transformers.AutoModelForCausalLM.from_pretrained.return_value = fake_model
        fake_transformers.AutoTokenizer = MagicMock()
        fake_transformers.AutoTokenizer.from_pretrained.return_value = fake_tokenizer

        with (
            patch.dict(
                "sys.modules",
                {"torch": fake_torch, "transformers": fake_transformers},
            ),
            patch("enhanced_rag_system.RAGRetriever") as mock_retriever_cls,
        ):
            mock_retriever_cls.return_value.is_available.return_value = False
            from enhanced_rag_system import EnhancedRAGSystem

            system = EnhancedRAGSystem()

        assert system.backend == "hf_transformers"


# ---------------------------------------------------------------------------
# Tests for generate() and query()
# ---------------------------------------------------------------------------


class TestEnhancedRAGSystemGenerate:
    """Tests for the generate() method on both backends."""

    def setup_method(self) -> None:
        _make_fake_gguf_file()

    def teardown_method(self) -> None:
        _remove_fake_gguf_file()
        os.environ.pop("LOCAL_GGUF_MODEL", None)

    def _make_llama_system(self) -> Any:
        """Build an EnhancedRAGSystem wired to the llama.cpp backend."""
        os.environ["LOCAL_GGUF_MODEL"] = FAKE_GGUF_PATH

        fake_llm = MagicMock()
        fake_llm.return_value = {
            "choices": [{"text": " hello from llama"}]
        }
        mock_llama_module = MagicMock()
        mock_llama_module.Llama.return_value = fake_llm

        with (
            patch.dict("sys.modules", {"llama_cpp": mock_llama_module}),
            patch("enhanced_rag_system.RAGRetriever") as mock_retriever_cls,
        ):
            mock_retriever_cls.return_value.is_available.return_value = False
            from enhanced_rag_system import EnhancedRAGSystem

            system = EnhancedRAGSystem()

        # Keep the fake LLM accessible for assertions
        system._llm = fake_llm
        return system

    def test_generate_llama_cpp(self) -> None:
        """generate() returns stripped text from llama.cpp output."""
        system = self._make_llama_system()
        result = system.generate("hello world")
        assert result == "hello from llama"

    def test_generate_raises_when_no_backend(self) -> None:
        """generate() raises RuntimeError when no backend is active."""
        os.environ.pop("LOCAL_GGUF_MODEL", None)

        import types

        fake_torch = types.ModuleType("torch")
        fake_torch.float16 = "float16"

        fake_model = MagicMock()
        fake_tokenizer = MagicMock()
        fake_transformers = types.ModuleType("transformers")
        fake_transformers.AutoModelForCausalLM = MagicMock()
        fake_transformers.AutoModelForCausalLM.from_pretrained.return_value = fake_model
        fake_transformers.AutoTokenizer = MagicMock()
        fake_transformers.AutoTokenizer.from_pretrained.return_value = fake_tokenizer

        with (
            patch.dict(
                "sys.modules",
                {"torch": fake_torch, "transformers": fake_transformers},
            ),
            patch("enhanced_rag_system.RAGRetriever") as mock_retriever_cls,
        ):
            mock_retriever_cls.return_value.is_available.return_value = False
            from enhanced_rag_system import EnhancedRAGSystem

            system = EnhancedRAGSystem()

        system._backend = "none"  # forcefully break it
        with pytest.raises(RuntimeError, match="No LLM backend"):
            system.generate("test")


class TestEnhancedRAGSystemQuery:
    """Tests for the query() RAG pipeline."""

    def setup_method(self) -> None:
        _make_fake_gguf_file()
        os.environ["LOCAL_GGUF_MODEL"] = FAKE_GGUF_PATH

    def teardown_method(self) -> None:
        _remove_fake_gguf_file()
        os.environ.pop("LOCAL_GGUF_MODEL", None)

    def _build_system_with_rag(self, rag_context: str = "") -> Any:
        """Return an EnhancedRAGSystem with mocked llama.cpp and RAG."""
        from enhanced_rag_system import EnhancedRAGSystem

        fake_llm = MagicMock()
        fake_llm.return_value = {"choices": [{"text": "generated answer"}]}
        mock_llama_module = MagicMock()
        mock_llama_module.Llama.return_value = fake_llm

        mock_retriever = MagicMock()
        mock_retriever.is_available.return_value = bool(rag_context)
        mock_retriever.retrieve.return_value = []
        mock_retriever.format_context.return_value = rag_context

        with (
            patch.dict("sys.modules", {"llama_cpp": mock_llama_module}),
            patch("enhanced_rag_system.RAGRetriever", return_value=mock_retriever),
        ):
            system = EnhancedRAGSystem()

        system._llm = fake_llm
        system._retriever = mock_retriever
        return system

    def test_query_returns_required_keys(self) -> None:
        """query() always returns the four documented keys."""
        system = self._build_system_with_rag()
        result = system.query("test question")

        assert "answer" in result
        assert "context" in result
        assert "backend" in result
        assert "rag_results" in result

    def test_query_backend_is_correct(self) -> None:
        """query() reports the correct backend in its return value."""
        system = self._build_system_with_rag()
        result = system.query("test question")
        assert result["backend"] == "llama_cpp"

    def test_query_injects_rag_context_into_prompt(self) -> None:
        """When RAG context is available it is prepended to the prompt."""
        fake_context = "=== RELEVANT CODING EXAMPLES ===\nExample 1\n"
        system = self._build_system_with_rag(rag_context=fake_context)

        captured_prompts: list = []

        original_generate = system.generate

        def recording_generate(prompt: str, **kwargs: Any) -> str:
            captured_prompts.append(prompt)
            return original_generate(prompt, **kwargs)

        with patch.object(system, "generate", side_effect=recording_generate):
            system.query("Write a hello world function")

        assert captured_prompts, "generate() was not called"
        assert fake_context in captured_prompts[0], (
            "RAG context was not included in the prompt"
        )

    def test_query_without_rag_uses_plain_prompt(self) -> None:
        """When RAG is unavailable the raw question is used as the prompt."""
        system = self._build_system_with_rag(rag_context="")

        captured_prompts: list = []

        original_generate = system.generate

        def recording_generate(prompt: str, **kwargs: Any) -> str:
            captured_prompts.append(prompt)
            return original_generate(prompt, **kwargs)

        question = "Write a hello world function"
        with patch.object(system, "generate", side_effect=recording_generate):
            system.query(question)

        assert captured_prompts[0] == question
