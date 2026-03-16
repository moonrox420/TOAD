"""
Enhanced RAG System with optional LLM integration.

Combines RAG retrieval with a Hugging Face LLM for context-aware code
generation, with a clean fallback to the rule-based CodeGenerationAgent
when the LLM is unavailable.

LLM Configuration
-----------------
The default model is ``mistralai/Mistral-7B-Instruct-v0.2``, a fully public
model that does not require special Hugging Face access.

To override the model, set the ``MCFG_LLM`` environment variable before
launching:

    export MCFG_LLM="mistralai/Mistral-7B-Instruct-v0.2"   # default (public)
    export MCFG_LLM="tiiuae/falcon-7b-instruct"             # another public option

NOTE – Gated models (e.g. ``meta-llama/Meta-Llama-3.1-8B-Instruct``) require:
    1. A Hugging Face account with model access approved at
       https://huggingface.co/<model-id>
    2. A valid API token exported as ``HUGGING_FACE_HUB_TOKEN`` (or set via
       ``huggingface-cli login``).
    If the selected model cannot be loaded the system logs a warning and
    automatically falls back to the rule-based CodeGenerationAgent so that
    normal code generation continues uninterrupted.
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model selection
# ---------------------------------------------------------------------------
# Default: publicly accessible, no gating required.
# Override by setting MCFG_LLM in the environment.
_DEFAULT_LLM = "mistralai/Mistral-7B-Instruct-v0.2"
DEFAULT_LLM_MODEL: str = os.environ.get("MCFG_LLM", _DEFAULT_LLM)


def _load_llm_pipeline(model_id: str) -> Optional[Any]:
    """
    Attempt to load a Hugging Face text-generation pipeline.

    Args:
        model_id: Hugging Face model identifier (e.g.
                  ``"mistralai/Mistral-7B-Instruct-v0.2"``).

    Returns:
        A ``transformers.pipeline`` object on success, or ``None`` if the
        model cannot be loaded (missing library, gated/invalid model,
        insufficient memory, etc.).
    """
    try:
        from transformers import pipeline  # type: ignore[import]
    except ImportError:
        logger.warning(
            "The 'transformers' package is not installed. "
            "Install it with: pip install transformers\n"
            "Continuing without LLM; falling back to rule-based generation."
        )
        return None

    hf_token: Optional[str] = os.environ.get("HUGGING_FACE_HUB_TOKEN")

    try:
        logger.info("Loading LLM pipeline for model: %s", model_id)
        pipe = pipeline(
            "text-generation",
            model=model_id,
            token=hf_token or None,
            # Keep memory footprint small when no GPU is present
            device_map="auto",
            max_new_tokens=512,
        )
        logger.info("LLM pipeline loaded successfully: %s", model_id)
        return pipe
    except OSError as exc:
        # Covers 404 / gated-model / network errors from HF Hub
        logger.warning(
            "Could not load LLM '%s': %s\n"
            "If this is a gated model, ensure you have access and that "
            "HUGGING_FACE_HUB_TOKEN is set. "
            "Falling back to rule-based code generation.",
            model_id,
            exc,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning(
            "Unexpected error loading LLM '%s': %s\n"
            "Falling back to rule-based code generation.",
            model_id,
            exc,
        )
    return None


class EnhancedRAGSystem:
    """
    RAG-enhanced code generation system with optional LLM support.

    The system layers three capabilities in order:
        1. **RAG retrieval** – fetches relevant coding examples from the
           FAISS index (when the index has been built).
        2. **LLM generation** – uses a Hugging Face model to refine the
           retrieved context into final code (when a compatible model is
           available).
        3. **Rule-based fallback** – delegates to
           :class:`rag.integration.RAGEnhancedAgent` (which in turn uses
           the rule-based :class:`agent.CodeGenerationAgent`) whenever the
           LLM is unavailable.

    Configuration
    ~~~~~~~~~~~~~
    * Set ``MCFG_LLM`` to override the default LLM.
    * Set ``HUGGING_FACE_HUB_TOKEN`` for gated models.
    * If neither is set the system uses ``mistralai/Mistral-7B-Instruct-v0.2``
      and falls back silently on any load failure.

    Example::

        system = EnhancedRAGSystem()
        code = system.generate_code("Create a REST API with authentication")
    """

    def __init__(
        self,
        llm_model: Optional[str] = None,
        use_rag: bool = True,
        use_llm: bool = True,
    ) -> None:
        """
        Initialize the enhanced RAG system.

        Args:
            llm_model: Hugging Face model identifier. Defaults to the value
                       of the ``MCFG_LLM`` environment variable, or
                       ``mistralai/Mistral-7B-Instruct-v0.2`` if unset.
            use_rag:   Enable RAG retrieval (requires a built index).
            use_llm:   Attempt to load and use the LLM pipeline.
        """
        self.llm_model: str = llm_model or DEFAULT_LLM_MODEL
        self.use_rag = use_rag
        self.use_llm = use_llm
        self._llm_pipeline: Optional[Any] = None
        self._rag_agent: Optional[Any] = None
        self.llm_available: bool = False

        self._setup_rag_agent()
        if self.use_llm:
            self._setup_llm()

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def _setup_rag_agent(self) -> None:
        """Initialize the underlying RAGEnhancedAgent (fallback engine)."""
        try:
            from rag.integration import RAGEnhancedAgent  # noqa: PLC0415

            self._rag_agent = RAGEnhancedAgent(use_rag=self.use_rag)
            logger.info("RAGEnhancedAgent initialized (fallback ready).")
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(
                "Failed to initialize RAGEnhancedAgent: %s. "
                "Code generation will be unavailable.",
                exc,
            )

    def _setup_llm(self) -> None:
        """Initialize the LLM pipeline; set ``llm_available`` accordingly."""
        self._llm_pipeline = _load_llm_pipeline(self.llm_model)
        self.llm_available = self._llm_pipeline is not None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate_code(
        self,
        requirements: str,
        context: Optional[Dict[str, Any]] = None,
        refinement_passes: int = 5,
        max_new_tokens: int = 1024,
    ) -> str:
        """
        Generate code from natural-language requirements.

        When the LLM is available the method:
            1. Retrieves relevant RAG context (if available).
            2. Builds a prompt combining the context and requirements.
            3. Calls the LLM to produce a code completion.

        When the LLM is *not* available the call is transparently delegated
        to the rule-based :class:`rag.integration.RAGEnhancedAgent`.

        Args:
            requirements:     Natural-language description of the code to
                              generate.
            context:          Optional extra context dict forwarded to the
                              fallback agent.
            refinement_passes: Number of iterative refinement passes used by
                              the fallback agent (ignored when the LLM is
                              active).
            max_new_tokens:   Maximum number of tokens the LLM should
                              generate.

        Returns:
            Generated source code as a string.
        """
        if self.llm_available and self._llm_pipeline is not None:
            return self._generate_with_llm(requirements, max_new_tokens)
        return self._generate_with_fallback(requirements, context, refinement_passes)

    def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyse requirements using the underlying RAGEnhancedAgent.

        Args:
            requirements: Natural-language requirements string.

        Returns:
            Analysis dictionary (see :meth:`rag.integration.RAGEnhancedAgent.analyze_requirements`).
        """
        if self._rag_agent is None:
            return {"error": "RAGEnhancedAgent not available", "requirements": requirements}
        return self._rag_agent.analyze_requirements(requirements)

    def get_status(self) -> Dict[str, Any]:
        """
        Return a summary of component availability.

        Returns:
            Dict with keys ``llm_available``, ``llm_model``,
            ``rag_available``, and ``fallback_available``.
        """
        rag_available = (
            self._rag_agent is not None and getattr(self._rag_agent, "rag_available", False)
        )
        return {
            "llm_available": self.llm_available,
            "llm_model": self.llm_model,
            "rag_available": rag_available,
            "fallback_available": self._rag_agent is not None,
        }

    # ------------------------------------------------------------------
    # Private generation methods
    # ------------------------------------------------------------------

    def _build_llm_prompt(self, requirements: str, rag_context: str) -> str:
        """
        Build a prompt string for the LLM.

        Args:
            requirements: User requirements.
            rag_context:  Optionally retrieved RAG examples.

        Returns:
            Formatted prompt string.
        """
        parts: List[str] = []
        if rag_context:
            parts.append(rag_context)
        parts.append(
            f"Generate production-ready Python code for the following requirements:\n"
            f"{requirements}\n\nCode:"
        )
        return "\n\n".join(parts)

    def _generate_with_llm(self, requirements: str, max_new_tokens: int) -> str:
        """
        Generate code using the loaded LLM pipeline.

        Args:
            requirements:  Requirements string.
            max_new_tokens: Token budget for the LLM.

        Returns:
            Generated code string.
        """
        rag_context = ""
        if self._rag_agent is not None and getattr(self._rag_agent, "rag_available", False):
            try:
                rag_context = self._rag_agent._get_rag_context(requirements)  # noqa: SLF001
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("RAG context retrieval failed: %s", exc)

        prompt = self._build_llm_prompt(requirements, rag_context)

        try:
            outputs = self._llm_pipeline(
                prompt,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=1.0,
            )
            generated: str = outputs[0]["generated_text"]
            # Strip the echoed prompt if the model returns it
            if generated.startswith(prompt):
                generated = generated[len(prompt):].lstrip()
            return generated
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning(
                "LLM generation failed: %s. Falling back to rule-based generation.",
                exc,
            )
            return self._generate_with_fallback(requirements, None, 5)

    def _generate_with_fallback(
        self,
        requirements: str,
        context: Optional[Dict[str, Any]],
        refinement_passes: int,
    ) -> str:
        """
        Generate code using the rule-based RAGEnhancedAgent.

        Args:
            requirements:      Requirements string.
            context:           Optional context dict.
            refinement_passes: Number of refinement passes.

        Returns:
            Generated code string, or an error message if the fallback agent
            is also unavailable.
        """
        if self._rag_agent is None:
            logger.error("No code generation backend is available.")
            return "# Error: no code generation backend is available."
        return self._rag_agent.generate_code(
            requirements,
            context=context,
            refinement_passes=refinement_passes,
        )


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def create_enhanced_rag_system(
    llm_model: Optional[str] = None,
    use_rag: bool = True,
    use_llm: bool = True,
) -> EnhancedRAGSystem:
    """
    Factory function for :class:`EnhancedRAGSystem`.

    Args:
        llm_model: Hugging Face model identifier. Uses ``MCFG_LLM`` env var
                   or the public default when ``None``.
        use_rag:   Enable RAG retrieval.
        use_llm:   Attempt to load the LLM pipeline.

    Returns:
        Configured :class:`EnhancedRAGSystem` instance.
    """
    return EnhancedRAGSystem(llm_model=llm_model, use_rag=use_rag, use_llm=use_llm)
