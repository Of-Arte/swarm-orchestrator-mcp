"""
CodeAuditorRole: Autonomous code quality and documentation scanning.

This role identifies bugs, code smells, outdated documentation, and security
anti-patterns through static analysis and graph-based code understanding.
"""

from typing import Any, Dict, List
from .base import GitAgentRole, GitRole, ExitReport


class CodeAuditorRole(GitAgentRole):
    """
    Autonomous code quality auditor.
    
    Responsibilities:
    - Scan recently updated files via HippoRAG
    - Run static analysis (lint,type checks)
    - Identify unused imports, dead code, outdated docs
    - Generate audit report in memory_bank
    - Flag priority items for immediate fix
    """
    
    def __init__(self):
        super().__init__(GitRole.CODE_AUDITOR)
    
    def trigger_check(self, task: Any, context: Dict[str, Any]) -> bool:
        """
        Trigger on code_audit flag or periodic scan.
        
        Args:
            task: Task object
            context: Execution context
            
        Returns:
            True if audit should run
        """
        if hasattr(task, 'code_audit') and task.code_audit:
            return True
        
        if context.get('periodic_audit', False):
            return True
        
        return False
    
    def execute(self, task: Any, context: Dict[str, Any]) -> ExitReport:
        """
        Execute code audit workflow.
        
        Steps:
        1. Retrieve recently updated files
        2. Run static analysis
        3. Identify issues
        4. Generate report
        5. Flag priorities
        
        Args:
            task: Task object
            context: Execution context
            
        Returns:
            ExitReport with audit findings
        """
        warnings = []
        findings: List[Dict[str, Any]] = []
        
        # Step 1: Get recently updated files
        hipporag = context.get('hipporag_client')
        if hipporag:
            recent_files = self._get_recent_files(hipporag, context)
        else:
            warnings.append("HippoRAG not available - using git status")
            recent_files = self._get_files_from_git(context)
        
        # Step 2: Run static analysis
        for file_path in recent_files:
            file_findings = self._analyze_file(file_path, context)
            findings.extend(file_findings)
        
        # Step 3: Categorize by severity
        critical_findings = [f for f in findings if f.get('severity') == 'critical']
        high_findings = [f for f in findings if f.get('severity') == 'high']
        
        # Step 4: Generate report
        report = self._generate_report(findings, context)
        
        # Step 5: Flag priority items
        priority_tasks = self._create_priority_tasks(critical_findings + high_findings, context)
        
        return ExitReport(
            task_id=task.task_id if hasattr(task, 'task_id') else "unknown",
            status="COMPLETED",
            files_touched=recent_files,
            remaining_work=f"Found {len(findings)} issues ({len(critical_findings)} critical). Created {len(priority_tasks)} priority tasks.",
            warnings=warnings
        )
    
    def _get_recent_files(self, hipporag, context: Dict[str, Any]) -> List[str]:
        """Get list of recently modified files from HippoRAG."""
        # Placeholder: would query graph for recent modifications
        return []
    
    def _get_files_from_git(self, context: Dict[str, Any]) -> List[str]:
        """Fallback: get modified files from git status."""
        # Placeholder: would use GitWorker to get status
        return []
    
    def _analyze_file(self, file_path: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a single file for issues.
        
        Checks for:
        - Unused imports
        - Dead code
        - Outdated docstrings
        - Security anti-patterns
        
        Returns:
            List of finding dictionaries
        """
        findings = []
        
        # Placeholder: would integrate with linters, type checkers
        # Example finding structure:
        # {
        #     "file": file_path,
        #     "line": 42,
        #     "severity": "high",
        #     "category": "security",
        #     "message": "Hardcoded credential detected"
        # }
        
        return findings
    
    def _generate_report(self, findings: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Generate structured audit report for memory_bank."""
        # Placeholder: would format findings into markdown report
        return f"Code Audit Report: {len(findings)} findings"
    
    def _create_priority_tasks(self, findings: List[Dict[str, Any]], context: Dict[str, Any]) -> List[str]:
        """Create tasks for priority findings."""
        # Placeholder: would insert into task_queue
        return []
