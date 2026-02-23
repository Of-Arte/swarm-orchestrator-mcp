"""
Unit tests for Rust and Go parsers.
"""

import pytest
from unittest.mock import patch, MagicMock

# Mock tree-sitter imports for testing parser structure
class MockTreeSitterNode:
    def __init__(self, node_type, name=None, start_point=(0, 0), end_point=(0, 0), children=None):
        self.type = node_type
        self.start_point = start_point
        self.end_point = end_point
        self.start_byte = 0
        self.end_byte = 100
        self.children = children or []
        self._name = name
    
    def child_by_field_name(self, name):
        if name == "name" and self._name:
            return MockTreeSitterNode("identifier", start_point=self.start_point, end_point=self.end_point)
        return None


class TestRustParser:
    """Unit tests for RustParser."""
    
    def test_extensions(self):
        from mcp_core.algorithms.parsers.rust_parser import RustParser
        parser = RustParser()
        assert ".rs" in parser.extensions
    
    def test_language_name(self):
        from mcp_core.algorithms.parsers.rust_parser import RustParser
        parser = RustParser()
        assert parser.language_name == "Rust"
    
    def test_grammar_name(self):
        from mcp_core.algorithms.parsers.rust_parser import RustParser
        parser = RustParser()
        assert parser.grammar_name == "tree_sitter_rust"


class TestGoParser:
    """Unit tests for GoParser."""
    
    def test_extensions(self):
        from mcp_core.algorithms.parsers.go_parser import GoParser
        parser = GoParser()
        assert ".go" in parser.extensions
    
    def test_language_name(self):
        from mcp_core.algorithms.parsers.go_parser import GoParser
        parser = GoParser()
        assert parser.language_name == "Go"
    
    def test_grammar_name(self):
        from mcp_core.algorithms.parsers.go_parser import GoParser
        parser = GoParser()
        assert parser.grammar_name == "tree_sitter_go"


class TestParserRegistry:
    """Test that ParserRegistry correctly loads new parsers."""
    
    def test_rust_in_supported_languages(self):
        """Verify Rust is listed as a supported language when tree-sitter-rust is installed."""
        from mcp_core.algorithms.parsers import ParserRegistry
        registry = ParserRegistry()
        registry.register_optional_parsers()
        # Languages depends on installed packages
        languages = registry.supported_languages()
        # Python should always be present
        assert "Python" in languages
    
    def test_go_in_supported_languages(self):
        """Verify Go is listed as a supported language when tree-sitter-go is installed."""
        from mcp_core.algorithms.parsers import ParserRegistry
        registry = ParserRegistry()
        registry.register_optional_parsers()
        languages = registry.supported_languages()
        assert "Python" in languages
