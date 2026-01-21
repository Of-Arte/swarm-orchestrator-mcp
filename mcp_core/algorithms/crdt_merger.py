"""
CRDT Merger - Conflict-Free Replicated Data Types

Implements YATA Sequence CRDTs from v3.0 spec Section 2.5
using pycrdt (Python bindings to Yrs).
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

try:
    import pycrdt
    PYCRDT_AVAILABLE = True
except ImportError:
    PYCRDT_AVAILABLE = False
    logging.warning(
        "pycrdt not installed. CRDT functionality disabled. "
        "Install with: pip install pycrdt>=0.9.0"
    )

logger = logging.getLogger(__name__)

def _get_pycrdt_version_tuple():
    try:
        import pycrdt
        v = getattr(pycrdt, "__version__", "0.0.0")
        return tuple(map(int, v.split('.')[:3]))
    except (ImportError, ValueError):
        return (0, 0, 0)

_PYCRDT_VERSION_TUPLE = _get_pycrdt_version_tuple()
_IS_PYCRDT_NEW = _PYCRDT_VERSION_TUPLE >= (0, 12, 0)


@dataclass
class CRDTDocument:
    """Wrapper for a pycrdt document with metadata"""
    doc_id: str
    doc: 'pycrdt.Doc'
    text: 'pycrdt.Text'


class CRDTMerger:
    """
    Conflict-free text merging using YATA sequences.
    
    Provides strong eventual consistency for multi-agent collaborative editing.
    Each character has a unique ID (agent_id, position), ensuring no interleaving.
    """

    def __init__(self):
        """Initialize CRDT merger with document registry"""
        if not PYCRDT_AVAILABLE:
            raise ImportError(
                "pycrdt is required for CRDT functionality. "
                "Install with: pip install pycrdt>=0.9.0"
            )
        
        self.documents: Dict[str, CRDTDocument] = {}
    
    def create_document(self, doc_id: str, initial_content: str = "") -> None:
        """
        Initialize a new CRDT document.
        
        Args:
            doc_id: Unique identifier for document
            initial_content: Optional initial text content
        """
        if doc_id in self.documents:
            logger.warning(f"Document {doc_id} already exists, skipping creation")
            return
        
        doc = pycrdt.Doc()
        text = doc.get("content", type=pycrdt.Text)
        
        if initial_content:
            text += initial_content
        
        self.documents[doc_id] = CRDTDocument(
            doc_id=doc_id,
            doc=doc,
            text=text
        )
        
        logger.info(f"Created CRDT document: {doc_id}")
    
    def apply_update(self, doc_id: str, update: bytes) -> None:
        """
        Apply a binary update vector from an agent.
        
        Args:
            doc_id: Document identifier
            update: Binary encoded update from pycrdt
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        crdt_doc = self.documents[doc_id]
        
        # Apply the update to the document
        # pycrdt handles merging automatically via YATA
        if _IS_PYCRDT_NEW:
            crdt_doc.doc.apply_update(update)
        else:
            pycrdt.apply_update(crdt_doc.doc, update)
        
        logger.debug(f"Applied update to {doc_id}: {len(update)} bytes")
    
    def get_state(self, doc_id: str) -> str:
        """
        Get current merged text state.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Current text content after all merges
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        crdt_doc = self.documents[doc_id]
        return str(crdt_doc.text)
    
    def get_update_vector(self, doc_id: str) -> bytes:
        """
        Get binary diff for syncing to other replicas.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Binary encoded update vector
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        crdt_doc = self.documents[doc_id]
        
        # Get update representing current state
        if _IS_PYCRDT_NEW:
            update = crdt_doc.doc.get_update()
        else:
            update = pycrdt.encode_state_as_update(crdt_doc.doc)
        
        return update
    
    def insert_text(
        self,
        doc_id: str,
        position: int,
        text: str
    ) -> bytes:
        """
        Insert text at position and return update vector.
        
        Args:
            doc_id: Document identifier
            position: Character position for insertion
            text: Text to insert
            
        Returns:
            Binary update vector representing this change
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        crdt_doc = self.documents[doc_id]
        
        # Record state before change
        if _IS_PYCRDT_NEW:
            before_state = crdt_doc.doc.get_state()
        else:
            before_state = pycrdt.encode_state_vector(crdt_doc.doc)
        
        # Insert text
        crdt_doc.text[position:position] = text
        
        # Get diff since before_state
        if _IS_PYCRDT_NEW:
            update = crdt_doc.doc.get_update(before_state)
        else:
            update = pycrdt.encode_state_as_update(crdt_doc.doc, before_state)
        
        logger.debug(f"Inserted {len(text)} chars at pos {position} in {doc_id}")
        
        return update
    
    def delete_text(
        self,
        doc_id: str,
        start: int,
        end: int
    ) -> bytes:
        """
        Delete text range and return update vector.
        
        Args:
            doc_id: Document identifier
            start: Start position (inclusive)
            end: End position (exclusive)
            
        Returns:
            Binary update vector representing this change
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        crdt_doc = self.documents[doc_id]
        
        # Record state before change
        if _IS_PYCRDT_NEW:
            before_state = crdt_doc.doc.get_state()
        else:
            before_state = pycrdt.encode_state_vector(crdt_doc.doc)
        
        # Delete range
        del crdt_doc.text[start:end]
        
        # Get diff since before_state
        if _IS_PYCRDT_NEW:
            update = crdt_doc.doc.get_update(before_state)
        else:
            update = pycrdt.encode_state_as_update(crdt_doc.doc, before_state)
        
        logger.debug(f"Deleted chars [{start}:{end}] in {doc_id}")
        
        return update
    
    def get_history_length(self, doc_id: str) -> int:
        """
        Get number of operations in document history.
        
        Useful for time-travel and provenance tracking.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Number of operations
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")
        
        crdt_doc = self.documents[doc_id]
        
        # Get total number of structural updates
        # This reflects the collaborative editing history
        if _IS_PYCRDT_NEW:
            return len(crdt_doc.doc.get_update())
        else:
            return len(pycrdt.encode_state_as_update(crdt_doc.doc))
    
    def destroy_document(self, doc_id: str) -> None:
        """
        Remove document from registry.
        
        Args:
            doc_id: Document identifier
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            logger.info(f"Destroyed CRDT document: {doc_id}")
