import pytesseract
from PIL import Image
import os
import glob

images_dir = "pdf_pages_images"
output_dir = "pdf_pages_text"
os.makedirs(output_dir, exist_ok=True)

image_files = sorted(glob.glob(os.path.join(images_dir, "page_*.png")))
print(f"Running OCR on {len(image_files)} images...")

for img_path in image_files:
    basename = os.path.splitext(os.path.basename(img_path))[0]
    txt_path = os.path.join(output_dir, f"{basename}.txt")
    text = pytesseract.image_to_string(Image.open(img_path))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  {img_path} -> {txt_path}")

print(f"\nDone. {len(image_files)} text files saved to '{output_dir}/'")
