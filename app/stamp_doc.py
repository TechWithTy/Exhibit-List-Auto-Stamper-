import io
import os
import shutil
import tempfile
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.common import create_exhibit_stamp, normalize_color

DOCX_EXTENSIONS = ('.docx', '.doc')

def convert_docx_to_pdf_stream(filepath):
    """Converts a DOCX file to a PDF BytesIO stream."""
    temp_dir = tempfile.mkdtemp()
    temp_pdf = os.path.join(temp_dir, "temp_converted.pdf")

    try:
        # Try docx2pdf if installed
        try:
            from docx2pdf import convert
            convert(filepath, temp_pdf)
            if os.path.exists(temp_pdf):
                with open(temp_pdf, "rb") as f:
                    data = f.read()
                return io.BytesIO(data)
        except Exception:
            pass

        # Try win32com on Windows if MS Word is installed
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            abs_in = os.path.abspath(filepath)
            abs_out = os.path.abspath(temp_pdf)
            doc = word.Documents.Open(abs_in)
            doc.SaveAs(abs_out, FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
            word.Quit()
            if os.path.exists(temp_pdf):
                with open(temp_pdf, "rb") as f:
                    data = f.read()
                return io.BytesIO(data)
        except Exception:
            pass

        # Fallback: Render paragraph text directly into PDF using reportlab + python-docx
        try:
            import docx
            doc = docx.Document(filepath)
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            y = 750
            can.setFont("Helvetica", 10)
            for p in doc.paragraphs:
                text = p.text.strip()
                if text:
                    if y < 50:
                        can.showPage()
                        can.setFont("Helvetica", 10)
                        y = 750
                    can.drawString(50, y, text[:90])
                    y -= 15
            can.save()
            packet.seek(0)
            return packet
        except Exception:
            pass

        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def process_docx(filepath, exhibit_num, position="bottom-right", color="black", all_pages=False):
    """
    Converts a DOCX file to PDF stream, applies exhibit stamp, and returns a PdfWriter object.
    """
    color_hex = normalize_color(color)
    pdf_stream = convert_docx_to_pdf_stream(filepath)
    if pdf_stream is None:
        raise ValueError(f"Could not convert '{filepath}' to PDF.")

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
