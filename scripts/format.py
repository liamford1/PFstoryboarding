import os
import json
import time
from tqdm import tqdm
from openai import OpenAI

# === CONFIG ===
client = OpenAI(api_key="")

root_folder = "../data/penn/descriptions"  # folder containing .jsonl files
output_file = "final_training_dataset.jsonl"
dry_run = False  # Set to True to test without using the API

# === Format structured completion text ===
def format_completion(entry):
    return (
        f"Scene Label: {entry['scene_label']}\n"
        f"Scene Timing: {entry['scene_timing']}\n"
        f"Visual Description: {entry['visual_prompt']}\n"
        f"Camera Angle: {entry['camera_angle']}\n"
        f"Lighting: {entry['lighting']}\n"
        f"Mood: {entry['mood']}\n"
        f"Brand Style: {entry['brand_style']}\n"
        f"Brand: {entry['brand']}\n"
        f"Video Style: {entry['video_style']}\n"
        f"Video Title: {entry['video_title']}"
    )

# === Generate user-style prompt from structured description ===
def generate_user_prompt(completion_text):
    if dry_run:
        return f"[FAKE PROMPT based on: {completion_text[:60]}...]"

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
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

# === Main processing loop ===
with open(output_file, "w") as out_f:
    for filename in os.listdir(root_folder):
        if not filename.endswith(".jsonl"):
            continue
        file_path = os.path.join(root_folder, filename)

        video_id = filename.replace(".jsonl", "")
        print(f"Processing {video_id}...")

        with open(file_path, "r") as desc_file:
            for line in tqdm(desc_file, desc=video_id):
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
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Error in {video_id}: {e}")
                    continue
