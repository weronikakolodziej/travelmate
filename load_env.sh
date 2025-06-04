#!/bin/bash

# Load existing environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Google Maps API key is provided as argument
if [ -z "$1" ]; then
    echo "Please provide your Google Maps API key as an argument:"
    echo "./load_env.sh YOUR_API_KEY"
    exit 1
fi

# Save the API key to .env file
echo "GOOGLE_MAPS_API_KEY=$1" >> .env

# Export the API key to current session
export GOOGLE_MAPS_API_KEY=$1

echo "✅ Google Maps API key has been set!"
echo "🚀 You can now run the application with place verification enabled." 