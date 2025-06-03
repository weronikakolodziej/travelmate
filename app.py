import gradio as gr
import os
import time
from model_utils import load_model, generate_recommendation
from reddit_utils import fetch_reddit_data
import torch

# Set page title and description
title = "TravelMate Lite AI"
description = """
### Get AI-powered travel recommendations based on real Reddit discussions
Enter a city or region and your interests to receive personalized travel suggestions.
"""

# Check if CUDA is available
cuda_available = torch.cuda.is_available()
device_info = f"Using {'GPU: ' + torch.cuda.get_device_name(0) if cuda_available else 'CPU'}"

# Define CSS for styling
css = """
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.footer {
    margin-top: 20px;
    text-align: center;
    font-size: 0.8em;
    color: #666;
}
.device-info {
    margin-top: 10px;
    padding: 5px 10px;
    background-color: #f0f9ff;
    border-radius: 4px;
    display: inline-block;
    font-size: 0.9em;
}
.metrics {
    margin-top: 10px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 4px;
    font-family: monospace;
}
"""

# Load the model at startup
print("Loading model...")
start_time = time.time()
model, tokenizer = load_model()
model_load_time = time.time() - start_time
print(f"Model loaded in {model_load_time:.2f} seconds")

def process_request(city, interests, subreddits=["travel", "solotravel"], post_limit=5):
    """Process the user request and generate recommendations"""
    if not city.strip() or not interests.strip():
        return "Please provide both a city/region and your interests."
    
    # Fetch data from Reddit
    start_time = time.time()
    status_msg = f"Searching Reddit for information about {city}..."
    yield status_msg
    
    reddit_data = fetch_reddit_data(city, interests, subreddits, post_limit)
    reddit_time = time.time() - start_time
    
    if not reddit_data:
        return f"No relevant information found for {city} on Reddit. Please try another city or interests."
    
    # Generate recommendations using the model
    status_msg += f"\nGenerating personalized recommendations... This may take a moment."
    yield status_msg
    
    start_time = time.time()
    recommendation = generate_recommendation(model, tokenizer, city, interests, reddit_data)
    generation_time = time.time() - start_time
    
    # Format the result with metrics
    metrics = f"""
<div class="metrics">
Model load time: {model_load_time:.2f}s | Reddit data fetch: {reddit_time:.2f}s | Generation time: {generation_time:.2f}s
Device: {torch.cuda.get_device_name(0) if cuda_available else "CPU"}
{f"GPU Memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB / {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB" if cuda_available else ""}
</div>
"""
    
    return recommendation + metrics

# Define the Gradio interface
with gr.Blocks(css=css, title=title) as demo:
    gr.Markdown(f"# {title}")
    gr.Markdown(description)
    
    with gr.Row():
        with gr.Column(scale=3):
            city = gr.Textbox(label="City or Region", placeholder="e.g., Barcelona, Tokyo, Bali")
            interests = gr.Textbox(
                label="Your Interests", 
                placeholder="e.g., best cafes, local bars, hidden gems, family activities"
            )
            
        with gr.Column(scale=1):
            gr.Markdown(f"<div class='device-info'>{device_info}</div>")
    
    # Add advanced options (collapsible)
    with gr.Accordion("Advanced Options", open=False):
        subreddits = gr.CheckboxGroup(
            choices=["travel", "solotravel", "backpacking", "shoestring", "EuropeTravel"],
            value=["travel", "solotravel"],
            label="Subreddits to search"
        )
        post_limit = gr.Slider(minimum=3, maximum=10, value=5, step=1, label="Number of Reddit posts to analyze")
    
    # Submit button
    submit_btn = gr.Button("Get Recommendations", variant="primary")
    
    # Output area
    output = gr.Markdown(label="Recommendations")
    
    # Set up the submission action
    submit_btn.click(
        fn=process_request,
        inputs=[city, interests, subreddits, post_limit],
        outputs=output
    )
    
    # Add footer
    gr.Markdown("<div class='footer'>TravelMate Lite AI © 2025 | Powered by Mistral AI and Reddit data</div>")
    
    # Add a warning for first-time load
    if not cuda_available:
        gr.Markdown("⚠️ **Notice**: Running on CPU which may be slow. For better performance, use a system with NVIDIA GPU.")

if __name__ == "__main__":
    # Launch the app
    demo.launch(share=True)