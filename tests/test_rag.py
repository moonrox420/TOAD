"""
Comprehensive tests for the RAG system components.

Tests embedder, indexer, retriever, and integration modules.
"""

import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import RAGConfig, DatasetConfig, get_config, reset_config
from rag.datasets import (
    CodingDatasetLoader,
    CodeChunk,
    INSTRUCTION_FIELDS,
    RESPONSE_FIELDS,
)


class TestCodingDatasetLoader:
    """Tests for CodingDatasetLoader class."""
    
    def test_init_with_default_config(self):
        """Test initialization with default config."""
        loader = CodingDatasetLoader()
        
        assert loader.config is not None
        assert loader.stats["datasets_loaded"] == 0
    
    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        config = RAGConfig()
        loader = CodingDatasetLoader(config=config)
        
        assert loader.config is config
    
    def test_extract_instruction_response_standard_fields(self):
        """Test extraction with standard field names."""
        loader = CodingDatasetLoader()
        
        row = {
            "instruction": "Write a hello world function",
            "response": "def hello(): print('world')",
        }
        
        instruction, response = loader.extract_instruction_response(row)
        
        assert instruction == "Write a hello world function"
        assert response == "def hello(): print('world')"
    
    def test_extract_instruction_response_alternative_fields(self):
        """Test extraction with alternative field names."""
        loader = CodingDatasetLoader()
        
        row = {
            "prompt": "Create a function",
            "output": "def func(): pass",
        }
        
        instruction, response = loader.extract_instruction_response(row)
        
        assert instruction == "Create a function"
        assert response == "def func(): pass"
    
    def test_extract_instruction_response_missing_fields(self):
        """Test extraction with missing fields."""
        loader = CodingDatasetLoader()
        
        row = {"other_field": "value"}
        
        instruction, response = loader.extract_instruction_response(row)
        
        assert instruction is None
        assert response is None
    
    def test_create_chunk(self):
        """Test chunk creation."""
        loader = CodingDatasetLoader()
        
        chunk = loader.create_chunk(
            instruction="Test task",
            response="Test solution",
            source="test/dataset",
        )
        
        assert isinstance(chunk, CodeChunk)
        assert "Test task" in chunk.text
        assert "Test solution" in chunk.text
        assert "test/dataset" in chunk.text
        assert chunk.source == "test/dataset"
    
    def test_chunk_length_limits(self):
        """Test that chunks respect length limits."""
        loader = CodingDatasetLoader()
        
        long_instruction = "A" * 2000
        long_response = "B" * 5000
        
        chunk = loader.create_chunk(
            instruction=long_instruction,
            response=long_response,
            source="test",
        )
        
        # Instruction should be truncated to 1000 chars
        assert len(chunk.instruction) == 2000  # Original stored
        assert long_instruction[:1000] in chunk.text  # Truncated in text
    
    def test_get_statistics(self):
        """Test statistics retrieval."""
        loader = CodingDatasetLoader()
        
        stats = loader.get_statistics()
        
        assert "datasets_loaded" in stats
        assert "chunks_created" in stats
        assert "rows_processed" in stats
    
    def test_reset_statistics(self):
        """Test statistics reset."""
        loader = CodingDatasetLoader()
        loader.stats["datasets_loaded"] = 5
        
        loader.reset_statistics()
        
        assert loader.stats["datasets_loaded"] == 0


class TestCodeChunk:
    """Tests for CodeChunk dataclass."""
    
    def test_chunk_creation(self):
        """Test basic chunk creation."""
        chunk = CodeChunk(
            text="Test text",
            source="test/source",
            instruction="Test instruction",
            response="Test response",
            metadata={"key": "value"},
        )
        
        assert chunk.text == "Test text"
        assert chunk.source == "test/source"
        assert chunk.metadata["key"] == "value"


