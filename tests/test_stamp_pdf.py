import io
import os
import shutil
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app.stamp_pdf import process_pdf
from app.common import create_exhibit_stamp

class TestStampPDF(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_pdf(self, filename, num_pages=1):
        filepath = os.path.join(self.test_dir, filename)
        writer = PdfWriter()
        for i in range(num_pages):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(100, 700, f"Sample Document Page {i+1}")
            can.save()
            packet.seek(0)
            reader = PdfReader(packet)
            writer.add_page(reader.pages[0])

        with open(filepath, "wb") as f:
            writer.write(f)
        return filepath

    def test_process_pdf_single_page(self):
        pdf_path = self._create_sample_pdf("1_test.pdf", num_pages=2)
        writer = process_pdf(pdf_path, exhibit_num="1", position="bottom-right", color="black", all_pages=False)
        self.assertIsNotNone(writer)
        self.assertEqual(len(writer.pages), 2)

    def test_process_pdf_all_pages(self):
        pdf_path = self._create_sample_pdf("101_test.pdf", num_pages=3)
        writer = process_pdf(pdf_path, exhibit_num="101", position="top-left", color="red", all_pages=True)
        self.assertIsNotNone(writer)
        self.assertEqual(len(writer.pages), 3)

    def test_create_exhibit_stamp(self):
        stamp = create_exhibit_stamp("A", "top-right", "#000000")
        self.assertIsNotNone(stamp)
        self.assertGreater(stamp.mediabox.width, 0)

if __name__ == "__main__":
    unittest.main()
