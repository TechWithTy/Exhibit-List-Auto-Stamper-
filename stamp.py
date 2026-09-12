import argparse
import io
import os
import re
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_exhibit_stamp(exhibit_num, position, color_hex):
    """Creates a transparent PDF page with a custom color/positioned stamp."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Dimensions of standard letter page: 612 x 792 points
    # Box dimensions
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

def stamp_pdfs_in_dir(input_dir, position="bottom-right", color="black", all_pages=False, log_callback=None):
    """
    Stamps all PDFs in input_dir with exhibit labels.
    log_callback is an optional callable for progress reporting: log_callback(msg)
    Returns (processed_count, output_dir).
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg)

    # Normalize common color names to Hex strings
    color_map = {
        "black": "#000000",
        "red": "#D32F2F",
        "blue": "#1976D2",
        "navy": "#0D47A1",
    }
    color_hex = color_map.get(str(color).lower(), color)

    # Verify formatting if hex was supplied manually
    if not color_hex.startswith("#"):
        color_hex = f"#{color_hex}"

    if not os.path.exists(input_dir):
        log(f"Error: Directory '{input_dir}' does not exist.")
        return 0, None

    output_dir = os.path.join(input_dir, "stamped_exhibits")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not files:
        log(f"No PDF files found in '{input_dir}'.")
        return 0, output_dir

    processed_count = 0

    for filename in sorted(files):
        filepath = os.path.join(input_dir, filename)
        if not os.path.isfile(filepath):
            continue

        # Match either digits or letters at the start of the filename
        match = re.match(r"^([a-zA-Z0-9]+)", filename)
        if not match:
            log(f"Skipped {filename} (filename must start with numbers or letters)")
            continue

        exhibit_num = match.group(1).upper()
        log(f"Processing {filename} -> EXHIBIT {exhibit_num}")

        reader = PdfReader(filepath)
        writer = PdfWriter()

        try:
            stamp_page = create_exhibit_stamp(exhibit_num, position, color_hex)
        except Exception:
            log(f"Error parsing color choice '{color}'. Defaulting to black.")
            stamp_page = create_exhibit_stamp(exhibit_num, position, "#000000")

        for i, page in enumerate(reader.pages):
            if all_pages or i == 0:
                page.merge_page(stamp_page)
            writer.add_page(page)

        output_path = os.path.join(output_dir, f"Exhibit_{exhibit_num}_{filename}")
        with open(output_path, "wb") as out_file:
            writer.write(out_file)

        processed_count += 1

    log(f"\nDone! Stamped {processed_count} file(s) into '{output_dir}'.")
    return processed_count, output_dir

def main():
    import sys
    parser = argparse.ArgumentParser(
        description="Automatically stamp numbered or lettered PDFs with customized court exhibit labels."
    )
    parser.add_argument(
        "--position",
        choices=["top-right", "top-left", "bottom-right", "bottom-left"],
        default="bottom-right",
        help="Where to place the stamp on the page (default: bottom-right)",
    )
    parser.add_argument(
        "--color",
        default="black",
        help="Text color. Use common names (black, red, blue) or hex codes like #FF0000 (default: black)",
    )
    parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Apply the stamp to every single page of the PDF instead of just the first page",
    )
    parser.add_argument(
        "--dir",
        "-d",
        default=None,
        help="Directory containing the PDFs to stamp (default: current directory or launch GUI if unspecified)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface",
    )

    args = parser.parse_args()

    # Launch GUI if explicitly requested or if no arguments provided
    if args.gui or (len(sys.argv) == 1 and args.dir is None):
        try:
            from gui import launch_gui
            launch_gui()
            return
        except ImportError:
            pass

    target_dir = args.dir if args.dir else "."
    stamp_pdfs_in_dir(target_dir, position=args.position, color=args.color, all_pages=args.all_pages)

if __name__ == "__main__":
    main()

