from mcp_core.algorithms.occ_validator import OCCValidator

v = OCCValidator()

base = '''import os
from typing import Optional

VERSION = "1.0.0"

def func_a():
    pass

def func_b():
    pass
'''

ours = '''import os
from typing import Optional

VERSION = "1.0.0"

def func_a():
    return "modified"

def func_b():
    pass
'''

theirs = '''import os
from typing import Optional

VERSION = "1.0.0"

def func_a():
    pass

def func_b():
    return "modified"
'''

result = v.attempt_semantic_merge(base, ours, theirs)

print("=== MERGED CONTENT ===")
print(result)
print("\n=== CHECKS ===")
print(f"Has imports: {'import os' in result}")
print(f"Has VERSION: {'VERSION' in result}")
print(f"Has func_a modified: {'return \"modified\"' in result}")
