import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from prompts import get_recommendation_prompt
import time
import os
from tqdm import tqdm

def load_model():
    """
    Load the language model and tokenizer from Hugging Face.
    Will use GPU if available, otherwise fall back to CPU with a warning.
    """
    print("Starting model loading process...")
    # Check if CUDA is available
    cuda_available = torch.cuda.is_available()
    print(f"CUDA available: {cuda_available}")
    
    # Model ID
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    print(f"Loading model: {model_id}")
    
    try:
        # Configure model loading options
        if cuda_available:
            print("Configuring GPU settings...")
            # Use 4-bit quantization for GPU memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            
            # Load the model with GPU acceleration
            print("Loading model on GPU...")
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
            print("Loading model on CPU...")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32,  # Use float32 for CPU
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        
        # Load tokenizer
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        print("Model and tokenizer loaded successfully!")
        
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

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
    try:
        print(f"\nGenerating recommendations for {city}...")
        
        # Create the prompt with the Reddit data
        with tqdm(total=4, desc="Generation Progress", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
            pbar.set_description("Creating prompt")
            prompt = get_recommendation_prompt(city, interests, reddit_data)
            print(f"Prompt length: {len(prompt)} characters")
            pbar.update(1)
            
            # Prepare the input
            pbar.set_description("Tokenizing input")
            inputs = tokenizer(prompt, return_tensors="pt")
            print(f"Input length: {inputs.input_ids.shape[1]} tokens")
            pbar.update(1)
            
            # Move inputs to the same device as the model
            device = "cuda" if torch.cuda.is_available() else "cpu"
            pbar.set_description(f"Moving inputs to {device}")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            pbar.update(1)
            
            # Generate the recommendation
            pbar.set_description("Generating response")
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
            
            print("\nDecoding generated response...")
            # Decode the generated tokens
            generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            
            # Extract just the model's response (not the prompt)
            response = generated_text.split("[/INST]")[-1].strip()
            pbar.update(1)
        
        print("\n=== Generated Response ===")
        print(response)
        print("========================\n")
        
        return response
    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        raise