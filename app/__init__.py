import os
import re
from app.common import extract_exhibit_number, extract_folder_exhibit_number, normalize_color
from app.stamp_pdf import process_pdf
from app.stamp_img import process_image, IMAGE_EXTENSIONS
from app.stamp_doc import process_docx, DOCX_EXTENSIONS
from app.stamp_video import process_video, VIDEO_EXTENSIONS

PDF_EXTENSIONS = ('.pdf',)
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS + DOCX_EXTENSIONS + IMAGE_EXTENSIONS + VIDEO_EXTENSIONS

def stamp_files_in_dir(input_dir, position="bottom-right", color="black", all_pages=False, recursive=False, log_callback=None):
    """
    Batch stamps all supported files (PDFs, DOCX documents, Images, Videos) in input_dir with exhibit labels.
    If recursive=True, scans all nested subdirectories while preserving folder hierarchy in stamped_exhibits.
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

    target_files = []
    if recursive:
        for root, dirs, filenames in os.walk(input_dir):
            dirs[:] = [d for d in dirs if d != "stamped_exhibits" and not d.startswith(".")]
            for f in filenames:
                if f.lower().endswith(SUPPORTED_EXTENSIONS):
                    target_files.append((os.path.join(root, f), os.path.relpath(root, input_dir), f))
        target_files.sort(key=lambda x: (x[1].lower(), x[2].lower()))
    else:
        for f in sorted(os.listdir(input_dir)):
            full_path = os.path.join(input_dir, f)
            if os.path.isfile(full_path) and f.lower().endswith(SUPPORTED_EXTENSIONS):
                target_files.append((full_path, ".", f))

    if not target_files:
        mode_str = " (including nested folders)" if recursive else ""
        log(f"No supported files (PDF, DOCX, Images, Videos) found in '{input_dir}'{mode_str}.")
        return 0, output_dir

    processed_count = 0

    for filepath, rel_dir, filename in target_files:
        ext = os.path.splitext(filename)[1].lower()
        folder_exhibit_num = extract_folder_exhibit_number(rel_dir) if rel_dir != "." else None
        exhibit_num = folder_exhibit_num if folder_exhibit_num else extract_exhibit_number(filename)

        if not exhibit_num:
            log(f"Skipped {filename} (no exhibit identifier found in folder or filename)")
            continue

        display_name = os.path.join(rel_dir, filename) if rel_dir != "." else filename
        log(f"Processing {display_name} ({ext.upper()}) -> EXHIBIT {exhibit_num}")

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
        # Avoid duplicating Exhibit_{x}_ prefix if the original filename already includes it
        clean_prefix = rf"^exhibit[_\-\s]+{re.escape(exhibit_num)}[_\-\s]*"
        remainder = re.sub(clean_prefix, "", base_name, flags=re.IGNORECASE)
        if base_name.lower().startswith("exhibit"):
            output_filename = f"Exhibit_{exhibit_num}_{remainder}.pdf" if remainder else f"Exhibit_{exhibit_num}.pdf"
        elif base_name.lower().startswith(f"{exhibit_num.lower()}_"):
            output_filename = f"Exhibit_{base_name}.pdf"
        else:
            output_filename = f"Exhibit_{exhibit_num}_{base_name}.pdf"
        dest_dir = os.path.join(output_dir, rel_dir) if rel_dir != "." else output_dir
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        output_path = os.path.join(dest_dir, output_filename)
        with open(output_path, "wb") as out_file:
            writer.write(out_file)

        processed_count += 1

    log(f"\nDone! Stamped {processed_count} file(s) into '{output_dir}'.")
    return processed_count, output_dir

stamp_pdfs_in_dir = stamp_files_in_dir
