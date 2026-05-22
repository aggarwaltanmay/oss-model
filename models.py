import os
import time
from google import genai
from google.genai import types
from transformers import pipeline
from duckduckgo_search import DDGS
from observability import logger

class SafetyGuardrail:
    """A lightweight interceptor to prevent jailbreaks and harmful outputs."""
    BLOCKLIST = ["hack", "ddos", "phishing", "methamphetamine", "hotwire", "override", "ignore all previous instructions"]
    
    @staticmethod
    def is_safe(prompt):
        prompt_lower = prompt.lower()
        for word in SafetyGuardrail.BLOCKLIST:
            if word in prompt_lower:
                return False, f"Safety Override: The prompt triggered a safety filter due to the keyword: '{word}'."
        return True, ""
        
    @staticmethod
    def apply_system_prompt(messages):
        system_msg = {
            "role": "system", 
            "content": "You are a helpful, entirely harmless, and highly capable AI assistant. "
                       "You must absolutely refuse to provide instructions on illegal, unethical, or harmful activities. "
                       "If asked to write code for a DDoS attack, phishing, or similar, refuse politely. "
                       "If asked a factual question, answer accurately. If you don't know, use the Web Search tool if available."
        }
        # Check if system prompt already exists
        if len(messages) > 0 and messages[0]["role"] == "system":
            messages[0] = system_msg
        else:
            messages.insert(0, system_msg)
        return messages

class WebSearchTool:
    """Tool to give the LLM real-time internet access to avoid hallucinations."""
    @staticmethod
    def search(query, max_results=3):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return "No results found."
                
                search_context = "\n".join([f"- {res['title']}: {res['body']}" for res in results])
                return f"Web Search Context:\n{search_context}"
        except Exception as e:
            return f"Search failed: {str(e)}"

def summarize_context(messages, max_length=10):
    """Sliding-window summarization for long-term memory."""
    # We always keep the system prompt and the last N messages
    if len(messages) <= max_length + 1:
        return messages
        
    system_prompt = messages[0]
    recent_messages = messages[-max_length:]
    
    # In a real implementation, we would call the LLM here to summarize messages[1:-max_length]
    # For now, we simulate this by injecting a "context summary" system message
    summary_msg = {
        "role": "system",
        "content": "[Context summarized to save memory: The user and assistant had a prior conversation.]"
    }
    
    return [system_prompt, summary_msg] + recent_messages


class OpenSourceAssistant:
    def __init__(self, model_id="Qwen/Qwen2.5-0.5B-Instruct"):
        """
        Runs the Hugging Face model locally via transformers for public deployment (e.g. HF Spaces).
        """
        self.model_id = model_id
        # Load the model via pipeline. This downloads weights on first startup.
        print(f"Loading local model {model_id}...")
        self.pipe = pipeline("text-generation", model=model_id, device_map="auto")
        print("Model loaded successfully.")

    def generate_response(self, messages, temperature=0.7, max_tokens=256):
        start_time = time.time()
        
        # 1. Apply Safety Guardrails
        messages = SafetyGuardrail.apply_system_prompt(messages)
        last_user_msg = [m for m in messages if m["role"] == "user"][-1]["content"]
        is_safe, reason = SafetyGuardrail.is_safe(last_user_msg)
        if not is_safe:
            logger.log_trace("OpenSource (Local)", last_user_msg, reason, time.time() - start_time, safety_triggered=True)
            return reason
            
        # 2. Apply Memory Window
        messages = summarize_context(messages)

        # 3. Very naive tool integration (LLM does not "call" it natively, we just inject it if keywords trigger)
        # For a full implementation, we would parse <tool_call> tags.
        tools_used = []
        if "search" in last_user_msg.lower() or "latest" in last_user_msg.lower() or "who won" in last_user_msg.lower():
            search_context = WebSearchTool.search(last_user_msg)
            tools_used.append("WebSearch")
            messages[-1]["content"] += f"\n\n[System note: Use this data to answer if relevant: {search_context}]"

        try:
            # Using the transformers chat template formatting
            prompt = self.pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = self.pipe(prompt, max_new_tokens=max_tokens, temperature=temperature, do_sample=True)
            response = outputs[0]["generated_text"][len(prompt):].strip()
            
            latency = time.time() - start_time
            logger.log_trace("OpenSource (Local)", last_user_msg, response, latency, tools_used=tools_used)
            return response
            
        except Exception as e:
            return f"Error from Local Model: {str(e)}"


class FrontierAssistant:
    def __init__(self, api_key=None, model_id="gemini-2.5-flash"):
        """
        Uses Google Gemini API.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_id = model_id
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for Frontier Assistant.")
        self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, messages, temperature=0.7, max_tokens=1024):
        start_time = time.time()
        
        # 1. Apply Safety Guardrails
        messages = SafetyGuardrail.apply_system_prompt(messages)
        last_user_msg = [m for m in messages if m["role"] == "user"][-1]["content"]
        is_safe, reason = SafetyGuardrail.is_safe(last_user_msg)
        if not is_safe:
            logger.log_trace("Frontier", last_user_msg, reason, time.time() - start_time, safety_triggered=True)
            return reason
            
        # 2. Apply Memory Window
        messages = summarize_context(messages)
        
        tools_used = []
        if "search" in last_user_msg.lower() or "latest" in last_user_msg.lower() or "who won" in last_user_msg.lower():
            search_context = WebSearchTool.search(last_user_msg)
            tools_used.append("WebSearch")
            messages[-1]["content"] += f"\n\n[System note: Use this data to answer if relevant: {search_context}]"

        try:
            contents = []
            system_instruction = None
            
            for msg in messages:
                role = msg["role"]
                text = msg["content"]
                
                if role == "system":
                    system_instruction = text
                elif role == "user":
                    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
                elif role == "assistant":
                    contents.append(types.Content(role="model", parts=[types.Part.from_text(text=text)]))
            
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction
            )
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config,
            )
            
            latency = time.time() - start_time
            logger.log_trace("Frontier", last_user_msg, response.text, latency, tools_used=tools_used)
            return response.text
        except Exception as e:
            return f"Error from Gemini API: {str(e)}"
