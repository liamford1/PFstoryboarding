import os
import openai
import base64
import json
from tqdm import tqdm

# ========== CONFIG ==========
openai.api_key = "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"
input_dir = "../data/penn/lowpro4"  # One folder = one video
output_jsonl = "data.jsonl"

# Structured, brand-specific system prompt
SYSTEM_PROMPT = (
    "You are a creative director and prompt engineer working on a cinematic product advertisement for PENN, "
    "a premium saltwater fishing gear brand. Your task is to write a highly descriptive and structured visual prompt "
    "for a single frame in a storyboard. This prompt will be used to generate an image in a text-to-image model (like SDXL or DALL·E), "
    "so every detail must be concrete and specific.\n\n"
    "Follow this exact format and write each field with precision:\n"
    "1. Scene Label: A short, punchy title (e.g. The Cast Begins, Precision in the Smoke)\n"
    "2. Scene Timing: Describe where this shot fits in the storyboard (e.g. “Opening beat – establishing tone”, “Climactic moment – final product reveal”)\n"
    "3. Visual Description (at least 100 words): Describe the scene in vivid cinematic detail. Cover the subject (product or person), environment (location, time of day), actions (what’s happening), and context (why this moment matters). Use camera-ready language.\n"
    "4. Camera Angle: e.g. “Low-angle close-up”, “Eye-level wide shot”, “Macro detail from above”\n"
    "5. Lighting: Describe the light source(s), direction, temperature (cool/warm), intensity, contrast\n"
    "6. Mood: 1–3 adjectives capturing emotional tone (e.g., “tense, cinematic, isolated”)\n"
    "7. Brand Style: Always end with “PENN – cinematic realism with rugged performance tone”"
)

# ========== FUNCTIONS ==========

def encode_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def generate_frame_description(base64_image):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]}
        ],
        max_tokens=1000
    )
    content = response.choices[0].message.content.strip()

    # Parse the response into structured fields
    lines = content.split("\n")
    fields = {}
    for line in lines:
        if line.startswith("1. Scene Label:"):
            fields["scene_label"] = line.replace("1. Scene Label:", "").strip()
        elif line.startswith("2. Scene Timing:"):
            fields["scene_timing"] = line.replace("2. Scene Timing:", "").strip()
        elif line.startswith("3. Visual Description:"):
            fields["visual_prompt"] = line.replace("3. Visual Description:", "").strip()
        elif line.startswith("4. Camera Angle:"):
            fields["camera_angle"] = line.replace("4. Camera Angle:", "").strip()
        elif line.startswith("5. Lighting:"):
            fields["lighting"] = line.replace("5. Lighting:", "").strip()
        elif line.startswith("6. Mood:"):
            fields["mood"] = line.replace("6. Mood:", "").strip()
        elif line.startswith("7. Brand Style:"):
            fields["brand_style"] = line.replace("7. Brand Style:", "").strip()
    return fields

def load_jsonl(path):
    data = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except Exception:
                    pass
    return data

def save_jsonl(path, data):
    with open(path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

# ========== MAIN EXECUTION ==========

if __name__ == "__main__":
    existing_data = load_jsonl(output_jsonl)
    updated_data = []

    frames = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    for i, filename in enumerate(tqdm(frames), start=1):
        existing_entry = next((x for x in existing_data if x.get("frame_number") == i), None)

        # Only regenerate if missing or incomplete
        if not existing_entry or "scene_label" not in existing_entry:
            print(f"Updating frame {i}: {filename}")
            filepath = os.path.join(input_dir, filename)
            img_base64 = encode_image_base64(filepath)
            try:
                details = generate_frame_description(img_base64)
                updated_data.append({"frame_number": i, **details})
            except Exception as e:
                print(f"Error processing frame {i} ({filename}): {e}")
                updated_data.append({"frame_number": i})  # retain placeholder if fail
        else:
            updated_data.append(existing_entry)

    # Save updated data back to the same file
    save_jsonl(output_jsonl, updated_data)
