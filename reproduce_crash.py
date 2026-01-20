
import os
import logging
from mcp_core.llm import generate_response

# Mock environment
os.environ["GEMINI_API_KEY"] = "fake_key_for_test" 
# We expect fake key to fail auth, triggering fallback logic? 
# Or we rely on real key if available in env.
# In docker container, key is set. Here in agent shell, it might not be.
# I will assume I can run this inside the container if needed, or I rely on simple import test.

logging.basicConfig(level=logging.INFO)

print("--- Starting Crash Test ---")
try:
    # Trigger fallback cascade
    # gemini-3-flash-preview might fail if key invalid or model doesn't exist
    response = generate_response("Hello", model_alias="gemini-3-flash-preview")
    print(f"Response Status: {response.status}")
except Exception as e:
    print(f"CRASHED: {e}")
print("--- End Crash Test ---")
