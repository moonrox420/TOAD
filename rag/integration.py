"""
Integration of RAG retrieval with CodeGenerationAgent.

Provides RAGEnhancedAgent that extends the base CodeGenerationAgent
with retrieval-augmented generation capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path for agent import
sys.path.insert(0, str(Path(__file__).parent.parent))

from .config import RAGConfig, get_config
from .retriever import RAGRetriever, RetrievalResult

logger = logging.getLogger(__name__)


class RAGEnhancedAgent:
    """
    CodeGenerationAgent enhanced with RAG retrieval capabilities.
    
    This class wraps the base CodeGenerationAgent and enhances its
    code generation with relevant examples retrieved from the RAG index.
    
    Features:
        - Retrieves relevant coding examples for each request
        - Injects RAG context into the analysis phase
        - Extracts patterns from retrieved examples
        - Falls back gracefully when RAG is unavailable
    
    Example:
        >>> agent = RAGEnhancedAgent()
        >>> code = agent.generate_code("Create a REST API with authentication")
    """
    
    def __init__(
        self,
        name: str = "RAGEnhancedAgent",
        use_rag: bool = True,
        config: Optional[RAGConfig] = None,
        base_agent=None,
    ):
        """
        Initialize the RAG-enhanced agent.
        
        Args:
            name: Agent name
            use_rag: Whether to use RAG enhancement
            config: RAG configuration. If None, uses global config.
            base_agent: Pre-existing CodeGenerationAgent. If None, creates one.
        """
        self.name = name
        self.use_rag = use_rag
        self.config = config or get_config()
        self._retriever: Optional[RAGRetriever] = None
        self._base_agent = base_agent
        self._rag_available = False
        self.last_rag_context: Optional[str] = None
        self.last_rag_patterns: List[str] = []
        
        # Initialize RAG if enabled
        if self.use_rag:
            self._setup_rag()
        
        # Initialize base agent
        self._setup_base_agent()
    
    def _setup_rag(self) -> None:
        """Initialize RAG retriever if index exists."""
        try:
            self._retriever = RAGRetriever(config=self.config)
            self._rag_available = self._retriever.is_available()
            
            if self._rag_available:
                logger.info("RAG retriever initialized successfully")
            else:
                logger.warning(
                    "RAG index not found. Run 'python cli.py rag build' first. "
                    "Continuing without RAG enhancement."
                )
        except Exception as e:
            logger.warning(f"Failed to initialize RAG: {e}. Continuing without RAG.")
            self._rag_available = False
    
    def _setup_base_agent(self) -> None:
        """Initialize the base CodeGenerationAgent."""
        if self._base_agent is None:
            try:
                from agent import CodeGenerationAgent
                self._base_agent = CodeGenerationAgent(name=self.name)
                logger.info("Base CodeGenerationAgent initialized")
            except ImportError as e:
                logger.error(f"Failed to import CodeGenerationAgent: {e}")
                raise ImportError(
                    "CodeGenerationAgent not found. Ensure agent.py is in the TOAD directory."
                ) from e
    
    @property
    def retriever(self) -> Optional[RAGRetriever]:
        """Get the RAG retriever."""
        return self._retriever
    
    @property
    def base_agent(self):
        """Get the base CodeGenerationAgent."""
        return self._base_agent
    
    @property
    def rag_available(self) -> bool:
        """Check if RAG is available."""
        return self._rag_available and self._retriever is not None
    
    def _get_rag_context(
        self,
        requirements: str,
        top_k: Optional[int] = None,
    ) -> str:
        """
        Retrieve RAG context for the given requirements.
        
        Args:
            requirements: The code generation requirements
            top_k: Number of examples to retrieve
            
        Returns:
            Formatted RAG context string
        """
        if not self.rag_available:
            return ""
        
        try:
            top_k = top_k or self.config.retrieval.top_k
            results = self._retriever.retrieve(requirements, top_k=top_k)
            
            if results:
                self.last_rag_context = self._retriever.format_context(results)
                self.last_rag_patterns = self._retriever.get_relevant_patterns(results)
                logger.info(
                    f"Retrieved {len(results)} RAG examples, "
                    f"patterns: {self.last_rag_patterns}"
                )
                return self.last_rag_context
            else:
                logger.debug("No relevant RAG examples found")
                return ""
                
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return ""
    
    def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyze requirements with RAG enhancement.
        
        Extends base analysis with RAG context and detected patterns.
        
        Args:
            requirements: The code generation requirements
            
        Returns:
            Enhanced analysis dictionary
        """
        # Get base analysis
        analysis = self._base_agent.analyze_requirements(requirements)
        
        # Enhance with RAG if available
        if self.use_rag and self.rag_available:
            rag_context = self._get_rag_context(requirements)
            
            analysis["rag_enabled"] = True
            analysis["rag_context"] = rag_context
            analysis["rag_patterns"] = self.last_rag_patterns
            analysis["rag_examples_count"] = len(self.last_rag_patterns)
            
            # Merge RAG patterns with detected patterns
            existing_patterns = analysis.get("parsed_elements", {}).get("patterns", [])
            analysis["parsed_elements"]["patterns"] = list(
                set(existing_patterns + self.last_rag_patterns)
            )
        else:
            analysis["rag_enabled"] = False
            analysis["rag_context"] = ""
            analysis["rag_patterns"] = []
        
        return analysis
    
    def generate_code(
        self,
        requirements: str,
        context: Optional[Dict] = None,
        refinement_passes: int = 5,
        use_rag: Optional[bool] = None,
    ) -> str:
        """
        Generate code with RAG enhancement.
        
        Args:
            requirements: The code generation requirements
            context: Optional additional context
            refinement_passes: Number of refinement passes
            use_rag: Override RAG usage. If None, uses instance setting.
            
        Returns:
            Generated code string
        """
        use_rag = use_rag if use_rag is not None else self.use_rag
        
        # Get RAG context if enabled
        rag_context = ""
        if use_rag and self.rag_available:
            rag_context = self._get_rag_context(requirements)
        
        # Enhance requirements with RAG context
        enhanced_requirements = requirements
        if rag_context:
            enhanced_requirements = f"{requirements}\n\n{rag_context}"
            logger.info("Enhanced requirements with RAG context")
        
        # Generate code using base agent
        code = self._base_agent.generate_code(
            enhanced_requirements,
            context=context,
            refinement_passes=refinement_passes,
        )
        
        return code
    
    def generate_code_with_analysis(
        self,
        requirements: str,
        context: Optional[Dict] = None,
        refinement_passes: int = 5,
    ) -> Dict[str, Any]:
        """
        Generate code and return with analysis.
        
        Args:
            requirements: The code generation requirements
            context: Optional additional context
            refinement_passes: Number of refinement passes
            
        Returns:
            Dictionary with code, analysis, and RAG info
        """
        # Analyze with RAG enhancement
        analysis = self.analyze_requirements(requirements)
        
        # Generate code
        code = self.generate_code(
            requirements,
            context=context,
            refinement_passes=refinement_passes,
        )
        
        # Validate
        validation = self._base_agent._validate_code(code)
        
        return {
            "code": code,
            "analysis": analysis,
            "validation": validation,
            "rag_enabled": analysis.get("rag_enabled", False),
            "rag_patterns": analysis.get("rag_patterns", []),
            "rag_context_used": bool(analysis.get("rag_context")),
        }
    
    # Delegate other methods to base agent
    def __getattr__(self, name):
        """Delegate attribute access to base agent."""
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        return getattr(self._base_agent, name)
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities including RAG."""
        capabilities = list(self._base_agent.skills)
        if self.rag_available:
            capabilities.append("rag_retrieval")
            capabilities.append("example_based_generation")
        return capabilities
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics including RAG stats."""
        stats = {
            "name": self.name,
            "rag_enabled": self.use_rag,
            "rag_available": self.rag_available,
            "base_agent_name": self._base_agent.name,
        }
        
        if self.rag_available and self._retriever:
            stats["rag_stats"] = self._retriever.get_stats()
        
        return stats


def create_enhanced_agent(
    use_rag: bool = True,
    config: Optional[RAGConfig] = None,
) -> RAGEnhancedAgent:
    """
    Factory function to create a RAG-enhanced agent.
    
    Args:
        use_rag: Whether to enable RAG
        config: RAG configuration
        
    Returns:
        Configured RAGEnhancedAgent instance
    """
    return RAGEnhancedAgent(use_rag=use_rag, config=config)


# Convenience function for quick code generation with RAG
def generate_with_rag(
    requirements: str,
    top_k: int = 5,
    refinement_passes: int = 5,
) -> str:
    """
    Generate code with RAG enhancement (convenience function).
    
    Args:
        requirements: The code generation requirements
        top_k: Number of RAG examples to retrieve
        refinement_passes: Number of refinement passes
        
    Returns:
        Generated code string
    """
    config = get_config()
    config.retrieval.top_k = top_k
    
    agent = RAGEnhancedAgent(config=config)
    return agent.generate_code(requirements, refinement_passes=refinement_passes)
