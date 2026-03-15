"""
Document Requirement Service for SamvaadAI.

Provides deterministic document requirement prediction for government schemes.
Extracts required documents from scheme metadata with sub-millisecond performance.

Architectural Guarantees:
- Deterministic document extraction from scheme JSON
- Performance-optimized (<1ms per scheme)
- No external dependencies or LLM usage
- Automatic compatibility with new schemes
- Thread-safe operations
"""

from typing import Dict, List, Any
import logging
import time

logger = logging.getLogger(__name__)


class DocumentRequirementService:
    """
    Service for extracting required documents from scheme metadata.
    
    Provides deterministic document prediction by reading from scheme JSON
    required_documents field with guaranteed sub-millisecond performance.
    """
    
    def __init__(self):
        """Initialize the document requirement service."""
        logger.info("DocumentRequirementService initialized")
    
    def get_required_documents(self, scheme: Dict[str, Any]) -> List[str]:
        """
        Extract required documents from a single scheme.
        
        Args:
            scheme: Scheme dictionary containing metadata
            
        Returns:
            List of required document names, empty list if not found
        """
        start_time = time.perf_counter()
        
        try:
            # Handle None or invalid scheme input
            if scheme is None or not isinstance(scheme, dict):
                logger.warning(
                    "Invalid scheme input",
                    extra={
                        "scheme_type": type(scheme).__name__,
                        "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 3)
                    }
                )
                return []
            
            # Extract documents from scheme metadata
            documents = scheme.get("required_documents", [])
            
            # Ensure we return a list even if the field contains other types
            if not isinstance(documents, list):
                logger.warning(
                    "Invalid required_documents field type",
                    extra={
                        "scheme_id": scheme.get("scheme_id", "unknown"),
                        "field_type": type(documents).__name__
                    }
                )
                documents = []
            
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.debug(
                "Documents extracted for scheme",
                extra={
                    "scheme_id": scheme.get("scheme_id", "unknown"),
                    "document_count": len(documents),
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            return documents
            
        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.error(
                "Error extracting documents from scheme",
                extra={
                    "scheme_id": scheme.get("scheme_id", "unknown") if scheme and isinstance(scheme, dict) else "unknown",
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            # Return empty list on error to maintain pipeline stability
            return []
    
    def get_documents_for_schemes(self, schemes: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract required documents for multiple schemes in batch.
        
        Args:
            schemes: List of scheme dictionaries
            
        Returns:
            Dictionary mapping scheme_id to list of required documents
        """
        start_time = time.perf_counter()
        
        try:
            result = {}
            
            for scheme in schemes:
                scheme_id = scheme.get("scheme_id", "")
                documents = self.get_required_documents(scheme)
                result[scheme_id] = documents
            
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(
                "Batch document extraction completed",
                extra={
                    "schemes_processed": len(schemes),
                    "total_documents": sum(len(docs) for docs in result.values()),
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            return result
            
        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.error(
                "Error in batch document extraction",
                extra={
                    "schemes_count": len(schemes) if schemes else 0,
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            # Return empty dict on error to maintain pipeline stability
            return {}
    
    def get_all_unique_documents(self, schemes: List[Dict[str, Any]]) -> List[str]:
        """
        Get deduplicated list of all documents required across schemes.
        
        Args:
            schemes: List of scheme dictionaries
            
        Returns:
            Sorted list of unique document names
        """
        start_time = time.perf_counter()
        
        try:
            all_documents = set()
            
            for scheme in schemes:
                documents = self.get_required_documents(scheme)
                all_documents.update(documents)
            
            # Return sorted list for consistent ordering
            unique_documents = sorted(list(all_documents))
            
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(
                "Unique documents aggregated",
                extra={
                    "schemes_processed": len(schemes),
                    "unique_documents_count": len(unique_documents),
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            return unique_documents
            
        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            
            logger.error(
                "Error aggregating unique documents",
                extra={
                    "schemes_count": len(schemes) if schemes else 0,
                    "error_type": type(e).__name__,
                    "execution_time_ms": round(execution_time_ms, 3)
                }
            )
            
            # Return empty list on error
            return []