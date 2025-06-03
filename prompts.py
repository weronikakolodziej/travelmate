def get_recommendation_prompt(city, interests, reddit_data):
    """
    Create a prompt for the language model to generate travel recommendations.
    
    Args:
        city (str): The city or region the user is interested in
        interests (str): The user's specific interests
        reddit_data (str): Formatted data collected from Reddit
    
    Returns:
        str: The formatted prompt for the language model
    """
    # Base prompt template using Mistral's chat format
    system_prompt = """You are TravelMate AI, an expert travel recommendation system. 
Your goal is to provide personalized, helpful travel recommendations based on real discussions from Reddit.
Use the provided Reddit data to create specific, practical, and detailed recommendations.

Follow these guidelines:
1. Focus only on the specific city and interests mentioned
2. Provide practical, actionable advice that the user can follow
3. Structure your response with clear headings and bullet points
4. Include specific locations, names of places, and practical tips
5. If the Reddit data doesn't cover some aspects of the request, acknowledge this
6. Be friendly and conversational, but prioritize specific information over general advice
7. Cite specific Reddit mentions when relevant (e.g., "According to Reddit users...")
8. Include a short summary at the end with 3-5 must-do activities

IMPORTANT: Base your recommendations ONLY on the Reddit data provided. Do not make up information or draw from general knowledge.
"""

    # Format the user query
    user_query = f"I'm planning to visit {city} and I'm interested in {interests}. Based on the Reddit data, what are your recommendations?"
    
    # Construct the full prompt
    prompt = f"<s>[INST] {system_prompt}\n\nREDDIT DATA:\n{reddit_data}\n\n{user_query} [/INST]"
    
    return prompt