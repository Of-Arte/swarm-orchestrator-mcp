
import os
import logging
import json

from templates.agent_response_schema import AgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_response(prompt: str, model_alias: str = "gemini-2.0-flash-exp") -> AgentResponse:
    """
    Route the prompt to the configured LLM provider and Model ID.
    Supports: "gemini-2.0-flash-exp", "claude-3-5-sonnet", etc.
    """
    logger.info(f"🧠 Routing to Model: {model_alias}")

    # Routing Logic
    is_gemini = "gemini" in model_alias or "antigravity" in model_alias
    is_gpt = "gpt" in model_alias
    
    # [v3.2] OpenRouter Routing (Cost Optimization)
    # Route to OpenRouter if model is in FREE_MODELS or explicitly "free"/"llama"
    from mcp_core.providers.openrouter import FREE_MODELS, call_openrouter_json
    is_openrouter = model_alias in FREE_MODELS or "free" in model_alias or "llama" in model_alias or "mistral" in model_alias
    
    if is_openrouter:
        try:
            # Pass model ID directly
            data = call_openrouter_json(prompt, model_alias=model_alias)
            return AgentResponse(**data)
        except Exception as e:
            logger.error(f"❌ OpenRouter Error: {e}. Falling back to default.")
            # Fallback to Gemini/OpenAI if OpenRouter fails
            pass

    # [v3.3] Local LLM Support (Ollama/LM Studio)
    is_local = "ollama" in model_alias or "local" in model_alias or "lmstudio" in model_alias
    local_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/v1") # Default to Ollama

    if is_local:
        return _call_local(local_url, prompt, model_alias)

    # Check for API Keys
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if is_gemini and gemini_key:
        # Pass model ID directly (User manages mapping in config)
        return _call_gemini(gemini_key, prompt, model_alias)

    elif is_gpt and openai_key:
        return _call_openai(openai_key, prompt, model_alias)
    
    elif openai_key: # Fallback to OpenAI if Gemini requested but key missing
        logger.warning(f"⚠️ Requested {model_alias} but GEMINI_KEY missing. Fallback to OpenAI.")
        return _call_openai(openai_key, prompt, "gpt-4o")

    elif gemini_key: # Fallback to Gemini if OpenRouter/GPT requested but key missing
        logger.warning(f"⚠️ Requested {model_alias} but key missing/failed. Fallback to Gemini.")
        return _call_gemini(gemini_key, prompt, "gemini-2.0-flash-exp")

    else:
        logger.warning(
            "⚠️ No API keys found. Returning MOCK response."
        )
        return _mock_response(prompt)


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
