"""
HuggingFace dataset loading and processing for RAG system.

Loads elite coding datasets, extracts instruction-response pairs,
and creates formatted chunks for embedding and indexing.
"""

import logging
from typing import Dict, List, Optional, Tuple, Generator, Any
from dataclasses import dataclass

from .config import RAGConfig, DatasetConfig, CHUNK_TEMPLATE, get_config

logger = logging.getLogger(__name__)

# Field names to search for instruction content
INSTRUCTION_FIELDS = [
    "instruction",
    "input", 
    "prompt",
    "question",
    "text",
    "query",
    "problem",
    "task",
]

# Field names to search for response content
RESPONSE_FIELDS = [
    "response",
    "output",
    "answer",
    "code",
    "solution",
    "completion",
    "result",
    "generated",
]


@dataclass
class CodeChunk:
    """A processed code chunk ready for embedding."""
    text: str
    source: str
    instruction: str
    response: str
    metadata: Dict[str, Any]


class CodingDatasetLoader:
    """
    Loads and processes coding datasets from HuggingFace.
    
    This class handles:
    - Loading datasets from HuggingFace Hub
    - Extracting instruction-response pairs from various schema formats
    - Creating formatted chunks for embedding
    - Graceful handling of gated/unavailable datasets
    
    Example:
        >>> loader = CodingDatasetLoader()
        >>> for chunk in loader.load_all_chunks():
        ...     print(chunk.text[:100])
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize the dataset loader.
        
        Args:
            config: RAG configuration. If None, uses global config.
        """
        self.config = config or get_config()
        self.stats: Dict[str, int] = {
            "datasets_loaded": 0,
            "datasets_failed": 0,
            "chunks_created": 0,
            "rows_processed": 0,
            "rows_skipped": 0,
        }
    
    def load_dataset_safe(self, dataset_config: DatasetConfig) -> Optional[Any]:
        """
        Safely load a dataset with error handling.
        
        Args:
            dataset_config: Configuration for the dataset to load
            
        Returns:
            Loaded dataset or None if loading failed
        """
        try:
            from datasets import load_dataset
            
            logger.info(f"Loading dataset: {dataset_config.name}")
            
            # Load with optional sample limit
            if dataset_config.max_samples:
                ds = load_dataset(
                    dataset_config.name,
                    split=f"{dataset_config.split}[:{dataset_config.max_samples}]",
                    cache_dir=str(self.config.paths.cache_dir),
                )
            else:
                ds = load_dataset(
                    dataset_config.name,
                    split=dataset_config.split,
                    cache_dir=str(self.config.paths.cache_dir),
                )
            
            logger.info(f"Successfully loaded {dataset_config.name}: {len(ds)} examples")
            self.stats["datasets_loaded"] += 1
            return ds
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "gated" in error_msg or "authentication" in error_msg:
                logger.warning(
                    f"Dataset {dataset_config.name} is gated. "
                    "Run 'huggingface-cli login' and accept terms on HF.co"
                )
            elif "not found" in error_msg or "doesn't exist" in error_msg:
                logger.warning(f"Dataset {dataset_config.name} not found")
            else:
                logger.error(f"Failed to load {dataset_config.name}: {e}")
            
            self.stats["datasets_failed"] += 1
            return None
    
    def extract_instruction_response(
        self, row: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract instruction and response from a dataset row.
        
        Handles various schema formats by searching for common field names.
        
        Args:
            row: A single row from the dataset
            
        Returns:
            Tuple of (instruction, response) or (None, None) if extraction fails
        """
        instruction = None
        response = None
        
        # Find instruction field
        for field in INSTRUCTION_FIELDS:
            if field in row and row[field]:
                instruction = str(row[field]).strip()
                break
        
        # Find response field
        for field in RESPONSE_FIELDS:
            if field in row and row[field]:
                response = str(row[field]).strip()
                break
        
        # Handle combined text fields (e.g., "text" containing both)
        if instruction and not response:
            # Check if instruction contains a response marker
            markers = ["### Response:", "### Answer:", "### Output:", "```"]
            for marker in markers:
                if marker in instruction:
                    parts = instruction.split(marker, 1)
                    if len(parts) == 2:
                        instruction = parts[0].strip()
                        response = marker + parts[1].strip()
                        break
        
        return instruction, response
    
    def create_chunk(
        self,
        instruction: str,
        response: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CodeChunk:
        """
        Create a formatted chunk for embedding.
        
        Args:
            instruction: The coding task/question
            response: The solution/code
            source: Dataset source name
            metadata: Optional additional metadata
            
        Returns:
            CodeChunk object with formatted text
        """
        # Format the chunk text using the template
        text = CHUNK_TEMPLATE.format(
            source=source,
            instruction=instruction[:1000],  # Limit instruction length
            response=response[:4000],  # Limit response length
        )
        
        return CodeChunk(
            text=text,
            source=source,
            instruction=instruction,
            response=response,
            metadata=metadata or {},
        )
    
    def process_dataset(
        self, dataset: Any, source: str
    ) -> Generator[CodeChunk, None, None]:
        """
        Process a loaded dataset and yield chunks.
        
        Args:
            dataset: Loaded HuggingFace dataset
            source: Dataset source name
            
        Yields:
            CodeChunk objects for each valid row
        """
        for idx, row in enumerate(dataset):
            try:
                instruction, response = self.extract_instruction_response(row)
                
                if instruction and response:
                    chunk = self.create_chunk(
                        instruction=instruction,
                        response=response,
                        source=source,
                        metadata={"row_index": idx},
                    )
                    self.stats["chunks_created"] += 1
                    self.stats["rows_processed"] += 1
                    yield chunk
                else:
                    self.stats["rows_skipped"] += 1
                    
            except Exception as e:
                logger.debug(f"Error processing row {idx} from {source}: {e}")
                self.stats["rows_skipped"] += 1
    
    def load_all_chunks(self) -> Generator[CodeChunk, None, None]:
        """
        Load all enabled datasets and yield chunks.
        
        This is the main entry point for loading data for indexing.
        
        Yields:
            CodeChunk objects from all enabled datasets
        """
        enabled_datasets = self.config.get_enabled_datasets()
        logger.info(f"Loading {len(enabled_datasets)} datasets...")
        
        for ds_config in enabled_datasets:
            dataset = self.load_dataset_safe(ds_config)
            
            if dataset is not None:
                yield from self.process_dataset(dataset, ds_config.name)
    
    def load_all_texts(self) -> Generator[str, None, None]:
        """
        Load all chunks and yield just the text content.
        
        Convenience method for indexing where only text is needed.
        
        Yields:
            Text content of each chunk
        """
        for chunk in self.load_all_chunks():
            yield chunk.text
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get loading statistics.
        
        Returns:
            Dictionary with loading statistics
        """
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset the statistics counters."""
        self.stats = {
            "datasets_loaded": 0,
            "datasets_failed": 0,
            "chunks_created": 0,
            "rows_processed": 0,
            "rows_skipped": 0,
        }


def load_datasets_to_list(
    config: Optional[RAGConfig] = None,
    max_chunks: Optional[int] = None,
) -> Tuple[List[str], Dict[str, int]]:
    """
    Convenience function to load all datasets into a list.
    
    Args:
        config: RAG configuration. If None, uses global config.
        max_chunks: Maximum number of chunks to load. If None, load all.
        
    Returns:
        Tuple of (list of chunk texts, statistics dict)
    """
    loader = CodingDatasetLoader(config)
    texts = []
    
    for chunk in loader.load_all_chunks():
        texts.append(chunk.text)
        
        if max_chunks and len(texts) >= max_chunks:
            logger.info(f"Reached max_chunks limit: {max_chunks}")
            break
    
    return texts, loader.get_statistics()
