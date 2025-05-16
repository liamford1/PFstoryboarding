import json

# === CONFIG ===
input_file = "../data/penn/descriptions/its_time.jsonl"  # Change this to your target file path
brand = "PENN"
video_style = "Cinematic product advertisement"
video_title = "It’s Time for a Change. It’s Time for the PENN Low Profile Reels."

# === PROCESS FILE ===
updated_lines = []
with open(input_file, "r") as f:
    for line in f:
        if line.strip():
            data = json.loads(line)
            data["brand"] = brand
            data["video_style"] = video_style
            data["video_title"] = video_title
            updated_lines.append(json.dumps(data))

# === OVERWRITE FILE ===
with open(input_file, "w") as f:
    for updated_line in updated_lines:
        f.write(updated_line + "\n")

print(f"Updated: {input_file}")
