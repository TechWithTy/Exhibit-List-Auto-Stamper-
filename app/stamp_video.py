import io
import os
import tempfile
import shutil
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from app.common import create_exhibit_stamp, normalize_color

VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.wmv')

def extract_video_thumbnail_and_info(filepath):
    """
    Extracts video duration, resolution, file size, and a thumbnail frame if OpenCV is installed.
    """
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    info = {
        "filename": os.path.basename(filepath),
        "size_str": f"{file_size_mb:.2f} MB",
        "duration_str": "Unknown",
        "resolution_str": "Unknown",
        "thumbnail_path": None,
        "temp_dir": None
    }

    # Try extracting frame using OpenCV if available
    try:
        import cv2
        cap = cv2.VideoCapture(filepath)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if fps > 0 and frame_count > 0:
                duration_sec = frame_count / fps
                mins, secs = divmod(int(duration_sec), 60)
                info["duration_str"] = f"{mins}m {secs}s ({duration_sec:.1f}s)"

            if width > 0 and height > 0:
                info["resolution_str"] = f"{width} x {height}"

            # Grab frame at 20% mark
            target_frame = int(frame_count * 0.2)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()

            if ret and frame is not None:
                temp_dir = tempfile.mkdtemp()
                info["temp_dir"] = temp_dir
                thumb_path = os.path.join(temp_dir, "thumbnail.jpg")
                cv2.imwrite(thumb_path, frame)
                info["thumbnail_path"] = thumb_path

            cap.release()
    except Exception:
        pass

    return info

def create_video_cover_pdf_stream(filepath, exhibit_num):
    """Generates a legal Video Exhibit Cover Sheet PDF stream."""
    packet = io.BytesIO()
    info = extract_video_thumbnail_and_info(filepath)
    page_w, page_h = letter  # 612 x 792 points

    can = canvas.Canvas(packet, pagesize=letter)

    # Document Header
    can.setFont("Helvetica-Bold", 18)
    can.setFillColor(HexColor("#1A2530"))
    can.drawString(50, 730, "VIDEO EVIDENCE EXHIBIT COVER SHEET")

    can.setStrokeColor(HexColor("#CCCCCC"))
    can.setLineWidth(1)
    can.line(50, 715, 562, 715)

    # Video Metadata Box
    can.setFont("Helvetica-Bold", 12)
    can.setFillColor(HexColor("#333333"))
    can.drawString(50, 680, "Exhibit Details & File Information")

    can.setFont("Helvetica", 10)
    y_pos = 655
    meta_items = [
        ("Exhibit ID:", f"EXHIBIT {exhibit_num}"),
        ("Source File:", info["filename"]),
        ("File Size:", info["size_str"]),
        ("Duration:", info["duration_str"]),
        ("Resolution:", info["resolution_str"]),
    ]

    for label, val in meta_items:
        can.setFont("Helvetica-Bold", 10)
        can.drawString(60, y_pos, label)
        can.setFont("Helvetica", 10)
        can.drawString(160, y_pos, str(val))
        y_pos -= 20

    # Draw Thumbnail Preview if extracted
    if info["thumbnail_path"] and os.path.exists(info["thumbnail_path"]):
        can.setFont("Helvetica-Bold", 12)
        can.drawString(50, 520, "Video Keyframe Preview:")

        try:
            # Draw preview thumbnail box
            can.drawImage(info["thumbnail_path"], 50, 240, width=512, height=260, preserveAspectRatio=True)
            can.setStrokeColor(HexColor("#999999"))
            can.rect(50, 240, 512, 260, fill=0, stroke=1)
        except Exception:
            pass
    else:
        # Placeholder box for video preview
        can.setStrokeColor(HexColor("#DDDDDD"))
        can.setFillColorRGB(0.96, 0.96, 0.96)
        can.rect(50, 260, 512, 220, fill=1, stroke=1)
        can.setFillColor(HexColor("#666666"))
        can.setFont("Helvetica-Bold", 12)
        can.drawCentredString(306, 370, "[ Video Media File Attached ]")
        can.setFont("Helvetica", 10)
        can.drawCentredString(306, 350, f"File Name: {info['filename']}")

    # Footer Disclaimer
    can.setFont("Helvetica-Oblique", 9)
    can.setFillColor(HexColor("#777777"))
    can.drawString(50, 60, "Note: This cover sheet serves as the official stamped exhibit record for the attached media file.")

    can.save()
    packet.seek(0)

    # Clean up temp folder if thumbnail was created
    if info["temp_dir"] and os.path.exists(info["temp_dir"]):
        try:
            shutil.rmtree(info["temp_dir"], ignore_errors=True)
        except Exception:
            pass

    return packet

def process_video(filepath, exhibit_num, position="bottom-right", color="black", all_pages=False):
    """
    Generates a Video Exhibit Cover Sheet PDF, applies exhibit stamp, and returns a PdfWriter.
    """
    color_hex = normalize_color(color)
    pdf_stream = create_video_cover_pdf_stream(filepath, exhibit_num)
    reader = PdfReader(pdf_stream)
    writer = PdfWriter()

    try:
        stamp_page = create_exhibit_stamp(exhibit_num, position, color_hex)
    except Exception:
        stamp_page = create_exhibit_stamp(exhibit_num, position, "#000000")

    for page in reader.pages:
        page.merge_page(stamp_page)
        writer.add_page(page)

    return writer
