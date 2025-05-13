import os
import openai
import base64
import json
from tqdm import tqdm

# ========== CONFIG ==========

openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your API key
input_dir = "path/to/your/folder_of_frames"  # One folder = one video
output_jsonl = "penn_storyboard_dataset.jsonl"

# Optional system prompt for consistent cinematic tone
SYSTEM_PROMPT = (
    "You are a cinematic visual prompt engineer and creative director. "
    "For each image you are shown, write a highly detailed, frame-specific storyboard description. "
    "Include the setting, lighting, mood, camera angle, and visual composition. "
    "Maintain PENN’s brand tone: bold, gritty, expert-driven, with cinematic realism and performance emphasis."
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
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

# ========== MAIN SCRIPT ==========

def process_video_folder_to_jsonl(folder_path, output_path):
    frames = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    storyboard = []

    for i, filename in enumerate(tqdm(frames), start=1):
        filepath = os.path.join(folder_path, filename)
        img_base64 = encode_image_base64(filepath)
        try:
            detailed_desc = generate_frame_description(img_base64)
            storyboard.append({
                "frame_number": i,
                "scene_label": f"Frame {i}",
                "scene_role": "Progression",
                "visual_prompt": detailed_desc,
                "camera_angle": "TBD",
                "lighting": "TBD",
                "mood": "TBD",
                "brand_style": "PENN – cinematic realism with rugged performance tone"
            })
        except Exception as e:
            print(f"Error processing frame {i}: {e}")

    jsonl_line = {
        "prompt": "Generate a detailed cinematic storyboard for a PENN product video, with frame-by-frame scene breakdowns.",
        "completion": storyboard
    }

    with open(output_path, "a") as f:
        f.write(json.dumps(jsonl_line) + "\n")

# ========== RUN ==========

if __name__ == "__main__":
    process_video_folder_to_jsonl(input_dir, output_jsonl)
