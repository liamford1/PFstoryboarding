from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import os

# Paths
image_folder = os.path.expanduser("./frames")
caption_file = os.path.join(image_folder, "captions.txt")

# Load BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Run captioning
with open(caption_file, "w") as f:
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(".jpg"):
            image_path = os.path.join(image_folder, filename)
            image = Image.open(image_path).convert('RGB')

            inputs = processor(images=image, return_tensors="pt")
            out = model.generate(**inputs)
            caption = processor.decode(out[0], skip_special_tokens=True)

            print(f"{filename}: {caption}")
            f.write(f"{filename}: {caption}\n")
