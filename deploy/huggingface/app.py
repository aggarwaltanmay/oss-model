import os
import gradio as gr
from src.model_loader import load_model

# Load model once at startup
model, tokenizer = load_model()

def predict(prompt, max_new_tokens=256, temperature=0.7):
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        generation = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature=temperature)
    response = tokenizer.decode(generation[0], skip_special_tokens=True)
    return response

with gr.Blocks() as demo:
    gr.Markdown("# Qwen2.5‑0.5B‑Instruct Chat")
    with gr.Row():
        prompt = gr.Textbox(label="Prompt", lines=4)
        output = gr.Textbox(label="Response", lines=8)
    submit = gr.Button("Generate")
    submit.click(fn=predict, inputs=prompt, outputs=output)

demo.launch(share=True)
