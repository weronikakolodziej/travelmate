# TravelMate Lite AI

TravelMate Lite AI is a local application that uses AI to generate personalized travel recommendations based on real discussions from Reddit.

## Features

- 🌍 Get travel recommendations for any city or region
- 🧠 Powered by Mistral-7B-Instruct language model running locally
- 📱 Clean and intuitive Gradio interface
- 🚀 GPU acceleration with CUDA (with CPU fallback)
- 📊 Performance metrics tracking

## Setup

### Requirements

- Python 3.8+
- NVIDIA GPU with CUDA support (recommended) - CPU fallback available
- 16GB+ RAM (8GB minimum with CPU only)

### Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/travelmate-lite-ai.git
cd travelmate-lite-ai
```

2. Create and activate a virtual environment:

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n travelmate python=3.10
conda activate travelmate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Login to hugging face

```bash
huggingface_cli login
```

5. (Optional) Configure Reddit API credentials:

For full functionality, you'll need to [create a Reddit app](https://www.reddit.com/prefs/apps) and set the following environment variables:

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="TravelMate Lite AI v1.0"
```

Without these credentials, the app will run in demo mode with mock data for a few example cities.

## Usage

1. Start the application:

```bash
python app.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://127.0.0.1:7860)

3. Enter a city or region and your interests, then click "Get Recommendations"

## Performance Notes

- First load will download the model from Hugging Face (~4GB)
- GPU acceleration provides significantly faster generation (5-10x)
- Model loading takes 10-30 seconds on GPU, 1-2 minutes on CPU
- Generation takes ~5-15 seconds on GPU, 1-3 minutes on CPU

## Technical Details

- Language Model: mistralai/Mistral-7B-Instruct-v0.3
- Quantization: 4-bit for efficient GPU memory usage
- UI Framework: Gradio
- Reddit Data: Fetched from relevant travel subreddits
- Prompt Engineering: Custom prompts for travel recommendations

## License

MIT

## Acknowledgements

- [Hugging Face](https://huggingface.co/) for model hosting and transformers library
- [Mistral AI](https://mistral.ai/) for the open-source language model
- [Gradio](https://gradio.app/) for the UI framework
- [Reddit](https://www.reddit.com/) for the community data
# txravelmate
# travelmate
