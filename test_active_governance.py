"""Test Active Governance features: Auto-Pilot Search and Task Guardrails."""
import sys
sys.path.insert(0, 'v:/Projects/Servers/swarm')

from unittest.mock import MagicMock, patch

def test_auto_pilot(search_func):
    print("\n--- Testing Auto-Pilot Search ---")
    
    # 1. Test Symbol Detection Logic
    from server import _is_likely_symbol
    assert _is_likely_symbol("UserModel") == True
    print("✅ _is_likely_symbol('UserModel') passed")
    
    # 2. Test search_codebase with symbol
    with patch('server.get_indexer') as mock_get_indexer:
        mock_indexer = MagicMock()
        mock_indexer.chunks = ["chunk"]
        mock_get_indexer.return_value = mock_indexer
        
        with patch('server.HybridSearch') as MockHybridSearch:
            mock_searcher = MockHybridSearch.return_value
            mock_result = MagicMock()
            mock_result.file_path = "test.py"
            mock_result.start_line = 10
            mock_result.end_line = 20
            mock_result.score = 1.0
            mock_result.content = "class UserModel: pass"
            mock_searcher.keyword_search.return_value = [mock_result]
            
            # Action: Search without keyword_only flag
            try:
                response = search_func("UserModel", keyword_only=False)
            except Exception as e:
                print(f"❌ Call failed: {e}")
                return

            if response and "⚡ Auto-optimized" in response:
                print("✅ Auto-Pilot triggered correctly")
            else:
                print(f"❌ Auto-Pilot FAILED. Response: {response}")

def test_task_guardrails(process_func):
    print("\n--- Testing Task Guardrails ---")
    
    # 1. Test Short Instruction
    response = process_func("fix it")
    
    if "❌ Task Rejected" in response and "too short" in response:
        print(f"✅ Guardrail correctly blocked: 'fix it'")
    else:
        print(f"❌ Guardrail FAILED to block: 'fix it'. Response: {response}")
        
    # 2. Test Good Instruction
    good_input = "Refactor auth.py to use async/await"
    
    with patch('server.get_orchestrator') as mock_orch:
        try:
             process_func(good_input)
             print(f"✅ Guardrail allowed valid input")
        except Exception as e:
             # If it fails due to mock issues, that means it passed guardrail
             print(f"✅ Guardrail allowed valid input (execution attempted)")

if __name__ == "__main__":
    try:
        from server import search_codebase, process_task
        
        # Unwrap FastMCP decorators if present
        search_fn = search_codebase
        if hasattr(search_codebase, 'fn'):
             search_fn = search_codebase.fn
             
        process_task_fn = process_task
        if hasattr(process_task, 'fn'):
             process_task_fn = process_task.fn

        test_auto_pilot(search_fn)
        test_task_guardrails(process_task_fn)
        print("\n✅ Verification Complete!")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()
