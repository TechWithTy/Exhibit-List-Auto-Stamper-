import io
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.common import create_exhibit_stamp, normalize_color

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')

def convert_image_to_pdf_stream(filepath):
    """Converts an image file into a Letter-sized PDF BytesIO stream."""
    packet = io.BytesIO()
    page_w, page_h = letter  # 612 x 792 points

    try:
        from PIL import Image
        with Image.open(filepath) as img:
            img_w, img_h = img.size
    except Exception:
        img_w, img_h = 612, 792

    # Calculate aspect-ratio scaling to fit on Letter page with margins
    margin = 36
    max_w = page_w - (2 * margin)
    max_h = page_h - (2 * margin)

    scale = min(max_w / img_w, max_h / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x = (page_w - draw_w) / 2
    y = (page_h - draw_h) / 2

    can = canvas.Canvas(packet, pagesize=letter)
    can.drawImage(filepath, x, y, width=draw_w, height=draw_h)
    can.save()
    packet.seek(0)
    return packet

def process_image(filepath, exhibit_num, position="bottom-right", color="black", all_pages=False):
    """
    Converts an image to a PDF stream, applies exhibit stamp, and returns a PdfWriter object.
    """
    color_hex = normalize_color(color)
    pdf_stream = convert_image_to_pdf_stream(filepath)
    reader = PdfReader(pdf_stream)
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
