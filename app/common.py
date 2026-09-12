import io
import re
from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

COLOR_MAP = {
    "black": "#000000",
    "red": "#D32F2F",
    "blue": "#1976D2",
    "navy": "#0D47A1",
}

def normalize_color(color):
    """Normalizes color string names to Hex color codes."""
    color_hex = COLOR_MAP.get(str(color).lower(), str(color))
    if not color_hex.startswith("#"):
        color_hex = f"#{color_hex}"
    return color_hex

def extract_exhibit_number(filename):
    """Extracts alphanumeric exhibit identifier at the start of a filename."""
    match = re.match(r"^([a-zA-Z0-9]+)", filename)
    if match:
        return match.group(1).upper()
    return None

def create_exhibit_stamp(exhibit_num, position, color_hex):
    """Creates a transparent PDF page with a custom color/positioned stamp."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Dimensions of standard letter page: 612 x 792 points
    box_w = 120
    box_h = 32

    # Determine coordinates based on position choice
    if position == "top-right":
        x, y = 612 - box_w - 30, 792 - box_h - 30
    elif position == "top-left":
        x, y = 30, 792 - box_h - 30
    elif position == "bottom-left":
        x, y = 30, 30
    else:  # bottom-right (default)
        x, y = 612 - box_w - 30, 30

    # Draw background box (white fill, dark gray border)
    can.setFillColorRGB(1, 1, 1)
    can.setStrokeColor(HexColor("#333333"))
    can.setLineWidth(1)
    can.rect(x, y, box_w, box_h, fill=1, stroke=1)

    # Use the selected color for text (always Bold)
    can.setFillColor(HexColor(color_hex))
    can.setFont("Helvetica-Bold", 12)

    # Center the text inside the box dynamically
    text = f"EXHIBIT {exhibit_num}"
    can.drawCentredString(x + (box_w / 2), y + 11, text)

    can.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]
