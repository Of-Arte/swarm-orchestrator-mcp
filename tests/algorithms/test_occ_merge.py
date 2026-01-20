import pytest
from mcp_core.algorithms.occ_validator import OCCValidator, OCCStatus


class TestOCCSemanticMerge:
    """Test AST-based merge for concurrent edits."""
    
    def test_disjoint_function_edits_merge_successfully(self):
        """Two agents modify different functions → merge succeeds."""
        validator = OCCValidator()
        
        base = """
def function_a():
    return "original_a"

def function_b():
    return "original_b"
"""
        
        # Agent A modifies function_a
        ours = """
def function_a():
    return "modified_by_agent_a"

def function_b():
    return "original_b"
"""
        
        # Agent B modifies function_b
        theirs = """
def function_a():
    return "original_a"

def function_b():
    return "modified_by_agent_b"
"""
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        assert merged is not None
        assert "modified_by_agent_a" in merged
        assert "modified_by_agent_b" in merged
    
    def test_same_function_edit_conflicts(self):
        """Two agents modify same function → merge fails."""
        validator = OCCValidator()
        
        base = """
def shared_function():
    return "original"
"""
        
        # Agent A modifies
        ours = """
def shared_function():
    return "agent_a_version"
"""
        
        # Agent B also modifies
        theirs = """
def shared_function():
    return "agent_b_version"
"""
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        assert merged is None  # Conflict detected
    
    def test_identical_changes_merge_successfully(self):
        """Two agents make identical changes → no conflict."""
        validator = OCCValidator()
        
        base = """
def function_x():
    return "old"
"""
        
        # Both agents make same change
        ours = theirs = """
def function_x():
    return "new"
"""
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        assert merged is not None
        assert "new" in merged
    
    def test_preserve_imports_and_module_code(self):
        """Merged file preserves imports and module-level statements."""
        validator = OCCValidator()
        
        base = """
import os
from typing import Optional

VERSION = "1.0.0"

def func_a():
    pass

def func_b():
    pass
"""
        
        ours = """
import os
from typing import Optional

VERSION = "1.0.0"

def func_a():
    return "modified"

def func_b():
    pass
"""
        
        theirs = """
import os
from typing import Optional

VERSION = "1.0.0"

def func_a():
    pass

def func_b():
    return "modified"
"""
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        assert merged is not None
        assert "import os" in merged
        assert "from typing import Optional" in merged
        # AST may normalize quotes, check for either style
        assert ("VERSION = \"1.0.0\"" in merged or "VERSION = '1.0.0'" in merged)
    
    def test_non_python_fallback(self):
        """Non-Python files fall back to line-based merge."""
        validator = OCCValidator()
        
        base = "# Not Python\n{ invalid syntax }"
        ours = "# Modified by A\n{ invalid syntax }"
        theirs = "# Modified by B\n{ invalid syntax }"
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        # Should attempt line-based merge (currently returns None)
        assert merged is None
    
    def test_new_function_added_by_one_agent(self):
        """One agent adds a new function → merge succeeds."""
        validator = OCCValidator()
        
        base = """
def existing_func():
    pass
"""
        
        # Agent A adds new function
        ours = """
def existing_func():
    pass

def new_func_from_a():
    return "new"
"""
        
        # Agent B doesn't change anything
        theirs = base
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        assert merged is not None
        assert "new_func_from_a" in merged
        assert "existing_func" in merged
    
    def test_both_agents_add_different_functions(self):
        """Both agents add different new functions → merge succeeds."""
        validator = OCCValidator()
        
        base = """
def original():
    pass
"""
        
        ours = """
def original():
    pass

def added_by_a():
    return "a"
"""
        
        theirs = """
def original():
    pass

def added_by_b():
    return "b"
"""
        
        merged = validator.attempt_semantic_merge(base, ours, theirs)
        
        assert merged is not None
        assert "added_by_a" in merged
        assert "added_by_b" in merged
        assert "original" in merged
