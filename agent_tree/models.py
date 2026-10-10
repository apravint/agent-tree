import os
import json
import urllib.request
from typing import Dict, Any, Optional

def get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    conf_path = os.path.expanduser("~/.config/environment.d/20-gemini.conf")
    if os.path.exists(conf_path):
        try:
            with open(conf_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        return line.strip().split("=", 1)[1].strip('"').strip("'")
        except Exception:
            pass
    return ""

def get_claude_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "")

def get_openai_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "")

def query_model(model_name: str, prompt: str, system_prompt: str = "") -> str:
    """
    Unified LLM query routing across Gemini, Claude, OpenAI, and local Ollama.
    """
    # 1. Anthropic Claude
    claude_key = get_claude_key()
    if claude_key and ("claude" in model_name.lower()):
        try:
            url = "https://api.anthropic.com/v1/messages"
            payload = {
                "model": model_name,
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                payload["system"] = system_prompt
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-api-key": claude_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["content"][0]["text"].strip()
        except Exception:
            pass

    # 2. Google Gemini
    gemini_key = get_gemini_key()
    if gemini_key and ("claude" not in model_name.lower()):
        gemini_model = model_name if "gemini" in model_name else "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": gemini_key}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass

    # 3. Local Ollama Fallback ($0 Local Execution)
    ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434/api/generate")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
    full_prompt = f"{system_prompt}\n\nTask:\n{prompt}" if system_prompt else prompt
    try:
        req = urllib.request.Request(
            ollama_url,
            data=json.dumps({"model": ollama_model, "prompt": full_prompt, "stream": False}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except Exception as e:
        return f"[Fallback Execution Note: Local/API unavailable ({e})]"
