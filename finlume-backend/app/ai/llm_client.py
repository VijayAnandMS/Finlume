import os
from typing import List, Dict, Any
from app.core.config import settings
import json

class MockTextBlock:
    def __init__(self, text: str):
        self.type = "text"
        self.text = text

class MockToolUseBlock:
    def __init__(self, name: str, tool_id: str, input_args: dict = None):
        self.type = "tool_use"
        self.name = name
        self.id = tool_id
        self.input = input_args or {}

class MockMessageResponse:
    def __init__(self, content: list):
        self.content = content

def call_llm_with_tools(
    system_prompt: str,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    max_tokens: int = 500
) -> MockMessageResponse:
    provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else "anthropic"
    
    if provider == "gemini":
        return _call_gemini(system_prompt, messages, tools, max_tokens)
    else:
        return _call_anthropic(system_prompt, messages, tools, max_tokens)

def _call_anthropic(system_prompt: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], max_tokens: int) -> MockMessageResponse:
    api_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Anthropic API Key is missing.")

    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    
    # Clean up any custom keys we added for Gemini before sending to Anthropic
    clean_messages = []
    for msg in messages:
        clean_msg = {"role": msg["role"], "content": msg["content"]}
        if isinstance(clean_msg["content"], list):
            clean_content = []
            for block in clean_msg["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    clean_block = {k: v for k, v in block.items() if k in ["type", "tool_use_id", "content"]}
                    clean_content.append(clean_block)
                else:
                    clean_content.append(block)
            clean_msg["content"] = clean_content
        clean_messages.append(clean_msg)
        
    model = settings.LLM_MODEL or "claude-3-5-sonnet-20241022"
    if "gemini" in model:
        model = "claude-3-5-sonnet-20241022" # fallback if env was mixed up
        
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=clean_messages,
        tools=tools
    )
    return response

def _call_gemini(system_prompt: str, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], max_tokens: int) -> MockMessageResponse:
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API Key is missing.")
        
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    # 1. Convert Anthropic tools to Gemini format
    gemini_tools = []
    if tools:
        declarations = []
        for t in tools:
            # Gemini expects 'type': 'OBJECT' (uppercase string enum usually, but 'object' works in dicts)
            declarations.append({
                "name": t["name"],
                "description": t["description"],
                "parameters": {
                    "type": "object",
                    "properties": t["input_schema"].get("properties", {})
                }
            })
        gemini_tools = [{"function_declarations": declarations}]
        
    # Helper to find tool name by id
    def find_tool_name(tool_id: str) -> str:
        for m in messages:
            if isinstance(m["content"], list):
                for b in m["content"]:
                    if hasattr(b, "type") and b.type == "tool_use" and b.id == tool_id:
                        return b.name
        return "unknown_tool"

    # 2. Convert messages to Gemini format
    gemini_contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        parts = []
        
        if isinstance(msg["content"], str):
            parts.append({"text": msg["content"]})
        elif isinstance(msg["content"], list):
            for block in msg["content"]:
                # Anthropic tool_result dict
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    tool_name = block.get("tool_name") or find_tool_name(block["tool_use_id"])
                    parts.append({
                        "function_response": {
                            "name": tool_name,
                            "response": {"result": block["content"]}
                        }
                    })
                # Anthropic object (from our Mock class or Anthropic SDK)
                elif hasattr(block, "type"):
                    if block.type == "text":
                        parts.append({"text": block.text})
                    elif block.type == "tool_use":
                        if hasattr(block, "original_part"):
                            parts.append(block.original_part)
                        else:
                            args = getattr(block, "input", {})
                            parts.append({
                                "function_call": {
                                    "name": block.name,
                                    "args": args
                                }
                            })
                        
        gemini_contents.append({"role": role, "parts": parts})
        
    # 3. Call Gemini
    model_name = settings.GEMINI_MODEL or "gemini-flash-latest"
    print(f"DEBUG 6: Sending request to Gemini using model: {model_name}")
        
    model = genai.GenerativeModel(
        model_name=model_name,
        tools=gemini_tools if gemini_tools else None,
        system_instruction=system_prompt
    )
    
    response = model.generate_content(
        gemini_contents,
        generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens)
    )
    
    # 4. Convert response back to Anthropic format
    anthropic_content = []
    if not response.candidates:
        return MockMessageResponse(anthropic_content)
        
    candidate = response.candidates[0]
    for part in candidate.content.parts:
        if part.text:
            anthropic_content.append(MockTextBlock(text=part.text))
        elif part.function_call:
            # Generate a pseudo-id since Gemini doesn't use explicit tool_use_ids
            import uuid
            tool_id = f"toolu_{uuid.uuid4().hex[:16]}"
            
            # Extract args from protobuf map
            args = {}
            for k, v in part.function_call.args.items():
                args[k] = v
                
            block = MockToolUseBlock(
                name=part.function_call.name,
                tool_id=tool_id,
                input_args=args
            )
            block.original_part = part
            anthropic_content.append(block)
            
    return MockMessageResponse(content=anthropic_content)
