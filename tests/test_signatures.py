"""Test cryptographic signatures for AuthorSignature schema."""
import pytest
from mcp_core.swarm_schemas import AuthorSignature


def test_signature_creation():
    """Test creating a signed author signature."""
    content = "def hello():\n    return 'world'"
    
    sig = AuthorSignature.create(
        agent_id="engineer-001",
        role="engineer",
        action="created",
        content=content
    )
    
    assert sig.agent_id == "engineer-001"
    assert sig.role == "engineer"
    assert sig.action == "created"
    assert sig.content_hash  # Should have a hash
    assert sig.signature  # Should have a signature
    assert len(sig.signature) == 64  # SHA256 is 64 hex chars


def test_signature_verification_success():
    """Test verifying a valid signature."""
    content = "def hello():\n    return 'world'"
    
    sig = AuthorSignature.create(
        agent_id="engineer-001",
        role="engineer",
        action="created",
        content=content
    )
    
    # Verification should succeed with original content
    assert sig.verify(content) is True


def test_signature_verification_tampered_content():
    """Test detecting tampered content."""
    original_content = "def hello():\n    return 'world'"
    tampered_content = "def hello():\n    return 'hacked'"
    
    sig = AuthorSignature.create(
        agent_id="engineer-001",
        role="engineer",
        action="created",
        content=original_content
    )
    
    # Verification should fail with tampered content
    assert sig.verify(tampered_content) is False


def test_signature_deterministic():
    """Test that same input produces same signature."""
    content = "test content"
    
    sig1 = AuthorSignature.create("agent-1", "engineer", "created", content)
    sig2 = AuthorSignature.create("agent-1", "engineer", "created", content)
    
    assert sig1.signature == sig2.signature
    assert sig1.content_hash == sig2.content_hash


def test_different_agents_different_signatures():
    """Test that different agents produce different signatures."""
    content = "test content"
    
    sig1 = AuthorSignature.create("agent-1", "engineer", "created", content)
    sig2 = AuthorSignature.create("agent-2", "engineer", "created", content)
    
    # Same content, different agents = different signatures
    assert sig1.content_hash == sig2.content_hash  # Same content hash
    assert sig1.signature != sig2.signature  # Different signatures
