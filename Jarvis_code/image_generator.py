import os
import base64
import requests
import webbrowser
from io import BytesIO
from dotenv import load_dotenv

# --- Load API keys ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
IMGBB_KEY = os.getenv("IMGBB_KEY")

MODEL_ID = "black-forest-labs/FLUX.1-dev"

def generate_image(prompt: str) -> bytes:
    """Generate raw image bytes using Hugging Face model."""
    print(f"🎨 Generating image from prompt: {prompt}")
    url = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"HF error {response.status_code}: {response.text}")

    print("✅ Image generated successfully.")
    return response.content  # raw bytes

def upload_to_imgbb(image_bytes: bytes) -> str:
    """Upload image bytes directly to imgbb and return public URL."""
    print("☁️ Uploading image to imgbb...")
    encoded = base64.b64encode(image_bytes)
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMGBB_KEY, "image": encoded}

    res = requests.post(url, data=payload)
    if res.status_code != 200:
        raise Exception(f"imgbb upload failed: {res.text}")

    data = res.json()
    image_url = data["data"]["url"]
    print("🌐 Image hosted at:", image_url)
    return image_url

def show_in_browser(url: str):
    """Open the image in the default browser."""
    print("🖥️ Opening image in browser...")
    webbrowser.open_new_tab(url)

if __name__ == "__main__":
    prompt = input("📝 Enter prompt: ")
    try:
        image_bytes = generate_image(prompt)
        image_url = upload_to_imgbb(image_bytes)
        show_in_browser(image_url)
        print("✅ Done — image opened in browser!")
    except Exception as e:
        print("❌ Error:", e)
