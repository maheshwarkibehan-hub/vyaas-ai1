import os
import base64
import requests
import webbrowser
from dotenv import load_dotenv
from livekit.agents import function_tool  # ✅ LiveKit compatible decorator

# Load API keys from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
IMGBB_KEY = os.getenv("IMGBB_KEY")

MODEL_ID = "black-forest-labs/FLUX.1-dev"


@function_tool()
async def generate_image_tool(prompt: str) -> str:
    """
    Generates an AI image using Hugging Face FLUX.1-dev model 
    and displays it directly in the browser via imgbb (no download).

    Example prompts:
    - "एक सुंदर sunset की image दिखाओ"
    - "Show me a cyberpunk city at night"
    """

    # --- Step 1: Generate image from Hugging Face ---
    print(f"🎨 Generating image from prompt: {prompt}")
    url = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return f"❌ Hugging Face error: {response.status_code} - {response.text}"

    image_bytes = response.content
    print("✅ Image generated successfully.")

    # --- Step 2: Upload to imgbb ---
    print("☁️ Uploading to imgbb...")
    encoded = base64.b64encode(image_bytes)
    upload_url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMGBB_KEY, "image": encoded}

    res = requests.post(upload_url, data=payload)
    if res.status_code != 200:
        return f"❌ imgbb upload failed: {res.text}"

    image_url = res.json()["data"]["url"]
    print("🌐 Image hosted at:", image_url)

    # --- Step 3: Open in browser ---
    webbrowser.open_new_tab(image_url)
    print("🖥️ Image opened in browser.")

    return f"✅ Generated image is now visible in browser: {image_url}"
