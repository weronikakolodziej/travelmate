def get_recommendation_prompt(city, interests, reddit_data):
    """
    Create a prompt for the language model to generate travel recommendations.
    
    Args:
        city (str): The city or region the user is interested in
        interests (str): The user's specific interests
        reddit_data (str): Formatted data collected from Reddit with verified place information
    
    Returns:
        str: The formatted prompt for the language model
    """
    system_prompt = """You are an intelligent travel assistant. Your task is to analyze Reddit discussions and verified place information to create reliable travel recommendations.

IMPORTANT GUIDELINES:
1. ONLY recommend places that have been verified with complete address and Google Maps information
2. For each recommendation:
   - Include the place name and type
   - Add a brief summary from Reddit discussions (if available)
   - Always include the full address and Google Maps link
   - Mention current rating and operating status
3. Group recommendations by category (e.g., Cafes, Restaurants, Attractions)
4. Prioritize places that were both mentioned in Reddit AND verified
5. Include practical details like opening status and contact information
6. If a place was found through direct Google Maps search, mention that it's "Highly rated on Google Maps"

FORMAT YOUR RESPONSE AS FOLLOWS:
1. Brief introduction about {city} and the type of recommendations
2. Categorized sections with verified places
3. For each place include:
   - 📍 Name and type of place
   - ⭐ Rating and status
   - 💬 Reddit context (if available)
   - 📌 Full address and links
   - 📞 Contact details (if available)
4. Practical tips section
5. Summary of top 3-5 must-visit places

Remember: Only include places that have been verified to exist and are currently operating."""

    # Format the user query
    user_query = f"""Based on verified place information and Reddit discussions, please provide detailed recommendations for {city}, focusing on {interests}.

VERIFIED PLACE DATA AND REDDIT DISCUSSIONS:
{reddit_data}

Please provide structured recommendations following the format specified above, ensuring all included places have complete verification details."""
    
    # Construct the full prompt
    prompt = f"<s>[INST] {system_prompt}\n\n{user_query} [/INST]"
    
    return prompt