

import os
import logging
import json
from typing import List

from templates.agent_response_schema import AgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_response(prompt: str, model_alias: str = "gemini-3-flash-preview") -> AgentResponse:
    """
    Route the prompt to the configured LLM provider and Model ID.
    Supports: "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash", etc.
    """
    logger.info(f"🧠 Routing to Model: {model_alias}")

    # [v3.5] Google Gemini-First Architecture with Cascading Fallback
    
    # 1. Local LLM Check (Opt-in via alias)
    is_local = "ollama" in model_alias or "local" in model_alias or "lmstudio" in model_alias
    local_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/v1")
    
    if is_local:
        return _call_local(local_url, prompt, model_alias)

    # 2. Main Logic - Gemini Priority with Cascading Fallback
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    # Gemini Model Cascade (try in order, remember what works)
    GEMINI_CASCADE = [
        "gemini-3-flash-preview",  # Primary (fastest, latest)
        "gemini-2.5-flash",        # Fallback 1 (stable)
        "gemini-2.5-pro",          # Fallback 2 (reasoning)
    ]
    
    is_gemini = "gemini" in model_alias or "flash" in model_alias or "pro" in model_alias
    
    if gemini_key and (is_gemini or not model_alias):
        # If specific model requested, try it first
        models_to_try = [model_alias] if model_alias in GEMINI_CASCADE else GEMINI_CASCADE
        
        for model in models_to_try:
            try:
                result = _call_gemini(gemini_key, prompt, model)
                if result.status != "FAILED":
                    # Success! Update project_profile if we had to fallback
                    if model != model_alias:
                        logger.info(f"✅ Model {model} worked. Consider updating project_profile.json.")
                        _update_working_model(model)
                    return result
            except Exception as e:
                logger.warning(f"⚠️ {model} failed: {e}. Trying next...")
                continue
        
        # All Gemini models failed
        logger.error("❌ All Gemini models failed.")

    # 3. OpenAI Fallback (if available)
    if openai_key:
        return _call_openai(openai_key, prompt, "gpt-4o")

    # 4. No keys/all failed
    logger.warning("⚠️ No API keys or all models failed. Returning MOCK response.")
    return _mock_response(prompt)


def _update_working_model(model: str) -> None:
    """Update project_profile.json with the working model (Thread/Process Safe)."""
    try:
        import json
        from pathlib import Path
        from filelock import FileLock
        
        profile_path = Path("project_profile.json")
        lock_path = "project_profile.json.lock"
        
        # Use simple blocking lock to avoid race with Orchestrator
        with FileLock(lock_path, timeout=5):
            if profile_path.exists():
                data = json.loads(profile_path.read_text())
                if "worker_models" in data:
                    # Only update if changed
                    if data["worker_models"].get("default") != model:
                        data["worker_models"]["default"] = model
                        profile_path.write_text(json.dumps(data, indent=2))
                        logger.info(f"📝 Updated project_profile.json: default → {model}")
    except Exception as e:
        logger.warning(f"Could not update project_profile.json: {e}")


def _call_local(base_url: str, prompt: str, model_id: str) -> AgentResponse:
    """
    Call Local LLM (Ollama/LM Studio) via OpenAI-compatible endpoint.
    """
    try:
        from openai import OpenAI
        
        # Strip provider prefix if present (e.g. "ollama/llama3" -> "llama3")
        if "/" in model_id:
            model_id = model_id.split("/")[-1]
            
        client = OpenAI(base_url=base_url, api_key="lm-studio") # Key often ignored
        
        logger.info(f"🖥️  Calling Local LLM at {base_url} ({model_id})")

        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", 
                 "content": "You are an AI coding agent. Respond in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        content = completion.choices[0].message.content
        data = json.loads(content)
        return AgentResponse(**data)

    except ImportError:
        logger.error("❌ openai library not installed. Run: pip install openai")
        return _mock_response(prompt)
    except Exception as e:
        logger.error(f"❌ Local LLM Error: {e}")
        # Fail gracefully to MOCK or consider fallback? 
        # For local, usually we want to fail so user knows connection is broken.
        return AgentResponse(
            status="FAILED", 
            reasoning_trace=f"Local LLM Connection Failed: {str(e)}"
        )


def _mock_response(prompt: str) -> AgentResponse:
    """
    Return a valid dummy response for testing/demo purposes.
    """
    return AgentResponse(
        status="SUCCESS",
        reasoning_trace="[MOCK] No API key. Simulating success.",
        validation_score=1.0,
        tool_calls=[],
        blackboard_update={}
    )


def _call_gemini(api_key: str, prompt: str, model_id: str) -> AgentResponse:
    """
    Call Google Gemini API with specific model.
    """
    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_id)

        # Enforce JSON output in system prompt
        full_prompt = (
            f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON "
            "matching the AgentResponse schema."
        )

        response = model.generate_content(full_prompt)
        text = response.text

        # Clean markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]

        data = json.loads(text)
        return AgentResponse(**data)

    except ImportError:
        logger.error(
            "❌ google-generativeai library not installed. "
            "Run: pip install google-generativeai"
        )
        return _mock_response(prompt)
    except Exception as e:
        logger.error(f"❌ Gemini API Error: {e}")
        return AgentResponse(
            status="FAILED",
            reasoning_trace=f"API Error: {str(e)}",
            validation_score=0.0
        )


def _call_openai(api_key: str, prompt: str, model_id: str) -> AgentResponse:
    """
    Call OpenAI API (GPT-4o or config).
    """
    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)

        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system",
                 "content": "You are an AI coding agent. Respond in JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = completion.choices[0].message.content
        data = json.loads(content)
        return AgentResponse(**data)

    except ImportError:
        logger.error("❌ openai library not installed. Run: pip install openai")
        return _mock_response(prompt)
    except Exception as e:
        logger.error(f"❌ OpenAI API Error: {e}")
        return AgentResponse(
            status="FAILED",
            reasoning_trace=f"API Error: {str(e)}",
            validation_score=0.0
        )


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using configured provider (Gemini → OpenAI fallback).
    Returns a 768-dimensional vector.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    # Try Gemini first
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.warning(f"Gemini embedding failed: {e}, trying OpenAI...")
    
    # Fallback to OpenAI
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    raise RuntimeError("No embedding provider available (GEMINI_API_KEY or OPENAI_API_KEY required)")
