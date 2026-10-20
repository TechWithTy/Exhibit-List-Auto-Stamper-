import io
import re
import logging
import warnings
from pypdf import PdfReader
from reportlab.lib.colors import HexColor

# Silence non-critical pypdf parser warnings
logging.getLogger("pypdf").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="pypdf")
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
    """
    Extracts alphanumeric exhibit identifier at the start of a filename.
    Supports both:
      - 'Exhibit_{x}_...' or 'Exhibit_{x}' (e.g., Exhibit_1_Contract.pdf -> '1', Exhibit_A_Notes.pdf -> 'A')
      - Direct '{x}_...' (e.g., 1_Contract.pdf -> '1', 101_Deposition.pdf -> '101')
    """
    # Check for 'Exhibit_{x}_' or 'Exhibit_{x}' convention (case-insensitive)
    exhibit_match = re.match(r"^exhibit[_\-\s]+([a-zA-Z0-9]+)(?=[_\-\s\.]|$)", filename, re.IGNORECASE)
    if exhibit_match:
        return exhibit_match.group(1).upper()

    # Fallback to direct prefix (e.g. 1_..., A_...)
    match = re.match(r"^([a-zA-Z0-9]+)", filename)
    if match:
        return match.group(1).upper()
    return None

def extract_folder_exhibit_number(folder_path):
    """
    Extracts exhibit identifier from a directory path or folder name.
    Inspects relative path components (from top-level down) for patterns like:
      - 'Exhibit_25_Tyrique on 08.31.2026' -> '25'
      - 'Exhibit A - Photos' -> 'A'
      - 'Exhibit 10' -> '10'
      - '25_Tyrique' -> '25'
      - 'A_Financials' -> 'A'
    """
    if not folder_path or folder_path == ".":
        return None

    parts = [p for p in folder_path.replace("\\", "/").split("/") if p and p != "."]
    for part in parts:
        # 1. Explicit 'Exhibit_{x}' convention
        m = re.match(r"^exhibit[_\-\s]+([a-zA-Z0-9]+)(?=[_\-\s\.]|$)", part, re.IGNORECASE)
        if m:
            return m.group(1).upper()

        # 2. Leading digits followed by separator (e.g., 25_Tyrique, 25 - Tyrique)
        m = re.match(r"^(\d+[a-zA-Z]?)(?=[_\-\s]|$)", part)
        if m:
            return m.group(1).upper()

        # 3. Leading single/double letter exhibit followed by separator (e.g., A_Financials, BB - Reports)
        m = re.match(r"^([a-zA-Z]{1,2})(?=[_\-\s])", part)
        if m:
            return m.group(1).upper()

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
