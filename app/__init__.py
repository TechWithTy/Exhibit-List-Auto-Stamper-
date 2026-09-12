import os
from app.common import extract_exhibit_number, normalize_color
from app.stamp_pdf import process_pdf
from app.stamp_img import process_image, IMAGE_EXTENSIONS
from app.stamp_doc import process_docx, DOCX_EXTENSIONS
from app.stamp_video import process_video, VIDEO_EXTENSIONS

PDF_EXTENSIONS = ('.pdf',)
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS + DOCX_EXTENSIONS + IMAGE_EXTENSIONS + VIDEO_EXTENSIONS

def stamp_files_in_dir(input_dir, position="bottom-right", color="black", all_pages=False, log_callback=None):
    """
    Batch stamps all supported files (PDFs, DOCX documents, Images, Videos) in input_dir with exhibit labels.
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    if not os.path.exists(input_dir):
        log(f"Error: Directory '{input_dir}' does not exist.")
        return 0, None

    output_dir = os.path.join(input_dir, "stamped_exhibits")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not files:
        log(f"No supported files (PDF, DOCX, Images, Videos) found in '{input_dir}'.")
        return 0, output_dir

    processed_count = 0

    for filename in sorted(files):
        filepath = os.path.join(input_dir, filename)
        if not os.path.isfile(filepath):
            continue

        ext = os.path.splitext(filename)[1].lower()
        exhibit_num = extract_exhibit_number(filename)

        if not exhibit_num:
            log(f"Skipped {filename} (filename must start with numbers or letters)")
            continue

        log(f"Processing {filename} ({ext.upper()}) -> EXHIBIT {exhibit_num}")

        try:
            if ext in PDF_EXTENSIONS:
                writer = process_pdf(filepath, exhibit_num, position, color, all_pages)
            elif ext in IMAGE_EXTENSIONS:
                writer = process_image(filepath, exhibit_num, position, color, all_pages)
            elif ext in DOCX_EXTENSIONS:
                writer = process_docx(filepath, exhibit_num, position, color, all_pages)
            elif ext in VIDEO_EXTENSIONS:
                writer = process_video(filepath, exhibit_num, position, color, all_pages)
            else:
                continue
        except Exception as e:
            log(f"Error processing '{filename}': {str(e)}")
            continue

        base_name = os.path.splitext(filename)[0]
        output_filename = f"Exhibit_{exhibit_num}_{base_name}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "wb") as out_file:
            writer.write(out_file)

        processed_count += 1

    log(f"\nDone! Stamped {processed_count} file(s) into '{output_dir}'.")
    return processed_count, output_dir

stamp_pdfs_in_dir = stamp_files_in_dir