class TestCodeEmbedder:
    """Tests for CodeEmbedder class (mocked)."""
    
    @patch("rag.embedder.SentenceTransformer")
    def test_embedder_init(self, mock_st):
        """Test embedder initialization."""
        from rag.embedder import CodeEmbedder
        
        embedder = CodeEmbedder()
        
        # Model should not be loaded until first use
        mock_st.assert_not_called()
    
    @patch("rag.embedder.SentenceTransformer")
    def test_get_dimension(self, mock_st):
        """Test getting embedding dimension."""
        from rag.embedder import CodeEmbedder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model
        
        embedder = CodeEmbedder()
        dim = embedder.get_dimension()
        
        assert dim == 768
    
    @patch("rag.embedder.SentenceTransformer")
    def test_encode_single_text(self, mock_st):
        """Test encoding a single text."""
        from rag.embedder import CodeEmbedder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.random.randn(1, 768).astype("float32")
        mock_st.return_value = mock_model
        
        embedder = CodeEmbedder()
        embeddings = embedder.encode("test text")
        
        assert embeddings.shape == (1, 768)
        assert embeddings.dtype == np.float32
    
    @patch("rag.embedder.SentenceTransformer")
    def test_encode_multiple_texts(self, mock_st):
        """Test encoding multiple texts."""
        from rag.embedder import CodeEmbedder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.random.randn(3, 768).astype("float32")
        mock_st.return_value = mock_model
        
        embedder = CodeEmbedder()
        embeddings = embedder.encode(["text1", "text2", "text3"])
        
        assert embeddings.shape == (3, 768)
    
    @patch("rag.embedder.SentenceTransformer")
    def test_encode_query(self, mock_st):
        """Test encoding a query."""
        from rag.embedder import CodeEmbedder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.random.randn(1, 768).astype("float32")
        mock_st.return_value = mock_model
        
        embedder = CodeEmbedder()
        embedding = embedder.encode_query("test query")
        
        assert embedding.shape == (768,)


class TestRAGIndexBuilder:
    """Tests for RAGIndexBuilder class (mocked)."""
    
    @patch("rag.indexer.faiss")
    @patch("rag.embedder.SentenceTransformer")
    def test_index_creation(self, mock_st, mock_faiss):
        """Test index creation."""
        from rag.indexer import RAGIndexBuilder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model
        
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        builder = RAGIndexBuilder()
        _ = builder.index
        
        mock_faiss.IndexFlatIP.assert_called_once_with(768)
    
    @patch("rag.indexer.faiss")
    @patch("rag.embedder.SentenceTransformer")
    def test_add_vectors(self, mock_st, mock_faiss):
        """Test adding vectors to index."""
        from rag.indexer import RAGIndexBuilder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model
        
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        builder = RAGIndexBuilder()
        embeddings = np.random.randn(5, 768).astype("float32")
        texts = ["text1", "text2", "text3", "text4", "text5"]
        
        builder.add_vectors(embeddings, texts)
        
        mock_index.add.assert_called_once()
        assert len(builder._metadata) == 5
    
    @patch("rag.indexer.faiss")
    @patch("rag.embedder.SentenceTransformer")
    def test_get_stats(self, mock_st, mock_faiss):
        """Test getting index statistics."""
        from rag.indexer import RAGIndexBuilder
        
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_st.return_value = mock_model
        
        mock_index = Mock()
        mock_index.ntotal = 100
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        builder = RAGIndexBuilder()
        _ = builder.index
        
        stats = builder.get_stats()
        
        assert stats["total_vectors"] == 100
        assert stats["dimension"] == 768


class TestRAGRetriever:
    """Tests for RAGRetriever class."""
    
    def test_retriever_not_available_without_index(self):
        """Test retriever is not available without index."""
        from rag.retriever import RAGRetriever
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RAGConfig()
            config.paths.index_dir = Path(tmpdir)
            
            retriever = RAGRetriever(config=config)
            
            assert retriever.is_available() is False
    
    def test_format_context_empty_results(self):
        """Test formatting empty results."""
        from rag.retriever import RAGRetriever
        
        retriever = RAGRetriever()
        context = retriever.format_context([])
        
        assert context == ""
    
    def test_get_relevant_patterns(self):
        """Test pattern extraction from results."""
        from rag.retriever import RAGRetriever, RetrievalResult
        
        retriever = RAGRetriever()
        
        results = [
            RetrievalResult(
                text="from fastapi import FastAPI\n@app.route\nasync def",
                score=0.9,
                rank=1,
            ),
            RetrievalResult(
                text="import pytest\ndef test_something():",
                score=0.8,
                rank=2,
            ),
        ]
        
        patterns = retriever.get_relevant_patterns(results)
        
        assert "api" in patterns
        assert "async" in patterns
        assert "testing" in patterns


