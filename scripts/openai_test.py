from dotenv import load_dotenv
import os
import openai
import base64
import json
from tqdm import tqdm

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# ========== CONFIG ==========
input_dir = "../data/penn/battle3"  # Replace with your test image folder
output_jsonl = "penn_storyboard_dataset.jsonl"
USE_OPENAI = False  # Set to True when you're ready to use real API credits

# Structured prompt for GPT-4o or dummy simulation
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
    if not USE_OPENAI:
        # Fake response for testing
        return {
            "scene_label": "Test Frame",
            "scene_timing": "Test Timing – placeholder",
            "visual_prompt": "This is a test description with over 100 words to simulate the output of the real GPT model. "
                             "The scene features a PENN spinning reel set dramatically in the center of the frame, "
                             "with a dramatic background and professional lighting to highlight its features. "
                             "The shot includes cinematic depth of field and moody oceanic tones, captured with high detail "
                             "to emphasize craftsmanship and premium design elements. The focus is clear and intentional.",
            "camera_angle": "Eye-level close-up",
            "lighting": "Warm key light from front, soft fill from side, medium contrast",
            "mood": "cinematic, gritty, intentional",
            "brand_style": "PENN – cinematic realism with rugged performance tone"
        }

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

    # Parse structured output
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

# ========== MAIN SCRIPT ==========

def process_video_folder_to_jsonl(folder_path, output_path):
    frames = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    with open(output_path, "a") as f:
        for i, filename in enumerate(tqdm(frames), start=1):
            filepath = os.path.join(folder_path, filename)
            img_base64 = encode_image_base64(filepath)
            try:
                details = generate_frame_description(img_base64)
                frame_data = {
                    "frame_number": i,
                    **details
                }
                f.write(json.dumps(frame_data) + "\n")
            except Exception as e:
                print(f"Error processing frame {i} ({filename}): {e}")

# ========== RUN ==========

if __name__ == "__main__":
    process_video_folder_to_jsonl(input_dir, output_jsonl)
