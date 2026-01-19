"""Test the _is_likely_symbol function for correctness."""
import sys
sys.path.insert(0, 'v:/Projects/Servers/swarm')

from server import _is_likely_symbol

# Test cases: (query, expected_result)
test_cases = [
    ('UserModel', True),
    ('calculate_tax', True),
    ('authenticate()', True),
    ('MAX_SIZE', True),
    ('API_KEY', True),
    ('HttpClient', True),
    ('user_id', True),
    ('.validate', True),
    ('authentication logic', False),
    ('error handling patterns', False),
    ('database connection pooling', False),
    ('find all users', False),
]

print("Testing _is_likely_symbol() function:\n")
print(f"{'Query':<35} {'Result':<8} {'Expected':<10} {'Status'}")
print("=" * 70)

all_passed = True
for query, expected in test_cases:
    result = _is_likely_symbol(query)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    if result != expected:
        all_passed = False
    print(f"{query:<35} {str(result):<8} {str(expected):<10} {status}")

print("\n" + "=" * 70)
if all_passed:
    print("✅ All tests passed!")
else:
    print("❌ Some tests failed!")
    sys.exit(1)
