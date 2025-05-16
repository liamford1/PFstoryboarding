import os
import json
import openai
from PIL import Image
from tqdm import tqdm
import base64
from io import BytesIO

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Paths
frames_folder = "path/to/your/frames"  # e.g., "data/penn/clash2/"
descriptions_jsonl = "path/to/your/completions.jsonl"
output_jsonl = "final_finetune_data.jsonl"

# Load your PENN completions
with open(descriptions_jsonl, "r") as f:
    completions = [json.loads(line.strip()) for line in f]

# Get image files sorted
image_files = sorted([f for f in os.listdir(frames_folder) if f.endswith((".jpg", ".png"))])
assert len(image_files) == len(completions), "Mismatch between image files and completions!"

def encode_image_base64(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()

def get_image_prompt_from_gpt4o(image_path):
    base64_image = encode_image_base64(image_path)

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are generating prompts to train an AI to describe cinematic fishing scenes like PENN ads. Your task is to write one clear, neutral, literal sentence describing what's happening in the image. Do not write in a marketing tone. Just describe the image plainly as if someone asked what they are seeing."
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=50,
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()

# Output
output_data = []

for idx, filename in tqdm(enumerate(image_files), total=len(image_files)):
    image_path = os.path.join(frames_folder, filename)
    prompt = get_image_prompt_from_gpt4o(image_path)
    c = completions[idx]

    formatted_completion = (
        f"Scene Label: {c['scene_label']}\n"
        f"Scene Timing: {c['scene_timing']}\n"
        f"Camera Angle: {c['camera_angle']}\n"
        f"Lighting: {c['lighting']}\n"
        f"Mood: {c['mood']}\n"
        f"Visual Description: {c['visual_prompt']}\n"
        f"Brand Style: {c.get('brand_style', 'PENN – cinematic realism with rugged performance tone')}"
    )

    output_data.append({
        "prompt": prompt,
        "completion": formatted_completion
    })

# Write output JSONL
with open(output_jsonl, "w") as f:
    for item in output_data:
        f.write(json.dumps(item) + "\n")

print(f"✅ Done. Output saved to {output_jsonl}")