class TestRetrievalResult:
    """Tests for RetrievalResult dataclass."""
    
    def test_result_creation(self):
        """Test basic result creation."""
        from rag.retriever import RetrievalResult
        
        result = RetrievalResult(
            text="Test text",
            score=0.95,
            rank=1,
        )
        
        assert result.text == "Test text"
        assert result.score == 0.95
        assert result.rank == 1
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        from rag.retriever import RetrievalResult
        
        result = RetrievalResult(
            text="Test text",
            score=0.95,
            rank=1,
            source="test/source",
        )
        
        d = result.to_dict()
        
        assert d["text"] == "Test text"
        assert d["score"] == 0.95
        assert d["source"] == "test/source"
    
    def test_result_parse_chunk(self):
        """Test parsing chunk text."""
        from rag.retriever import RetrievalResult
        
        chunk_text = """ELITE CODING REFERENCE
Source: test/dataset
Task: Write a hello function
Elite Solution & Reasoning:
def hello():
    print("Hello, World!")
"""
        
        result = RetrievalResult(text=chunk_text, score=0.9, rank=1)
        
        assert result.source == "test/dataset"
        assert "Write a hello function" in result.instruction
        assert "def hello():" in result.response


class TestRAGEnhancedAgent:
    """Tests for RAGEnhancedAgent class (mocked)."""
    
    @patch("rag.integration.RAGRetriever")
    @patch("rag.integration.CodeGenerationAgent")
    def test_agent_init_without_rag(self, mock_agent, mock_retriever):
        """Test agent initialization without RAG."""
        from rag.integration import RAGEnhancedAgent
        
        mock_retriever_instance = Mock()
        mock_retriever_instance.is_available.return_value = False
        mock_retriever.return_value = mock_retriever_instance
        
        mock_agent_instance = Mock()
        mock_agent_instance.name = "TestAgent"
        mock_agent_instance.skills = {"code_generation"}
        mock_agent.return_value = mock_agent_instance
        
        agent = RAGEnhancedAgent(use_rag=False)
        
        assert agent.use_rag is False
    
    @patch("rag.integration.RAGRetriever")
    @patch("rag.integration.CodeGenerationAgent")
    def test_get_capabilities_with_rag(self, mock_agent, mock_retriever):
        """Test getting capabilities with RAG enabled."""
        from rag.integration import RAGEnhancedAgent
        
        mock_retriever_instance = Mock()
        mock_retriever_instance.is_available.return_value = True
        mock_retriever.return_value = mock_retriever_instance
        
        mock_agent_instance = Mock()
        mock_agent_instance.name = "TestAgent"
        mock_agent_instance.skills = {"code_generation", "testing"}
        mock_agent.return_value = mock_agent_instance
        
        agent = RAGEnhancedAgent(use_rag=True)
        agent._rag_available = True
        
        capabilities = agent.get_capabilities()
        
        assert "code_generation" in capabilities
        assert "rag_retrieval" in capabilities


class TestIntegrationWorkflow:
    """Integration tests for the complete RAG workflow."""
    
    @patch("rag.indexer.faiss")
    @patch("rag.embedder.SentenceTransformer")
    def test_build_and_search_workflow(self, mock_st, mock_faiss):
        """Test complete build and search workflow."""
        from rag.indexer import RAGIndexBuilder
        
        # Setup mocks
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_model.encode.return_value = np.random.randn(3, 768).astype("float32")
        mock_st.return_value = mock_model
        
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.search.return_value = (
            np.array([[0.9, 0.8, 0.7]]),
            np.array([[0, 1, 2]]),
        )
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        # Build index
        builder = RAGIndexBuilder()
        texts = ["text1", "text2", "text3"]
        builder.build_from_texts(texts)
        
        # Search
        query_embedding = np.random.randn(768).astype("float32")
        scores, indices, result_texts = builder.search(query_embedding, k=3)
        
        assert len(scores) == 3
        assert len(result_texts) == 3
