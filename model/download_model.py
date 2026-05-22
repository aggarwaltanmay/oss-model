# model/download_model.py
"""Utility to download and convert the Qwen2.5-0.5B-Instruct model.
Uses HuggingFace Transformers to fetch the model and optionally convert to a format
compatible with vLLM.
"""

import os
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
TARGET_DIR = Path(__file__).resolve().parent.parent / "model" / "qwen2.5-0.5b-instruct"

def download():
    os.makedirs(TARGET_DIR, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype="auto", device_map="auto")
    tokenizer.save_pretrained(TARGET_DIR)
    model.save_pretrained(TARGET_DIR)
    print(f"Model saved to {TARGET_DIR}")

if __name__ == "__main__":
    download()
