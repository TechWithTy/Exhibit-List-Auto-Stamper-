from pypdf import PdfReader, PdfWriter
from app.common import create_exhibit_stamp, normalize_color

def process_pdf(filepath, exhibit_num, position="bottom-right", color="black", all_pages=False):
    """
    Reads a PDF file, overlays exhibit stamp on page(s), and returns a PdfWriter object.
    """
    color_hex = normalize_color(color)
    reader = PdfReader(filepath)
    writer = PdfWriter()

    try:
        stamp_page = create_exhibit_stamp(exhibit_num, position, color_hex)
    except Exception:
        stamp_page = create_exhibit_stamp(exhibit_num, position, "#000000")

    for i, page in enumerate(reader.pages):
        if all_pages or i == 0:
            page.merge_page(stamp_page)
        writer.add_page(page)

    return writer
