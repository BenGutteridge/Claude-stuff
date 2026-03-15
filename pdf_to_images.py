from pdf2image import convert_from_path
import os

pdf_path = "Mostellar — 50 Challenging Problems in Probability.pdf"
output_dir = "pdf_pages_images"
os.makedirs(output_dir, exist_ok=True)

print(f"Converting {pdf_path} to images...")
pages = convert_from_path(pdf_path, dpi=200)

for i, page in enumerate(pages, start=1):
    img_path = os.path.join(output_dir, f"page_{i:03d}.png")
    page.save(img_path, "PNG")
    print(f"  Saved {img_path}")

print(f"\nDone. {len(pages)} pages saved to '{output_dir}/'")
