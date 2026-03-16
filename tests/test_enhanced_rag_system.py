"""
Tests for enhanced_rag_system.py.

Covers:
- Default model selection and MCFG_LLM environment variable override
- LLM pipeline loading (success and failure paths)
- Graceful fallback to rule-based agent when LLM is unavailable
- EnhancedRAGSystem.generate_code delegation
- get_status reporting
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers / constants
# ---------------------------------------------------------------------------

PUBLIC_DEFAULT = "mistralai/Mistral-7B-Instruct-v0.2"


# ---------------------------------------------------------------------------
# Module-level default model tests
# ---------------------------------------------------------------------------

class TestDefaultLLMModel:
    """Verify that the default model is the public, ungated alternative."""

    def test_default_model_is_public(self):
        """DEFAULT_LLM_MODEL must not be a gated meta-llama identifier."""
        import importlib
        import enhanced_rag_system as ers

        importlib.reload(ers)  # reload to reset after any env mutation
        assert ers.DEFAULT_LLM_MODEL == PUBLIC_DEFAULT

    def test_env_override_mcfg_llm(self, monkeypatch):
        """MCFG_LLM environment variable must override the default model."""
        import importlib
        import enhanced_rag_system as ers

        monkeypatch.setenv("MCFG_LLM", "tiiuae/falcon-7b-instruct")
        importlib.reload(ers)
        assert ers.DEFAULT_LLM_MODEL == "tiiuae/falcon-7b-instruct"
        # Reload without env var for subsequent tests
        monkeypatch.delenv("MCFG_LLM", raising=False)
        importlib.reload(ers)

    def test_no_gated_llama_as_default(self):
        """The default must not be the gated meta-llama/Llama-3-8b-Instruct."""
        import importlib
        import enhanced_rag_system as ers

        importlib.reload(ers)
        assert ers.DEFAULT_LLM_MODEL != "meta-llama/Llama-3-8b-Instruct"


# ---------------------------------------------------------------------------
# _load_llm_pipeline tests
# ---------------------------------------------------------------------------

class TestLoadLLMPipeline:
    """Test _load_llm_pipeline under various conditions."""

    def test_returns_none_when_transformers_missing(self):
        """Return None (with a warning) when transformers is not installed."""
        import enhanced_rag_system as ers

        with patch.dict("sys.modules", {"transformers": None}):
            result = ers._load_llm_pipeline("any-model")
        assert result is None

    def test_returns_none_on_os_error(self):
        """Return None when the HF Hub raises OSError (404 / gated model)."""
        import enhanced_rag_system as ers

        mock_pipeline = MagicMock(side_effect=OSError("404 Not Found"))
        fake_transformers = MagicMock()
        fake_transformers.pipeline = mock_pipeline

        with patch.dict("sys.modules", {"transformers": fake_transformers}):
            result = ers._load_llm_pipeline("meta-llama/Llama-3-8b-Instruct")

        assert result is None

    def test_returns_none_on_unexpected_error(self):
        """Return None when any unexpected error occurs during pipeline load."""
        import enhanced_rag_system as ers

        mock_pipeline = MagicMock(side_effect=RuntimeError("CUDA out of memory"))
        fake_transformers = MagicMock()
        fake_transformers.pipeline = mock_pipeline

        with patch.dict("sys.modules", {"transformers": fake_transformers}):
            result = ers._load_llm_pipeline("some/model")

        assert result is None

    def test_returns_pipeline_on_success(self):
        """Return the pipeline object when loading succeeds."""
        import enhanced_rag_system as ers

        mock_pipe = MagicMock()
        mock_pipeline_fn = MagicMock(return_value=mock_pipe)
        fake_transformers = MagicMock()
        fake_transformers.pipeline = mock_pipeline_fn

        with patch.dict("sys.modules", {"transformers": fake_transformers}):
            result = ers._load_llm_pipeline(PUBLIC_DEFAULT)

        assert result is mock_pipe

    def test_uses_hf_token_when_set(self, monkeypatch):
        """Pass HUGGING_FACE_HUB_TOKEN to the pipeline constructor."""
        import enhanced_rag_system as ers

        monkeypatch.setenv("HUGGING_FACE_HUB_TOKEN", "hf_test_token")

        mock_pipe = MagicMock()
        mock_pipeline_fn = MagicMock(return_value=mock_pipe)
        fake_transformers = MagicMock()
        fake_transformers.pipeline = mock_pipeline_fn

        with patch.dict("sys.modules", {"transformers": fake_transformers}):
            ers._load_llm_pipeline(PUBLIC_DEFAULT)

        call_kwargs = mock_pipeline_fn.call_args[1]
        assert call_kwargs.get("token") == "hf_test_token"


# ---------------------------------------------------------------------------
# EnhancedRAGSystem initialization tests
# ---------------------------------------------------------------------------

class TestEnhancedRAGSystemInit:
    """Test EnhancedRAGSystem initialization and component availability."""

    @patch("enhanced_rag_system._load_llm_pipeline", return_value=None)
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_llm_unavailable_flag_when_load_fails(self, mock_rag, mock_llm):
        """llm_available must be False when _load_llm_pipeline returns None."""
        from enhanced_rag_system import EnhancedRAGSystem

        system = EnhancedRAGSystem(use_llm=True)
        assert system.llm_available is False

    @patch("enhanced_rag_system._load_llm_pipeline")
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_llm_available_flag_when_load_succeeds(self, mock_rag, mock_llm):
        """llm_available must be True when _load_llm_pipeline returns a pipeline."""
        from enhanced_rag_system import EnhancedRAGSystem

        mock_llm.return_value = MagicMock()
        system = EnhancedRAGSystem(use_llm=True)
        assert system.llm_available is True

    @patch("enhanced_rag_system._load_llm_pipeline", return_value=None)
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_custom_model_stored(self, mock_rag, mock_llm):
        """Constructor should store the supplied model identifier."""
        from enhanced_rag_system import EnhancedRAGSystem

        system = EnhancedRAGSystem(llm_model="tiiuae/falcon-7b-instruct")
        assert system.llm_model == "tiiuae/falcon-7b-instruct"

    @patch("enhanced_rag_system._load_llm_pipeline", return_value=None)
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_use_llm_false_skips_pipeline_load(self, mock_rag, mock_llm):
        """Setting use_llm=False must skip pipeline loading entirely."""
        from enhanced_rag_system import EnhancedRAGSystem

        EnhancedRAGSystem(use_llm=False)
        mock_llm.assert_not_called()


# ---------------------------------------------------------------------------
# EnhancedRAGSystem.generate_code delegation tests
# ---------------------------------------------------------------------------

class TestEnhancedRAGSystemGenerateCode:
    """Test that generate_code routes to the correct backend."""

    def _make_system(self, llm_pipeline=None, rag_agent=None):
        """Create an EnhancedRAGSystem with mocked internals."""
        from enhanced_rag_system import EnhancedRAGSystem

        with (
            patch("enhanced_rag_system._load_llm_pipeline", return_value=llm_pipeline),
            patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent"),
        ):
            system = EnhancedRAGSystem(use_llm=llm_pipeline is not None)

        system._rag_agent = rag_agent
        return system

    def test_falls_back_to_rag_agent_when_llm_unavailable(self):
        """When LLM is unavailable, delegate to _rag_agent.generate_code."""
        mock_rag = MagicMock()
        mock_rag.generate_code.return_value = "# fallback code"

        system = self._make_system(llm_pipeline=None, rag_agent=mock_rag)
        result = system.generate_code("Create an API")

        mock_rag.generate_code.assert_called_once()
        assert result == "# fallback code"

    def test_uses_llm_when_available(self):
        """When LLM is available, use _generate_with_llm."""
        mock_pipeline = MagicMock(
            return_value=[{"generated_text": "prompt\n\nCode:\ndef api(): pass"}]
        )
        mock_rag = MagicMock()
        mock_rag.rag_available = False

        system = self._make_system(llm_pipeline=mock_pipeline, rag_agent=mock_rag)
        system.llm_available = True
        system._llm_pipeline = mock_pipeline

        result = system.generate_code("Create an API")

        mock_pipeline.assert_called_once()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_fallback_when_rag_agent_none(self):
        """Return an error string if both LLM and fallback agent are absent."""
        system = self._make_system(llm_pipeline=None, rag_agent=None)
        result = system.generate_code("Create an API")

        assert "error" in result.lower() or result.startswith("#")

    def test_llm_error_falls_back_to_rag_agent(self):
        """If LLM raises during generation, fall back to rule-based agent."""
        mock_pipeline = MagicMock(side_effect=RuntimeError("model crash"))
        mock_rag = MagicMock()
        mock_rag.generate_code.return_value = "# rule-based code"
        mock_rag.rag_available = False

        system = self._make_system(llm_pipeline=mock_pipeline, rag_agent=mock_rag)
        system.llm_available = True
        system._llm_pipeline = mock_pipeline

        result = system.generate_code("Create an API")

        # Should have fallen back to the rule-based agent
        assert result == "# rule-based code"


# ---------------------------------------------------------------------------
# EnhancedRAGSystem.get_status tests
# ---------------------------------------------------------------------------

class TestEnhancedRAGSystemGetStatus:
    """Test the get_status() reporting method."""

    @patch("enhanced_rag_system._load_llm_pipeline", return_value=None)
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_status_keys_present(self, mock_rag, mock_llm):
        """get_status must return a dict with all required keys."""
        from enhanced_rag_system import EnhancedRAGSystem

        system = EnhancedRAGSystem()
        status = system.get_status()

        assert "llm_available" in status
        assert "llm_model" in status
        assert "rag_available" in status
        assert "fallback_available" in status

    @patch("enhanced_rag_system._load_llm_pipeline", return_value=None)
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_status_llm_model_matches(self, mock_rag, mock_llm):
        """llm_model in status must match the instance attribute."""
        from enhanced_rag_system import EnhancedRAGSystem

        system = EnhancedRAGSystem(llm_model="tiiuae/falcon-7b-instruct")
        assert system.get_status()["llm_model"] == "tiiuae/falcon-7b-instruct"


# ---------------------------------------------------------------------------
# Factory function test
# ---------------------------------------------------------------------------

class TestCreateEnhancedRAGSystem:
    """Test create_enhanced_rag_system factory function."""

    @patch("enhanced_rag_system._load_llm_pipeline", return_value=None)
    @patch("enhanced_rag_system.EnhancedRAGSystem._setup_rag_agent")
    def test_factory_returns_instance(self, mock_rag, mock_llm):
        """Factory must return an EnhancedRAGSystem instance."""
        from enhanced_rag_system import EnhancedRAGSystem, create_enhanced_rag_system

        system = create_enhanced_rag_system(use_llm=False)
        assert isinstance(system, EnhancedRAGSystem)
