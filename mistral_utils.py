from typing import Optional
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from prompts import get_recommendation_prompt

def initialize_mistral_client() -> MistralClient:
    """Initialize the Mistral AI client"""
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set")
    return MistralClient(api_key=api_key)

def get_recommendations(city: str, interests: str, formatted_data: str) -> str:
    """
    Generate travel recommendations using Mistral AI.
    
    Args:
        city (str): The city or region to get recommendations for
        interests (str): User's interests
        formatted_data (str): Formatted and verified place data
    
    Returns:
        str: Generated recommendations
    """
    client = initialize_mistral_client()
    
    # Get the prompt
    prompt = get_recommendation_prompt(city, interests, formatted_data)
    
    # Generate recommendations
    messages = [
        ChatMessage(role="user", content=prompt)
    ]
    
    chat_response = client.chat(
        model="mistral-large-latest",
        messages=messages,
        temperature=0.7,
        max_tokens=2000
    )
    
    return chat_response.choices[0].message.content 