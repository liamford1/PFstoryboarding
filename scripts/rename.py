import os

# ========== CONFIG ==========
folder_path = "../data/penn/slammer"  # ← replace this with the path to your image folder
file_prefix = "frame_"                # Or change to "image_" or "shot_", etc.
file_extension = ".jpg"              # Change to ".png" or ".jpeg" if needed
zero_padding = 4                     # 0001, 0002, etc.

# ========== RENAME LOGIC ==========
def rename_images(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith(file_extension)]
    files.sort()  # Sort alphabetically — ensures consistent renaming

    for idx, filename in enumerate(files, start=1):
        new_name = f"{file_prefix}{str(idx).zfill(zero_padding)}{file_extension}"
        src = os.path.join(folder, filename)
        dst = os.path.join(folder, new_name)
        os.rename(src, dst)
        print(f"Renamed: {filename} → {new_name}")

# ========== RUN ==========
if __name__ == "__main__":
    rename_images(folder_path)
