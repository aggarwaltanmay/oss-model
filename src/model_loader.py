import os
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model(model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
    """Download and load the specified model and tokenizer.
    Returns a tuple (model, tokenizer)."""
    # Ensure model files are cached locally
    cache_dir = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    # Download model files (if not already cached)
    hf_hub_download(repo_id=model_name, filename="pytorch_model.bin", cache_dir=cache_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir, torch_dtype="auto", device_map="auto")
    return model, tokenizer
