import os
import shutil
import tempfile
import unittest
import io
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from app import stamp_files_in_dir, stamp_pdfs_in_dir
from app.common import create_exhibit_stamp

class TestExhibitIndexerIntegration(unittest.TestCase):
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

    def test_stamp_pdfs_in_dir_success(self):
        self._create_sample_pdf("1_exhibit_one.pdf", num_pages=2)
        self._create_sample_pdf("B_exhibit_two.pdf", num_pages=1)
        self._create_sample_pdf("notes.txt")

        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=self.test_dir,
            position="top-right",
            color="red",
            all_pages=False,
            log_callback=logs.append
        )

        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(output_dir))

        stamped_files = os.listdir(output_dir)
        self.assertEqual(len(stamped_files), 2)
        self.assertIn("Exhibit_1_1_exhibit_one.pdf", stamped_files)
        self.assertIn("Exhibit_B_B_exhibit_two.pdf", stamped_files)

    def test_stamp_pdfs_in_dir_nonexistent(self):
        logs = []
        count, output_dir = stamp_files_in_dir(
            input_dir=os.path.join(self.test_dir, "invalid"),
            log_callback=logs.append
        )
        self.assertEqual(count, 0)
        self.assertIsNone(output_dir)

if __name__ == "__main__":
    unittest.main()
