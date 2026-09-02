import fitz
import os

# -----------------------------
# FOLDERS
# -----------------------------

INPUT_FOLDER = "resumes"
TEXT_FOLDER = "extracted_text"
IMAGE_FOLDER = "extracted_images"

os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)


# -----------------------------
# PROCESS EACH PDF
# -----------------------------

for filename in os.listdir(INPUT_FOLDER):

    if not filename.lower().endswith(".pdf"):
        continue

    pdf_path = os.path.join(INPUT_FOLDER, filename)
    resume_id = os.path.splitext(filename)[0]

    print(f"\nProcessing: {filename}")

    # Create image folder for this resume
    resume_image_folder = os.path.join(IMAGE_FOLDER, resume_id)
    os.makedirs(resume_image_folder, exist_ok=True)

    doc = fitz.open(pdf_path)

    full_text = ""
    total_images = 0

    # -----------------------------
    # PROCESS PAGES
    # -----------------------------

    for page_number, page in enumerate(doc, start=1):

        # 1. Extract normal text
        page_text = page.get_text("text")
        full_text += page_text + "\n"

        # 2. Save entire page as PNG
        pix = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )

        page_image_path = os.path.join(
            resume_image_folder,
            f"page_{page_number}.png"
        )

        pix.save(page_image_path)

        # 3. Extract embedded images
        images = page.get_images(full=True)

        for image_number, image in enumerate(images, start=1):

            xref = image[0]

            try:
                image_data = doc.extract_image(xref)

                image_bytes = image_data["image"]
                image_ext = image_data["ext"]

                image_path = os.path.join(
                    resume_image_folder,
                    f"embedded_{page_number}_{image_number}.{image_ext}"
                )

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                total_images += 1

            except Exception as e:
                print(
                    f"Could not extract embedded image "
                    f"from page {page_number}: {e}"
                )

    doc.close()

    # -----------------------------
    # SAVE TEXT
    # -----------------------------

    text_path = os.path.join(
        TEXT_FOLDER,
        f"{resume_id}.txt"
    )

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(full_text.strip())

    # -----------------------------
    # RESULT
    # -----------------------------

    if full_text.strip():
        print(f"Text extracted: {resume_id}.txt")
    else:
        print("No selectable text found.")

    print(f"Page images saved in: extracted_images/{resume_id}/")
    print(f"Embedded images found: {total_images}")


print("\nPDF processing completed!")