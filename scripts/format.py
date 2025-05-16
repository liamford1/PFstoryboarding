import os
import json
import openai
from tqdm import tqdm
import time

# === CONFIG ===
openai.api_key = "your-api-key"
root_folder = "data/penn"  # Contains folders like 'battle3', 'clash2.1', each with descriptions.jsonl
output_file = "final_training_dataset.jsonl"
dry_run = True  # Set to False to enable actual OpenAI API usage

# === Format the structured completion from description entry ===
def format_completion(entry):
    return (
        f"Scene Label: {entry['scene_label']}\n"
        f"Scene Timing: {entry['scene_timing']}\n"
        f"Visual Description: {entry['visual_prompt']}\n"
        f"Camera Angle: {entry['camera_angle']}\n"
        f"Lighting: {entry['lighting']}\n"
        f"Mood: {entry['mood']}\n"
        f"Brand Style: {entry['brand_style']}"
    )

# === Generate user-style prompt from full scene description ===
def generate_user_prompt(completion_text):
    if dry_run:
        return f"[FAKE USER PROMPT based on: {completion_text[:60]}...]"

    system_prompt = (
        "You are a creative user writing prompts for a cinematic product storyboard generator "
        "tailored to the PENN brand. Your goal is to describe the scene in a short, natural sentence "
        "that a user might type into a generator — something like: 'a low-angle shot of an angler reeling in a tuna at sunset.' "
        "Do not include camera, lighting, or mood details unless they’re implied naturally."
    )

    user_prompt = (
        f"Here is the full scene description:\n\n"
        f"{completion_text}\n\n"
        "Write a single-line prompt that a PENN brand user might input to generate this kind of cinematic scene:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

# === Process all description files ===
with open(output_file, "w") as out_f:
    for subfolder in os.listdir(root_folder):
        sub_path = os.path.join(root_folder, subfolder)
        if not os.path.isdir(sub_path):
            continue

        desc_file_path = os.path.join(sub_path, "descriptions.jsonl")
        if not os.path.exists(desc_file_path):
            print(f"Skipping {subfolder}: no descriptions.jsonl found")
            continue

        print(f"Processing {subfolder}...")

        with open(desc_file_path, "r") as desc_file:
            for line in tqdm(desc_file, desc=f"{subfolder}"):
                try:
                    entry = json.loads(line)
                    completion = format_completion(entry)
                    prompt = generate_user_prompt(completion)
                    if prompt is None:
                        continue
                    pair = {
                        "prompt": prompt,
                        "completion": completion
                    }
                    out_f.write(json.dumps(pair) + "\n")
                    if not dry_run:
                        time.sleep(0.5)  # Friendly delay to avoid rate limits
                except Exception as e:
                    print(f"Error in {subfolder}: {e}")
                    continue
