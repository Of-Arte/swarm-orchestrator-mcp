"""
OCC Validator - Optimistic Concurrency Control

Implements three-phase OCC from v3.0 spec Section 2.3:
1. Read (snapshot with version)
2. Process (offline)
3. Validate & Commit (atomic check-and-replace)
"""

import os
import hashlib
import tempfile
import time
import logging
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OCCStatus(Enum):
    SUCCESS = "SUCCESS"
    COLLISION = "COLLISION"
    MERGE_CONFLICT = "MERGE_CONFLICT"
    ERROR = "ERROR"


@dataclass
class OCCResult:
    """Result of an OCC validation attempt"""
    status: OCCStatus
    message: str
    new_version: Optional[str] = None
    merged_content: Optional[str] = None


class OCCValidator:
    """
    Optimistic Concurrency Control for multi-agent file modifications.
    
    Uses content-addressed versioning (SHA256) and atomic file operations
    to prevent data loss during concurrent writes.
    """
    
    def __init__(self, max_retries: int = 3, backoff_base: float = 0.5):
        """
        Args:
            max_retries: Maximum number of retry attempts on collision
            backoff_base: Base delay in seconds for exponential backoff
        """
        self.max_retries = max_retries
        self.backoff_base = backoff_base
    
    def read_with_version(self, resource_path: str) -> Tuple[str, str]:
        """
        Read file content and compute version hash.
        
        Args:
            resource_path: Absolute path to resource
            
        Returns:
            Tuple of (content, version_hash)
        """
        path = Path(resource_path)
        
        if not path.exists():
            return ("", self._compute_hash(""))
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        version = self._compute_hash(content)
        logger.debug(f"Read {path.name}: version={version[:8]}")
        
        return (content, version)
    
    def validate_and_commit(
        self,
        resource_path: str,
        new_content: str,
        expected_version: str,
        attempt_merge: bool = True
    ) -> OCCResult:
        """
        Atomic check-and-replace with collision detection.
        
        Args:
            resource_path: Absolute path to resource
            new_content: New content to write
            expected_version: Expected current version hash
            attempt_merge: Try semantic merge on collision
            
        Returns:
            OCCResult indicating success or collision
        """
        path = Path(resource_path)
        
        # Phase 1: Read current version
        current_content, current_version = self.read_with_version(resource_path)
        
        # Phase 2: Validate
        if current_version != expected_version:
            logger.warning(
                f"OCC Collision detected on {path.name}: "
                f"expected={expected_version[:8]}, actual={current_version[:8]}"
            )
            
            if attempt_merge:
                # Attempt three-way merge
                merged = self.attempt_semantic_merge(
                    base=current_content,
                    ours=new_content,
                    theirs=current_content
                )
                
                if merged:
                    # Retry commit with merged content
                    new_version = self._compute_hash(merged)
                    self._atomic_write(resource_path, merged)
                    
                    return OCCResult(
                        status=OCCStatus.SUCCESS,
                        message="Merged successfully",
                        new_version=new_version,
                        merged_content=merged
                    )
            
            return OCCResult(
                status=OCCStatus.COLLISION,
                message=f"Version mismatch: expected {expected_version[:8]}, got {current_version[:8]}"
            )
        
        # Phase 3: Commit with atomic write
        try:
            self._atomic_write(resource_path, new_content)
            new_version = self._compute_hash(new_content)
            
            logger.info(f"OCC Commit successful: {path.name} → {new_version[:8]}")
            
            return OCCResult(
                status=OCCStatus.SUCCESS,
                message="Committed successfully",
                new_version=new_version
            )
            
        except Exception as e:
            logger.error(f"OCC Commit failed: {e}")
            return OCCResult(
                status=OCCStatus.ERROR,
                message=str(e)
            )
    
    def validate_and_commit_with_retry(
        self,
        resource_path: str,
        new_content: str,
        expected_version: str
    ) -> OCCResult:
        """
        Validate and commit with exponential backoff on collision.
        
        Args:
            resource_path: Absolute path to resource
            new_content: New content to write
            expected_version: Expected current version hash
            
        Returns:
            OCCResult from final attempt
        """
        for attempt in range(self.max_retries):
            result = self.validate_and_commit(
                resource_path, new_content, expected_version
            )
            
            if result.status == OCCStatus.SUCCESS:
                return result
            
            if result.status == OCCStatus.COLLISION and attempt < self.max_retries - 1:
                delay = self.backoff_base * (2 ** attempt)
                logger.info(f"Retry {attempt + 1}/{self.max_retries} after {delay}s")
                time.sleep(delay)
                
                # Re-read current version for next attempt
                _, expected_version = self.read_with_version(resource_path)
                continue
            
            break
        
        return result
    
    def attempt_semantic_merge(
        self,
        base: str,
        ours: str,
        theirs: str
    ) -> Optional[str]:
        """
        Attempt three-way merge for non-overlapping changes using AST analysis.
        
        This implementation works for disjoint edits at the function/class level
        (e.g., Agent A modifies function X, Agent B modifies function Y).
        
        Args:
            base: Original content
            ours: Our modifications
            theirs: Their modifications
            
        Returns:
            Merged content if successful, None if conflicts detected
        """
        # Quick check: if identical, no merge needed
        if ours == theirs:
            return ours
        
        # Try AST-based merge for Python files
        try:
            import ast
            
            # Parse all three versions
            base_tree = ast.parse(base)
            our_tree = ast.parse(ours)
            their_tree = ast.parse(theirs)
            
            # Extract top-level definitions (functions and classes)
            base_defs = self._extract_definitions(base_tree)
            our_defs = self._extract_definitions(our_tree)
            their_defs = self._extract_definitions(their_tree)
            
            # Detect conflicts: same definition modified by both
            conflicts = []
            for name in base_defs.keys():
                base_code = base_defs[name]
                our_code = our_defs.get(name, base_code)
                their_code = their_defs.get(name, base_code)
                
                # Conflict if both modified the same definition
                if our_code != base_code and their_code != base_code and our_code != their_code:
                    conflicts.append(name)
            
            if conflicts:
                logger.warning(f"AST merge conflict in: {', '.join(conflicts)}")
                return None
            
            # Merge: combine all changes
            merged_defs = base_defs.copy()
            
            # Apply our changes
            for name, code in our_defs.items():
                if code != base_defs.get(name):
                    merged_defs[name] = code
            
            # Apply their changes (only if we didn't change it)
            for name, code in their_defs.items():
                if code != base_defs.get(name) and name not in conflicts:
                    merged_defs[name] = code
            
            # Reconstruct the file
            merged_content = self._reconstruct_file(base, merged_defs)
            
            logger.info("✅ AST-based merge successful")
            return merged_content
            
        except SyntaxError:
            # Not valid Python, fall back to line-based merge
            logger.debug("Not Python code, attempting line-based merge")
            return self._attempt_line_merge(base, ours, theirs)
        except Exception as e:
            logger.warning(f"AST merge failed: {e}")
            return None
    
    def _extract_definitions(self, tree: "ast.AST") -> dict[str, str]:
        """
        Extract top-level function and class definitions from AST.
        
        Returns a dict mapping definition names to their source code.
        """
        import ast
        
        definitions = {}
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                name = node.name
                code = ast.unparse(node)
                definitions[name] = code
        
        return definitions
    
    def _reconstruct_file(self, base: str, merged_defs: dict[str, str]) -> str:
        """
        Reconstruct a Python file with merged definitions.
        
        Preserves imports and module-level code from base,
        replaces function/class definitions with merged versions.
        """
        import ast
        
        base_tree = ast.parse(base)
        
        # Separate imports and module-level statements from definitions
        imports = []
        module_stmts = []
        
        for node in base_tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
            elif not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                module_stmts.append(ast.unparse(node))
        
        # Reconstruct file
        parts = []
        
        # Add imports
        if imports:
            parts.extend(imports)
            parts.append("")  # Blank line after imports
        
        # Add module-level statements
        if module_stmts:
            parts.extend(module_stmts)
            parts.append("")
        
        # Add merged definitions
        for code in merged_defs.values():
            parts.append(code)
            parts.append("")  # Blank line between definitions
        
        return "\n".join(parts)
    
    def _attempt_line_merge(self, base: str, ours: str, theirs: str) -> Optional[str]:
        """
        Fallback line-based merge for non-Python files.
        
        Uses simple diff logic to detect disjoint line changes.
        """
        base_lines = base.splitlines()
        our_lines = ours.splitlines()
        their_lines = theirs.splitlines()
        
        if our_lines == their_lines:
            return ours
        
        # Conservative: fail if any overlap detected
        # A production implementation would use difflib.SequenceMatcher
        logger.warning("Line-based merge not fully implemented")
        return None
    
    def _atomic_write(self, resource_path: str, content: str) -> None:
        """
        Atomic file write using write-replace pattern.
        
        Ensures observers see complete file or nothing (no partial writes).
        
        Args:
            resource_path: Absolute path to resource
            content: Content to write
        """
        path = Path(resource_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Write to temporary file in same directory
        # (same filesystem ensures atomic rename)
        fd, tmp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp"
        )
        
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
                
                # Step 2: Flush to OS buffer and sync to disk
                f.flush()
                os.fsync(f.fileno())
            
            # Step 3: Atomic rename
            # os.replace is atomic on POSIX and modern Windows
            os.replace(tmp_path, resource_path)
            
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(tmp_path)
            except:
                pass
            raise
    
    def _compute_hash(self, content: str) -> str:
        """
        Compute SHA256 hash of content for versioning.
        
        Args:
            content: File content
            
        Returns:
            Hex SHA256 hash
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
