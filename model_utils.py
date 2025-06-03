import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from prompts import get_recommendation_prompt
import time
import os

def load_model():
    """
    Load the language model and tokenizer from Hugging Face.
    Will use GPU if available, otherwise fall back to CPU with a warning.
    """
    # Check if CUDA is available
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")
    
    # Model ID
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    
    # Configure model loading options
    if cuda_available:
        # Use 4-bit quantization for GPU memory efficiency
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        
        # Load the model with GPU acceleration
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
    else:
        # Warning for CPU usage
        print("WARNING: Running on CPU. This will be very slow.")
        print("Consider using a machine with an NVIDIA GPU for better performance.")
        
        # Load a smaller model if on CPU to improve performance
        model_id = "mistralai/Mistral-7B-Instruct-v0.3"  # You might want to use an even smaller model for CPU
        
        # Load the model on CPU
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float32,  # Use float32 for CPU
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    return model, tokenizer

def generate_recommendation(model, tokenizer, city, interests, reddit_data):
    """
    Generate travel recommendations using the LLM based on Reddit data.
    
    Args:
        model: The loaded language model
        tokenizer: The model's tokenizer
        city: The city or region the user is interested in
        interests: The user's specific interests
        reddit_data: The data collected from Reddit
    
    Returns:
        str: The generated recommendation
    """
    # Create the prompt with the Reddit data
    prompt = get_recommendation_prompt(city, interests, reddit_data)
    
    # Prepare the input
    inputs = tokenizer(prompt, return_tensors="pt")
    
    # Move inputs to the same device as the model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate the recommendation
    with torch.no_grad():
        generation_config = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": tokenizer.eos_token_id
        }
        
        generated_ids = model.generate(
            **inputs,
            **generation_config
        )
    
    # Decode the generated tokens
    generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    
    # Extract just the model's response (not the prompt)
    response = generated_text.split("[/INST]")[-1].strip()
    
    return response